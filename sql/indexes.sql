-- Performance Indexes for SmartCart AI

CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_store_id ON price_history(store_id);
CREATE INDEX IF NOT EXISTS idx_price_history_captured_at ON price_history(captured_at);
CREATE INDEX IF NOT EXISTS idx_price_history_date_captured ON price_history(date_captured);
CREATE INDEX IF NOT EXISTS idx_price_history_product_date ON price_history(product_id, date_captured);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_name_gin ON products USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_store_products_product_id ON store_products(product_id);
CREATE INDEX IF NOT EXISTS idx_store_products_store_id ON store_products(store_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_product_store ON forecasts(product_id, store_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_forecast_date ON forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_recommendations_source ON recommendations(source_product_id);
CREATE INDEX IF NOT EXISTS idx_baskets_user_id ON baskets(user_id);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_price_history_is_on_sale ON price_history(is_on_sale) WHERE is_on_sale = TRUE;
