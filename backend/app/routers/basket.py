"""
Basket router — create, save, and optimize grocery baskets.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import uuid

from app.database import get_db
from app.schemas.basket import BasketCreate, BasketOut, BasketOptimizeRequest, BasketOptimizeResult
from app.services.basket_optimizer import BasketOptimizer

router = APIRouter()


@router.post("/optimize", response_model=dict)
def optimize_basket(request: BasketOptimizeRequest, db: Session = Depends(get_db)):
    """
    Find the cheapest store (or combination) for the basket items.
    Returns per-store totals and a split recommendation if it saves money.
    """
    optimizer = BasketOptimizer(db)
    return optimizer.optimize(request.items)


@router.post("/compare")
def compare_basket(request: BasketOptimizeRequest, db: Session = Depends(get_db)):
    """Compare basket total across all stores."""
    optimizer = BasketOptimizer(db)
    return optimizer.compare_stores(request.items)


@router.post("", response_model=dict)
def save_basket(basket: BasketCreate, db: Session = Depends(get_db)):
    """Save a basket for later retrieval."""
    basket_id = str(uuid.uuid4())
    items_json = [item.dict() for item in basket.items]

    query = text("""
        INSERT INTO baskets (id, name, items, user_id)
        VALUES (:id, :name, :items::jsonb, :user_id)
        RETURNING id::text, name, items, created_at
    """)
    result = db.execute(query, {
        "id": basket_id,
        "name": basket.name,
        "items": str(items_json).replace("'", '"'),
        "user_id": str(basket.user_id) if basket.user_id else None,
    })
    db.commit()
    row = result.mappings().first()
    return dict(row) if row else {"id": basket_id, "name": basket.name}


@router.get("/{basket_id}")
def get_basket(basket_id: str, db: Session = Depends(get_db)):
    """Retrieve a saved basket."""
    query = text("""
        SELECT id::text, name, items, optimization_result, created_at
        FROM baskets WHERE id = :basket_id
    """)
    result = db.execute(query, {"basket_id": basket_id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Basket not found")
    return dict(row)
