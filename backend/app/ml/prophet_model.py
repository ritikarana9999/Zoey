"""
Prophet-based price forecasting model (alternative to XGBoost).
Uses Facebook Prophet for time-series decomposition.
"""
import pandas as pd
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ProphetPriceModel:
    """
    Facebook Prophet price forecasting model.

    Handles:
    - Seasonality (weekly, annual)
    - Holiday effects (Australian public holidays)
    - Trend changes (price jumps/drops)
    """

    def __init__(self):
        self.model = None
        self.is_trained = False

    def train(self, df: pd.DataFrame, seasonality_mode: str = "multiplicative") -> dict:
        """Train Prophet model on price history."""
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet not installed. Install with: pip install prophet")

        if len(df) < 14:
            raise ValueError("Need at least 14 days of data for Prophet")

        # Prophet expects columns 'ds' and 'y'
        train_df = df[["ds", "y"]].copy()
        train_df["ds"] = pd.to_datetime(train_df["ds"])
        train_df["y"] = train_df["y"].astype(float)
        train_df = train_df.dropna()

        self.model = Prophet(
            seasonality_mode=seasonality_mode,
            weekly_seasonality=True,
            yearly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            interval_width=0.95,
        )

        # Add Australian holidays as regressors (simplified)
        self.model.add_country_holidays(country_name="AU")

        self.model.fit(train_df)
        self.is_trained = True

        logger.info(f"Prophet trained on {len(train_df)} data points")
        return {"data_points": len(train_df), "status": "trained"}

    def predict_future(self, horizon: int = 30) -> List[dict]:
        """Generate forecasts for future dates."""
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model must be trained before predicting")

        future = self.model.make_future_dataframe(periods=horizon)
        forecast = self.model.predict(future)

        # Return only the future portion
        future_forecast = forecast.tail(horizon)

        result = []
        for _, row in future_forecast.iterrows():
            result.append({
                "date": row["ds"].date().isoformat(),
                "predicted_price": round(max(0.01, float(row["yhat"])), 2),
                "lower_bound": round(max(0.01, float(row["yhat_lower"])), 2),
                "upper_bound": round(float(row["yhat_upper"]), 2),
                "trend": round(float(row["trend"]), 4),
            })

        return result

    def get_components(self) -> Optional[pd.DataFrame]:
        """Get trend and seasonality components."""
        if not self.is_trained or self.model is None:
            return None
        future = self.model.make_future_dataframe(periods=0)
        return self.model.predict(future)[["ds", "trend", "weekly", "yearly"]]
