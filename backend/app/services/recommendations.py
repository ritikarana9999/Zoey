"""
Recommendations service — find cheaper alternatives using category + price similarity.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Generates product substitution recommendations."""

    def __init__(self, db: Session):
        self.db = db

    def generate_recommendations_for_product(self, product_id: str) -> List[Dict]:
        """Find cheaper alternatives in the same category."""
        # Get source product info
        source_query = text("""
            SELECT
                p.id::text,
                p.name,
                p.category_id,
                c.name AS category_name,
                lp.avg_price AS current_avg_price
            FROM products p
            JOIN categories c ON c.id = p.category_id
            LEFT JOIN (
                SELECT product_id, AVG(price) AS avg_price
                FROM price_history
                WHERE date_captured >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY product_id
            ) lp ON lp.product_id = p.id
            WHERE p.id = :product_id
        """)
        source = self.db.execute(source_query, {"product_id": product_id}).mappings().first()
        if not source:
            return []

        # Find cheaper alternatives in same category
        alts_query = text("""
            SELECT
                p.id::text AS recommended_id,
                p.name,
                p.brand,
                p.weight_volume,
                ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price,
                ROUND(:source_price - AVG(ph.price)::NUMERIC, 2) AS savings
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            WHERE p.category_id = :category_id
              AND p.id != :product_id
              AND p.is_active = TRUE
              AND ph.date_captured >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY p.id, p.name, p.brand, p.weight_volume
            HAVING AVG(ph.price) < :source_price
            ORDER BY savings DESC
            LIMIT 10
        """)
        result = self.db.execute(alts_query, {
            "category_id": str(source["category_id"]),
            "product_id": product_id,
            "source_price": float(source["current_avg_price"] or 0),
        })
        return [dict(r) for r in result.mappings().all()]

    def bulk_generate_and_save(self, limit: int = 100):
        """Generate and save recommendations for top products."""
        products_query = text("""
            SELECT DISTINCT ph.product_id::text
            FROM price_history ph
            WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '7 days'
            LIMIT :limit
        """)
        products = [r[0] for r in self.db.execute(products_query, {"limit": limit}).fetchall()]

        saved = 0
        for pid in products:
            alts = self.generate_recommendations_for_product(pid)
            for alt in alts[:3]:
                try:
                    self.db.execute(text("""
                        INSERT INTO recommendations
                            (source_product_id, recommended_product_id, price_savings, reason)
                        VALUES (:src, :rec, :savings, 'Cheaper alternative in same category')
                        ON CONFLICT DO NOTHING
                    """), {
                        "src": pid,
                        "rec": alt["recommended_id"],
                        "savings": alt.get("savings", 0),
                    })
                    saved += 1
                except Exception as e:
                    logger.warning(f"Could not save recommendation: {e}")
        self.db.commit()
        return {"saved": saved}
