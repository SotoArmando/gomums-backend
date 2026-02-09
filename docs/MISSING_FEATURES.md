# Missing Backend Features

Analysis of DATABASE_SCHEMA.sql vs Implemented APIs

## ✅ Fully Implemented

| Feature | Routes | Repository | Tables | Status |
|---------|--------|------------|--------|--------|
| **Authentication** | ✅ auth.py | ✅ user_repository.py | users | Complete |
| **User Profile** | ✅ user_profile.py | ✅ user_profile_repository.py | user_preferences | Complete |
| **Journal/Diary** | ✅ journal.py | ✅ journal_repository.py | journal_entries, meal_purchase_links | Complete |
| **Budget Tracking** | ✅ budget.py | ✅ budget_repository.py | budget_entries, budget_settings | Complete |
| **Recipes** | ✅ recipe.py | ✅ recipe_repository.py | recipes | Complete |
| **Missions** | ✅ mission.py | ✅ mission_repository.py | missions, user_missions, mission_goals | Complete |
| **Challenges** | ✅ challenge.py | ✅ challenge_repository.py | challenges, user_challenges, challenge_goals, user_challenge_goals | Complete |
| **AI Recipes** | ✅ ai_recipes.py | N/A | N/A | Complete |

---

## ❌ Missing Major Features

### 1. 📅 Meal Planning System
**Priority: HIGH** - Core feature for weekly meal organization

**Database Tables:**
- `meal_plans` - Week-specific containers
- `planned_meals` - Recipes assigned to specific dates/times
- `shopping_list_items` - Auto-generated from planned meals

**Missing APIs:**
```
GET    /api/meal-plans
POST   /api/meal-plans
GET    /api/meal-plans/{id}
PUT    /api/meal-plans/{id}
DELETE /api/meal-plans/{id}

POST   /api/meal-plans/{id}/meals
PUT    /api/meal-plans/{id}/meals/{meal_id}
DELETE /api/meal-plans/{id}/meals/{meal_id}

GET    /api/meal-plans/{id}/shopping-list
POST   /api/meal-plans/{id}/shopping-list/items
PUT    /api/meal-plans/{id}/shopping-list/items/{item_id}
DELETE /api/meal-plans/{id}/shopping-list/items/{item_id}
PATCH  /api/meal-plans/{id}/shopping-list/items/{item_id}/purchased
```

**Key Features Needed:**
- Create weekly meal plans
- Drag-and-drop meal scheduling (date + meal_type)
- Auto-generate shopping lists from planned meals
- Mark shopping items as purchased
- Calculate total meal plan cost
- Meal plan status (draft, active, completed)

**Business Logic:**
- Each week = separate MealPlan record
- PlannedMeal links recipe to specific date/time
- Shopping list aggregates ingredients from all planned meals
- Deduplicates ingredients across multiple recipes

---

### 2. 🏆 Achievements System
**Priority: MEDIUM** - Gamification and user engagement

**Database Tables:**
- `achievements` - Achievement definitions
- `user_achievements` - User unlock tracking

**Missing APIs:**
```
GET    /api/achievements
GET    /api/achievements/{id}
GET    /api/user/achievements
POST   /api/user/achievements/{id}/unlock
GET    /api/user/achievements/progress
```

**Key Features Needed:**
- List all available achievements
- Track user progress toward achievements
- Auto-unlock based on user actions
- Achievement categories (cooking, budget, waste reduction)
- Points system integration

**Achievement Types:**
- Milestone achievements (10 meals cooked, 100 meals cooked)
- Streak achievements (7-day streak, 30-day streak)
- Challenge achievements (Complete Budget Boss Challenge)
- Exploration achievements (Try 5 cuisines)
- Efficiency achievements (Zero waste week)

**Currently:** Challenges/missions reference `reward_achievement_ids` but achievements system doesn't exist.

---

### 3. 📊 User Stats Dashboard
**Priority: MEDIUM** - Analytics and progress tracking

**Database Table:**
- `user_stats` - User activity statistics

**Fields (from schema):**
- `total_meals_cooked`
- `total_money_saved`
- `current_streak`
- `achievements_unlocked`
- `level`
- `points`
- `last_activity_date`

**Missing APIs:**
```
GET    /api/user/stats
GET    /api/user/stats/summary
GET    /api/user/leaderboard
POST   /api/user/stats/increment
```

**Key Features Needed:**
- Real-time stat updates on user actions
- Streak tracking (daily cooking)
- Level progression system
- Points accumulation
- Leaderboard (optional)
- Weekly/monthly summaries

**Currently:** Table exists but no dedicated endpoints or auto-increment logic.

---

