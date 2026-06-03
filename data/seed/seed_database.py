"""
SmartCart AI — Database Seeder
Seeds the database with realistic grocery data for development and testing.
"""
import os
import sys
import uuid
import json
import logging
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data.seed.generate_data import STORES, CATEGORIES, PRODUCTS, generate_price_series

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://smartcart:smartcart_secret@localhost:5432/smartcart"
)


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def seed_categories(cur) -> dict:
    """Seed categories and return slug -> id mapping."""
    logger.info("Seeding categories...")
    cat_ids = {}
    for cat in CATEGORIES:
        cat_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO categories (id, name, slug, icon)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
            RETURNING id::text, slug
        """, (cat_id, cat["name"], cat["slug"], cat.get("icon")))
        row = cur.fetchone()
        cat_ids[row[1]] = row[0]
    logger.info(f"  Seeded {len(cat_ids)} categories")
    return cat_ids


def seed_stores(cur) -> dict:
    """Seed stores and return slug -> id mapping."""
    logger.info("Seeding stores...")
    store_ids = {}
    for store in STORES:
        store_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO stores (id, name, slug, website)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
            RETURNING id::text, slug
        """, (store_id, store["name"], store["slug"], store.get("website")))
        row = cur.fetchone()
        store_ids[row[1]] = row[0]
    logger.info(f"  Seeded {len(store_ids)} stores")
    return store_ids


def seed_products(cur, cat_ids: dict) -> dict:
    """Seed products and return name -> id mapping."""
    logger.info("Seeding products...")
    product_ids = {}

    product_data = []
    for product_tuple in PRODUCTS:
        name, brand, cat_slug, base_price, weight_volume = product_tuple
        product_id = str(uuid.uuid4())
        cat_id = cat_ids.get(cat_slug)
        product_data.append((
            product_id, name, brand, cat_id, weight_volume,
            f"{name} — quality grocery product"
        ))
        product_ids[name] = product_id

    execute_batch(cur, """
        INSERT INTO products (id, name, brand, category_id, weight_volume, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, product_data)

    logger.info(f"  Seeded {len(product_ids)} products")
    return product_ids


def seed_store_products(cur, product_ids: dict, store_ids: dict) -> dict:
    """Create store_product records and return (product_id, store_id) -> sp_id."""
    logger.info("Creating store-product associations...")
    sp_ids = {}

    sp_data = []
    for product_name, product_id in product_ids.items():
        for store_slug, store_id in store_ids.items():
            sp_id = str(uuid.uuid4())
            sp_data.append((sp_id, product_id, store_id))
            sp_ids[(product_id, store_id)] = sp_id

    execute_batch(cur, """
        INSERT INTO store_products (id, product_id, store_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (product_id, store_id) DO NOTHING
    """, sp_data)

    logger.info(f"  Created {len(sp_ids)} store-product associations")
    return sp_ids


def seed_price_history(
    cur,
    product_ids: dict,
    store_ids: dict,
    sp_ids: dict,
    days: int = 180,
):
    """Seed price history for all products across all stores."""
    logger.info(f"Seeding {days} days of price history...")

    total_records = 0
    batch = []
    BATCH_SIZE = 5000

    for product_tuple in PRODUCTS:
        name, brand, cat_slug, base_price, weight_volume = product_tuple
        product_id = product_ids.get(name)
        if not product_id:
            continue

        for store_slug, store_id in store_ids.items():
            sp_id = sp_ids.get((product_id, store_id))
            if not sp_id:
                continue

            series = generate_price_series(base_price, store_slug, days=days)

            for price_date, price, is_on_sale, original_price in series:
                batch.append((
                    str(uuid.uuid4()),
                    sp_id,
                    product_id,
                    store_id,
                    price,
                    is_on_sale,
                    original_price,
                    price_date,
                    price_date,
                ))

                if len(batch) >= BATCH_SIZE:
                    execute_batch(cur, """
                        INSERT INTO price_history
                            (id, store_product_id, product_id, store_id, price, is_on_sale, original_price, captured_at, date_captured)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, batch)
                    total_records += len(batch)
                    batch = []
                    logger.info(f"  Inserted {total_records:,} price records...")

    if batch:
        execute_batch(cur, """
            INSERT INTO price_history
                (id, store_product_id, product_id, store_id, price, is_on_sale, original_price, captured_at, date_captured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, batch)
        total_records += len(batch)

    logger.info(f"  Total price records seeded: {total_records:,}")


def seed_recommendations(cur, product_ids: dict):
    """Generate simple price-based recommendations."""
    logger.info("Seeding recommendations...")

    # Group products by category
    from data.seed.generate_data import PRODUCTS as PROD_LIST
    cat_products: dict = {}
    for prod in PROD_LIST:
        name, brand, cat_slug, base_price, _ = prod
        if cat_slug not in cat_products:
            cat_products[cat_slug] = []
        cat_products[cat_slug].append((name, base_price))

    recs = []
    for cat_slug, prods in cat_products.items():
        # Sort by price
        prods_sorted = sorted(prods, key=lambda x: x[1])
        for i, (src_name, src_price) in enumerate(prods_sorted[1:], 1):
            src_id = product_ids.get(src_name)
            if not src_id:
                continue
            for rec_name, rec_price in prods_sorted[:i]:
                rec_id = product_ids.get(rec_name)
                if rec_id and src_id != rec_id and src_price > rec_price:
                    savings = round(src_price - rec_price, 2)
                    recs.append((
                        str(uuid.uuid4()),
                        src_id,
                        rec_id,
                        round(0.7 + (savings / src_price) * 0.3, 4),
                        savings,
                        f"Cheaper alternative in same category (save ${savings:.2f})",
                    ))
                    if len(recs) > 500:
                        break
            if len(recs) > 500:
                break

    execute_batch(cur, """
        INSERT INTO recommendations
            (id, source_product_id, recommended_product_id, similarity_score, price_savings, reason)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, recs[:500])

    logger.info(f"  Seeded {min(len(recs), 500)} recommendations")


def main():
    logger.info("=" * 50)
    logger.info("SmartCart AI — Database Seeder")
    logger.info("=" * 50)

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Seed in order
        cat_ids = seed_categories(cur)
        conn.commit()

        store_ids = seed_stores(cur)
        conn.commit()

        product_ids = seed_products(cur, cat_ids)
        conn.commit()

        sp_ids = seed_store_products(cur, product_ids, store_ids)
        conn.commit()

        seed_price_history(cur, product_ids, store_ids, sp_ids, days=180)
        conn.commit()

        seed_recommendations(cur, product_ids)
        conn.commit()

        cur.close()
        conn.close()

        logger.info("=" * 50)
        logger.info("Database seeding complete!")
        logger.info(f"  Categories: {len(cat_ids)}")
        logger.info(f"  Stores: {len(store_ids)}")
        logger.info(f"  Products: {len(product_ids)}")
        logger.info(f"  Store-Products: {len(sp_ids)}")
        logger.info(f"  Price records: ~{len(product_ids) * len(store_ids) * 180:,}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    main()
