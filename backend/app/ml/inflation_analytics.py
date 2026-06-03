"""
Inflation analytics — statistical analysis of grocery price inflation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class InflationAnalytics:
    """
    Computes grocery-specific inflation metrics.

    Metrics:
    - Week-over-week (WoW) inflation per category
    - Month-over-month (MoM) inflation
    - Annualised inflation rate
    - Price volatility (coefficient of variation)
    - Trend detection (sustained increases/decreases)
    """

    def compute_inflation_rate(
        self,
        prices: pd.Series,
        dates: pd.Series,
        period: str = "weekly",
    ) -> pd.DataFrame:
        """
        Compute period-over-period inflation rates from a price series.

        Args:
            prices: Series of prices
            dates: Series of dates corresponding to prices
            period: 'weekly' or 'monthly'

        Returns:
            DataFrame with period, avg_price, inflation_pct columns
        """
        df = pd.DataFrame({"date": pd.to_datetime(dates), "price": prices.astype(float)})

        freq = "W" if period == "weekly" else "ME"
        grouped = df.groupby(pd.Grouper(key="date", freq=freq))["price"].mean().reset_index()
        grouped.columns = ["period", "avg_price"]
        grouped = grouped.dropna()

        grouped["inflation_pct"] = grouped["avg_price"].pct_change() * 100
        grouped["annualised_pct"] = grouped["inflation_pct"] * (52 if period == "weekly" else 12)

        return grouped.round(4)

    def detect_trend(self, prices: pd.Series, window: int = 14) -> Dict[str, Any]:
        """
        Detect price trend using linear regression.

        Returns:
            dict with slope, direction, p_value, is_significant
        """
        if len(prices) < window:
            return {"direction": "stable", "slope": 0.0, "is_significant": False}

        recent = prices.tail(window).reset_index(drop=True)
        x = np.arange(len(recent))
        y = recent.values.astype(float)

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        direction = "stable"
        if p_value < 0.05:
            if slope > 0.001:
                direction = "up"
            elif slope < -0.001:
                direction = "down"

        return {
            "direction": direction,
            "slope_per_day": round(float(slope), 6),
            "r_squared": round(float(r_value ** 2), 4),
            "p_value": round(float(p_value), 6),
            "is_significant": bool(p_value < 0.05),
            "annualised_pct": round(float(slope * 365 / max(recent.mean(), 0.01) * 100), 2),
        }

    def compute_volatility(self, prices: pd.Series) -> Dict[str, float]:
        """Compute price volatility metrics."""
        if len(prices) < 2:
            return {"cv": 0.0, "std_dev": 0.0, "range_pct": 0.0}

        mean = float(prices.mean())
        std = float(prices.std())
        cv = std / max(mean, 0.01) * 100  # Coefficient of variation

        return {
            "mean_price": round(mean, 2),
            "std_dev": round(std, 4),
            "cv_pct": round(cv, 2),
            "min_price": round(float(prices.min()), 2),
            "max_price": round(float(prices.max()), 2),
            "range_pct": round((float(prices.max()) - float(prices.min())) / max(mean, 0.01) * 100, 2),
        }

    def find_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify seasonal price patterns by month and day-of-week.

        Args:
            df: DataFrame with 'ds' (date) and 'y' (price) columns
        """
        df = df.copy()
        df["ds"] = pd.to_datetime(df["ds"])
        df["month"] = df["ds"].dt.month
        df["dow"] = df["ds"].dt.dayofweek

        monthly = df.groupby("month")["y"].agg(["mean", "std"]).round(4)
        dow = df.groupby("dow")["y"].mean().round(4)

        cheapest_month = int(monthly["mean"].idxmin())
        cheapest_dow = int(dow.idxmin())

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        return {
            "monthly_avg": monthly["mean"].to_dict(),
            "dow_avg": dow.to_dict(),
            "cheapest_month": months[cheapest_month - 1],
            "cheapest_day": days[cheapest_dow],
            "price_range_by_month_pct": round(
                (monthly["mean"].max() - monthly["mean"].min()) /
                max(float(monthly["mean"].mean()), 0.01) * 100,
                2
            ),
        }

    def basket_inflation(
        self,
        basket_prices: Dict[str, List[Dict]],
        base_period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compute inflation for a basket of goods over time.

        Args:
            basket_prices: {product_name: [{date, price}]}
            base_period: Optional base date for index (YYYY-MM-DD)

        Returns:
            basket inflation metrics
        """
        all_records = []
        for product, records in basket_prices.items():
            for r in records:
                all_records.append({"product": product, "date": r["date"], "price": float(r["price"])})

        if not all_records:
            return {}

        df = pd.DataFrame(all_records)
        df["date"] = pd.to_datetime(df["date"])

        weekly = df.groupby(pd.Grouper(key="date", freq="W"))["price"].mean()
        weekly = weekly.dropna()

        if len(weekly) < 2:
            return {"error": "Insufficient data"}

        first_price = float(weekly.iloc[0])
        last_price = float(weekly.iloc[-1])

        total_inflation = (last_price - first_price) / max(first_price, 0.01) * 100
        weeks = len(weekly)
        annualised = total_inflation * (52 / max(weeks, 1))

        return {
            "basket_start_price": round(first_price, 2),
            "basket_current_price": round(last_price, 2),
            "total_inflation_pct": round(total_inflation, 2),
            "annualised_inflation_pct": round(annualised, 2),
            "weeks_measured": weeks,
        }
