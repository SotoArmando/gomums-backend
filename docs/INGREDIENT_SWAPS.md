# Ingredient Swap System

## Overview

The ingredient swap system allows users to track when they substitute ingredients in recipes, including the cost comparison between original and swapped ingredients. This enables automatic challenge tracking and savings calculation.

## Data Structure

### IngredientSwap Model

```json
{
  "recipe_id": "recipe-001",
  "original_ingredient": "bacon",
  "original_cost": 5.99,
  "swapped_ingredient": "beans",
  "swapped_cost": 1.99,
  "savings": 4.00
}
```

**Fields:**
- `recipe_id` (string, required): Reference to the recipe being modified
- `original_ingredient` (string, required): Name of the ingredient from the original recipe
- `original_cost` (float, optional): Cost of the original ingredient (≥ 0)
- `swapped_ingredient` (string, required): Name of the substituted ingredient used
- `swapped_cost` (float, optional): Cost of the swapped ingredient (≥ 0)
- `savings` (float, optional): Calculated savings (original_cost - swapped_cost)

## API Usage

### Creating a Meal with Ingredient Swaps

```http
POST /api/journal/entries
Content-Type: application/json

{
  "type": "meal",
  "title": "Budget Pasta",
  "meal_type": "dinner",
  "portions": 3,
  "ingredient_swaps": [
    {
      "recipe_id": "recipe-001",
      "original_ingredient": "bacon",
      "original_cost": 5.99,
      "swapped_ingredient": "beans",
      "swapped_cost": 1.99,
      "savings": 4.00
    },
    {
      "recipe_id": "recipe-001",
      "original_ingredient": "parmesan cheese",
      "original_cost": 6.49,
      "swapped_ingredient": "nutritional yeast",
      "swapped_cost": 3.99,
      "savings": 2.50
    }
  ]
}
```

### Response

```json
{
  "id": "meal-123",
  "user_id": "user-456",
  "type": "meal",
  "title": "Budget Pasta",
  "meal_type": "dinner",
  "portions": 3,
  "ingredient_swaps": [
    {
      "recipe_id": "recipe-001",
      "original_ingredient": "bacon",
      "original_cost": 5.99,
      "swapped_ingredient": "beans",
      "swapped_cost": 1.99,
      "savings": 4.00
    },
    {
      "recipe_id": "recipe-001",
      "original_ingredient": "parmesan cheese",
      "original_cost": 6.49,
      "swapped_ingredient": "nutritional yeast",
      "swapped_cost": 3.99,
      "savings": 2.50
    }
  ],
  "created_at": "2026-02-07T10:30:00Z"
}
```

## Challenge Integration

### Automatic Goal Tracking

When a meal with ingredient swaps is logged, the system automatically updates related challenge goals:

1. **Any Swap Goals**: Goals that mention "swap", "substitute", "ingredient", "replace", or "alternative" will progress when any ingredient_swaps data is present
   - Example: "Log a meal with a swapped ingredient" ✅

2. **Savings-Based Goals**: Goals that mention "save" or "savings" will ONLY progress when swaps have positive savings
   - Example: "Swap & Save Challenge" requires `savings > 0`
   - Verifies that swaps actually saved money

### Logic Flow

```python
if ingredient_swaps and len(ingredient_swaps) > 0:
    if "save" in goal_description:
        # Verify at least one swap has positive savings
        for swap in ingredient_swaps:
            if swap['savings'] > 0:
                increment_goal()
                break
    else:
        # Any swap counts for non-savings goals
        increment_goal()
```

## Use Cases

### 1. Budget-Conscious Swaps
Track when users substitute expensive ingredients with cheaper alternatives:
- Premium cuts → standard cuts
- Imported items → local alternatives
- Brand name → generic

### 2. Dietary Swaps
Track dietary substitutions (cost tracking optional):
- Meat → plant-based proteins
- Dairy → non-dairy alternatives
- Gluten → gluten-free alternatives

### 3. Challenge Completion
Automatically complete challenges like:
- "Swap & Save Challenge" (requires positive savings)
- "Try Ingredient Substitutions" (any swap counts)
- "Budget-Friendly Cooking" (must save money)

## Database Storage

Ingredient swaps are stored in the `journal_entries` table as a JSONB column:

```sql
ingredient_swaps JSONB -- Array of swap objects with cost information
```

Example stored value:
```json
[
  {
    "recipe_id": "recipe-001",
    "original_ingredient": "bacon",
    "original_cost": 5.99,
    "swapped_ingredient": "beans",
    "swapped_cost": 1.99,
    "savings": 4.00
  }
]
```

## Frontend Best Practices

### 1. Recipe-Based Input
When users cook from a recipe:
- Pre-fill original_ingredient from recipe data
- Fetch historical cost or use recipe's estimated cost
- Let user input swapped ingredient and its cost
- Auto-calculate savings

### 2. Progressive Enhancement
- **Minimum**: Just track swap names (original → swapped)
- **Better**: Include costs for savings calculation
- **Best**: Link to purchase history for automatic cost lookup

### 3. User Experience
```
┌─────────────────────────────────────┐
│ Recipe: Pasta Carbonara             │
├─────────────────────────────────────┤
│ Ingredients You Changed:            │
│                                     │
│ ✓ Bacon ($5.99) → Beans ($1.99)   │
│   💰 Saved $4.00                    │
│                                     │
│ ✓ Parmesan ($6.49) → Yeast ($3.99) │
│   💰 Saved $2.50                    │
│                                     │
│ Total Savings: $6.50                │
└─────────────────────────────────────┘
```

## Testing

See [test_all_challenges.py](../test_all_challenges.py) for example usage:

```python
meal_data = {
    "type": "meal",
    "title": "Budget Pasta",
    "meal_type": "dinner",
    "portions": 3,
    "ingredient_swaps": [
        {
            "recipe_id": "recipe-001",
            "original_ingredient": "bacon",
            "original_cost": 5.99,
            "swapped_ingredient": "beans",
            "swapped_cost": 1.99,
            "savings": 4.00
        }
    ]
}
```

## Migration

The `ingredient_swaps` column was added via migration:

```bash
python3 apply_ingredient_swaps_migration.py
```

This adds the JSONB column to the `journal_entries` table with appropriate comments and indexing.
