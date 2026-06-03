"""
Prices router — current prices, top movers, alerts.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/current")
def get_current_prices(
    category: Optional[str] = None,
    store: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get latest price for each product per store."""
    base = """
        SELECT DISTINCT ON (ph.product_id, ph.store_id)
            ph.product_id::text,
            p.name AS product_name,
            p.brand,
            p.weight_volume,
            c.name AS category_name,
            ph.store_id::text,
            s.name AS store_name,
            s.slug AS store_slug,
            ph.price AS current_price,
            ph.is_on_sale,
            ph.original_price,
            ph.date_captured::text
        FROM price_history ph
        JOIN products p ON p.id = ph.product_id
        JOIN stores s ON s.id = ph.store_id
        JOIN categories c ON c.id = p.category_id
        WHERE p.is_active = TRUE
    """
    params = {"limit": limit, "offset": offset}

    if category:
        base += " AND c.slug = :category"
        params["category"] = category
    if store:
        base += " AND s.slug = :store"
        params["store"] = store

    base += """
        ORDER BY ph.product_id, ph.store_id, ph.date_captured DESC
        LIMIT :limit OFFSET :offset
    """
    result = db.execute(text(base), params)
    return [dict(r) for r in result.mappings().all()]


@router.get("/top-movers")
def get_top_movers(
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """Products with biggest price changes in the last 7 days."""
    query = text("""
        WITH prices_now AS (
            SELECT DISTINCT ON (product_id, store_id)
                product_id, store_id, price AS current_price
            FROM price_history
            ORDER BY product_id, store_id, date_captured DESC
        ),
        prices_week_ago AS (
            SELECT DISTINCT ON (product_id, store_id)
                product_id, store_id, price AS old_price
            FROM price_history
            WHERE date_captured <= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY product_id, store_id, date_captured DESC
        )
        SELECT
            p.id::text AS product_id,
            p.name AS product_name,
            c.name AS category,
            s.name AS store_name,
            pn.current_price,
            pa.old_price,
            ROUND((pn.current_price - pa.old_price)::NUMERIC, 2) AS price_delta,
            ROUND(((pn.current_price - pa.old_price) / NULLIF(pa.old_price, 0) * 100)::NUMERIC, 2) AS pct_change
        FROM prices_now pn
        JOIN prices_week_ago pa ON pa.product_id = pn.product_id AND pa.store_id = pn.store_id
        JOIN products p ON p.id = pn.product_id
        JOIN categories c ON c.id = p.category_id
        JOIN stores s ON s.id = pn.store_id
        ORDER BY ABS(pn.current_price - pa.old_price) DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit})
    rows = []
    for r in result.mappings().all():
        row = dict(r)
        row["direction"] = "up" if row["price_delta"] > 0 else "down"
        rows.append(row)
    return rows


@router.get("/alerts")
def get_price_alerts(
    db: Session = Depends(get_db),
):
    """Products currently near their 90-day low — good time to buy."""
    query = text("""
        WITH price_stats AS (
            SELECT
                product_id,
                store_id,
                MIN(price) AS min_90d,
                AVG(price) AS avg_90d
            FROM price_history
            WHERE date_captured >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY product_id, store_id
        ),
        current_prices AS (
            SELECT DISTINCT ON (product_id, store_id)
                product_id, store_id, price AS current_price
            FROM price_history
            ORDER BY product_id, store_id, date_captured DESC
        )
        SELECT
            p.id::text AS product_id,
            p.name AS product_name,
            c.name AS category,
            s.name AS store_name,
            s.slug AS store_slug,
            cp.current_price,
            ps.min_90d,
            ROUND(ps.avg_90d::NUMERIC, 2) AS avg_90d,
            ROUND(((cp.current_price - ps.min_90d) / NULLIF(ps.avg_90d, 0) * 100)::NUMERIC, 1) AS pct_above_low,
            CASE
                WHEN cp.current_price <= ps.min_90d * 1.05 THEN 'BUY NOW'
                WHEN cp.current_price <= ps.avg_90d THEN 'GOOD PRICE'
                ELSE 'WAIT'
            END AS signal
        FROM current_prices cp
        JOIN price_stats ps ON ps.product_id = cp.product_id AND ps.store_id = cp.store_id
        JOIN products p ON p.id = cp.product_id
        JOIN categories c ON c.id = p.category_id
        JOIN stores s ON s.id = cp.store_id
        ORDER BY pct_above_low ASC
        LIMIT 50
    """)
    result = db.execute(query)
    return [dict(r) for r in result.mappings().all()]


@router.get("/stores")
def get_stores(db: Session = Depends(get_db)):
    """List all active stores."""
    query = text("SELECT id::text, name, slug, logo_url, website FROM stores WHERE is_active = TRUE ORDER BY name")
    result = db.execute(query)
    return [dict(r) for r in result.mappings().all()]
