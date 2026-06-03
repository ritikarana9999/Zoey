-- SmartCart AI Database Schema
-- Production-ready schema for grocery price intelligence

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stores
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    logo_url VARCHAR(500),
    website VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(200),
    category_id UUID REFERENCES categories(id),
    barcode VARCHAR(50),
    description TEXT,
    weight_volume VARCHAR(100),
    weight_grams DECIMAL(10,2),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Store Products (product at specific store)
CREATE TABLE IF NOT EXISTS store_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    store_id UUID REFERENCES stores(id),
    store_sku VARCHAR(200),
    store_url VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(product_id, store_id)
);

-- Price History
CREATE TABLE IF NOT EXISTS price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_product_id UUID REFERENCES store_products(id),
    product_id UUID REFERENCES products(id),
    store_id UUID REFERENCES stores(id),
    price DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(10,4),
    unit_type VARCHAR(50),
    is_on_sale BOOLEAN DEFAULT FALSE,
    original_price DECIMAL(10,2),
    captured_at TIMESTAMP DEFAULT NOW(),
    date_captured DATE DEFAULT CURRENT_DATE
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(300) NOT NULL UNIQUE,
    name VARCHAR(200),
    preferred_store_id UUID REFERENCES stores(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Baskets
CREATE TABLE IF NOT EXISTS baskets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(200),
    items JSONB NOT NULL DEFAULT '[]',
    optimization_result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Forecasts
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    store_id UUID REFERENCES stores(id),
    forecast_date DATE NOT NULL,
    predicted_price DECIMAL(10,2) NOT NULL,
    lower_bound DECIMAL(10,2),
    upper_bound DECIMAL(10,2),
    model_name VARCHAR(100),
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_product_id UUID REFERENCES products(id),
    recommended_product_id UUID REFERENCES products(id),
    similarity_score DECIMAL(5,4),
    price_savings DECIMAL(10,2),
    reason VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product Embeddings (for similarity search)
CREATE TABLE IF NOT EXISTS product_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) UNIQUE,
    embedding_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
