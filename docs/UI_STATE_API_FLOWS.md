# UI → State → API Flow Documentation

This document maps the frontend UI views to app state and their corresponding API endpoints.

---

## 1. Log a Meal Flow

### UI Screens
```
[What would you like to log?] → [Select Recipe] → [Choose Preferences] → Submit
```

### Step-by-Step Flow

#### Step 1: "What would you like to log?" View
User selects "Log a Meal"

**App State:**
```typescript
{
  logType: 'meal'
}
```

---

#### Step 2: Select Recipe View
User browses and picks a recipe from contextual sources

**API Calls:**
```
// Primary: Today's planned meals (from meal plan)
GET /api/meal-plans/current
→ Extract planned_meals where date = today

// Secondary: User's private recipes added this week
GET /api/user-recipes/by-week?week_start=2026-02-09
→ Shows recipes grouped by day they were created

// Fallback/Browse More: All user recipes or public recipes
GET /api/user-recipes/?limit=20               // User's private recipes
GET /api/recipes/?limit=20                    // Public recipes
```

**Recipe Sources (in priority order):**

| Source | Description | API |
|--------|-------------|-----|
| Today's Plan | Meals already planned for today | `GET /api/meal-plans/current` → filter by today |
| This Week's Recipes | User's private recipes from this week | `GET /api/user-recipes/by-week` |
| My Recipes | All user's saved recipes | `GET /api/user-recipes/` |
| Public Recipes | Browse all available recipes | `GET /api/recipes/` |

**App State (after selection):**
```typescript
{
  logType: 'meal',
  selectedRecipe: {
    id: 'abc-123',
    name: 'Chicken Stir Fry',
    ingredients: ['chicken', 'broccoli', 'soy sauce'],
    servings: 4
  }
}
```

---

#### Step 3: Choose Preferences View
User configures meal details before logging

**UI Fields:**

| Field | Type | Options | Default |
|-------|------|---------|---------|
| Meal Type | Select | `breakfast`, `lunch`, `dinner`, `snack` | Based on time of day |
| Portions | Number | 1-20 | Recipe's `servings` value |
| Status | Select | `fresh`, `leftovers`, `frozen` | `fresh` |
| Used Leftovers? | Toggle | true/false | `false` |
| Has Leftovers? | Toggle | true/false | `false` |
| Is Batch Cooking? | Toggle | true/false | `false` |
| Ingredients Used | Multi-select | From recipe ingredients | All selected |

**App State (after preferences):**
```typescript
{
  logType: 'meal',
  selectedRecipe: { id: 'abc-123', name: 'Chicken Stir Fry', ... },
  mealPreferences: {
    meal_type: 'dinner',
    portions: 4,
    status: 'fresh',
    used_leftovers: false,
    has_leftovers: true,
    is_batch: false,
    ingredients_used: ['chicken', 'broccoli', 'soy sauce']
  }
}
```

---

#### Step 4: Submit → POST /api/journal/entries

**Request:**
```json
POST /api/journal/entries
{
  "type": "meal",
  "title": "Chicken Stir Fry",
  "meal_type": "dinner",
  "portions": 4,
  "status": "fresh",
  "used_leftovers": false,
  "has_leftovers": true,
  "is_batch": false,
  "ingredients_used": ["chicken", "broccoli", "soy sauce"]
}
```

**Response:**
```json
{
  "id": "entry-uuid",
  "user_id": "user-uuid",
  "type": "meal",
  "title": "Chicken Stir Fry",
  "meal_type": "dinner",
  "portions": 4,
  "portions_left": null,
  "status": "fresh",
  "ingredients_used": ["chicken", "broccoli", "soy sauce"],
  "is_batch": false,
  "used_leftovers": false,
  "has_leftovers": true,
  "needs_restock": false,
  "timestamp": "2026-02-10T18:30:00Z",
  "created_at": "2026-02-10T18:30:00Z",
  "updated_at": "2026-02-10T18:30:00Z"
}
```

---

## 2. Log a Purchase Flow

### UI Screens
```
[What would you like to log?] → [Purchase Details] → Submit
```

### Step-by-Step Flow

#### Step 1: "What would you like to log?" View
User selects "Log a Purchase"

**App State:**
```typescript
{
  logType: 'purchase'
}
```

---

#### Step 2: Purchase Details View
User enters store and items

**UI Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | Yes | Purchase description (e.g., "Weekly groceries") |
| Store | Text | Yes | Store name (e.g., "Walmart") |
| Items | List | Yes | Array of purchased items |

**Item Fields:**

| Field | Type | Required | Example |
|-------|------|----------|---------|
| name | Text | Yes | "Chicken breast" |
| quantity | Text | Yes | "2 lb" |
| cost | Number | Yes | 8.99 |
| category | Text | No | "proteins" |

**App State:**
```typescript
{
  logType: 'purchase',
  purchaseDetails: {
    title: 'Weekly groceries',
    store: 'Walmart',
    items: [
      { name: 'Chicken breast', quantity: '2 lb', cost: 8.99, category: 'proteins' },
      { name: 'Broccoli', quantity: '1 head', cost: 1.50, category: 'vegetables' },
      { name: 'Rice', quantity: '5 lb', cost: 4.99, category: 'grains' }
    ]
  }
}
```

---

#### Step 3: Submit → POST /api/journal/entries

