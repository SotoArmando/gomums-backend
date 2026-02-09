# API Endpoints Reference

Complete list of REST API endpoints for the GoMums backend server.

## Base URL
```
http://localhost:8000/api
```

**Note:** Port 8000 is the default for this FastAPI backend. Adjust if you've configured a different port in your `.env` file.

---

## 🔐 Authentication

### POST `/auth/register`
Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:** `201 Created`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "is_premium": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### POST `/auth/login`
Authenticate user and receive token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:** `200 OK` (Same as register)

---

### POST `/auth/logout`
Invalidate current session.

**Headers:** `Authorization: Bearer {token}`

**Response:** `204 No Content`

---

### POST `/auth/refresh`
Refresh access token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### GET `/auth/me`
Get current user profile.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "avatar_url": "https://lh3.googleusercontent.com/...",
  "oauth_provider": "google",
  "oauth_id": "1234567890",
  "is_active": true,
  "is_premium": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### POST `/auth/google`
Authenticate with Google OAuth.

**Request Body:**
```json
{
  "token": "google_oauth_token_from_client"
}
```

**Response:** `200 OK` (Same as register)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "oauth_provider": "google",
    "oauth_id": "1234567890",
    "is_active": true,
    "is_premium": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Notes:**
- If user doesn't exist, creates new account
- If user exists with same email, links OAuth account
- Frontend should use Google Sign-In JavaScript library to get token

---

### GET `/auth/google/url`
Get Google OAuth authorization URL for redirect flow.

**Response:** `200 OK`
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=..."
}
```

---

### POST `/auth/google/callback`
Handle Google OAuth callback with authorization code.

**Request Body:**
```json
{
  "code": "authorization_code_from_google"
}
```

**Response:** `200 OK` (Same as `/auth/google`)

**Note:** Google OAuth endpoints are planned but not yet implemented as of v1.0.0

---

### GET `/auth/health`
Health check endpoint for authentication service.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "auth"
}
```

---

## 📔 Journal / Diary

### GET `/journal/entries`
Get all journal entries (meals + purchases) for current user.

**Query Params:**
- `type` (optional): `meal` | `purchase`
- `from` (optional): ISO date - start date filter
- `to` (optional): ISO date - end date filter
- `limit` (optional): number
- `offset` (optional): number

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "type": "meal",
    "timestamp": "2024-02-06T12:00:00Z",
    "title": "Chicken Stir Fry",
    "meal_type": "lunch",
    "portions": 4,
    "portions_left": 2,
    "status": "fresh",
    "ingredients_used": ["chicken", "vegetables"],
    "is_batch": false,
    "used_leftovers": false,
    "needs_restock": false,
    "purchase_id": "uuid",
    "created_at": "2024-02-06T12:00:00Z",
    "updated_at": "2024-02-06T12:00:00Z"
  },
  {
    "id": "uuid",
    "user_id": "uuid",
    "type": "purchase",
    "timestamp": "2024-02-05T18:30:00Z",
    "title": "Walmart Grocery Run",
    "store": "Walmart",
    "items": [
      {
        "name": "Chicken breast",
        "quantity": "2 lbs",
        "cost": 12.99,
        "category": "protein"
      },
      {
        "name": "Mixed vegetables",
        "quantity": "1 bag",
        "cost": 4.50,
        "category": "produce"
      },
      {
        "name": "Rice",
        "quantity": "5 lbs",
        "cost": 8.99,
        "category": "pantry"
      }
    ],
    "total_cost": 26.48,
    "created_at": "2024-02-05T18:30:00Z",
    "updated_at": "2024-02-05T18:30:00Z"
  }
]
```

---

### GET `/journal/entries/:id`
Get single journal entry by ID.

**Response:** `200 OK` (Single entry object)

---

### POST `/journal/entries`
Create new journal entry (meal or purchase).

**Request Body:**
```json
{
  "type": "meal",
  "title": "Pasta Carbonara",
  "meal_type": "dinner",
  "portions": 2,
  "status": "fresh"
}
```

**Response:** `201 Created` (Entry object)

---

### PATCH `/journal/entries/:id`
Update existing journal entry.

**Request Body:**
```json
{
  "portions_left": 1,
  "status": "leftover"
}
```

**Response:** `200 OK` (Updated entry object)

---

### DELETE `/journal/entries/:id`
Delete journal entry.

**Response:** `204 No Content`

---

### GET `/journal/meals`
Get only meals (shortcut for `/entries?type=meal`).

**Response:** `200 OK` (Array of meals)

---

### GET `/journal/purchases`
Get only purchases (shortcut for `/entries?type=purchase`).

**Response:** `200 OK` (Array of purchases)

---

### POST `/journal/meals/:mealId/link-purchase`
Link a meal to a purchase with matched ingredients.

**Request Body:**
```json
{
  "purchase_id": "uuid",
  "ingredients_used": ["chicken", "rice"]
}
```

**Response:** `200 OK` (Updated meal object)

---

## 💰 Budget

### GET `/budget/stats`
Get budget statistics for current user.

**Query Params:**
- `period` (optional): `week` | `month` | `year` (default: `week`)

**Response:** `200 OK`
```json
{
  "score": 85,
  "avg_cost_per_meal": 4.50,
  "savings_vs_restaurant": 120.00,
  "meals_this_week": 15,
  "total_spent": 67.50,
  "weekly_budget": 100.00,
  "remaining_budget": 32.50
}
```

---

### GET `/budget/entries`
Get budget entries for current user.

**Query Params:**
- `from` (optional): ISO date
- `to` (optional): ISO date
- `category` (optional): string
- `limit` (optional): number
- `offset` (optional): number

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "date": "2024-02-06",
    "meal_name": "Chicken Stir Fry",
    "cost": 12.50,
    "servings": 4,
    "cost_per_serving": 3.13,
    "category": "homemade",
    "notes": "Used vegetables from garden",
    "journal_entry_id": "uuid",
    "created_at": "2024-02-06T12:00:00Z",
    "updated_at": "2024-02-06T12:00:00Z"
  }
]
```

