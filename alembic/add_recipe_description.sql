-- Migration: Add description column to recipes table
-- Description: Adds a text description field for detailed recipe information

BEGIN;

-- Add description column
ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add comment
COMMENT ON COLUMN recipes.description IS 'Detailed description of the recipe';

COMMIT;

-- Verify the change
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'recipes' AND column_name = 'description';