**Request:**
```json
POST /api/journal/entries
{
  "type": "purchase",
  "title": "Weekly groceries",
  "store": "Walmart",
  "items": [
    { "name": "Chicken breast", "quantity": "2 lb", "cost": 8.99, "category": "proteins" },
    { "name": "Broccoli", "quantity": "1 head", "cost": 1.50, "category": "vegetables" },
    { "name": "Rice", "quantity": "5 lb", "cost": 4.99, "category": "grains" }
  ]
}
```

**Response:**
```json
{
  "id": "entry-uuid",
  "user_id": "user-uuid",
  "type": "purchase",
  "title": "Weekly groceries",
  "store": "Walmart",
  "items": [...],
  "timestamp": "2026-02-10T14:00:00Z",
  "created_at": "2026-02-10T14:00:00Z",
  "updated_at": "2026-02-10T14:00:00Z"
}
```

---

## 3. Add Recipe to Meal Plan (Calendar) Flow

### UI Screens
```
[Calendar Strip] → [+] → [Select Recipe] → Submit
```

### Step-by-Step Flow

#### Step 1: Calendar Strip
User taps a date

**App State:**
```typescript
{
  selectedDate: '2026-02-10'  // From calendar strip
}
```

---

#### Step 2: Tap "+" to Add Meal
Opens recipe selection

---

#### Step 3: Select Recipe View
Same as Log Meal flow - user picks a recipe

**App State:**
```typescript
{
  selectedDate: '2026-02-10',
  selectedRecipe: {
    id: 'abc-123',
    name: 'Chicken Stir Fry'
  }
}
```

---

#### Step 4: Choose Meal Type (Quick Preference)
Simple picker for meal slot

**UI Fields:**

| Field | Type | Options |
|-------|------|---------|
| Meal Type | Select | `breakfast`, `lunch`, `dinner`, `snack` |
| Servings | Number | 1-10 (default: recipe servings) |

**App State:**
```typescript
{
  selectedDate: '2026-02-10',
  selectedRecipe: { id: 'abc-123', name: 'Chicken Stir Fry' },
  mealSlot: {
    meal_type: 'dinner',
    servings: 4
  }
}
```

---

#### Step 5: Submit → POST /api/meal-plans/add-to-date

**Request:**
```json
POST /api/meal-plans/add-to-date
{
  "date": "2026-02-10",
  "meal_type": "dinner",
  "recipe_name": "Chicken Stir Fry",
  "recipe_id": "abc-123",
  "servings": 4
}
```

**Response:**
```json
{
  "id": "planned-meal-uuid",
  "meal_plan_id": "meal-plan-uuid",
  "date": "2026-02-10",
  "meal_type": "dinner",
  "recipe_id": "abc-123",
  "recipe_name": "Chicken Stir Fry",
  "servings": 4,
  "is_batch": false,
  "is_leftovers": false,
  "created_at": "2026-02-10T10:00:00Z",
  "updated_at": "2026-02-10T10:00:00Z"
}
```

---

## 4. Copy Public Recipe to My Recipes Flow

### UI Screens
```
[Browse Recipes] → [Recipe Detail] → [Save to My Recipes] → Done
```

### Flow

#### Step 1: Browse Public Recipes
```
GET /api/recipes/?limit=20
```

#### Step 2: View Recipe Detail
```
GET /api/recipes/{recipe_id}
```

**App State:**
```typescript
{
  viewingRecipe: {
    id: 'public-recipe-123',
    name: 'Apple Chicken',
    ingredients: [...],
    instructions: [...]
  }
}
```

#### Step 3: Tap "Save to My Recipes"
```
POST /api/user-recipes/copy-from-public/{recipe_id}
```

**Response:**
```json
{
  "id": "new-user-recipe-uuid",
  "user_id": "user-uuid",
  "name": "Apple Chicken",
  "source_recipe_id": "public-recipe-123",
  "is_favorite": false,
  ...
}
```

---

## State Management Summary

### Global App State Shape
```typescript
interface AppState {
  // Current flow
  currentFlow: 'log-meal' | 'log-purchase' | 'add-to-plan' | null;
  
  // Calendar
  selectedDate: string | null;  // ISO date 'YYYY-MM-DD'
  
  // Recipe selection
  selectedRecipe: Recipe | null;
  
  // Meal logging preferences
  mealPreferences: {
    meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
    portions: number;
    status: 'fresh' | 'leftovers' | 'frozen';
    used_leftovers: boolean;
    has_leftovers: boolean;
    is_batch: boolean;
    ingredients_used: string[];
  } | null;
  
  // Purchase logging
  purchaseDetails: {
    title: string;
    store: string;
    items: PurchaseItem[];
  } | null;
}

interface PurchaseItem {
  name: string;
  quantity: string;
  cost: number;
  category?: string;
}
```

---

## API Endpoint Quick Reference

| Action | Endpoint | Method |
|--------|----------|--------|
| Log meal or purchase | `/api/journal/entries` | POST |
| Get today's planned meals | `/api/meal-plans/current` | GET |
| Get user recipes by week | `/api/user-recipes/by-week?week_start=YYYY-MM-DD` | GET |
| Get public recipes | `/api/recipes/` | GET |
| Get my recipes | `/api/user-recipes/` | GET |
| Copy public recipe | `/api/user-recipes/copy-from-public/{id}` | POST |
| Add recipe to calendar date | `/api/meal-plans/add-to-date` | POST |
| Get week's meal plan | `/api/meal-plans/week?date=YYYY-MM-DD` | GET |
| Get current week's plan | `/api/meal-plans/current` | GET |
