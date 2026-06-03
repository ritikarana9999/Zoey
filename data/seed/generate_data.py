"""
SmartCart AI — Realistic Grocery Data Generator
Generates 180 days of price history for 100+ products across 3 stores.
"""
import random
import math
from datetime import date, timedelta
from typing import List, Dict, Tuple
import csv
import os

random.seed(42)

# ---- Stores ----
STORES = [
    {"name": "Woolworths", "slug": "woolworths", "website": "https://www.woolworths.com.au"},
    {"name": "Coles", "slug": "coles", "website": "https://www.coles.com.au"},
    {"name": "Aldi", "slug": "aldi", "website": "https://www.aldi.com.au"},
]

# ---- Categories ----
CATEGORIES = [
    {"name": "Dairy", "slug": "dairy", "icon": "🥛"},
    {"name": "Bakery", "slug": "bakery", "icon": "🍞"},
    {"name": "Produce", "slug": "produce", "icon": "🥬"},
    {"name": "Meat & Seafood", "slug": "meat", "icon": "🥩"},
    {"name": "Pantry", "slug": "pantry", "icon": "🥫"},
    {"name": "Beverages", "slug": "beverages", "icon": "🥤"},
    {"name": "Frozen", "slug": "frozen", "icon": "🧊"},
    {"name": "Snacks", "slug": "snacks", "icon": "🍿"},
]

