"""
XGBoost price prediction model with feature engineering.
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class XGBoostPriceModel:
    """
    XGBoost-based grocery price predictor.

    Features:
    - Calendar features (day of week, month, quarter, week of year)
    - Lag features (7, 14, 30 days)
    - Rolling statistics (7-day, 14-day mean and std)
    - Trend (linear time index)
    - Sale frequency encoding
    """

    FEATURES = [
        "day_of_week", "day_of_month", "month", "week_of_year", "quarter",
        "lag_7", "lag_14", "lag_30",
        "rolling_7_mean", "rolling_14_mean", "rolling_7_std",
        "trend",
    ]

    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_importance: dict = {}

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features from raw price history DataFrame."""
        df = df.copy().sort_values("ds")

        # Calendar
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

        # Linear trend
        df["trend"] = np.arange(len(df))

        return df.dropna(subset=["lag_30"])

    def train(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        Train the XGBoost model.
        Returns (train_rmse, val_rmse).
        """
        try:
            from xgboost import XGBRegressor
            from sklearn.metrics import mean_squared_error
        except ImportError:
            raise ImportError("XGBoost and scikit-learn required for training")

        feat_df = self.prepare_features(df)
        if len(feat_df) < 20:
            raise ValueError("Insufficient data for training (need at least 20 points after feature engineering)")

        available = [f for f in self.FEATURES if f in feat_df.columns]
        X = feat_df[available].fillna(feat_df[available].mean())
        y = feat_df["y"]

        # Time-based train/val split
        split = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split], X.iloc[split:]
        y_train, y_val = y.iloc[:split], y.iloc[split:]

        self.model = XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            random_state=42,
            verbosity=0,
            early_stopping_rounds=20,
            eval_metric="rmse",
        )

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        train_pred = self.model.predict(X_train)
        val_pred = self.model.predict(X_val)

        train_rmse = float(np.sqrt(mean_squared_error(y_train, train_pred)))
        val_rmse = float(np.sqrt(mean_squared_error(y_val, val_pred)))

        # Feature importances
        self.feature_importance = dict(zip(available, self.model.feature_importances_))
        self.is_trained = True
        self._available_features = available

        logger.info(f"XGBoost trained | train_rmse={train_rmse:.4f} val_rmse={val_rmse:.4f}")
        return train_rmse, val_rmse

    def predict_future(self, df: pd.DataFrame, horizon: int = 30) -> List[dict]:
        """Generate future price predictions."""
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model must be trained before predicting")

        last_values = df["y"].values.tolist()
        last_date = pd.Timestamp(df["ds"].iloc[-1])
        from datetime import timedelta

        std_dev = float(np.std(last_values[-30:]) if len(last_values) >= 5 else 0.1)
        predictions = []

        for i in range(1, horizon + 1):
            future_date = last_date + timedelta(days=i)
            row = {
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
                "trend": len(df) + i,
            }

            X = pd.DataFrame([row])
            available = [f for f in self._available_features if f in X.columns]
            pred = float(self.model.predict(X[available])[0])
            pred = max(0.01, pred)

            predictions.append({
                "date": future_date.date().isoformat(),
                "predicted_price": round(pred, 2),
                "lower_bound": round(max(0.01, pred - 1.65 * std_dev), 2),
                "upper_bound": round(pred + 1.65 * std_dev, 2),
                "confidence": 0.90,
            })
            last_values.append(pred)

        return predictions
