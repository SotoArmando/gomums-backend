-- Migration: Add Mission Goals Tables (Multi-Goal Support for Missions)
-- This adds multi-goal support to the existing missions system
-- Maintains backward compatibility with single-goal missions

-- ==========================================
-- MISSION GOALS TABLE (Multi-Step Support)
-- ==========================================

CREATE TABLE IF NOT EXISTS mission_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL, -- e.g., "Cook 3 meals"
    target INTEGER NOT NULL, -- Goal target value
    order_index INTEGER NOT NULL DEFAULT 0, -- Display order (0, 1, 2...)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- USER MISSION GOALS TABLE (Per-Goal Tracking)
-- ==========================================

CREATE TABLE IF NOT EXISTS user_mission_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_mission_id UUID NOT NULL REFERENCES user_missions(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES mission_goals(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    progress INTEGER DEFAULT 0, -- Current progress toward goal target
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_mission_id, goal_id)
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_mission_goals_mission_id ON mission_goals(mission_id);
CREATE INDEX IF NOT EXISTS idx_user_mission_goals_user_mission ON user_mission_goals(user_mission_id);

-- ==========================================
-- TRIGGERS FOR updated_at
-- ==========================================

DROP TRIGGER IF EXISTS update_mission_goals_updated_at ON mission_goals;
CREATE TRIGGER update_mission_goals_updated_at 
BEFORE UPDATE ON mission_goals 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_mission_goals_updated_at ON user_mission_goals;
CREATE TRIGGER update_user_mission_goals_updated_at 
BEFORE UPDATE ON user_mission_goals 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- BACKWARD COMPATIBILITY
-- ==========================================

-- For existing missions with only a 'target' field and no goals,
-- we'll treat them as single-goal missions at the application level.
-- New missions should define goals explicitly.

-- Migration completed successfully
