"""
Recommendations router — product alternatives and suggestions.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/{product_id}")
def get_recommendations(
    product_id: str,
    limit: int = Query(5, le=20),
    db: Session = Depends(get_db),
):
    """Get cheaper alternatives for a product."""
    query = text("""
        SELECT
            r.id::text,
            r.recommended_product_id::text AS recommended_id,
            p2.name AS recommended_name,
            p2.brand AS recommended_brand,
            p2.weight_volume,
            r.similarity_score,
            r.price_savings,
            r.reason,
            lp.current_price,
            lp.store_name
        FROM recommendations r
        JOIN products p2 ON p2.id = r.recommended_product_id
        LEFT JOIN (
            SELECT DISTINCT ON (product_id)
                product_id,
                price AS current_price,
                s.name AS store_name
            FROM price_history ph
            JOIN stores s ON s.id = ph.store_id
            ORDER BY product_id, date_captured DESC
        ) lp ON lp.product_id = r.recommended_product_id
        WHERE r.source_product_id = :product_id
        ORDER BY r.price_savings DESC NULLS LAST
        LIMIT :limit
    """)
    result = db.execute(query, {"product_id": product_id, "limit": limit})
    return [dict(r) for r in result.mappings().all()]


@router.get("/similar/{product_id}")
def get_similar_products(
    product_id: str,
    limit: int = Query(8, le=20),
    db: Session = Depends(get_db),
):
    """Get similar products in the same category."""
    query = text("""
        SELECT
            p2.id::text,
            p2.name,
            p2.brand,
            p2.weight_volume,
            c.name AS category_name,
            lp.min_price,
            lp.store_name
        FROM products p1
        JOIN products p2 ON p2.category_id = p1.category_id
            AND p2.id != p1.id
            AND p2.is_active = TRUE
        JOIN categories c ON c.id = p2.category_id
        LEFT JOIN (
            SELECT DISTINCT ON (product_id)
                product_id,
                price AS min_price,
                s.name AS store_name
            FROM price_history ph
            JOIN stores s ON s.id = ph.store_id
            ORDER BY product_id, price ASC
        ) lp ON lp.product_id = p2.id
        WHERE p1.id = :product_id
        ORDER BY lp.min_price ASC NULLS LAST
        LIMIT :limit
    """)
    result = db.execute(query, {"product_id": product_id, "limit": limit})
    return [dict(r) for r in result.mappings().all()]
