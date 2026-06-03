"""
Forecasting service — generates price predictions using XGBoost + time-series features.
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class ForecastingService:
    """Generates 30-day price forecasts using XGBoost with feature engineering."""

    def __init__(self, db: Session):
        self.db = db
        self.horizon = 30

    def _get_price_history(self, product_id: str, store_id: Optional[str] = None) -> pd.DataFrame:
        """Fetch price history for model training."""
        query = """
            SELECT
                ph.date_captured AS ds,
                ph.price AS y,
                ph.store_id::text AS store_id,
                s.name AS store_name,
                ph.is_on_sale
            FROM price_history ph
            JOIN stores s ON s.id = ph.store_id
            WHERE ph.product_id = :product_id
        """
        params = {"product_id": product_id}
        if store_id:
            query += " AND ph.store_id = :store_id"
            params["store_id"] = store_id
        query += " ORDER BY ph.date_captured, ph.store_id"

        result = self.db.execute(text(query), params)
        rows = result.mappings().all()
        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame([dict(r) for r in rows])
        df["ds"] = pd.to_datetime(df["ds"])
        df["y"] = df["y"].astype(float)
        return df

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-series features for XGBoost."""
        df = df.copy().sort_values("ds")
        df["day_of_week"] = df["ds"].dt.dayofweek
        df["day_of_month"] = df["ds"].dt.day
        df["month"] = df["ds"].dt.month
        df["week_of_year"] = df["ds"].dt.isocalendar().week.astype(int)
        df["quarter"] = df["ds"].dt.quarter

        # Lag features
        df["lag_7"] = df["y"].shift(7)
        df["lag_14"] = df["y"].shift(14)
        df["lag_30"] = df["y"].shift(30)

        # Rolling stats
        df["rolling_7_mean"] = df["y"].rolling(7, min_periods=1).mean()
        df["rolling_14_mean"] = df["y"].rolling(14, min_periods=1).mean()
        df["rolling_7_std"] = df["y"].rolling(7, min_periods=1).std().fillna(0)

        # Trend
        df["trend"] = np.arange(len(df))

        return df.dropna(subset=["lag_30"])

    def _train_xgboost(self, df: pd.DataFrame):
        """Train XGBoost model on price history."""
        try:
            from xgboost import XGBRegressor
        except ImportError:
            return None

        features = [
            "day_of_week", "day_of_month", "month", "week_of_year", "quarter",
            "lag_7", "lag_14", "lag_30",
            "rolling_7_mean", "rolling_14_mean", "rolling_7_std", "trend",
        ]

        available = [f for f in features if f in df.columns]
        X = df[available].fillna(df[available].mean())
        y = df["y"]

        model = XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42,
            verbosity=0,
        )
        model.fit(X, y)
        return model, available

    def _simple_forecast(self, df: pd.DataFrame) -> List[dict]:
        """Fallback: linear trend + noise forecast."""
        if df.empty:
            return []

        recent = df["y"].tail(30).values
        trend = (recent[-1] - recent[0]) / max(len(recent), 1) if len(recent) > 1 else 0
        last_price = float(recent[-1])
        std = float(df["y"].std()) if len(df) > 1 else 0.05

        forecast = []
        today = date.today()
        for i in range(1, self.horizon + 1):
            predicted = max(0.01, last_price + trend * i + np.random.normal(0, std * 0.3))
            forecast.append({
                "date": (today + timedelta(days=i)).isoformat(),
                "predicted_price": round(float(predicted), 2),
                "lower_bound": round(float(predicted - std * 1.5), 2),
                "upper_bound": round(float(predicted + std * 1.5), 2),
            })
        return forecast

    def generate_forecast(self, product_id: str, store_id: Optional[str] = None) -> List[dict]:
        """Generate price forecast for a product."""
        df = self._get_price_history(product_id, store_id)

        if df.empty:
            return []

        results = []
        stores = [store_id] if store_id else df["store_id"].unique().tolist()

        for sid in stores:
            store_df = df[df["store_id"] == sid].copy()
            store_name = store_df["store_name"].iloc[0] if not store_df.empty else "Unknown"

            if len(store_df) < 14:
                forecast_points = self._simple_forecast(store_df)
                model_name = "LinearTrend"
            else:
                feat_df = self._engineer_features(store_df)
                try:
                    model, features = self._train_xgboost(feat_df)
                    forecast_points = self._xgb_predict(model, features, feat_df, store_df)
                    model_name = "XGBoost"
                except Exception as e:
                    logger.warning(f"XGBoost failed for {product_id}/{sid}: {e}")
                    forecast_points = self._simple_forecast(store_df)
                    model_name = "LinearTrend"

            # Compute trend direction
            if forecast_points:
                current = float(store_df["y"].iloc[-1])
                final = forecast_points[-1]["predicted_price"]
                pct_change = (final - current) / max(current, 0.01) * 100
                trend = "up" if pct_change > 1 else "down" if pct_change < -1 else "stable"
            else:
                pct_change = 0.0
                trend = "stable"

            results.append({
                "store_id": sid,
                "store_name": store_name,
                "product_id": product_id,
                "current_price": float(store_df["y"].iloc[-1]) if not store_df.empty else None,
                "forecast": forecast_points,
                "trend": trend,
                "predicted_change_pct": round(pct_change, 2),
                "model_name": model_name,
                "recommendation": "Buy now — price rising" if trend == "up" else (
                    "Wait — price falling" if trend == "down" else "Hold — price stable"
                ),
            })

        return results

    def _xgb_predict(self, model, features, feat_df, raw_df) -> List[dict]:
        """Use trained XGBoost model to generate future predictions."""
        today = date.today()
        forecast = []

        last_values = raw_df["y"].values.tolist()
        last_date = raw_df["ds"].iloc[-1]

        for i in range(1, self.horizon + 1):
            future_date = last_date + timedelta(days=i)
            future_df = pd.DataFrame([{
                "day_of_week": future_date.dayofweek,
                "day_of_month": future_date.day,
                "month": future_date.month,
                "week_of_year": future_date.isocalendar()[1],
                "quarter": (future_date.month - 1) // 3 + 1,
                "lag_7": last_values[-7] if len(last_values) >= 7 else last_values[-1],
                "lag_14": last_values[-14] if len(last_values) >= 14 else last_values[-1],
                "lag_30": last_values[-30] if len(last_values) >= 30 else last_values[-1],
                "rolling_7_mean": np.mean(last_values[-7:]),
                "rolling_14_mean": np.mean(last_values[-14:]),
                "rolling_7_std": np.std(last_values[-7:]) if len(last_values) >= 2 else 0.0,
                "trend": len(feat_df) + i,
            }])

            available = [f for f in features if f in future_df.columns]
            pred = float(model.predict(future_df[available])[0])
            pred = max(0.01, pred)

            std_dev = float(np.std(last_values[-30:]) if len(last_values) >= 5 else 0.1)
            forecast.append({
                "date": (today + timedelta(days=i)).isoformat(),
                "predicted_price": round(pred, 2),
                "lower_bound": round(max(0.01, pred - 1.5 * std_dev), 2),
                "upper_bound": round(pred + 1.5 * std_dev, 2),
            })
            last_values.append(pred)

        return forecast

    def generate_and_save_forecast(self, product_id: str):
        """Generate and persist forecasts to the database."""
        forecasts = self.generate_forecast(product_id)
        for store_forecast in forecasts:
            sid = store_forecast["store_id"]
            for point in store_forecast["forecast"]:
                try:
                    self.db.execute(text("""
                        INSERT INTO forecasts
                            (product_id, store_id, forecast_date, predicted_price, lower_bound, upper_bound, model_name, confidence)
                        VALUES
                            (:product_id, :store_id, :forecast_date, :predicted_price, :lower_bound, :upper_bound, :model_name, 0.80)
                        ON CONFLICT DO NOTHING
                    """), {
                        "product_id": product_id,
                        "store_id": sid,
                        "forecast_date": point["date"],
                        "predicted_price": point["predicted_price"],
                        "lower_bound": point.get("lower_bound"),
                        "upper_bound": point.get("upper_bound"),
                        "model_name": store_forecast.get("model_name", "XGBoost"),
                    })
                except Exception as e:
                    logger.error(f"Failed to save forecast point: {e}")
        self.db.commit()
