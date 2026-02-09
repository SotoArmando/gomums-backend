-- ==========================================
-- ADD STRUCTURED INGREDIENTS TO RECIPES
-- ==========================================

-- Add structured_ingredients JSONB column to recipes table
-- This allows recipes to optionally have structured ingredient data
-- with catalog references, amounts, units, and author costs
-- alongside the existing TEXT[] ingredients column.

ALTER TABLE recipes
    ADD COLUMN IF NOT EXISTS structured_ingredients JSONB DEFAULT '[]'::jsonb;

-- Add structured_ingredients comment
COMMENT ON COLUMN recipes.structured_ingredients IS
    'Optional structured ingredients: [{name, amount, unit, notes, ingredient_catalog_id, author_cost}]';
