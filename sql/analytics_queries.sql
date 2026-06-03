-- SmartCart AI - Advanced Analytics Queries

-- 1. Price trend over 30 days per product per store (window function)
SELECT
    p.name AS product_name,
    s.name AS store_name,
    ph.date_captured,
    ph.price,
    AVG(ph.price) OVER (
        PARTITION BY ph.product_id, ph.store_id
        ORDER BY ph.date_captured
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day,
    FIRST_VALUE(ph.price) OVER (
        PARTITION BY ph.product_id, ph.store_id
        ORDER BY ph.date_captured
    ) AS first_price,
    ph.price - FIRST_VALUE(ph.price) OVER (
        PARTITION BY ph.product_id, ph.store_id
        ORDER BY ph.date_captured
    ) AS price_change_total
FROM price_history ph
JOIN products p ON p.id = ph.product_id
JOIN stores s ON s.id = ph.store_id
WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY p.name, s.name, ph.date_captured;

-- 2. Category-level inflation rate (week over week)
WITH weekly_prices AS (
    SELECT
        c.name AS category,
        DATE_TRUNC('week', ph.date_captured) AS week,
        AVG(ph.price) AS avg_price
    FROM price_history ph
    JOIN products p ON p.id = ph.product_id
    JOIN categories c ON c.id = p.category_id
    GROUP BY c.name, DATE_TRUNC('week', ph.date_captured)
),
inflation AS (
    SELECT
        category,
        week,
        avg_price,
        LAG(avg_price) OVER (PARTITION BY category ORDER BY week) AS prev_week_price,
        ROUND(
            ((avg_price - LAG(avg_price) OVER (PARTITION BY category ORDER BY week))
            / NULLIF(LAG(avg_price) OVER (PARTITION BY category ORDER BY week), 0)) * 100,
            2
        ) AS wow_inflation_pct
    FROM weekly_prices
)
SELECT * FROM inflation
WHERE week >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY category, week;

-- 3. Best store for each product today
WITH latest_prices AS (
    SELECT DISTINCT ON (product_id, store_id)
        product_id,
        store_id,
        price,
        date_captured
    FROM price_history
    ORDER BY product_id, store_id, date_captured DESC
),
ranked AS (
    SELECT
        p.name AS product_name,
        s.name AS store_name,
        lp.price,
        RANK() OVER (PARTITION BY lp.product_id ORDER BY lp.price ASC) AS price_rank,
        MIN(lp.price) OVER (PARTITION BY lp.product_id) AS min_price,
        MAX(lp.price) OVER (PARTITION BY lp.product_id) AS max_price,
        MAX(lp.price) OVER (PARTITION BY lp.product_id) - MIN(lp.price) OVER (PARTITION BY lp.product_id) AS price_spread
    FROM latest_prices lp
    JOIN products p ON p.id = lp.product_id
    JOIN stores s ON s.id = lp.store_id
)
SELECT * FROM ranked ORDER BY product_name, price_rank;

-- 4. Top 20 biggest price movers this week
WITH prices_now AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        price AS current_price,
        date_captured
    FROM price_history
    ORDER BY product_id, date_captured DESC
),
prices_week_ago AS (
    SELECT DISTINCT ON (product_id)
        product_id,
        price AS old_price
    FROM price_history
    WHERE date_captured <= CURRENT_DATE - INTERVAL '7 days'
    ORDER BY product_id, date_captured DESC
)
SELECT
    p.name,
    c.name AS category,
    pw.current_price,
    pa.old_price,
    ROUND(pw.current_price - pa.old_price, 2) AS price_delta,
    ROUND(((pw.current_price - pa.old_price) / NULLIF(pa.old_price, 0)) * 100, 2) AS pct_change
FROM prices_now pw
JOIN prices_week_ago pa ON pa.product_id = pw.product_id
JOIN products p ON p.id = pw.product_id
JOIN categories c ON c.id = p.category_id
ORDER BY ABS(pw.current_price - pa.old_price) DESC
LIMIT 20;

