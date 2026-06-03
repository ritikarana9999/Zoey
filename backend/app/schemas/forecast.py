from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date


class ForecastOut(BaseModel):
    id: UUID
    product_id: UUID
    store_id: UUID
    forecast_date: date
    predicted_price: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    model_name: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class ForecastPoint(BaseModel):
    date: str
    predicted_price: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class ForecastSeries(BaseModel):
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    current_price: Optional[float] = None
    forecast: List[ForecastPoint] = []
    trend: str = "stable"  # "up", "down", "stable"
    predicted_change_pct: float = 0.0
    recommendation: str = "Hold"
    model_name: str = "XGBoost"
