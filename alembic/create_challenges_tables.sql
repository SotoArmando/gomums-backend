-- Migration: Create Challenges Tables (Multi-Goal Support)
-- This creates separate tables for challenges with multi-goal support
-- Missions table remains for simple single-goal tasks

-- ==========================================
-- CHALLENGES TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL, -- e.g., 'batch_cooking', 'budget_savings', 'zero_waste'
    duration INTEGER NOT NULL, -- days (e.g., 7 for weekly, 30 for monthly)
    start_date DATE, -- NULL means available anytime
    end_date DATE, -- NULL means no end date
    reward_points INTEGER DEFAULT 0,
    reward_achievement_ids UUID[], -- Multiple achievements can be awarded
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- CHALLENGE GOALS TABLE (Multi-Step Support)
-- ==========================================

CREATE TABLE IF NOT EXISTS challenge_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL, -- e.g., "Cook 3 batch meals"
    target INTEGER NOT NULL, -- Goal target value
    order_index INTEGER NOT NULL DEFAULT 0, -- Display order (0, 1, 2...)
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- USER CHALLENGES TABLE (Assignment & Progress)
-- ==========================================

CREATE TABLE IF NOT EXISTS user_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed')),
    progress INTEGER DEFAULT 0, -- Overall progress (can be derived from goals)
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, challenge_id)
);

-- ==========================================
-- USER CHALLENGE GOALS TABLE (Per-Goal Tracking)
-- ==========================================

CREATE TABLE IF NOT EXISTS user_challenge_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_challenge_id UUID NOT NULL REFERENCES user_challenges(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES challenge_goals(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    progress INTEGER DEFAULT 0, -- Current progress toward goal target
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_challenge_id, goal_id)
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_challenges_type ON challenges(type);
CREATE INDEX IF NOT EXISTS idx_challenges_dates ON challenges(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_challenge_goals_challenge_id ON challenge_goals(challenge_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_user_status ON user_challenges(user_id, status);
CREATE INDEX IF NOT EXISTS idx_user_challenge_goals_user_challenge ON user_challenge_goals(user_challenge_id);

-- ==========================================
-- TRIGGERS FOR updated_at
-- ==========================================

DROP TRIGGER IF EXISTS update_challenges_updated_at ON challenges;
CREATE TRIGGER update_challenges_updated_at 
BEFORE UPDATE ON challenges 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_challenge_goals_updated_at ON challenge_goals;
CREATE TRIGGER update_challenge_goals_updated_at 
BEFORE UPDATE ON challenge_goals 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_challenges_updated_at ON user_challenges;
CREATE TRIGGER update_user_challenges_updated_at 
BEFORE UPDATE ON user_challenges 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_challenge_goals_updated_at ON user_challenge_goals;
CREATE TRIGGER update_user_challenge_goals_updated_at 
BEFORE UPDATE ON user_challenge_goals 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Migration completed successfully