---

### GET `/budget/entries/:id`
Get single budget entry.

**Response:** `200 OK` (Entry object)

---

### POST `/budget/entries`
Create new budget entry.

**Request Body:**
```json
{
  "date": "2024-02-06",
  "meal_name": "Pasta Carbonara",
  "cost": 8.50,
  "servings": 2,
  "category": "homemade",
  "notes": "Optional note"
}
```

**Response:** `201 Created` (Entry object)

---

### PATCH `/budget/entries/:id`
Update budget entry.

**Request Body:**
```json
{
  "cost": 9.00,
  "notes": "Updated cost"
}
```

**Response:** `200 OK` (Updated entry)

---

### DELETE `/budget/entries/:id`
Delete budget entry.

**Response:** `204 No Content`

---

### GET `/budget/category-breakdown`
Get spending breakdown by category.

**Query Params:**
- `period` (optional): `week` | `month` | `year`

**Response:** `200 OK`
```json
{
  "homemade": 150.00,
  "batch_cooking": 80.00,
  "takeout": 45.00
}
```

---

### GET `/budget/settings`
Get user's budget settings and configuration.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "weekly_budget": 150.00,
  "budget_period": "weekly",
  "alert_threshold": 80,
  "created_at": "2024-02-01T00:00:00Z",
  "updated_at": "2024-02-01T00:00:00Z"
}
```

---

### POST `/budget/settings`
Create or update budget settings.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "weekly_budget": 150.00,
  "budget_period": "weekly",
  "alert_threshold": 80
}
```

**Response:** `201 Created` (Budget settings object)

---

## 🎯 Missions

### GET `/missions`
Get all available missions (not yet started by user).

**Query Params:**
- `type` (optional): `daily` | `weekly` | `monthly`
- `category` (optional): string

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "Cook 3 Meals This Week",
    "description": "Cook at least 3 home meals",
    "type": "weekly",
    "category": "cooking",
    "difficulty": "easy",
    "target": 3,
    "reward_points": 50,
    "created_at": "2024-02-01T00:00:00Z"
  }
]
```

---

### GET `/missions/active`
Get user's active missions with progress.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "mission_id": "uuid",
    "title": "Cook 3 Meals This Week",
    "type": "weekly",
    "category": "cooking",
    "status": "active",
    "progress": 2,
    "target": 3,
    "difficulty": "easy",
    "started_at": "2024-02-03T10:00:00Z",
    "expires_at": "2024-02-10T23:59:59Z"
  }
]
```

---

