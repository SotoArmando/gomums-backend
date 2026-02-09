-- ==========================================
-- INGREDIENT CATALOG (Master reference prices by region)
-- ==========================================

CREATE TABLE IF NOT EXISTS ingredient_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    name_local VARCHAR(255),              -- Local language name (e.g., "Habichuelas Rojas")
    category VARCHAR(100) NOT NULL,       -- e.g., "vegetables", "proteins", "dairy"
    unit VARCHAR(100) NOT NULL,           -- e.g., "1 kg", "500 g", "Each"
    price DECIMAL(10, 2) NOT NULL,        -- Average/typical price
    price_low DECIMAL(10, 2),             -- Low end of price range
    price_high DECIMAL(10, 2),            -- High end of price range
    currency VARCHAR(10) NOT NULL,        -- e.g., "RD$", "USD"
    region VARCHAR(100) NOT NULL,         -- e.g., "Dominican Republic", "Kansas"
    language VARCHAR(10) NOT NULL DEFAULT 'en', -- e.g., "en", "es"
    source VARCHAR(100) DEFAULT 'manual', -- Where the data came from
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Unique constraint: one entry per ingredient per region
CREATE UNIQUE INDEX IF NOT EXISTS idx_ingredient_catalog_unique
    ON ingredient_catalog(LOWER(name), LOWER(region));

-- Query indexes
CREATE INDEX IF NOT EXISTS idx_ingredient_catalog_region
    ON ingredient_catalog(region);
CREATE INDEX IF NOT EXISTS idx_ingredient_catalog_category
    ON ingredient_catalog(category);
CREATE INDEX IF NOT EXISTS idx_ingredient_catalog_name
    ON ingredient_catalog(LOWER(name));