### 4. 🏠 Home Sections (Dynamic Content)
**Priority: LOW** - Personalized home screen widgets

**Database Table:**
- `home_sections` - Configurable home screen sections

**Missing APIs:**
```
GET    /api/home/sections
POST   /api/home/sections
PUT    /api/home/sections/{id}
DELETE /api/home/sections/{id}
PATCH  /api/home/sections/{id}/order
```

**Key Features Needed:**
- Dynamic section ordering
- User-specific vs global sections
- Section types (featured recipes, active challenges, budget stats)
- Show/hide sections
- JSONB data field for flexible content

**Sample Section Types:**
- Featured recipes carousel
- Active missions/challenges
- Quick stats (meals this week, money saved)
- Smart suggestions
- Recently cooked meals

---

### 5. 💡 Smart Suggestions
**Priority: MEDIUM** - Intelligent recommendations

**Database Table:**
- `smart_suggestions` - Contextual user suggestions

**Missing APIs:**
```
GET    /api/suggestions
POST   /api/suggestions/{id}/dismiss
GET    /api/suggestions/active
```

**Key Features Needed:**
- AI-powered meal suggestions
- Budget optimization tips
- Leftover usage reminders
- Shopping trip recommendations
- Mission/challenge nudges
- Priority-based ordering
- Dismissable suggestions

**Suggestion Types:**
- "You have leftovers expiring soon"
- "Your weekly budget is 80% used"
- "Try a new cuisine this week"
- "Complete this mission for 100 points"
- "Plan meals to save $50 this month"

---

### 6. 📚 Content System (Articles & Videos)
**Priority: LOW** - Educational content

**Database Tables:**
- `authors` - Content creators
- `articles` - Blog posts and guides
- `videos` - Video tutorials

**Missing APIs:**
```
GET    /api/articles
GET    /api/articles/{id}
GET    /api/articles?category={category}

GET    /api/videos
GET    /api/videos/{id}
GET    /api/videos?category={category}

GET    /api/authors/{id}
```

**Key Features Needed:**
- Article CRUD (admin)
- Video CRUD (admin)
- Category filtering
- Search functionality
- Read time calculation
- Author profiles

**Content Categories:**
- Cooking tips and techniques
- Budget management guides
- Meal prep strategies
- Nutrition education
- Zero waste tips
- Recipe inspiration

---

## ⚠️ Partial Implementations

### User Preferences
**Status:** ✅ Basic CRUD implemented, but may need:
- Additional fields (notification preferences)
- Validation rules
- Premium feature toggles (linked to `is_premium` in users table)

### Premium Features
**Status:** ❌ Not implemented
- `users.is_premium` field exists but no premium logic
- No subscription management
- No feature gating based on premium status

---

## 🎯 Recommended Implementation Order

### Phase 1: Core User Experience
1. **User Stats** (2-3 days)
   - Essential for gamification
   - Ties into achievements and challenges
   - Auto-increment on user actions

2. **Achievements** (3-4 days)
   - Enhances engagement
   - Works with existing missions/challenges
   - Reward system already referenced

### Phase 2: Planning & Organization
3. **Meal Planning** (5-7 days)
   - Most complex feature
   - High user value
   - Integrates with recipes, budget, and shopping

### Phase 3: Intelligence & Content
4. **Smart Suggestions** (2-3 days)
   - Improves user retention
   - Leverages existing data
   - Can use simple rules initially

5. **Home Sections** (1-2 days)
   - UI customization
   - Showcases other features
   - Low complexity

6. **Content System** (2-3 days)
   - Educational value
   - Can be admin-only initially
   - Optional feature

---

## 📋 Quick Reference: What's Missing

```
❌ Meal Planning (meal_plans, planned_meals, shopping_list_items)
❌ Achievements (achievements, user_achievements)
❌ User Stats endpoints (user_stats table exists)
❌ Home Sections (home_sections)
❌ Smart Suggestions (smart_suggestions)
❌ Content System (authors, articles, videos)
⚠️  Premium Features (is_premium exists but no logic)
```

**Total Missing Endpoints:** ~35-40 API endpoints
**Estimated Dev Time:** 18-26 days (for all features)

---

## 🚀 Next Steps

1. **Prioritize features** based on your app's core value proposition
2. **Start with User Stats + Achievements** (foundation for gamification)
3. **Implement Meal Planning next** (high user value)
4. **Add Smart Suggestions + Home Sections** (polish)
5. **Content System last** (nice-to-have)

Would you like me to implement any of these features? I recommend starting with:
1. **User Stats** - Quick win, enables other features
2. **Achievements** - High engagement value, builds on existing work
3. **Meal Planning** - Core feature, significant user value
