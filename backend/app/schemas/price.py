from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class PriceHistoryOut(BaseModel):
    id: UUID
    product_id: UUID
    store_id: UUID
    price: float
    unit_price: Optional[float] = None
    is_on_sale: bool = False
    original_price: Optional[float] = None
    date_captured: date

    class Config:
        from_attributes = True


class CurrentPriceOut(BaseModel):
    product_id: UUID
    product_name: str
    brand: Optional[str] = None
    category_name: str
    store_id: UUID
    store_name: str
    store_slug: str
    current_price: float
    is_on_sale: bool = False
    original_price: Optional[float] = None
    weight_volume: Optional[str] = None
    date_captured: Optional[date] = None

    class Config:
        from_attributes = True


class TopMoverOut(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    category: str
    current_price: float
    old_price: float
    price_delta: float
    pct_change: float
    direction: str  # "up" or "down"
