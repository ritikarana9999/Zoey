"""
Basket optimizer — finds cheapest store or split-store strategy for a grocery list.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BasketOptimizer:
    """Optimizes grocery baskets across stores."""

    def __init__(self, db: Session):
        self.db = db

    def _get_current_prices(self, product_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch latest prices for basket items across all stores."""
        if not product_names:
            return {}

        # Build parameterized ILIKE conditions
        conditions = " OR ".join([f"p.name ILIKE :name_{i}" for i in range(len(product_names))])
        params = {f"name_{i}": f"%{name}%" for i, name in enumerate(product_names)}

        query = f"""
            SELECT DISTINCT ON (p.id, ph.store_id)
                p.id::text AS product_id,
                p.name AS product_name,
                ph.store_id::text,
                s.name AS store_name,
                s.slug AS store_slug,
                ph.price,
                ph.is_on_sale,
                ph.date_captured::text
            FROM products p
            JOIN price_history ph ON ph.product_id = p.id
            JOIN stores s ON s.id = ph.store_id
            WHERE ({conditions})
              AND p.is_active = TRUE
            ORDER BY p.id, ph.store_id, ph.date_captured DESC
        """

        result = self.db.execute(text(query), params)
        rows = result.mappings().all()

        # Structure: {product_name -> {store_slug -> price_info}}
        prices = {}
        for row in rows:
            r = dict(row)
            pname = r["product_name"]
            slug = r["store_slug"]
            if pname not in prices:
                prices[pname] = {}
            prices[pname][slug] = r

        return prices

    def _match_items_to_prices(
        self,
        items: List[Any],
        prices: Dict,
    ) -> Dict[str, Dict[str, Any]]:
        """Match basket items to the fetched price data."""
        matched = {}
        for item in items:
            item_name = item.product_name if hasattr(item, "product_name") else item.get("product_name", "")
            # Find closest match
            for product_name, store_prices in prices.items():
                if item_name.lower() in product_name.lower() or product_name.lower() in item_name.lower():
                    matched[item_name] = store_prices
                    break
        return matched

    def compare_stores(self, items: List[Any]) -> Dict[str, Any]:
        """Return per-store basket totals."""
        item_names = [
            item.product_name if hasattr(item, "product_name") else item.get("product_name", "")
            for item in items
        ]
        prices = self._get_current_prices(item_names)
        matched = self._match_items_to_prices(items, prices)

        # Get all stores
        stores_query = text("SELECT name, slug FROM stores WHERE is_active = TRUE ORDER BY name")
        stores = {row["slug"]: row["name"] for row in self.db.execute(stores_query).mappings().all()}

        store_totals: Dict[str, Dict] = {}
        for slug, name in stores.items():
            total = 0.0
            breakdown = []
            missing = []

            for item in items:
                item_name = item.product_name if hasattr(item, "product_name") else item.get("product_name", "")
                qty = item.quantity if hasattr(item, "quantity") else item.get("quantity", 1)

                if item_name in matched and slug in matched[item_name]:
                    price_info = matched[item_name][slug]
                    line_total = float(price_info["price"]) * qty
                    total += line_total
                    breakdown.append({
                        "product": item_name,
                        "price": float(price_info["price"]),
                        "qty": qty,
                        "line_total": round(line_total, 2),
                        "is_on_sale": price_info.get("is_on_sale", False),
                    })
                else:
                    missing.append(item_name)

            store_totals[slug] = {
                "store_name": name,
                "store_slug": slug,
                "total": round(total, 2),
                "items_found": len(breakdown),
                "items_missing": missing,
                "breakdown": breakdown,
            }

        return {
            "stores": list(store_totals.values()),
            "item_count": len(items),
        }

    def optimize(self, items: List[Any]) -> Dict[str, Any]:
        """Find best single-store and split-store strategy."""
        comparison = self.compare_stores(items)
        stores = comparison["stores"]

        if not stores:
            return {"error": "No price data found for basket items"}

        # Sort by total (stores with all items first)
        stores_with_items = [s for s in stores if s["items_found"] == len(items)]
        all_stores_sorted = sorted(stores, key=lambda x: x["total"])

        best_single = min(
            stores_with_items or all_stores_sorted,
            key=lambda x: x["total"]
        )
        worst_single = max(all_stores_sorted, key=lambda x: x["total"])

        savings = round(worst_single["total"] - best_single["total"], 2)
        savings_pct = round(
            savings / max(worst_single["total"], 0.01) * 100,
            1
        )

        return {
            "best_single_store": best_single,
            "all_stores": all_stores_sorted,
            "potential_savings": savings,
            "savings_pct": savings_pct,
            "recommendation": (
                f"Shop at {best_single['store_name']} to save ${savings:.2f} "
                f"({savings_pct}%) compared to the most expensive option."
            ) if savings > 0 else f"Prices are similar across stores.",
        }