# ---- Products: (name, brand, category_slug, base_price, weight_volume) ----
PRODUCTS = [
    # Dairy
    ("Full Cream Milk 2L", "Woolworths", "dairy", 3.49, "2L"),
    ("Full Cream Milk 3L", "Pauls", "dairy", 5.50, "3L"),
    ("Skim Milk 2L", "Devondale", "dairy", 3.20, "2L"),
    ("Lactose Free Milk 1L", "Liddells", "dairy", 4.50, "1L"),
    ("Greek Yoghurt 500g", "Chobani", "dairy", 4.99, "500g"),
    ("Natural Yoghurt 1kg", "Jalna", "dairy", 6.50, "1kg"),
    ("Butter Salted 250g", "Western Star", "dairy", 5.20, "250g"),
    ("Butter Unsalted 250g", "Lurpak", "dairy", 7.00, "250g"),
    ("Cheddar Cheese 500g", "Mainland", "dairy", 8.00, "500g"),
    ("Tasty Cheese 500g", "Perfect Italiano", "dairy", 7.50, "500g"),
    ("Mozzarella 250g", "Mil Lel", "dairy", 4.80, "250g"),
    ("Sour Cream 300ml", "Bulla", "dairy", 3.00, "300ml"),
    ("Cream 300ml", "Pauls", "dairy", 2.50, "300ml"),
    ("Free Range Eggs 12pk", "Sunny Queen", "dairy", 7.00, "12 pack"),
    ("Eggs 700g Cage Free 12pk", "Coles", "dairy", 5.50, "12 pack"),

    # Bakery
    ("White Sandwich Bread 700g", "Tip Top", "bakery", 3.80, "700g"),
    ("Wholemeal Bread 750g", "Helga's", "bakery", 5.50, "750g"),
    ("Sourdough Loaf 680g", "Bakers Delight", "bakery", 6.00, "680g"),
    ("Multigrain Bread 750g", "Wonder White", "bakery", 4.20, "750g"),
    ("Dinner Rolls 6pk", "Woolworths", "bakery", 3.20, "6 pack"),
    ("Croissants 4pk", "Coles", "bakery", 4.50, "4 pack"),
    ("Crumpets 6pk", "Thomas'", "bakery", 3.00, "6 pack"),
    ("Pita Bread 5pk", "Mission", "bakery", 3.50, "5 pack"),
    ("Wraps 8pk", "Mission", "bakery", 4.00, "8 pack"),
    ("Breadcrumbs 400g", "Panko", "bakery", 3.20, "400g"),

    # Produce
    ("Bananas 1kg", None, "produce", 2.90, "1kg"),
    ("Apples Pink Lady 1kg", None, "produce", 4.50, "1kg"),
    ("Oranges 2kg", None, "produce", 5.00, "2kg"),
    ("Strawberries 250g", None, "produce", 3.50, "250g"),
    ("Baby Spinach 120g", None, "produce", 3.50, "120g"),
    ("Broccoli 1 head", None, "produce", 3.00, "1 head"),
    ("Carrots 1kg", None, "produce", 2.00, "1kg"),
    ("Potatoes 2kg Washed", None, "produce", 4.00, "2kg"),
    ("Tomatoes 400g Punnet", None, "produce", 4.50, "400g"),
    ("Avocado Each", None, "produce", 2.50, "each"),
    ("Capsicum Red Each", None, "produce", 2.50, "each"),
    ("Cucumber Each", None, "produce", 2.00, "each"),
    ("Onion Brown 1kg", None, "produce", 2.00, "1kg"),
    ("Garlic Bulb Each", None, "produce", 1.50, "each"),
    ("Lemon Each", None, "produce", 1.20, "each"),

    # Meat & Seafood
    ("Chicken Breast Fillet 1kg", "Ingham's", "meat", 12.00, "1kg"),
    ("Chicken Thigh Fillets 1kg", "Steggles", "meat", 9.00, "1kg"),
    ("Beef Mince 500g", "Woolworths", "meat", 9.00, "500g"),
    ("Beef Mince 1kg", "Coles", "meat", 15.00, "1kg"),
    ("Lamb Chops 500g", None, "meat", 11.00, "500g"),
    ("Pork Sausages 500g", "Hans", "meat", 8.00, "500g"),
    ("Bacon Rindless 250g", "Don", "meat", 7.50, "250g"),
    ("Salmon Fillets 400g", "Tassal", "meat", 12.00, "400g"),
    ("Tuna in Spring Water 95g", "John West", "meat", 2.00, "95g"),
    ("Prawns Cooked 500g", None, "meat", 14.00, "500g"),

    # Pantry
    ("White Rice 1kg", "SunRice", "pantry", 3.50, "1kg"),
    ("Basmati Rice 1kg", "Uncle Ben's", "pantry", 4.50, "1kg"),
    ("Pasta Penne 500g", "San Remo", "pantry", 2.50, "500g"),
    ("Pasta Spaghetti 500g", "Barilla", "pantry", 3.50, "500g"),
    ("Diced Tomatoes 400g", "Mutti", "pantry", 2.00, "400g"),
    ("Tomato Paste 140g", "Leggo's", "pantry", 1.50, "140g"),
    ("Olive Oil 750ml", "Cobram Estate", "pantry", 12.00, "750ml"),
    ("Canola Oil 750ml", "Crisco", "pantry", 4.50, "750ml"),
    ("Rolled Oats 1kg", "Uncle Toby's", "pantry", 4.50, "1kg"),
    ("Weet-Bix 750g", "Sanitarium", "pantry", 5.50, "750g"),
    ("Cornflakes 725g", "Kellogg's", "pantry", 5.00, "725g"),
    ("White Sugar 1kg", "CSR", "pantry", 2.50, "1kg"),
    ("Plain Flour 1kg", "White Wings", "pantry", 2.50, "1kg"),
    ("Honey 500g", "Capilano", "pantry", 7.00, "500g"),
    ("Peanut Butter Smooth 375g", "Bega", "pantry", 4.50, "375g"),

    # Beverages
    ("Orange Juice 2L", "Tropicana", "beverages", 6.50, "2L"),
    ("Apple Juice 2L", "Golden Circle", "beverages", 4.50, "2L"),
    ("Coca-Cola 1.25L", "Coca-Cola", "beverages", 4.80, "1.25L"),
    ("Pepsi 1.25L", "Pepsi", "beverages", 4.00, "1.25L"),
    ("Sparkling Water 1.25L", "Mount Franklin", "beverages", 2.50, "1.25L"),
    ("Milk Tea 1L", "Lipton", "beverages", 3.00, "1L"),
    ("Coffee Beans 1kg", "Lavazza", "beverages", 20.00, "1kg"),
    ("Instant Coffee 250g", "Nescafé", "beverages", 12.00, "250g"),
    ("Tea Bags 100pk", "Tetley", "beverages", 5.00, "100 pack"),
    ("Energy Drink 4pk", "V", "beverages", 11.00, "4 pack"),

    # Frozen
    ("Frozen Peas 1kg", "Birds Eye", "frozen", 4.00, "1kg"),
    ("Frozen Mixed Veg 1kg", "Woolworths", "frozen", 3.50, "1kg"),
    ("Frozen Chips 1kg", "McCain", "frozen", 5.50, "1kg"),
    ("Frozen Pizza Margherita", "Dr. Oetker", "frozen", 8.00, "each"),
    ("Ice Cream 2L", "Peters", "frozen", 9.00, "2L"),
    ("Frozen Berries Mixed 500g", "Creative Gourmet", "frozen", 6.00, "500g"),
    ("Frozen Fish Fillets 400g", "I&J", "frozen", 8.00, "400g"),
    ("Dim Sims 1kg", "Ming's", "frozen", 9.00, "1kg"),

    # Snacks
    ("Shapes BBQ 175g", "Arnott's", "snacks", 4.00, "175g"),
    ("Tim Tams Original 200g", "Arnott's", "snacks", 5.00, "200g"),
    ("Grain Waves 170g", "Grain Waves", "snacks", 3.50, "170g"),
    ("Smith's Chips Original 170g", "Smith's", "snacks", 4.00, "170g"),
    ("Muesli Bars 6pk", "Uncle Toby's", "snacks", 5.50, "6 pack"),
    ("Rice Crackers 100g", "Sakata", "snacks", 3.00, "100g"),
    ("Dark Chocolate 100g", "Lindt", "snacks", 4.50, "100g"),
    ("Popcorn Salted 100g", "Cobs", "snacks", 3.50, "100g"),
    ("Nuts Mixed 200g", "Woolworths", "snacks", 6.00, "200g"),
    ("Pretzels 200g", "Snyder's", "snacks", 5.00, "200g"),
]


