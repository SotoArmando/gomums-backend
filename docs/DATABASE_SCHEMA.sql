-- GoMums PostgreSQL Database Schema
-- Generated from TypeScript types in DATA_TYPES_DIAGRAMS.md

-- ==========================================
-- USERS & AUTHENTICATION
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- Nullable for OAuth-only users
    oauth_provider VARCHAR(50) CHECK (oauth_provider IN ('google', 'facebook', 'apple', 'email')),
    oauth_id VARCHAR(255), -- Provider's user ID
    avatar_url TEXT, -- Profile picture from OAuth provider
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    -- Note: Removed password_or_oauth constraint to allow account linking
    -- Users can have both email/password AND OAuth authentication methods
);

-- Index for OAuth lookups
CREATE UNIQUE INDEX idx_users_oauth ON users(oauth_provider, oauth_id) WHERE oauth_provider IS NOT NULL;

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dietary_restrictions TEXT[],
    allergies TEXT[],
    budget_goal DECIMAL(10, 2),
    household_size INTEGER,
    skill_level VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE TABLE user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_meals_cooked INTEGER DEFAULT 0,
    total_money_saved DECIMAL(10, 2) DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    achievements_unlocked INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    points INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ==========================================
-- JOURNAL & DIARY
-- ==========================================

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('meal', 'purchase')),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    title VARCHAR(255) NOT NULL,
    
    -- Meal-specific fields
    meal_type VARCHAR(50) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    portions INTEGER,
    portions_left INTEGER,
    status VARCHAR(50) CHECK (status IN ('fresh', 'leftovers', 'frozen', 'completed')),
    ingredients_used TEXT[],
    ingredient_swaps JSONB, -- Array of {recipe_id (optional), original_ingredient, original_cost, swapped_ingredient, swapped_cost, savings}
    is_batch BOOLEAN DEFAULT FALSE, -- Batch cooking indicator
    used_leftovers BOOLEAN DEFAULT FALSE, -- Made from leftovers
    has_leftovers BOOLEAN DEFAULT FALSE, -- Meal wasn't fully consumed, leftovers remain
    needs_restock BOOLEAN DEFAULT FALSE, -- Ingredients need restocking
    purchase_id UUID REFERENCES journal_entries(id) ON DELETE SET NULL,
    
    -- Purchase-specific fields
    store VARCHAR(255),
    items JSONB, -- Array of {name, quantity, cost, category}
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_journal_user_timestamp ON journal_entries(user_id, timestamp DESC);
CREATE INDEX idx_journal_type ON journal_entries(type);
CREATE INDEX idx_journal_purchase_id ON journal_entries(purchase_id);

-- Many-to-many relationship for meals linked to purchases
CREATE TABLE meal_purchase_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    purchase_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    ingredients_matched TEXT[],
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(meal_id, purchase_id)
);

-- ==========================================
-- RECIPES
-- ==========================================

CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    image TEXT,
    prep_time VARCHAR(50),
    servings INTEGER,
    difficulty VARCHAR(50) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    ingredients TEXT[],
    instructions TEXT[],
    steps JSONB DEFAULT '[]'::jsonb,  -- Structured steps: [{order, phase, text, items, time_minutes, tip}]
    structured_ingredients JSONB DEFAULT '[]'::jsonb,  -- Optional structured ingredients: [{name, amount, unit, notes, ingredient_catalog_id, author_cost}]
    
    -- Nutrition info (inline for simplicity)
    calories INTEGER,
    protein VARCHAR(50),
    carbs VARCHAR(50),
    fat VARCHAR(50),
    fiber VARCHAR(50),
    
    -- Metadata
    featured BOOLEAN DEFAULT FALSE,
    category VARCHAR(100),
    tags TEXT[],
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recipes_featured ON recipes(featured);
CREATE INDEX idx_recipes_category ON recipes(category);

-- ==========================================
-- MEAL PLANNING
-- ==========================================

-- MealPlan: Week-specific container
-- Each week has its own MealPlan with separate meals and shopping list
CREATE TABLE meal_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_cost DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- PlannedMeal: Recipe assigned to specific date and meal time
-- Belongs to a MealPlan (week container)
CREATE TABLE planned_meals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_plan_id UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
    date DATE NOT NULL, -- Actual date (e.g., '2024-02-06'), not just 'Monday'
    meal_type VARCHAR(50) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,
    recipe_name VARCHAR(255) NOT NULL,
    servings INTEGER NOT NULL DEFAULT 1,
    is_batch BOOLEAN DEFAULT FALSE,
    is_leftovers BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ShoppingListItem: Generated from PlannedMeals in a specific MealPlan
-- Belongs to a MealPlan (week container)
CREATE TABLE shopping_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_plan_id UUID NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    quantity VARCHAR(100),
    category VARCHAR(100),
    purchased BOOLEAN DEFAULT FALSE,
    estimated_cost DECIMAL(10, 2),
    related_recipes UUID[],
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- BUDGET
-- ==========================================

CREATE TABLE budget_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    meal_name VARCHAR(255) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    servings INTEGER NOT NULL DEFAULT 1,
    cost_per_serving DECIMAL(10, 2) GENERATED ALWAYS AS (cost / servings) STORED,
    category VARCHAR(100),
    notes TEXT,
    journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_budget_user_date ON budget_entries(user_id, date DESC);
CREATE INDEX idx_budget_category ON budget_entries(category);

-- Budget settings per user
CREATE TABLE budget_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    weekly_budget DECIMAL(10, 2),
    monthly_budget DECIMAL(10, 2),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ==========================================