### POST `/missions/:id/start`
Start/join a mission.

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "mission_id": "uuid",
  "status": "active",
  "progress": 0,
  "started_at": "2024-02-06T12:00:00Z",
  "expires_at": "2024-02-13T23:59:59Z"
}
```

---

### POST `/missions/:id/complete`
Mark mission as complete (if target reached).

**Response:** `200 OK`
```json
{
  "mission": { /* updated mission */ },
  "rewards": {
    "points": 50,
    "achievements": ["uuid"]
  }
}
```

---

### PATCH `/missions/:id/progress`
Update mission progress.

**Request Body:**
```json
{
  "progress": 2
}
```

**Response:** `200 OK` (Updated mission object)

---

### GET `/missions/check-availability/:mission_id`
Check if a mission is available for the user to start (e.g., cooldown period check).

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "available": true,
  "reason": null,
  "cooldown_expires_at": null
}
```

Or if unavailable:
```json
{
  "available": false,
  "reason": "Mission on cooldown",
  "cooldown_expires_at": "2024-02-10T00:00:00Z"
}
```

---

### GET `/missions/stats`
Get user's mission statistics.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "total_completed": 15,
  "total_active": 3,
  "total_points_earned": 750,
  "success_rate": 85.5,
  "current_streak": 7
}
```

---

### POST `/missions/assign-daily`
Automatically assign daily missions to the current user.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "assigned": 2,
  "missions": [
    {
      "id": "uuid",
      "mission_id": "uuid",
      "title": "Cook 1 Meal Today",
      "status": "active"
    }
  ]
}
```

---

### POST `/missions/assign/:mission_id`
Manually assign a specific mission to the current user.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "success": true,
  "user_mission": {
    "id": "uuid",
    "mission_id": "uuid",
    "status": "active",
    "progress": 0
  }
}
```

---

## 🏆 Challenges

### GET `/challenges`
Get all challenges.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "Batch Cooking Challenge",
    "description": "Cook in batches for 7 days",
    "type": "batch_cooking",
    "duration": 7,
    "start_date": "2024-02-01",
    "end_date": "2024-02-07",
    "reward_points": 200,
    "goals": [
      {
        "id": "uuid",
        "description": "Make 1 batch meal",
        "target": 1,
        "order_index": 0
      }
    ]
  }
]
```

---

### GET `/challenges/active`
Get user's active challenges with progress.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "challenge_id": "uuid",
    "title": "Batch Cooking Challenge",
    "type": "batch_cooking",
    "status": "active",
    "progress": 60,
    "started_at": "2024-02-01T00:00:00Z",
    "goals": [
      {
        "id": "uuid",
        "goal_id": "uuid",
        "description": "Make 1 batch meal",
        "completed": true,
        "progress": 1,
        "target": 1
      }
    ]
  }
]
```

---

### POST `/challenges/:id/join`
Join a challenge.

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "challenge_id": "uuid",
  "status": "active",
  "progress": 0,
  "started_at": "2024-02-06T12:00:00Z"
}
```

---

### PATCH `/challenges/:challengeId/goals/:goalId`
Update challenge goal progress.

**Request Body:**
```json
{
  "progress": 1,
  "completed": true
}
```

**Response:** `200 OK` (Updated goal object)

---

### GET `/challenges/completed/all`
Get all completed challenges for the current user.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "challenge_id": "uuid",
    "title": "Batch Cooking Challenge",
    "type": "batch_cooking",
    "status": "completed",
    "progress": 100,
    "completed_at": "2024-02-07T00:00:00Z"
  }
]
```

---

### GET `/challenges/active/:user_challenge_id`
Get detailed information about a specific active challenge.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "challenge_id": "uuid",
  "title": "Budget Boss Challenge",
  "description": "Master your meal budget",
  "status": "active",
  "progress": 60,
  "started_at": "2024-02-01T00:00:00Z",
  "goals": [
    {
      "goal_id": "uuid",
      "description": "Stay under daily budget 20 days",
      "progress": 12,
      "target": 20,
      "completed": false
    }
  ]
}
```

---