-- 5. Sale frequency analysis per product
SELECT
    p.name,
    s.name AS store_name,
    COUNT(*) AS total_records,
    SUM(CASE WHEN ph.is_on_sale THEN 1 ELSE 0 END) AS sale_count,
    ROUND(SUM(CASE WHEN ph.is_on_sale THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS sale_frequency_pct,
    ROUND(AVG(CASE WHEN ph.is_on_sale THEN ph.original_price - ph.price END), 2) AS avg_discount_amount
FROM price_history ph
JOIN products p ON p.id = ph.product_id
JOIN stores s ON s.id = ph.store_id
GROUP BY p.name, s.name
HAVING COUNT(*) > 10
ORDER BY sale_frequency_pct DESC;

-- 6. Price volatility index per product
SELECT
    p.name,
    c.name AS category,
    ROUND(STDDEV(ph.price)::NUMERIC, 4) AS price_stddev,
    ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price,
    ROUND((STDDEV(ph.price) / NULLIF(AVG(ph.price), 0) * 100)::NUMERIC, 2) AS coefficient_of_variation,
    MIN(ph.price) AS min_price,
    MAX(ph.price) AS max_price
FROM price_history ph
JOIN products p ON p.id = ph.product_id
JOIN categories c ON c.id = p.category_id
WHERE ph.date_captured >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY p.name, c.name
ORDER BY coefficient_of_variation DESC;

-- 7. Store price competitiveness ranking
WITH store_ranks AS (
    SELECT
        s.name AS store_name,
        COUNT(DISTINCT lp.product_id) AS products_tracked,
        AVG(lp.price) AS avg_price_index,
        SUM(CASE WHEN rank_data.price_rank = 1 THEN 1 ELSE 0 END) AS cheapest_count
    FROM (
        SELECT DISTINCT ON (product_id, store_id)
            product_id, store_id, price
        FROM price_history
        ORDER BY product_id, store_id, date_captured DESC
    ) lp
    JOIN stores s ON s.id = lp.store_id
    LEFT JOIN (
        SELECT
            product_id,
            store_id,
            RANK() OVER (PARTITION BY product_id ORDER BY price) AS price_rank
        FROM (
            SELECT DISTINCT ON (product_id, store_id)
                product_id, store_id, price
            FROM price_history
            ORDER BY product_id, store_id, date_captured DESC
        ) inner_lp
    ) rank_data ON rank_data.product_id = lp.product_id AND rank_data.store_id = lp.store_id
    GROUP BY s.name
)
SELECT
    store_name,
    products_tracked,
    ROUND(avg_price_index::NUMERIC, 2) AS avg_price_index,
    cheapest_count,
    ROUND(cheapest_count * 100.0 / NULLIF(products_tracked, 0), 1) AS pct_cheapest
FROM store_ranks
ORDER BY cheapest_count DESC;

-- 8. Weekly basket cost comparison across stores
WITH basket_items AS (
    SELECT unnest(ARRAY[
        'Full Cream Milk 2L',
        'White Sandwich Bread',
        'Free Range Eggs 12pk',
        'Cheddar Cheese 500g',
        'Chicken Breast 1kg'
    ]) AS item_name
),
latest_prices AS (
    SELECT DISTINCT ON (p.name, ph.store_id)
        p.name,
        ph.store_id,
        ph.price
    FROM price_history ph
    JOIN products p ON p.id = ph.product_id
    ORDER BY p.name, ph.store_id, ph.date_captured DESC
)
SELECT
    s.name AS store_name,
    SUM(lp.price) AS basket_total,
    COUNT(lp.name) AS items_found
FROM basket_items bi
JOIN latest_prices lp ON lp.name ILIKE '%' || bi.item_name || '%'
JOIN stores s ON s.id = lp.store_id
GROUP BY s.name
ORDER BY basket_total;

-- 9. Monthly price trends by category (cohort analysis)
SELECT
    c.name AS category,
    TO_CHAR(DATE_TRUNC('month', ph.date_captured), 'YYYY-MM') AS month,
    ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price,
    COUNT(DISTINCT ph.product_id) AS products_measured,
    ROUND(
        (AVG(ph.price) - FIRST_VALUE(AVG(ph.price)) OVER (
            PARTITION BY c.name ORDER BY DATE_TRUNC('month', ph.date_captured)
        )) / NULLIF(FIRST_VALUE(AVG(ph.price)) OVER (
            PARTITION BY c.name ORDER BY DATE_TRUNC('month', ph.date_captured)
        ), 0) * 100,
        2
    ) AS pct_change_from_baseline
FROM price_history ph
JOIN products p ON p.id = ph.product_id
JOIN categories c ON c.id = p.category_id
GROUP BY c.name, DATE_TRUNC('month', ph.date_captured)
ORDER BY c.name, month;

-- 10. Products with sustained price increases (3+ consecutive weeks)
WITH weekly_avg AS (
    SELECT
        product_id,
        DATE_TRUNC('week', date_captured) AS week,
        AVG(price) AS avg_price
    FROM price_history
    GROUP BY product_id, DATE_TRUNC('week', date_captured)
),
with_lag AS (
    SELECT
        product_id,
        week,
        avg_price,
        LAG(avg_price) OVER (PARTITION BY product_id ORDER BY week) AS prev_avg
    FROM weekly_avg
),
is_increase AS (
    SELECT
        product_id,
        week,
        avg_price,
        CASE WHEN avg_price > prev_avg THEN 1 ELSE 0 END AS is_up
    FROM with_lag
    WHERE prev_avg IS NOT NULL
),
streaks AS (
    SELECT
        product_id,
        week,
        is_up,
        SUM(CASE WHEN is_up = 0 THEN 1 ELSE 0 END) OVER (
            PARTITION BY product_id ORDER BY week
        ) AS streak_group
    FROM is_increase
)
SELECT
    p.name,
    MAX(s.week) AS last_week,
    COUNT(*) AS consecutive_increases
FROM streaks s
JOIN products p ON p.id = s.product_id
WHERE s.is_up = 1
GROUP BY p.name, s.product_id, s.streak_group
HAVING COUNT(*) >= 3
ORDER BY consecutive_increases DESC;

-- 11. Price percentile analysis
SELECT
    p.name,
    s.name AS store_name,
    ph.price AS current_price,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ph2.price) AS p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY ph2.price) AS median_price,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ph2.price) AS p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY ph2.price) AS p90,
    CASE
        WHEN ph.price <= PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ph2.price) THEN 'GREAT DEAL'
        WHEN ph.price <= PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY ph2.price) THEN 'GOOD PRICE'
        WHEN ph.price <= PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ph2.price) THEN 'FAIR PRICE'
        ELSE 'HIGH PRICE'
    END AS price_verdict