-- MISSIONS & CHALLENGES
-- ==========================================

CREATE TABLE missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('daily', 'weekly', 'monthly')),
    category VARCHAR(100),
    difficulty VARCHAR(50) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    target INTEGER NOT NULL DEFAULT 1,
    reward_points INTEGER DEFAULT 0,
    reward_achievement_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE user_missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'expired')),
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, mission_id)
);

CREATE TABLE challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL,
    duration INTEGER NOT NULL, -- days
    start_date DATE,
    end_date DATE,
    reward_points INTEGER DEFAULT 0,
    reward_achievement_ids UUID[],
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE challenge_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL,
    target INTEGER NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE user_challenges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id UUID NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed')),
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, challenge_id)
);

CREATE TABLE user_challenge_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_challenge_id UUID NOT NULL REFERENCES user_challenges(id) ON DELETE CASCADE,
    goal_id UUID NOT NULL REFERENCES challenge_goals(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    progress INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_challenge_id, goal_id)
);

CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(255),
    category VARCHAR(100),
    target INTEGER,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_date TIMESTAMP NOT NULL DEFAULT NOW(),
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- ==========================================
-- HOME SECTIONS & SUGGESTIONS
-- ==========================================

CREATE TABLE home_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL for global sections
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    visible BOOLEAN DEFAULT TRUE,
    order_index INTEGER NOT NULL DEFAULT 0,
    data JSONB, -- Flexible data storage
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE smart_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255),
    description TEXT,
    type VARCHAR(100) NOT NULL,
    dot_color VARCHAR(50),
    action_text VARCHAR(100),
    priority INTEGER DEFAULT 0,
    dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_suggestions_user_priority ON smart_suggestions(user_id, priority DESC) WHERE NOT dismissed;

-- ==========================================
-- CONTENT (ARTICLES & VIDEOS)
-- ==========================================

CREATE TABLE authors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    avatar TEXT,
    bio TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    image TEXT,
    category VARCHAR(100),
    read_time VARCHAR(50),
    author_id UUID REFERENCES authors(id) ON DELETE SET NULL,
    published_date TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    thumbnail TEXT,
    duration VARCHAR(50),
    category VARCHAR(100),
    published_date TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- TRIGGERS FOR updated_at
-- ==========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_stats_updated_at BEFORE UPDATE ON user_stats FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON journal_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_meal_plans_updated_at BEFORE UPDATE ON meal_plans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_planned_meals_updated_at BEFORE UPDATE ON planned_meals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_shopping_list_items_updated_at BEFORE UPDATE ON shopping_list_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budget_entries_updated_at BEFORE UPDATE ON budget_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budget_settings_updated_at BEFORE UPDATE ON budget_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_missions_updated_at BEFORE UPDATE ON missions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_missions_updated_at BEFORE UPDATE ON user_missions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_challenges_updated_at BEFORE UPDATE ON challenges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_challenges_updated_at BEFORE UPDATE ON user_challenges FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_achievements_updated_at BEFORE UPDATE ON achievements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_achievements_updated_at BEFORE UPDATE ON user_achievements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_home_sections_updated_at BEFORE UPDATE ON home_sections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_smart_suggestions_updated_at BEFORE UPDATE ON smart_suggestions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- USEFUL VIEWS
-- ==========================================

-- View: Current week's budget stats per user
CREATE VIEW current_week_budget_stats AS
SELECT 
    user_id,
    COUNT(*) as meals_this_week,
    SUM(cost) as total_spent,
    AVG(cost_per_serving) as avg_cost_per_meal,
    SUM(cost_per_serving * servings * 3) - SUM(cost) as savings_vs_restaurant
FROM budget_entries
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY user_id;

-- View: Active missions with progress
CREATE VIEW user_active_missions AS
SELECT 
    um.user_id,
    m.id as mission_id,
    m.title,
    m.type,
    m.category,
    m.difficulty,
    um.status,
    um.progress,
    m.target,
    ROUND((um.progress::DECIMAL / m.target) * 100, 2) as progress_percentage,
    um.started_at,
    um.expires_at
FROM user_missions um
JOIN missions m ON um.mission_id = m.id
WHERE um.status = 'active';

-- View: Purchases with linked meals
CREATE VIEW purchases_with_meals AS
SELECT 
    p.id as purchase_id,
    p.user_id,
    p.title as purchase_title,
    p.store,
    p.items,
    p.timestamp as purchase_date,
    json_agg(
        json_build_object(
            'meal_id', m.id,
            'meal_title', m.title,
            'meal_type', m.meal_type,
            'timestamp', m.timestamp,
            'ingredients_matched', mpl.ingredients_matched
        )
    ) FILTER (WHERE m.id IS NOT NULL) as linked_meals
FROM journal_entries p
LEFT JOIN meal_purchase_links mpl ON p.id = mpl.purchase_id
LEFT JOIN journal_entries m ON mpl.meal_id = m.id
WHERE p.type = 'purchase'
GROUP BY p.id, p.user_id, p.title, p.store, p.items, p.timestamp;

-- ==========================================
-- SAMPLE DATA INDEXES
-- ==========================================

-- Performance indexes for common queries
CREATE INDEX idx_user_missions_status ON user_missions(user_id, status);
CREATE INDEX idx_user_challenges_status ON user_challenges(user_id, status);
CREATE INDEX idx_user_achievements ON user_achievements(user_id);
CREATE INDEX idx_planned_meals_plan_date ON planned_meals(meal_plan_id, date);
CREATE INDEX idx_shopping_list_plan ON shopping_list_items(meal_plan_id);
