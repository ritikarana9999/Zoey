"""
Tests for Products API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from main import app

client = TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session."""
    with patch("app.database.get_db") as mock:
        db = MagicMock()
        mock.return_value = iter([db])
        yield db


class TestProductsEndpoints:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SmartCart AI"
        assert data["version"] == "1.0.0"

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_products_list_requires_db(self, mock_db):
        """Products endpoint should accept query parameters."""
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        response = client.get("/api/products")
        # Should return 200 with empty list when DB returns nothing
        assert response.status_code == 200

    def test_products_list_with_category_filter(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        response = client.get("/api/products?category=dairy")
        assert response.status_code == 200

    def test_products_list_with_search(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        response = client.get("/api/products?search=milk")
        assert response.status_code == 200

    def test_products_search_requires_min_2_chars(self):
        response = client.get("/api/products/search?q=m")
        assert response.status_code == 422  # Validation error

    def test_products_search_valid_query(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        response = client.get("/api/products/search?q=milk")
        assert response.status_code == 200

    def test_categories_endpoint(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = [
            {"id": "abc123", "name": "Dairy", "slug": "dairy", "icon": "🥛", "product_count": 10}
        ]
        mock_db.execute.return_value = mock_result

        response = client.get("/api/products/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_product_not_found(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.first.return_value = None
        mock_db.execute.return_value = mock_result

        response = client.get("/api/products/nonexistent-id")
        assert response.status_code == 404

    def test_products_limit_parameter(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # Valid limit
        response = client.get("/api/products?limit=10")
        assert response.status_code == 200

        # Exceeds max limit
        response = client.get("/api/products?limit=999")
        assert response.status_code == 422


class TestPricesEndpoints:
    def test_top_movers_endpoint(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        response = client.get("/api/prices/top-movers")
        assert response.status_code == 200

    def test_price_alerts_endpoint(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        response = client.get("/api/prices/alerts")
        assert response.status_code == 200

    def test_stores_endpoint(self, mock_db):
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = [
            {"id": "1", "name": "Woolworths", "slug": "woolworths", "logo_url": None, "website": "https://woolworths.com.au"}
        ]
        mock_db.execute.return_value = mock_result

        response = client.get("/api/prices/stores")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "woolworths"