FROM (
    SELECT DISTINCT ON (product_id, store_id)
        product_id, store_id, price
    FROM price_history
    ORDER BY product_id, store_id, date_captured DESC
) ph
JOIN price_history ph2 ON ph2.product_id = ph.product_id AND ph2.store_id = ph.store_id
JOIN products p ON p.id = ph.product_id
JOIN stores s ON s.id = ph.store_id
GROUP BY p.name, s.name, ph.price
ORDER BY p.name;

-- 12. Seasonal price patterns (by month)
SELECT
    p.name,
    EXTRACT(MONTH FROM ph.date_captured) AS month_num,
    TO_CHAR(ph.date_captured, 'Month') AS month_name,
    ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price,
    ROUND(MIN(ph.price)::NUMERIC, 2) AS min_price,
    ROUND(MAX(ph.price)::NUMERIC, 2) AS max_price
FROM price_history ph
JOIN products p ON p.id = ph.product_id
GROUP BY p.name, EXTRACT(MONTH FROM ph.date_captured), TO_CHAR(ph.date_captured, 'Month')
ORDER BY p.name, month_num;

-- 13. Substitution savings opportunities
SELECT
    p1.name AS original_product,
    p2.name AS substitute_product,
    c.name AS category,
    lp1.price AS original_price,
    lp2.price AS substitute_price,
    ROUND(lp1.price - lp2.price, 2) AS savings,
    ROUND((lp1.price - lp2.price) / NULLIF(lp1.price, 0) * 100, 1) AS savings_pct
