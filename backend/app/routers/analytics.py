"""
Analytics router — inflation, store comparison, dashboard summary.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.database import get_db

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """High-level metrics for the dashboard."""
    stats_query = text("""
        SELECT
            COUNT(DISTINCT p.id) AS total_products,
            COUNT(DISTINCT s.id) AS total_stores,
            COUNT(DISTINCT c.id) AS total_categories,
            COUNT(ph.id) AS total_price_records,
            ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price_today,
            SUM(CASE WHEN ph.is_on_sale THEN 1 ELSE 0 END) AS items_on_sale
        FROM products p
        CROSS JOIN stores s
        LEFT JOIN price_history ph ON ph.product_id = p.id
            AND ph.date_captured = CURRENT_DATE
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.is_active = TRUE
    """)
    stats = db.execute(stats_query).mappings().first()

    # Week-over-week inflation
    inflation_query = text("""
        WITH weekly AS (
            SELECT
                DATE_TRUNC('week', date_captured) AS week,
                AVG(price) AS avg_price
            FROM price_history
            GROUP BY DATE_TRUNC('week', date_captured)
            ORDER BY week DESC
            LIMIT 2
        )
        SELECT
            MAX(avg_price) FILTER (WHERE week = (SELECT MAX(week) FROM weekly)) AS this_week,
            MAX(avg_price) FILTER (WHERE week = (SELECT MIN(week) FROM weekly)) AS last_week
        FROM weekly
    """)
    infl = db.execute(inflation_query).mappings().first()

    wow_inflation = 0.0
    if infl and infl["this_week"] and infl["last_week"] and infl["last_week"] > 0:
        wow_inflation = round(
            (float(infl["this_week"]) - float(infl["last_week"])) / float(infl["last_week"]) * 100,
            2
        )

    result = dict(stats) if stats else {}
    result["wow_inflation_pct"] = wow_inflation
    return result


@router.get("/inflation")
def get_inflation(
    period: str = Query("weekly", regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db),
):
    """Category-level inflation rates."""
    if period == "weekly":
        query = text("""
            WITH weekly_prices AS (
                SELECT
                    c.name AS category,
                    c.slug,
                    DATE_TRUNC('week', ph.date_captured) AS period,
                    AVG(ph.price) AS avg_price
                FROM price_history ph
                JOIN products p ON p.id = ph.product_id
                JOIN categories c ON c.id = p.category_id
                WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '12 weeks'
                GROUP BY c.name, c.slug, DATE_TRUNC('week', ph.date_captured)
            )
            SELECT
                category,
                slug,
                TO_CHAR(period, 'YYYY-MM-DD') AS period,
                ROUND(avg_price::NUMERIC, 2) AS avg_price,
                ROUND(
                    (avg_price - LAG(avg_price) OVER (PARTITION BY category ORDER BY period)) /
                    NULLIF(LAG(avg_price) OVER (PARTITION BY category ORDER BY period), 0) * 100,
                    2
                ) AS change_pct
            FROM weekly_prices
            ORDER BY category, period
        """)
    else:
        query = text("""
            WITH monthly_prices AS (
                SELECT
                    c.name AS category,
                    c.slug,
                    DATE_TRUNC('month', ph.date_captured) AS period,
                    AVG(ph.price) AS avg_price
                FROM price_history ph
                JOIN products p ON p.id = ph.product_id
                JOIN categories c ON c.id = p.category_id
                WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY c.name, c.slug, DATE_TRUNC('month', ph.date_captured)
            )
            SELECT
                category,
                slug,
                TO_CHAR(period, 'YYYY-MM') AS period,
                ROUND(avg_price::NUMERIC, 2) AS avg_price,
                ROUND(
                    (avg_price - LAG(avg_price) OVER (PARTITION BY category ORDER BY period)) /
                    NULLIF(LAG(avg_price) OVER (PARTITION BY category ORDER BY period), 0) * 100,
                    2
                ) AS change_pct
            FROM monthly_prices
            ORDER BY category, period
        """)

    result = db.execute(query)
    return [dict(r) for r in result.mappings().all()]


@router.get("/store-comparison")
def get_store_comparison(db: Session = Depends(get_db)):
    """Price competitiveness index per store."""
    query = text("""
        WITH latest AS (
            SELECT DISTINCT ON (product_id, store_id)
                product_id, store_id, price
            FROM price_history
            ORDER BY product_id, store_id, date_captured DESC
        ),
        ranked AS (
            SELECT
                product_id,
                store_id,
                price,
                RANK() OVER (PARTITION BY product_id ORDER BY price ASC) AS price_rank
            FROM latest
        )
        SELECT
            s.name AS store_name,
            s.slug,
            COUNT(DISTINCT r.product_id) AS products_tracked,
            ROUND(AVG(r.price)::NUMERIC, 2) AS avg_price,
            SUM(CASE WHEN r.price_rank = 1 THEN 1 ELSE 0 END) AS cheapest_count,
            ROUND(
                SUM(CASE WHEN r.price_rank = 1 THEN 1 ELSE 0 END) * 100.0 /
                NULLIF(COUNT(DISTINCT r.product_id), 0),
                1
            ) AS pct_cheapest
        FROM ranked r
        JOIN stores s ON s.id = r.store_id
        GROUP BY s.name, s.slug
        ORDER BY cheapest_count DESC
    """)
    result = db.execute(query)
    return [dict(r) for r in result.mappings().all()]


@router.get("/price-trends")
def get_price_trends(
    days: int = Query(30, le=180),
    db: Session = Depends(get_db),
):
    """Overall price trend data for the dashboard chart."""
    query = text("""
        SELECT
            date_captured::text AS date,
            ROUND(AVG(price)::NUMERIC, 2) AS avg_price,
            COUNT(DISTINCT product_id) AS products_measured
        FROM price_history
        WHERE date_captured >= CURRENT_DATE - :days * INTERVAL '1 day'
        GROUP BY date_captured
        ORDER BY date_captured
    """)
    result = db.execute(query, {"days": days})
    return [dict(r) for r in result.mappings().all()]


@router.get("/category-breakdown")
def get_category_breakdown(db: Session = Depends(get_db)):
    """Current average prices and recent inflation per category."""
    query = text("""
        WITH current_avg AS (
            SELECT
                c.id::text AS category_id,
                c.name AS category,
                c.slug,
                c.icon,
                ROUND(AVG(ph.price)::NUMERIC, 2) AS current_avg_price,
                COUNT(DISTINCT ph.product_id) AS product_count
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            JOIN categories c ON c.id = p.category_id
            WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY c.id, c.name, c.slug, c.icon
        ),
        month_ago AS (
            SELECT
                p.category_id,
                ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price_30d_ago
            FROM price_history ph
            JOIN products p ON p.id = ph.product_id
            WHERE ph.date_captured BETWEEN CURRENT_DATE - INTERVAL '37 days' AND CURRENT_DATE - INTERVAL '30 days'
            GROUP BY p.category_id
        )
        SELECT
            ca.*,
            ma.avg_price_30d_ago,
            ROUND(
                (ca.current_avg_price - ma.avg_price_30d_ago) /
                NULLIF(ma.avg_price_30d_ago, 0) * 100,
                2
            ) AS mom_change_pct
        FROM current_avg ca
        LEFT JOIN month_ago ma ON ma.category_id::uuid = ca.category_id::uuid
        ORDER BY ca.category
    """)
    result = db.execute(query)
    return [dict(r) for r in result.mappings().all()]