### POST `/challenges/progress/update`
Manually trigger a challenge progress update (usually done automatically).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "user_challenge_id": "uuid",
  "action_type": "journal_entry",
  "entry_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "updated": true,
  "progress": 65,
  "goals_updated": [
    {
      "goal_id": "uuid",
      "new_progress": 13,
      "completed": false
    }
  ]
}
```

---

### POST `/challenges`
Create a new challenge (admin/testing only).

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "title": "New Challenge",
  "description": "Challenge description",
  "type": "custom",
  "duration": 7,
  "reward_points": 200,
  "goals": [
    {
      "description": "Complete task 1",
      "target": 5,
      "order_index": 0
    }
  ]
}
```

**Response:** `201 Created` (Challenge object)

---

## 🏅 Achievements

### GET `/achievements`
Get all achievements.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "First Meal",
    "description": "Log your first meal",
    "icon": "🍳",
    "category": "milestone",
    "target": 1,
    "points": 10
  }
]
```

---

### GET `/achievements/unlocked`
Get user's unlocked achievements.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "achievement_id": "uuid",
    "title": "First Meal",
    "icon": "🍳",
    "unlocked_date": "2024-02-05T12:00:00Z",
    "progress": 1,
    "category": "milestone"
  }
]
```

---

## 🏠 Home Sections

### GET `/home/sections`
Get home page sections for current user.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "type": "budget_score",
    "title": "Your Budget Score",
    "subtitle": "This week",
    "visible": true,
    "order": 1,
    "data": {
      "score": 85,
      "trend": "up"
    }
  },
  {
    "id": "uuid",
    "type": "featured_recipes",
    "title": "Try These Recipes",
    "visible": true,
    "order": 2,
    "data": {
      "recipe_ids": ["uuid1", "uuid2"]
    }
  }
]
```

---

### PATCH `/home/sections/reorder`
Update section order.

**Request Body:**
```json
{
  "sections": [
    { "id": "uuid1", "order": 1 },
    { "id": "uuid2", "order": 2 }
  ]
}
```

**Response:** `200 OK` (Updated sections)

---

### GET `/home/suggestions`
Get smart suggestions for user.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "Use leftover chicken",
    "subtitle": "Save $5",
    "description": "You have chicken from yesterday",
    "type": "use_leftovers",
    "dot_color": "green",
    "action_text": "Cook now",
    "priority": 1
  }
]
```

---

## 🍳 Recipes

### GET `/recipes`
Get all recipes.

