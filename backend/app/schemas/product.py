from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    weight_volume: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    category_id: UUID


class ProductOut(ProductBase):
    id: UUID
    category_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StorePrice(BaseModel):
    store_id: UUID
    store_name: str
    store_slug: str
    current_price: Optional[float] = None
    is_on_sale: bool = False
    original_price: Optional[float] = None
    date_captured: Optional[str] = None


class ProductDetail(ProductOut):
    category_name: Optional[str] = None
    store_prices: List[StorePrice] = []
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    price_verdict: Optional[str] = None
