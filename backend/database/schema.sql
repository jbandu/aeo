-- AEO Platform Database Schema

-- Products table: stores raw product data
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    raw_title TEXT NOT NULL,
    raw_description TEXT,
    category TEXT,
    brand TEXT,
    price REAL,
    attributes TEXT, -- JSON field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);

-- Enriched products table: stores AI-enhanced product data
CREATE TABLE IF NOT EXISTS enriched_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    enriched_title TEXT,
    long_description TEXT,
    key_attributes TEXT, -- JSON field
    faqs TEXT, -- JSON field
    semantic_tags TEXT, -- JSON field
    use_cases TEXT, -- JSON field
    aeo_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX idx_enriched_products_product_id ON enriched_products(product_id);
CREATE INDEX idx_enriched_products_aeo_score ON enriched_products(aeo_score);

-- Enrichment logs table: tracks AI enrichment operations
CREATE TABLE IF NOT EXISTS enrichment_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    enrichment_type TEXT NOT NULL,
    prompt_used TEXT,
    tokens_used INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX idx_enrichment_logs_product_id ON enrichment_logs(product_id);
CREATE INDEX idx_enrichment_logs_timestamp ON enrichment_logs(timestamp);