**Query Params:**
- `category` (optional): string
- `difficulty` (optional): `easy` | `medium` | `hard`
- `featured` (optional): boolean
- `limit` (optional): number
- `offset` (optional): number

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Chicken Stir Fry",
    "image": "https://...",
    "prep_time": "30 min",
    "servings": 4,
    "calories": 350,
    "difficulty": "easy",
    "ingredients": ["chicken", "vegetables", "soy sauce"],
    "instructions": ["Step 1...", "Step 2..."],
    "nutrition": {
      "protein": "30g",
      "carbs": "25g",
      "fat": "12g",
      "fiber": "5g",
      "calories": 350
    },
    "featured": true,
    "category": "dinner"
  }
]
```

---

### GET `/recipes/:id`
Get single recipe by ID.

**Response:** `200 OK` (Recipe object)

---

### GET `/recipes/search`
Search recipes.

**Query Params:**
- `q`: search query
- `ingredients` (optional): comma-separated ingredients

**Response:** `200 OK` (Array of recipes)

---

### GET `/recipes/featured`
Get featured recipes.

**Response:** `200 OK` (Array of featured recipes)

---

### GET `/recipes/count/total`
Get total count of recipes in database.

**Response:** `200 OK`
```json
{
  "total": 156
}
```

---

## 🤖 AI Recipes (Powered by OpenAI)

**Note:** Requires `OPENAI_API_KEY` in environment variables. See [AI_RECIPES.md](AI_RECIPES.md) for detailed setup guide.

### POST `/ai-recipes/generate`
Generate custom recipes using AI based on available ingredients and leftovers.

**🎯 Smart Defaults:** Automatically uses your saved profile preferences:
- **Dietary Restrictions** → Applied if not specified in request
- **Allergies** → Always enforced for safety (cannot be overridden)
- **Household Size** → Used as default servings
- **Skill Level** → Used as default difficulty (beginner→easy, intermediate→medium, advanced→hard)

**🛒 Smart Data Integration (NEW):** Automatically fetches from your journal:
- **Available Ingredients** → Uses items from your recent purchases (last 7 days)
- **Leftovers** → Fetches your active leftover meals (meals with portions remaining)
- Set `use_stored_data: false` to disable automatic fetching

**Headers:** `Authorization: Bearer {token}`

**Request Body (All fields optional!):**
```json
{
  "available_ingredients": [
    "chicken breast",
    "rice",
    "bell peppers"
  ],
  "leftovers": ["roasted vegetables"],
  "servings": 4,
  "difficulty": "easy",
  "dietary_restrictions": ["gluten-free"],
  "cuisine_preference": "italian",
  "max_recipes": 5,
  "save_to_database": true,
  "use_stored_data": true
}
```

**Minimal Request (Uses ALL smart defaults):**
```json
{
  "max_recipes": 5
}
```
This will:
- ✅ Fetch ingredients from your recent purchases
- ✅ Fetch leftovers from your journal
- ✅ Apply your dietary restrictions
- ✅ Use your household size for servings
- ✅ Avoid your allergies

**Optional Fields:**
- `available_ingredients` (array of strings, default: from recent purchases)
- `leftovers` (array of strings, default: from active leftover meals)
- `servings` (integer, 1-12, default: user's household_size or 4)
- `difficulty` (string: "easy", "medium", "hard", default: based on user's skill_level)
- `dietary_restrictions` (array of strings, default: user's dietary_restrictions)
- `cuisine_preference` (string)
- `max_recipes` (integer, 1-20, default: 5)
- `save_to_database` (boolean, default: false)
- `use_stored_data` (boolean, default: true)
- `minimize_shopping` (boolean, default: false) - **NEW!** Recipes only use available ingredients + common pantry staples (no shopping needed)

**🛒 Minimize Shopping Mode:**
Set `minimize_shopping: true` to get recipes that DON'T require buying new ingredients:
```json
{
  "minimize_shopping": true,
  "max_recipes": 5
}
```
Recipes will:
- ✅ Use ONLY your available ingredients (from purchases/manual list)
- ✅ Only add common pantry staples (salt, pepper, oil, flour, basic spices)
- ✅ NO fresh ingredients not in your list
- ✅ NO specialty or uncommon ingredients
- 🎯 Goal: Cook without going shopping!

**Note:** User's allergies are ALWAYS enforced even if not explicitly provided in the request.

**Response:** `200 OK`
```json
{
  "count": 5,
  "recipes": [
    {
      "name": "Mediterranean Chicken Rice Bowl",
      "description": "A healthy and flavorful one-bowl meal",
      "prep_time": "15 minutes",
      "servings": 4,
      "difficulty": "easy",
      "ingredients": [
        "400g chicken breast",
        "2 cups rice",
        "2 bell peppers, diced",
        "1 onion, chopped",
        "3 cloves garlic, minced"
      ],
      "instructions": [
        "Cook rice according to package instructions",
        "Season and cook chicken breast until golden",
        "Sauté vegetables in olive oil",
        "Combine all ingredients and serve hot"
      ],
      "tags": ["chicken", "rice", "healthy", "gluten-free"],
      "uses_leftovers": true,
      "leftover_items_used": ["roasted vegetables"],
      "calories": 450,
      "protein": "35g",
      "carbs": "48g",
      "fat": "12g"
    }
  ],
  "saved_to_database": true
}
```

---

### POST `/ai-recipes/quick-generate`
Quick recipe generation with just ingredients (simplified version).

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `max_recipes` (optional): integer, 1-20, default: 3

**Request Body:** Array of ingredient strings
```json
["pasta", "tomato sauce", "basil", "mozzarella", "olive oil"]
```

**Response:** `200 OK` (Same structure as `/generate`)

---

### POST `/ai-recipes/leftover-recipes`
Generate recipes specifically optimized for using leftovers.

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `leftovers` (required): array of leftover items
- `pantry_items` (optional): array of pantry staples available
- `max_recipes` (optional): integer, 1-20, default: 3

**Example Request:**
```
POST /api/ai-recipes/leftover-recipes?leftovers=leftover%20pizza&leftovers=half%20onion&pantry_items=eggs&pantry_items=cheese&max_recipes=3
```

**Response:** `200 OK` (Same structure as `/generate`)

---

### POST `/ai-recipes/for-challenge`
Generate recipes specifically tailored for a challenge or mission.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "challenge_id": "uuid-string",     // Optional: Challenge ID
  "mission_id": "uuid-string",       // Optional: Mission ID (one required)
  "max_recipes": 5,                  // Optional: default 5
  "save_to_database": false          // Optional: default false
}
```