FROM recommendations r
JOIN products p1 ON p1.id = r.source_product_id
JOIN products p2 ON p2.id = r.recommended_product_id
JOIN categories c ON c.id = p1.category_id
JOIN (
    SELECT DISTINCT ON (product_id) product_id, price
    FROM price_history ORDER BY product_id, date_captured DESC
) lp1 ON lp1.product_id = p1.id
JOIN (
    SELECT DISTINCT ON (product_id) product_id, price
    FROM price_history ORDER BY product_id, date_captured DESC
) lp2 ON lp2.product_id = p2.id
WHERE lp2.price < lp1.price
ORDER BY savings DESC;

-- 14. Running total savings from sales
SELECT
    s.name AS store_name,
    ph.date_captured,
    SUM(ph.original_price - ph.price) FILTER (WHERE ph.is_on_sale) AS daily_total_savings,
    SUM(SUM(ph.original_price - ph.price) FILTER (WHERE ph.is_on_sale)) OVER (
        PARTITION BY ph.store_id ORDER BY ph.date_captured
    ) AS cumulative_savings
FROM price_history ph
JOIN stores s ON s.id = ph.store_id
WHERE ph.is_on_sale AND ph.original_price IS NOT NULL
GROUP BY s.name, ph.store_id, ph.date_captured
ORDER BY s.name, ph.date_captured;

