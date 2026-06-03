"""
Products router — search, list, and detail endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas.product import ProductOut, ProductDetail

router = APIRouter()


@router.get("", response_model=List[dict])
def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List products with optional category filter and full-text search."""
    query = """
        SELECT
            p.id::text,
            p.name,
            p.brand,
            p.weight_volume,
            p.image_url,
            c.name AS category_name,
            c.slug AS category_slug,
            MIN(ph.price) AS min_price,
            MAX(ph.price) AS max_price,
            COUNT(DISTINCT ph.store_id) AS store_count
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN price_history ph ON ph.product_id = p.id
            AND ph.date_captured >= CURRENT_DATE - INTERVAL '7 days'
        WHERE p.is_active = TRUE
    """
    params: dict = {"limit": limit, "offset": offset}

    if category:
        query += " AND c.slug = :category"
        params["category"] = category

    if search:
        query += " AND p.name ILIKE :search"
        params["search"] = f"%{search}%"

    query += """
        GROUP BY p.id, p.name, p.brand, p.weight_volume, p.image_url, c.name, c.slug
        ORDER BY p.name
        LIMIT :limit OFFSET :offset
    """

    result = db.execute(text(query), params)
    rows = result.mappings().all()
    return [dict(row) for row in rows]


@router.get("/search")
def search_products(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    """Full-text search across product names and brands."""
    query = text("""
        SELECT
            p.id::text,
            p.name,
            p.brand,
            p.weight_volume,
            c.name AS category_name,
            ts_rank(to_tsvector('english', p.name || ' ' || COALESCE(p.brand, '')),
                    plainto_tsquery('english', :q)) AS rank
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.is_active = TRUE
          AND (
            to_tsvector('english', p.name || ' ' || COALESCE(p.brand, ''))
            @@ plainto_tsquery('english', :q)
            OR p.name ILIKE :ilike
          )
        ORDER BY rank DESC, p.name
        LIMIT :limit
    """)
    result = db.execute(query, {"q": q, "ilike": f"%{q}%", "limit": limit})
    rows = result.mappings().all()
    return [dict(row) for row in rows]


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """List all product categories with product counts."""
    query = text("""
        SELECT
            c.id::text,
            c.name,
            c.slug,
            c.icon,
            COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id AND p.is_active = TRUE
        GROUP BY c.id, c.name, c.slug, c.icon
        ORDER BY c.name
    """)
    result = db.execute(query)
    return [dict(row) for row in result.mappings().all()]


@router.get("/{product_id}", response_model=dict)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get detailed product information including prices across all stores."""
    query = text("""
        SELECT
            p.id::text,
            p.name,
            p.brand,
            p.description,
            p.weight_volume,
            p.weight_grams,
            p.image_url,
            p.barcode,
            c.name AS category_name,
            c.slug AS category_slug
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.id = :product_id AND p.is_active = TRUE
    """)
    result = db.execute(query, {"product_id": product_id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    product = dict(row)

    # Get current prices per store
    prices_query = text("""
        SELECT DISTINCT ON (ph.store_id)
            ph.store_id::text,
            s.name AS store_name,
            s.slug AS store_slug,
            ph.price AS current_price,
            ph.is_on_sale,
            ph.original_price,
            ph.date_captured::text
        FROM price_history ph
        JOIN stores s ON s.id = ph.store_id
        WHERE ph.product_id = :product_id
        ORDER BY ph.store_id, ph.date_captured DESC
    """)
    prices_result = db.execute(prices_query, {"product_id": product_id})
    product["store_prices"] = [dict(r) for r in prices_result.mappings().all()]

    # Price stats
    stats_query = text("""
        SELECT
            ROUND(MIN(price)::NUMERIC, 2) AS min_price,
            ROUND(MAX(price)::NUMERIC, 2) AS max_price,
            ROUND(AVG(price)::NUMERIC, 2) AS avg_price
        FROM price_history
        WHERE product_id = :product_id
          AND date_captured >= CURRENT_DATE - INTERVAL '90 days'
    """)
    stats = db.execute(stats_query, {"product_id": product_id}).mappings().first()
    if stats:
        product.update(dict(stats))

    return product


@router.get("/{product_id}/price-history")
def get_price_history(
    product_id: str,
    days: int = Query(90, le=365),
    store_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get price history for a product, optionally filtered by store."""
    query = """
        SELECT
            ph.date_captured::text AS date,
            ph.price,
            ph.is_on_sale,
            ph.original_price,
            s.name AS store_name,
            s.slug AS store_slug
        FROM price_history ph
        JOIN stores s ON s.id = ph.store_id
        WHERE ph.product_id = :product_id
          AND ph.date_captured >= CURRENT_DATE - INTERVAL ':days days'
    """
    params = {"product_id": product_id, "days": days}

    if store_id:
        query += " AND ph.store_id = :store_id"
        params["store_id"] = store_id

    query = """
        SELECT
            ph.date_captured::text AS date,
            ph.price,
            ph.is_on_sale,
            ph.original_price,
            s.name AS store_name,
            s.slug AS store_slug
        FROM price_history ph
        JOIN stores s ON s.id = ph.store_id
        WHERE ph.product_id = :product_id
          AND ph.date_captured >= CURRENT_DATE - :days * INTERVAL '1 day'
        ORDER BY ph.date_captured, s.name
    """
    result = db.execute(text(query), {"product_id": product_id, "days": days})
    return [dict(r) for r in result.mappings().all()]


@router.post("", response_model=dict, status_code=201)
def create_product(payload: dict, db: Session = Depends(get_db)):
    """Create a new product with an initial price entry."""
    from uuid import uuid4
    from datetime import date

    # Look up or create category
    cat_row = db.execute(
        text("SELECT id FROM categories WHERE slug = :slug"),
        {"slug": payload.get("category_slug", "pantry")}
    ).mappings().first()
    category_id = str(cat_row["id"]) if cat_row else None

    # Insert product
    product_id = str(uuid4())
    db.execute(text("""
        INSERT INTO products (id, name, brand, category_id, weight_volume, description, is_active, created_at, updated_at)
        VALUES (:id, :name, :brand, :category_id, :weight_volume, :description, TRUE, NOW(), NOW())
    """), {
        "id": product_id,
        "name": payload["name"],
        "brand": payload.get("brand", ""),
        "category_id": category_id,
        "weight_volume": payload.get("weight_volume", ""),
        "description": payload.get("description", ""),
    })

    # For each store price provided, insert store_product + price_history
    for store_price in payload.get("store_prices", []):
        store_row = db.execute(
            text("SELECT id FROM stores WHERE slug = :slug"),
            {"slug": store_price["store_slug"]}
        ).mappings().first()
        if not store_row:
            continue
        store_id = str(store_row["id"])

        sp_id = str(uuid4())
        db.execute(text("""
            INSERT INTO store_products (id, product_id, store_id, is_available, created_at)
            VALUES (:id, :product_id, :store_id, TRUE, NOW())
            ON CONFLICT (product_id, store_id) DO NOTHING
        """), {"id": sp_id, "product_id": product_id, "store_id": store_id})

        db.execute(text("""
            INSERT INTO price_history (id, product_id, store_id, price, unit_price, is_on_sale, captured_at, date_captured)
            VALUES (:id, :product_id, :store_id, :price, :unit_price, FALSE, NOW(), CURRENT_DATE)
        """), {
            "id": str(uuid4()),
            "product_id": product_id,
            "store_id": store_id,
            "price": float(store_price["price"]),
            "unit_price": float(store_price["price"]),
        })

    db.commit()
    return {"id": product_id, "name": payload["name"], "message": "Product created successfully"}