**Important:** Either `challenge_id` or `mission_id` is required.

**Challenge Type Handling:**
- **Budget Boss Challenge**: Generates affordable recipes, minimal shopping, easy difficulty
- **Zero Waste Challenge**: Prioritizes leftovers and waste reduction
- **Batch Cooking Challenge**: Meal-prep friendly, freezer-safe recipes

**Mission Category Handling:**
- **New Recipe Mission**: Adventurous cuisines and new techniques
- **Budget Mission**: Cost-conscious meal ideas
- **Leftover Mission**: Creative leftover repurposing

**Example Request:**
```json
{
  "challenge_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "max_recipes": 3,
  "save_to_database": false
}
```

**Response:** `200 OK`
```json
{
  "recipes": [
    {
      "name": "Budget-Friendly Veggie Stir Fry",
      "description": "Quick and affordable meal using pantry staples",
      "prep_time": "15 minutes",
      "servings": 4,
      "difficulty": "easy",
      "ingredients": ["rice", "frozen vegetables", "soy sauce", "garlic"],
      "instructions": ["Heat oil in wok...", "Add garlic and stir fry..."],
      "calories": 280,
      "protein": "8g",
      "carbs": "45g",
      "fat": "8g",
      "tags": ["budget-friendly", "quick", "vegetarian", "challenge"],
      "uses_leftovers": false,
      "leftover_items_used": null
    }
  ],
  "count": 1,
  "saved_to_database": false
}
```

**Features:**
- ✅ Analyzes challenge/mission goals and constraints
- ✅ Uses recent purchases and active leftovers
- ✅ Respects dietary restrictions and allergies
- ✅ Matches difficulty to mission level
- ✅ Provides context-aware recipe suggestions
- ✅ Fallback to static recipes if AI unavailable

**See Also:** [CHALLENGE_RECIPES.md](./CHALLENGE_RECIPES.md) for detailed documentation

---

## 📅 Meal Plans

**Important**: Each MealPlan represents a specific week. When users navigate between weeks in the planning view, they're switching between different MealPlan records. Each week has its own separate:
- Planned meals (PlannedMeal[])
- Shopping list (ShoppingListItem[])

### GET `/meal-plans`
Get user's meal plans.

**Query Params:**
- `status` (optional): `draft` | `active` | `completed`
- `from` (optional): Start date filter
- `to` (optional): End date filter

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Week of Feb 5",
    "start_date": "2024-02-05",
    "end_date": "2024-02-11",
    "status": "active",
    "total_cost": 75.50,
    "meals": [
      {
        "id": "uuid",
        "date": "2024-02-05",
        "meal_type": "dinner",
        "recipe_id": "uuid",
        "recipe_name": "Chicken Stir Fry",
        "servings": 4,
        "is_batch": true,
        "is_leftovers": false
      }
    ],
    "shopping_list": [
      {
        "id": "uuid",
        "name": "Chicken breast",
        "quantity": "2 lbs",
        "category": "protein",
        "purchased": false,
        "estimated_cost": 12.00
      }
    ]
  }
]
```

---

### GET `/meal-plans/:id`
Get single meal plan.

**Response:** `200 OK` (Meal plan object)

---

### GET `/meal-plans/current`
Get current active meal plan (for current week).

**Response:** `200 OK` (Meal plan object or 404 if none)

---

### GET `/meal-plans/week`
Get or create meal plan for a specific week.

**Query Params:**
- `date` (required): Any date within the week (ISO format)

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Week of Feb 12",
  "start_date": "2024-02-12",
  "end_date": "2024-02-18",
  "status": "draft",
  "meals": [],
  "shopping_list": []
}
```

---

### POST `/meal-plans`
Create new meal plan for a specific week.

**Request Body:**
```json
{
  "name": "Week of Feb 12",
  "start_date": "2024-02-12",
  "end_date": "2024-02-18",
  "meals": [
    {
      "date": "2024-02-12",
      "meal_type": "dinner",
      "recipe_id": "uuid",
      "recipe_name": "Pasta Carbonara",
      "servings": 2
    }
  ]
}
```

**Response:** `201 Created` (Meal plan object)

---