-- 15. Product availability gaps (days without price data)
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '30 days',
        CURRENT_DATE,
        INTERVAL '1 day'
    )::DATE AS day
),
product_store_combos AS (
    SELECT DISTINCT product_id, store_id FROM store_products WHERE is_available = TRUE
),
expected AS (
    SELECT psc.product_id, psc.store_id, ds.day
    FROM product_store_combos psc CROSS JOIN date_series ds
),
actual AS (
    SELECT DISTINCT product_id, store_id, date_captured FROM price_history
    WHERE date_captured >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
    p.name,
    s.name AS store_name,
    COUNT(*) AS missing_days
FROM expected e
LEFT JOIN actual a ON a.product_id = e.product_id AND a.store_id = e.store_id AND a.date_captured = e.day
JOIN products p ON p.id = e.product_id
JOIN stores s ON s.id = e.store_id
WHERE a.date_captured IS NULL
GROUP BY p.name, s.name
ORDER BY missing_days DESC;

-- 16. Price correlation between stores (do stores match each other?)
SELECT
    p.name,
    CORR(w.price, c.price) AS woolworths_coles_correlation
FROM (
    SELECT DISTINCT ON (product_id, date_captured)
        product_id, date_captured, price
    FROM price_history ph
    JOIN stores s ON s.id = ph.store_id
    WHERE s.slug = 'woolworths'
    ORDER BY product_id, date_captured
) w
JOIN (
    SELECT DISTINCT ON (product_id, date_captured)
        product_id, date_captured, price
    FROM price_history ph
    JOIN stores s ON s.id = ph.store_id
    WHERE s.slug = 'coles'
    ORDER BY product_id, date_captured
) c ON c.product_id = w.product_id AND c.date_captured = w.date_captured
JOIN products p ON p.id = w.product_id
GROUP BY p.name
HAVING COUNT(*) > 20
ORDER BY woolworths_coles_correlation DESC;

-- 17. Category budget allocation optimizer
WITH category_spend AS (
    SELECT
        c.name AS category,
        COUNT(DISTINCT p.id) AS product_count,
        ROUND(AVG(lp.price)::NUMERIC, 2) AS avg_product_price,
        ROUND(MIN(lp.price)::NUMERIC, 2) AS cheapest_option,
        ROUND(MAX(lp.price)::NUMERIC, 2) AS priciest_option,
        ROUND((MAX(lp.price) - MIN(lp.price))::NUMERIC, 2) AS price_range
    FROM (
        SELECT DISTINCT ON (product_id) product_id, price
        FROM price_history ORDER BY product_id, date_captured DESC
    ) lp
    JOIN products p ON p.id = lp.product_id
    JOIN categories c ON c.id = p.category_id
    GROUP BY c.name
)
SELECT *, ROUND(price_range / NULLIF(avg_product_price, 0) * 100, 1) AS savings_opportunity_pct
FROM category_spend
ORDER BY savings_opportunity_pct DESC;

-- 18. Day-of-week price patterns
SELECT
    p.name,
    TO_CHAR(ph.date_captured, 'Day') AS day_of_week,
    EXTRACT(DOW FROM ph.date_captured) AS dow_num,
    ROUND(AVG(ph.price)::NUMERIC, 2) AS avg_price,
    ROUND(MIN(ph.price)::NUMERIC, 2) AS min_price,
    COUNT(*) AS observations
FROM price_history ph
JOIN products p ON p.id = ph.product_id
GROUP BY p.name, TO_CHAR(ph.date_captured, 'Day'), EXTRACT(DOW FROM ph.date_captured)
ORDER BY p.name, dow_num;

-- 19. Price alert candidates (prices near 90-day low)
WITH price_stats AS (
    SELECT
        product_id,
        store_id,
        MIN(price) AS min_90d,
        AVG(price) AS avg_90d,
        MAX(price) AS max_90d
    FROM price_history
    WHERE date_captured >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY product_id, store_id
),
current_prices AS (
    SELECT DISTINCT ON (product_id, store_id)
        product_id, store_id, price AS current_price
    FROM price_history
    ORDER BY product_id, store_id, date_captured DESC
)
SELECT
    p.name,
    s.name AS store_name,
    cp.current_price,
    ps.min_90d,
    ps.avg_90d,
    ROUND((cp.current_price - ps.min_90d) / NULLIF(ps.avg_90d, 0) * 100, 1) AS pct_above_90d_low,
    CASE
        WHEN cp.current_price <= ps.min_90d * 1.05 THEN 'BUY NOW - Near 90d Low'
        WHEN cp.current_price <= ps.avg_90d THEN 'GOOD TIME - Below Average'
        ELSE 'WAIT - Above Average'
    END AS recommendation
FROM current_prices cp
JOIN price_stats ps ON ps.product_id = cp.product_id AND ps.store_id = cp.store_id
JOIN products p ON p.id = cp.product_id
JOIN stores s ON s.id = cp.store_id
ORDER BY pct_above_90d_low ASC;

-- 20. Inflation dashboard summary
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', date_captured) AS month,
        AVG(price) AS avg_price,
        COUNT(DISTINCT product_id) AS products
    FROM price_history
    GROUP BY DATE_TRUNC('month', date_captured)
)
SELECT
    TO_CHAR(month, 'YYYY-MM') AS period,
    ROUND(avg_price::NUMERIC, 4) AS avg_basket_price,
    products,
    ROUND(
        (avg_price - LAG(avg_price) OVER (ORDER BY month)) /
        NULLIF(LAG(avg_price) OVER (ORDER BY month), 0) * 100,
        2
    ) AS mom_inflation_pct,
    ROUND(
        (avg_price - FIRST_VALUE(avg_price) OVER (ORDER BY month)) /
        NULLIF(FIRST_VALUE(avg_price) OVER (ORDER BY month), 0) * 100,
        2
    ) AS ytd_inflation_pct
FROM monthly
ORDER BY month;
