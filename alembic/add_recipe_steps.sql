-- Migration: Add structured steps column to recipes table
-- Steps have phases (prep, cooking, serve) and reference specific ingredients/items

-- Add steps JSONB column to recipes table
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS steps JSONB DEFAULT '[]'::jsonb;

-- Add steps index for querying by phase
CREATE INDEX IF NOT EXISTS idx_recipes_steps ON recipes USING gin (steps);

-- Backfill: Convert existing instructions into steps with default "cooking" phase
-- This preserves existing data while adding the new structure
UPDATE recipes
SET steps = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'order', ordinality,
            'phase', 'cooking',
            'text', instruction,
            'items', '[]'::jsonb,
            'time_minutes', NULL,
            'tip', NULL
        )
    )
    FROM unnest(instructions) WITH ORDINALITY AS t(instruction, ordinality)
)
WHERE instructions IS NOT NULL AND array_length(instructions, 1) > 0 AND (steps IS NULL OR steps = '[]'::jsonb);