### PATCH `/meal-plans/:id`
Update meal plan.

**Request Body:**
```json
{
  "status": "active",
  "total_cost": 85.00
}
```

**Response:** `200 OK` (Updated meal plan)

---

### DELETE `/meal-plans/:id`
Delete meal plan.

**Response:** `204 No Content`

---

### POST `/meal-plans/:id/meals`
Add a meal to a meal plan.

**Request Body:**
```json
{
  "date": "2024-02-13",
  "meal_type": "lunch",
  "recipe_id": "uuid",
  "servings": 2
}
```

**Response:** `201 Created` (PlannedMeal object)

---

### PATCH `/meal-plans/:planId/meals/:mealId`
Update a planned meal.

**Request Body:**
```json
{
  "servings": 4,
  "is_batch": true
}
```

**Response:** `200 OK` (Updated PlannedMeal)

---

### DELETE `/meal-plans/:planId/meals/:mealId`
Remove a meal from the plan.

**Response:** `204 No Content`

---

### POST `/meal-plans/:id/shopping-list`
Add item to shopping list.

**Request Body:**
```json
{
  "name": "Olive oil",
  "quantity": "1 bottle",
  "category": "pantry",
  "estimated_cost": 8.99
}
```

**Response:** `201 Created` (ShoppingListItem object)

---

### PATCH `/meal-plans/:planId/shopping-list/:itemId`
Update shopping list item (e.g., mark as purchased).

**Request Body:**
```json
{
  "purchased": true
}
```

**Response:** `200 OK` (Updated ShoppingListItem)

---

### DELETE `/meal-plans/:planId/shopping-list/:itemId`
Remove item from shopping list.

**Response:** `204 No Content`

---

## 👤 User Profile

### GET `/user/me`
Get complete user information including profile, preferences, and stats in one call.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "profile": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "avatar_url": null,
    "is_active": true,
    "is_premium": false
  },
  "preferences": {
    "dietary_restrictions": ["vegetarian"],
    "allergies": ["peanuts"],
    "budget_goal": 100.00,
    "household_size": 2,
    "skill_level": "intermediate"
  },
  "stats": {
    "total_meals_cooked": 45,
    "total_money_saved": 340.50,
    "current_streak": 7,
    "achievements_unlocked": 12,
    "level": 5,
    "points": 1250
  }
}
```

---

### GET `/user/me/profile`
Get user profile only.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "avatar_url": null,
  "oauth_provider": null,
  "oauth_id": null,
  "is_active": true,
  "is_premium": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### PATCH `/user/me/me/profile`
Update user profile.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "John Smith"
}
```

**Response:** `200 OK` (Updated profile)

---

### GET `/user/me/preferences`
Get user preferences.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "dietary_restrictions": ["vegetarian"],
  "allergies": ["peanuts"],
  "budget_goal": 100.00,
  "household_size": 2,
  "skill_level": "intermediate"
}
```

---

### PATCH `/user/me/preferences`
Update user preferences.

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "budget_goal": 120.00,
  "household_size": 3
}
```

**Response:** `200 OK` (Updated preferences)

---

### GET `/user/me/stats`
Get user statistics.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "total_meals_cooked": 45,
  "total_money_saved": 340.50,
  "current_streak": 7,
  "achievements_unlocked": 12,
  "level": 5,
  "points": 1250
}
```

---

## 📝 Content

### GET `/articles`
Get articles.

**Query Params:**
- `category` (optional): string
- `limit` (optional): number

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "10 Budget Meal Prep Tips",
    "content": "Full article content...",
    "image": "https://...",
    "category": "tips",
    "read_time": "5 min",
    "author": {
      "name": "Jane Smith",
      "avatar": "https://..."
    },
    "published_date": "2024-02-01T00:00:00Z"
  }
]
```

---

### GET `/videos`
Get videos.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "How to Batch Cook",
    "url": "https://youtube.com/...",
    "thumbnail": "https://...",
    "duration": "10:35",
    "published_date": "2024-02-01T00:00:00Z"
  }
]
```

---

## 🔧 Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid auth token
- `403 Forbidden` - Not allowed to access resource
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server error

## 🔒 Authentication

All endpoints except `/auth/*` require the `Authorization` header:

```
Authorization: Bearer {token}
```

Tokens expire after 24 hours. Use `/auth/refresh` to get a new token.
