from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class BasketItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int = 1
    preferred_store: Optional[str] = None


class BasketCreate(BaseModel):
    name: Optional[str] = "My Basket"
    items: List[BasketItem]
    user_id: Optional[UUID] = None


class BasketOut(BaseModel):
    id: UUID
    name: Optional[str]
    items: List[Any]
    optimization_result: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BasketOptimizeRequest(BaseModel):
    items: List[BasketItem]


class StoreBasketTotal(BaseModel):
    store_name: str
    store_slug: str
    total: float
    items_found: int
    items_missing: List[str] = []
    breakdown: List[Dict[str, Any]] = []


class BasketOptimizeResult(BaseModel):
    best_single_store: StoreBasketTotal
    split_recommendation: Optional[Dict[str, Any]] = None
    all_stores: List[StoreBasketTotal] = []
    potential_savings: float = 0.0
    savings_pct: float = 0.0
