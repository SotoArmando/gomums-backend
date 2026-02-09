-- Migration: Add 'kind' field to missions table to distinguish between missions and challenges
-- This allows filtering and displaying missions vs challenges separately in the UI

-- Add the kind column
ALTER TABLE missions 
ADD COLUMN IF NOT EXISTS kind VARCHAR(20) DEFAULT 'mission';

-- Add check constraint to ensure valid values
ALTER TABLE missions 
ADD CONSTRAINT missions_kind_check 
CHECK (kind IN ('mission', 'challenge', 'event'));

-- Update existing challenge-style missions to be marked as challenges
UPDATE missions 
SET kind = 'challenge' 
WHERE title IN (
    'Batch Cooking Challenge',
    'Weekly Savings Challenge', 
    'No Spend Weekend',
    'Swap Challenge',
    'Swap & Save Challenge',
    'One Pot Wonder',
    'Cook Streak',
    'Leftover Makeover',
    'Batch Prep Master',
    'Zero Waste Week'
) OR title LIKE '%Challenge%';

-- Create index for faster filtering
CREATE INDEX IF NOT EXISTS idx_missions_kind ON missions(kind);

-- Add comment
COMMENT ON COLUMN missions.kind IS 'Type of mission: mission (regular), challenge (special), or event (limited-time)';