def generate_store_price_multiplier(store_slug: str) -> float:
    """Aldi is typically 10-20% cheaper; Coles and Woolworths are similar."""
    multipliers = {
        "woolworths": 1.00,
        "coles": 0.98,   # Slightly cheaper
        "aldi": 0.82,    # Significantly cheaper
    }
    return multipliers.get(store_slug, 1.0)


def generate_price_series(
    base_price: float,
    store_slug: str,
    days: int = 180,
) -> List[Tuple[date, float, bool, float | None]]:
    """
    Generate realistic price time series with:
    - Store-specific baseline
    - Gradual trend (slight inflation)
    - Random noise
    - Periodic sales (every 2-4 weeks)
    - Seasonal price effects
    """
    multiplier = generate_store_price_multiplier(store_slug)
    store_base = base_price * multiplier

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    series = []
    current_price = store_base

    # Sale schedule: random but periodic
    next_sale_day = random.randint(7, 21)
    sale_duration = 0
    sale_discount = 0.0
    in_sale = False

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        # Gradual inflation trend: ~3% per year
        daily_inflation = (1.03 ** (1 / 365)) - 1
        current_price *= (1 + daily_inflation)

        # Seasonal effect (produce is seasonal, others less so)
        month = current_date.month
        seasonal_factor = 1.0
        if month in [12, 1, 2]:  # Summer in Australia
            seasonal_factor = 1.02  # Slight summer premium
        elif month in [6, 7, 8]:  # Winter
            seasonal_factor = 0.98

        effective_price = current_price * seasonal_factor

        # Random daily noise (±1.5%)
        noise = random.gauss(0, 0.015)
        effective_price *= (1 + noise)

        # Sale logic
        if day_offset >= next_sale_day and not in_sale:
            # Start a sale
            sale_discount = random.uniform(0.10, 0.25)  # 10-25% off
            sale_duration = random.randint(3, 7)  # 3-7 day sale
            in_sale = True
            sale_end_day = day_offset + sale_duration
            next_sale_day = sale_end_day + random.randint(14, 28)  # Next sale

        if in_sale and day_offset >= next_sale_day - sale_duration + sale_duration:
            if day_offset >= next_sale_day - sale_duration + sale_duration:
                in_sale = False

        # Apply sale
        is_on_sale = False
        original_price = None

        if in_sale and day_offset < (next_sale_day - sale_duration + sale_duration):
            is_on_sale = True
            original_price = round(effective_price, 2)
            effective_price *= (1 - sale_discount)

        # Round to nearest 5 cents (Australian pricing)
        effective_price = round(round(effective_price * 20) / 20, 2)
        effective_price = max(0.10, effective_price)

        series.append((current_date, effective_price, is_on_sale, original_price))

    return series


def generate_all_data():
    """Generate complete dataset as Python dictionaries."""
    data = {
        "stores": STORES,
        "categories": CATEGORIES,
        "products": [],
        "price_history": [],
    }

    # Assign categories
    cat_slug_map = {c["slug"]: i for i, c in enumerate(CATEGORIES)}

    for product_tuple in PRODUCTS:
        name, brand, cat_slug, base_price, weight_volume = product_tuple

        product = {
            "name": name,
            "brand": brand,
            "category_slug": cat_slug,
            "base_price": base_price,
            "weight_volume": weight_volume,
            "description": f"{name} — quality {cat_slug} product",
        }
        data["products"].append(product)

        # Generate price history for each store
        for store in STORES:
            series = generate_price_series(base_price, store["slug"], days=180)
            for price_date, price, is_on_sale, original_price in series:
                data["price_history"].append({
                    "product_name": name,
                    "store_slug": store["slug"],
                    "date": price_date.isoformat(),
                    "price": price,
                    "is_on_sale": is_on_sale,
                    "original_price": original_price,
                })

    return data


def save_to_csv(output_dir: str):
    """Save generated data to CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    data = generate_all_data()

    # Save products
    products_file = os.path.join(output_dir, "products.csv")
    with open(products_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "brand", "category_slug", "base_price", "weight_volume"])
        writer.writeheader()
        writer.writerows([{
            "name": p["name"],
            "brand": p["brand"] or "",
            "category_slug": p["category_slug"],
            "base_price": p["base_price"],
            "weight_volume": p["weight_volume"],
        } for p in data["products"]])

    print(f"Saved {len(data['products'])} products to {products_file}")

    # Sample price history (first 1000 records)
    prices_file = os.path.join(output_dir, "price_history_sample.csv")
    with open(prices_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["product_name", "store_slug", "date", "price", "is_on_sale"])
        writer.writeheader()
        writer.writerows(data["price_history"][:1000])

    print(f"Saved sample price history to {prices_file}")
    print(f"Total price records: {len(data['price_history']):,}")


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "..", "sample")
    save_to_csv(output_dir)
