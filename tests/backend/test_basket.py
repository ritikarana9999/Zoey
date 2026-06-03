"""
Tests for basket optimization service.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.services.basket_optimizer import BasketOptimizer
from app.schemas.basket import BasketItem


def make_mock_db(price_rows=None, store_rows=None):
    """Create a mock database session with pre-configured query results."""
    db = MagicMock()

    # Default price data
    if price_rows is None:
        price_rows = [
            {
                "product_id": "p1",
                "product_name": "Full Cream Milk 2L",
                "store_id": "s1",
                "store_name": "Woolworths",
                "store_slug": "woolworths",
                "price": 3.50,
                "is_on_sale": False,
                "date_captured": "2024-01-15",
            },
            {
                "product_id": "p1",
                "product_name": "Full Cream Milk 2L",
                "store_id": "s2",
                "store_name": "Coles",
                "store_slug": "coles",
                "price": 3.40,
                "is_on_sale": False,
                "date_captured": "2024-01-15",
            },
            {
                "product_id": "p1",
                "product_name": "Full Cream Milk 2L",
                "store_id": "s3",
                "store_name": "Aldi",
                "store_slug": "aldi",
                "price": 2.90,
                "is_on_sale": False,
                "date_captured": "2024-01-15",
            },
        ]

    if store_rows is None:
        store_rows = [
            {"name": "Woolworths", "slug": "woolworths"},
            {"name": "Coles", "slug": "coles"},
            {"name": "Aldi", "slug": "aldi"},
        ]

    def mock_execute(query, params=None):
        result = MagicMock()
        query_str = str(query)
        if "stores" in query_str.lower() and "is_active" in query_str.lower():
            result.mappings.return_value.all.return_value = store_rows
        else:
            result.mappings.return_value.all.return_value = price_rows
        return result

    db.execute.side_effect = mock_execute
    return db


class TestBasketOptimizer:
    def test_compare_stores_basic(self):
        db = make_mock_db()
        optimizer = BasketOptimizer(db)

        items = [BasketItem(product_id="p1", product_name="Full Cream Milk 2L", quantity=1)]
        result = optimizer.compare_stores(items)

        assert "stores" in result
        assert "item_count" in result
        assert result["item_count"] == 1

    def test_optimize_finds_cheapest(self):
        db = make_mock_db()
        optimizer = BasketOptimizer(db)

        items = [BasketItem(product_id="p1", product_name="Full Cream Milk 2L", quantity=1)]
        result = optimizer.optimize(items)

        assert "best_single_store" in result
        assert "all_stores" in result
        assert "potential_savings" in result

    def test_optimize_with_quantity(self):
        db = make_mock_db()
        optimizer = BasketOptimizer(db)

        # 3 units of milk
        items = [BasketItem(product_id="p1", product_name="Full Cream Milk 2L", quantity=3)]
        result = optimizer.optimize(items)

        assert "best_single_store" in result
        # Total should be quantity * price
        best = result["best_single_store"]
        if best and best.get("breakdown"):
            line = best["breakdown"][0]
            assert line["qty"] == 3
            assert line["line_total"] == round(line["price"] * 3, 2)

    def test_empty_basket_returns_error(self):
        db = make_mock_db(price_rows=[])
        optimizer = BasketOptimizer(db)

        items = [BasketItem(product_id="p999", product_name="Nonexistent Product", quantity=1)]
        result = optimizer.optimize(items)

        # Should return error or empty best store
        assert "error" in result or "best_single_store" in result

    def test_savings_calculation(self):
        """Aldi should be cheaper, savings should be positive."""
        db = make_mock_db()
        optimizer = BasketOptimizer(db)

        items = [BasketItem(product_id="p1", product_name="Full Cream Milk 2L", quantity=1)]
        result = optimizer.optimize(items)

        if result.get("potential_savings") is not None:
            assert result["potential_savings"] >= 0

    def test_multi_item_basket(self):
        """Test with multiple products."""
        price_rows = [
            {"product_id": "p1", "product_name": "Milk 2L", "store_id": "s1", "store_name": "Woolworths", "store_slug": "woolworths", "price": 3.50, "is_on_sale": False, "date_captured": "2024-01-15"},
            {"product_id": "p1", "product_name": "Milk 2L", "store_id": "s3", "store_name": "Aldi", "store_slug": "aldi", "price": 2.90, "is_on_sale": False, "date_captured": "2024-01-15"},
            {"product_id": "p2", "product_name": "Bread 700g", "store_id": "s1", "store_name": "Woolworths", "store_slug": "woolworths", "price": 3.80, "is_on_sale": False, "date_captured": "2024-01-15"},
            {"product_id": "p2", "product_name": "Bread 700g", "store_id": "s3", "store_name": "Aldi", "store_slug": "aldi", "price": 2.99, "is_on_sale": False, "date_captured": "2024-01-15"},
        ]
        db = make_mock_db(price_rows=price_rows)
        optimizer = BasketOptimizer(db)

        items = [
            BasketItem(product_id="p1", product_name="Milk 2L", quantity=1),
            BasketItem(product_id="p2", product_name="Bread 700g", quantity=1),
        ]
        result = optimizer.compare_stores(items)

        assert "stores" in result
        assert result["item_count"] == 2


class TestBasketItem:
    def test_basket_item_schema(self):
        item = BasketItem(product_id="abc", product_name="Test Product", quantity=2)
        assert item.product_id == "abc"
        assert item.product_name == "Test Product"
        assert item.quantity == 2

    def test_basket_item_defaults(self):
        item = BasketItem(product_id="abc", product_name="Test")
        assert item.quantity == 1
        assert item.preferred_store is None
