"""
Forecasts router — price predictions.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.database import get_db
from app.services.forecasting import ForecastingService

router = APIRouter()


@router.get("/{product_id}")
def get_forecast(
    product_id: str,
    store_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get 30-day price forecast for a product."""
    # Check for existing forecasts first
    query = """
        SELECT
            f.id::text,
            f.product_id::text,
            f.store_id::text,
            f.forecast_date::text,
            f.predicted_price,
            f.lower_bound,
            f.upper_bound,
            f.model_name,
            f.confidence,
            s.name AS store_name,
            p.name AS product_name
        FROM forecasts f
        JOIN stores s ON s.id = f.store_id
        JOIN products p ON p.id = f.product_id
        WHERE f.product_id = :product_id
          AND f.created_at >= NOW() - INTERVAL '24 hours'
    """
    params = {"product_id": product_id}
    if store_id:
        query += " AND f.store_id = :store_id"
        params["store_id"] = store_id
    query += " ORDER BY f.store_id, f.forecast_date"

    result = db.execute(text(query), params)
    rows = [dict(r) for r in result.mappings().all()]

    if rows:
        return _group_forecasts_by_store(rows)

    # Generate on-the-fly
    service = ForecastingService(db)
    return service.generate_forecast(product_id, store_id)


@router.post("/generate/{product_id}")
def trigger_forecast(
    product_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger model retraining and forecast generation for a product."""
    service = ForecastingService(db)
    background_tasks.add_task(service.generate_and_save_forecast, product_id)
    return {"message": "Forecast generation queued", "product_id": product_id}


@router.get("/category/{category_slug}")
def get_category_forecast(
    category_slug: str,
    db: Session = Depends(get_db),
):
    """Get price outlook for a product category."""
    query = text("""
        WITH monthly AS (
            SELECT
                p.category_id,
                DATE_TRUNC('month', ph.date_captured) AS month,
                AVG(ph.price) AS avg_price
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            JOIN categories c ON c.id = p.category_id
            WHERE c.slug = :slug
              AND ph.date_captured >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY p.category_id, DATE_TRUNC('month', ph.date_captured)
        )
        SELECT
            TO_CHAR(month, 'YYYY-MM') AS month,
            ROUND(avg_price::NUMERIC, 2) AS avg_price,
            ROUND(
                (avg_price - LAG(avg_price) OVER (ORDER BY month)) /
                NULLIF(LAG(avg_price) OVER (ORDER BY month), 0) * 100,
                2
            ) AS mom_change_pct
        FROM monthly
        ORDER BY month
    """)
    result = db.execute(query, {"slug": category_slug})
    return [dict(r) for r in result.mappings().all()]


def _group_forecasts_by_store(rows):
    """Group forecast rows by store into a structured response."""
    stores = {}
    for row in rows:
        sid = row["store_id"]
        if sid not in stores:
            stores[sid] = {
                "store_id": sid,
                "store_name": row["store_name"],
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "forecast": [],
            }
        stores[sid]["forecast"].append({
            "date": row["forecast_date"],
            "predicted_price": float(row["predicted_price"]),
            "lower_bound": float(row["lower_bound"]) if row["lower_bound"] else None,
            "upper_bound": float(row["upper_bound"]) if row["upper_bound"] else None,
        })
    return list(stores.values())
