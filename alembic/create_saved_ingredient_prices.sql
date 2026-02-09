-- ==========================================
-- INGREDIENT PRICES (saved from Price Compare)
-- ==========================================

CREATE TABLE IF NOT EXISTS saved_ingredient_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipe_name VARCHAR(255) NOT NULL,
    ingredient_name VARCHAR(255) NOT NULL,
    original_price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    modified_name VARCHAR(255),           -- swapped ingredient name (NULL if not swapped)
    modified_price DECIMAL(10, 2),        -- swapped price (NULL if not swapped)
    status VARCHAR(20) NOT NULL DEFAULT 'original' CHECK (status IN ('original', 'swapped', 'removed')),
    is_homemade BOOLEAN DEFAULT FALSE,
    is_added BOOLEAN DEFAULT FALSE,       -- TRUE for user-added ingredients (not in original recipe)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saved_prices_user ON saved_ingredient_prices(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_prices_recipe ON saved_ingredient_prices(user_id, recipe_name);
