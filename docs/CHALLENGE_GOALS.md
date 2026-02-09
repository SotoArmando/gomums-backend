# Challenge Goals System

## Goal Types

### 1. **Auto-Trackable Goals**
Goals that can be automatically tracked based on journal entries:

- **Meal Count Goals**: "Cook X meals at home"
  - Triggers: Any `meal` journal entry
  
- **Leftover Goals**: "Use leftovers X times"
  - Triggers: `meal` entries with `used_leftovers=true` or `status='leftovers'`
  
- **Batch Cooking Goals**: "Cook X meals with 3+ servings"
  - Triggers: `meal` entries with `portions >= 3`
  
- **Freeze Goals**: "Freeze X meals"
  - Triggers: `meal` entries with `status='frozen'`
  
- **New Recipe Goals**: "Try X new recipes"
  - Triggers: First time a unique recipe name is used
  
- **Ingredient Swap Goals**: "Log a meal with swapped ingredient"
  - Triggers: `meal` entries with `ingredient_swaps` data
  
- **Breakfast Goals**: "Cook breakfast X times"
  - Triggers: `meal` entries with `meal_type='breakfast'`
  
- **Consecutive Days**: "Cook for X consecutive days"
  - Calculates: Count of consecutive days with meal entries
  
- **Daily Budget Goals**: "Stay under daily budget X days" ✅ **NOW AUTO-TRACKED**
  - Requires: Budget settings via `/api/budget/settings` (weekly_budget)
  - Calculates: Daily budget = weekly_budget / 7
  - Tracks: Distinct days where total purchases ≤ daily budget
  
- **Savings Goals**: "Save $X total on groceries" ✅ **NOW AUTO-TRACKED**
  - Tracks: Cumulative `savings` from `ingredient_swaps` in purchase entries
  - Progress: Dollar amount saved (not count)

### 2. **Scoreable Goals (Manual Tracking Required)**
Goals that require additional systems or manual score updates:
  
- **Cuisine Goals**: "Cook recipes from X different cuisines"
  - Requires: Recipe metadata with cuisine tags
  - Future: Auto-track via recipe categorization
  
- **Share Recipe Goals**: "Share X recipes with friends"
  - Requires: Social sharing tracking
  - Future: Integration with share endpoints

## Implementation Guide

### Auto-Trackable Goals
Located in: `app/services/challenge_service.py`

```python
def update_challenges_on_journal_entry(...):
    # Goals are checked against journal entry properties
    # When criteria match, goal progress is incremented
    if <condition>:
        should_increment = True
```

### Scoreable Goals
These require additional systems:

1. **Budget System** (for budget/savings goals)
   - User sets daily/weekly budget
   - Purchase entries compared against budget
   - API to manually update goal scores

2. **Manual Score Update** (temporary solution)
   ```
   POST /api/challenges/progress/update
   {
     "user_challenge_id": "uuid",
     "goal_id": "uuid",
     "progress_increment": 1
   }
   ```

3. **Absolute Progress Update** (for calculated values)
   ```python
   ChallengeRepository.update_goal_progress_absolute(
       user_challenge_id=uuid,
       goal_id=uuid,
       progress_value=consecutive_days
   )
   ```

## Adding New Goal Types

### 1. Identify Goal Pattern
Determine keywords in goal description:
```python
goal_description = "Cook 5 one-pot meals"
# Keywords: "one-pot", "cook", "meal"
```

### 2. Add Detection Logic
In `challenge_service.py`:
```python
if "one-pot" in goal_description or "one pot" in goal_description:
    if "one-pot" in (recipe_name or "").lower():
        should_increment = True
```

### 3. Update Test Script
In `test_all_challenges.py`:
```python
elif "one-pot" in goals_text or "one pot" in goals_text:
    print("\n🍲 Creating one-pot meal entries...")
    # Create test entries that match criteria
```

### 4. Document Goal Type
Add to this file and update API documentation.

## Testing Goals

Run challenge tests:
```bash
python3 cleanup_challenge_master.py && python3 test_all_challenges.py
```

Select a challenge to test automatic goal tracking.

## Future Enhancements

1. **Goal Metadata**
   - Add `tracking_type` field to challenge_goals table
   - Values: 'auto', 'manual', 'calculated'
   
2. **Budget Integration**
   - User budget settings
   - Purchase-to-budget comparison
   - Automatic savings calculation
   
3. **Recipe Metadata**
   - Cuisine tags
   - Difficulty levels
   - Cooking methods (one-pot, slow-cooker, etc.)
   
4. **Social Features**
   - Recipe sharing endpoints
   - Track share events for goals
