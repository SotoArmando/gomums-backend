# Challenge & Mission Recipe Generation

Generate AI-powered recipes specifically tailored to help users complete challenges and missions.

## Endpoint

```
POST /api/ai-recipes/for-challenge
```

## Features

- **Smart Context Awareness**: Analyzes challenge/mission goals and constraints
- **Budget Optimization**: For budget challenges, generates affordable recipes
- **Leftover Focus**: For waste-reduction challenges, prioritizes using leftovers
- **Meal Prep**: For batch cooking challenges, suggests freezer-friendly recipes
- **Difficulty Matching**: Respects mission difficulty levels
- **User Preferences**: Integrates dietary restrictions, allergies, and household size
- **Ingredient Intelligence**: Uses recent purchases and active leftovers

## Request Body

```json
{
  "challenge_id": "uuid-string",  // Optional: Challenge ID
  "mission_id": "uuid-string",    // Optional: Mission ID (one required)
  "max_recipes": 5,               // Optional: Number to generate (default: 5)
  "save_to_database": false       // Optional: Save recipes (default: false)
}
```

**Note**: Either `challenge_id` or `mission_id` is required, but not both.

## Response

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
      "instructions": ["Step 1...", "Step 2..."],
      "calories": 280,
      "protein": "8g",
      "carbs": "45g",
      "fat": "8g",
      "tags": ["budget-friendly", "quick", "vegetarian"],
      "uses_leftovers": false,
      "leftover_items_used": null
    }
  ],
  "count": 1,
  "saved_to_database": false
}
```

## Challenge Type Handling

### Budget Boss Challenge
- Generates affordable, cost-effective recipes
- Focuses on pantry staples and common ingredients
- Sets `minimize_shopping` to true
- Easy difficulty recipes
- Tags: `budget-friendly`, `affordable`

### Zero Waste Challenge
- Prioritizes using leftovers
- Suggests creative ways to repurpose meals
- Tags: `leftover-focused`, `waste-reduction`

### Batch Cooking Challenge
- Meal-prep friendly recipes
- Freezer-safe suggestions
- Larger portion sizes
- Tags: `meal-prep`, `freezer-friendly`

## Mission Category Handling

### New Recipe Mission
- Adventurous cuisines and techniques
- Encourages trying new ingredients
- Tags: `adventurous`, `new-cuisine`

### Budget Mission
- Cost-conscious meal ideas
- Similar to Budget Challenge handling
- Tags: `budget-friendly`

### Leftover Mission
- Specifically uses active leftovers
- Creative repurposing ideas
- Tags: `leftover-focused`

## Example Usage

### Generate Recipes for Active Challenge

```python
import requests

API_URL = "http://localhost:8000/api"
headers = {"Authorization": f"Bearer {access_token}"}

# Get active challenges first
challenges = requests.get(
    f"{API_URL}/challenges/user/active",
    headers=headers
).json()

challenge_id = challenges[0]['challenge_id']

# Generate recipes for the challenge
response = requests.post(
    f"{API_URL}/ai-recipes/for-challenge",
    json={
        "challenge_id": challenge_id,
        "max_recipes": 5,
        "save_to_database": False
    },
    headers=headers
)

recipes = response.json()
print(f"Generated {recipes['count']} recipes for the challenge!")
```

### Generate Recipes for Mission

```python
# Get active missions
missions = requests.get(
    f"{API_URL}/missions/active",
    headers=headers
).json()

mission_id = missions[0]['mission_id']

# Generate recipes for the mission
response = requests.post(
    f"{API_URL}/ai-recipes/for-challenge",
    json={
        "mission_id": mission_id,
        "max_recipes": 3,
        "save_to_database": True  # Save for future reference
    },
    headers=headers
)

recipes = response.json()
for recipe in recipes['recipes']:
    print(f"✓ {recipe['name']} - {recipe['prep_time']}")
```

## Error Handling

### 400 Bad Request
- Neither `challenge_id` nor `mission_id` provided
- Both `challenge_id` and `mission_id` provided

### 404 Not Found
- Challenge or mission doesn't exist
- Mission is not active for the user

### 500 Internal Server Error
- AI generation failed (fallback to static recipes)
- Database connection issues

## Fallback Behavior

When OpenAI API is unavailable:
1. Uses curated static recipe database (20 recipes)
2. Filters by dietary restrictions and allergies
3. Prioritizes recipes matching challenge type
4. Returns appropriate recipes for the context

## Integration with Smart Defaults

The endpoint automatically integrates:
- ✅ User dietary restrictions
- ✅ User allergies (strict exclusion)
- ✅ Household size for servings
- ✅ Skill level for difficulty
- ✅ Recent purchases (last 7 days)
- ✅ Active leftovers (portions > 0)

## Best Practices

1. **Fetch Challenge/Mission First**: Get the active challenge/mission details before generating
2. **Save Important Recipes**: Set `save_to_database: true` for recipes you plan to use
3. **Review Goals**: Check the challenge/mission goals to understand recipe alignment
4. **Monitor Progress**: Use generated recipes and track completion through normal endpoints
5. **Request Appropriate Amounts**: Don't request 20 recipes for a simple challenge

## Testing

Run the test suite:
```bash
python test_ai_recipes.py
```

The test includes a challenge-specific generation test (Test 7) that:
- Fetches active challenges
- Generates recipes for the first challenge
- Displays recipe suggestions with difficulty and time

## Related Endpoints

- `GET /api/challenges/user/active` - Get active challenges
- `GET /api/missions/active` - Get active missions
- `POST /api/ai-recipes/generate` - General recipe generation
- `POST /api/ai-recipes/quick-generate` - Quick recipe generation
- `POST /api/ai-recipes/leftover-recipes` - Leftover-focused recipes
