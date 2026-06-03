-- SmartCart AI - Database Views

-- Current prices view (latest price per product per store)
CREATE OR REPLACE VIEW current_prices AS
SELECT DISTINCT ON (ph.product_id, ph.store_id)
    ph.product_id,
    ph.store_id,
    ph.price AS current_price,
    ph.is_on_sale,
    ph.original_price,
    ph.date_captured,
    p.name AS product_name,
    p.brand,
    p.weight_volume,
    s.name AS store_name,
    s.slug AS store_slug,
    c.name AS category_name
FROM price_history ph
JOIN products p ON p.id = ph.product_id
JOIN stores s ON s.id = ph.store_id
JOIN categories c ON c.id = p.category_id
ORDER BY ph.product_id, ph.store_id, ph.date_captured DESC;

-- Best prices view (cheapest store per product)
CREATE OR REPLACE VIEW best_prices AS
SELECT DISTINCT ON (cp.product_id)
    cp.product_id,
    cp.product_name,
    cp.brand,
    cp.category_name,
    cp.store_id,
    cp.store_name,
    cp.current_price AS best_price,
    cp.is_on_sale
FROM current_prices cp
ORDER BY cp.product_id, cp.current_price ASC;

-- Price history summary view
CREATE OR REPLACE VIEW price_summary AS
SELECT
    ph.product_id,
    ph.store_id,
    p.name AS product_name,
    s.name AS store_name,
    ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price_90d,
    MIN(ph.price) AS min_price_90d,
    MAX(ph.price) AS max_price_90d,
    ROUND(STDDEV(ph.price)::NUMERIC, 4) AS price_stddev,
    COUNT(*) AS data_points
FROM price_history ph
JOIN products p ON p.id = ph.product_id
JOIN stores s ON s.id = ph.store_id
WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY ph.product_id, ph.store_id, p.name, s.name;

-- Category inflation view
CREATE OR REPLACE VIEW category_inflation AS
WITH weekly AS (
    SELECT
        p.category_id,
        DATE_TRUNC('week', ph.date_captured) AS week,
        AVG(ph.price) AS avg_price
    FROM price_history ph
    JOIN products p ON p.id = ph.product_id
    GROUP BY p.category_id, DATE_TRUNC('week', ph.date_captured)
)
SELECT
    c.id AS category_id,
    c.name AS category_name,
    w.week,
    ROUND(w.avg_price::NUMERIC, 2) AS avg_price,
    ROUND(
        (w.avg_price - LAG(w.avg_price) OVER (PARTITION BY c.id ORDER BY w.week)) /
        NULLIF(LAG(w.avg_price) OVER (PARTITION BY c.id ORDER BY w.week), 0) * 100,
        2
    ) AS wow_change_pct
FROM weekly w
JOIN categories c ON c.id = w.category_id
ORDER BY c.name, w.week;
