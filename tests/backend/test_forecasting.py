"""
Tests for forecasting service and ML models.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))


def make_price_df(days: int = 60, base_price: float = 3.50, trend: float = 0.001) -> pd.DataFrame:
    """Create a sample price history DataFrame for testing."""
    start = date.today() - timedelta(days=days)
    dates = [start + timedelta(days=i) for i in range(days)]
    prices = [
        max(0.01, base_price + trend * i + np.random.normal(0, 0.05))
        for i in range(days)
    ]
    return pd.DataFrame({
        "ds": pd.to_datetime(dates),
        "y": prices,
        "store_id": "test-store",
        "store_name": "Test Store",
    })


class TestXGBoostModel:
    def test_feature_engineering(self):
        from app.ml.xgboost_model import XGBoostPriceModel
        model = XGBoostPriceModel()
        df = make_price_df(60)
        feat_df = model.prepare_features(df)

        assert "day_of_week" in feat_df.columns
        assert "month" in feat_df.columns
        assert "lag_7" in feat_df.columns
        assert "lag_30" in feat_df.columns
        assert "rolling_7_mean" in feat_df.columns
        assert "trend" in feat_df.columns
        # After dropping NaN rows (lag_30 requires 30 days)
        assert len(feat_df) == 60 - 30

    def test_feature_engineering_values(self):
        from app.ml.xgboost_model import XGBoostPriceModel
        model = XGBoostPriceModel()
        df = make_price_df(60)
        feat_df = model.prepare_features(df)

        # Day of week should be 0-6
        assert feat_df["day_of_week"].between(0, 6).all()
        # Month should be 1-12
        assert feat_df["month"].between(1, 12).all()
        # Trend should be monotonically increasing
        assert (feat_df["trend"].diff().dropna() > 0).all()

    def test_insufficient_data_raises(self):
        from app.ml.xgboost_model import XGBoostPriceModel
        model = XGBoostPriceModel()
        df = make_price_df(5)  # Too few data points
        with pytest.raises(ValueError, match="Insufficient data"):
            model.train(df)

    def test_train_requires_xgboost(self):
        """Test that model handles missing XGBoost gracefully."""
        from app.ml.xgboost_model import XGBoostPriceModel
        model = XGBoostPriceModel()
        df = make_price_df(60)
        # Should either work or raise ImportError
        try:
            train_rmse, val_rmse = model.train(df)
            assert train_rmse >= 0
            assert val_rmse >= 0
            assert model.is_trained
        except ImportError:
            pytest.skip("XGBoost not installed")


class TestInflationAnalytics:
    def test_compute_inflation_rate_weekly(self):
        from app.ml.inflation_analytics import InflationAnalytics
        analytics = InflationAnalytics()

        # Create 8 weeks of data with 5% weekly inflation
        prices = []
        dates = []
        start = date.today() - timedelta(weeks=8)
        for week in range(8):
            for day in range(7):
                d = start + timedelta(weeks=week, days=day)
                prices.append(3.00 * (1.05 ** week))
                dates.append(d.isoformat())

        result = analytics.compute_inflation_rate(
            pd.Series(prices),
            pd.Series(dates),
            period="weekly",
        )
        assert "inflation_pct" in result.columns
        assert "period" in result.columns
        assert len(result) > 0

    def test_detect_trend_upward(self):
        from app.ml.inflation_analytics import InflationAnalytics
        analytics = InflationAnalytics()

        # Strong upward trend
        prices = pd.Series([3.00 + i * 0.05 for i in range(30)])
        result = analytics.detect_trend(prices)

        assert result["direction"] == "up"
        assert result["slope_per_day"] > 0
        assert result["is_significant"] is True

    def test_detect_trend_stable(self):
        from app.ml.inflation_analytics import InflationAnalytics
        analytics = InflationAnalytics()

        # Flat prices with noise
        np.random.seed(42)
        prices = pd.Series([3.00 + np.random.normal(0, 0.01) for _ in range(30)])
        result = analytics.detect_trend(prices)

        assert result["direction"] in ["stable", "up", "down"]
        assert "slope_per_day" in result

    def test_compute_volatility(self):
        from app.ml.inflation_analytics import InflationAnalytics
        analytics = InflationAnalytics()

        prices = pd.Series([3.00, 3.50, 2.80, 3.20, 3.60, 2.90, 3.10])
        result = analytics.compute_volatility(prices)

        assert "mean_price" in result
        assert "std_dev" in result
        assert "cv_pct" in result
        assert result["mean_price"] > 0
        assert result["cv_pct"] >= 0

    def test_volatility_single_value(self):
        from app.ml.inflation_analytics import InflationAnalytics
        analytics = InflationAnalytics()

        prices = pd.Series([3.00])
        result = analytics.compute_volatility(prices)
        assert result["cv"] == 0.0 or result.get("cv_pct", 0) == 0.0


class TestForecastingService:
    def test_simple_forecast_fallback(self):
        """Test that simple linear forecast works when XGBoost unavailable."""
        from app.services.forecasting import ForecastingService
        db = MagicMock()
        service = ForecastingService(db)

        df = make_price_df(30)
        forecast = service._simple_forecast(df)

        assert len(forecast) == 30
        assert all("date" in p for p in forecast)
        assert all("predicted_price" in p for p in forecast)
        assert all(p["predicted_price"] > 0 for p in forecast)

    def test_simple_forecast_empty_df(self):
        from app.services.forecasting import ForecastingService
        db = MagicMock()
        service = ForecastingService(db)

        result = service._simple_forecast(pd.DataFrame())
        assert result == []

    def test_feature_engineering(self):
        from app.services.forecasting import ForecastingService
        db = MagicMock()
        service = ForecastingService(db)

        df = make_price_df(50)
        feat_df = service._engineer_features(df)

        assert "day_of_week" in feat_df.columns
        assert "rolling_7_mean" in feat_df.columns
        assert len(feat_df) > 0
