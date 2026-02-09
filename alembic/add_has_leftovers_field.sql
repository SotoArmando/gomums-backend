-- Add has_leftovers field to journal_entries table
-- This field indicates when a meal wasn't fully consumed and leftovers remain

-- Add the column
ALTER TABLE journal_entries 
ADD COLUMN has_leftovers BOOLEAN DEFAULT FALSE;

-- Add comment for documentation
COMMENT ON COLUMN journal_entries.has_leftovers IS 'Indicates meal was not fully consumed and leftovers remain';

-- Optionally: Update existing records where portions_left > 0
-- UPDATE journal_entries 
-- SET has_leftovers = TRUE 
-- WHERE type = 'meal' AND portions_left > 0;
