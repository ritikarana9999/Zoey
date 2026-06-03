"""
Price tracker service — utilities for recording and analyzing price data.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class PriceTrackerService:
    """Records and queries price data."""

    def __init__(self, db: Session):
        self.db = db

    def record_price(
        self,
        product_id: str,
        store_id: str,
        price: float,
        is_on_sale: bool = False,
        original_price: Optional[float] = None,
    ) -> bool:
        """Record a new price observation."""
        try:
            # Get or create store_product
            sp_query = text("""
                INSERT INTO store_products (product_id, store_id)
                VALUES (:product_id, :store_id)
                ON CONFLICT (product_id, store_id) DO UPDATE SET is_available = TRUE
                RETURNING id
            """)
            sp_result = self.db.execute(sp_query, {"product_id": product_id, "store_id": store_id})
            store_product_id = sp_result.scalar()

            # Insert price record
            ph_query = text("""
                INSERT INTO price_history
                    (store_product_id, product_id, store_id, price, is_on_sale, original_price)
                VALUES
                    (:store_product_id, :product_id, :store_id, :price, :is_on_sale, :original_price)
            """)
            self.db.execute(ph_query, {
                "store_product_id": store_product_id,
                "product_id": product_id,
                "store_id": store_id,
                "price": price,
                "is_on_sale": is_on_sale,
                "original_price": original_price,
            })
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to record price: {e}")
            self.db.rollback()
            return False

    def get_price_stats(self, product_id: str, days: int = 90) -> Dict[str, Any]:
        """Get price statistics for a product."""
        query = text("""
            SELECT
                ph.store_id::text,
                s.name AS store_name,
                ROUND(MIN(ph.price)::NUMERIC, 2) AS min_price,
                ROUND(MAX(ph.price)::NUMERIC, 2) AS max_price,
                ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price,
                ROUND(STDDEV(ph.price)::NUMERIC, 4) AS std_dev,
                COUNT(*) AS data_points
            FROM price_history ph
            JOIN stores s ON s.id = ph.store_id
            WHERE ph.product_id = :product_id
              AND ph.date_captured >= CURRENT_DATE - :days * INTERVAL '1 day'
            GROUP BY ph.store_id, s.name
        """)
        result = self.db.execute(query, {"product_id": product_id, "days": days})
        return {"stats": [dict(r) for r in result.mappings().all()]}

    def detect_anomalies(self, threshold_pct: float = 20.0) -> List[Dict]:
        """Detect unusual price spikes or drops vs 30-day average."""
        query = text("""
            WITH avg_prices AS (
                SELECT
                    product_id, store_id,
                    AVG(price) AS avg_30d,
                    STDDEV(price) AS std_30d
                FROM price_history
                WHERE date_captured >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY product_id, store_id
            ),
            current AS (
                SELECT DISTINCT ON (product_id, store_id)
                    product_id, store_id, price AS current_price
                FROM price_history
                ORDER BY product_id, store_id, date_captured DESC
            )
            SELECT
                p.name,
                s.name AS store_name,
                c.current_price,
                a.avg_30d,
                ROUND(((c.current_price - a.avg_30d) / NULLIF(a.avg_30d, 0) * 100)::NUMERIC, 1) AS deviation_pct
            FROM current c
            JOIN avg_prices a ON a.product_id = c.product_id AND a.store_id = c.store_id
            JOIN products p ON p.id = c.product_id
            JOIN stores s ON s.id = c.store_id
            WHERE ABS((c.current_price - a.avg_30d) / NULLIF(a.avg_30d, 0) * 100) > :threshold
            ORDER BY ABS((c.current_price - a.avg_30d) / NULLIF(a.avg_30d, 0) * 100) DESC
        """)
        result = self.db.execute(query, {"threshold": threshold_pct})
        return [dict(r) for r in result.mappings().all()]
