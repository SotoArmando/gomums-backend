# AI Recipe Generation Setup & Usage Guide

## 🎯 Smart User Data Integration

**NEW:** AI recipe generation now automatically uses your complete profile and journal data!

### Automatic Data Sources:

#### 1. **User Profile Preferences:**
- **🚫 Allergies** - ALWAYS enforced for safety (e.g., peanuts, shellfish)
- **🥗 Dietary Restrictions** - Used if not specified (e.g., vegetarian, vegan)
- **👥 Household Size** - Sets default servings based on your household
- **📊 Skill Level** - Adjusts recipe difficulty:
  - Beginner → Easy recipes
  - Intermediate → Medium recipes
  - Advanced → Hard recipes

#### 2. **Journal Data (NEW!):**
- **🛒 Recent Purchases** - Automatically fetches ingredients from your last 7 days of purchases
- **🍽️ Active Leftovers** - Identifies meals with remaining portions to help reduce waste

### How It Works:

**Zero-Config Recipe Generation:**
```bash
POST /api/ai-recipes/generate
{
  "max_recipes": 5
}
```

**The AI automatically:**
1. ✅ Fetches ingredients from your recent grocery purchases
2. ✅ Identifies leftover meals you need to use up
3. ✅ Applies your dietary restrictions (e.g., vegetarian)
4. ✅ Avoids your allergies (e.g., peanuts, shellfish)
5. ✅ Adjusts servings to your household size
6. ✅ Matches your cooking skill level

**You get personalized recipes without typing a single ingredient!**

**How to Set Your Preferences:**
```bash
PATCH /api/user/me/preferences
{
  "dietary_restrictions": ["vegetarian"],
  "allergies": ["peanuts", "shellfish"],
  "household_size": 4,
  "skill_level": "intermediate"
}
```

### 💡 How It Works - Examples:

**1. Zero-Config (Fully Automatic):**
```json
{
  "max_recipes": 5
}
```
✨ **Automatically uses:**
- Ingredients from your last 7 days of purchases
- Your active leftovers
- Your dietary restrictions
- Your household size
- Your skill level
- Avoids your allergies

**2. Partial Override (Mix of Auto + Manual):**
```json
{
  "available_ingredients": ["pasta", "tomatoes"],
  "max_recipes": 3
}
```
✨ **Automatically uses:**
- Your specified ingredients (overrides purchases)
- Your active leftovers (auto-fetched)
- Your dietary restrictions
- Your household size

**3. Full Manual Control:**
```json
{
  "available_ingredients": ["pasta", "tomatoes", "basil"],
  "leftovers": ["grilled chicken"],
  "servings": 2,
  "difficulty": "easy",
  "dietary_restrictions": ["vegetarian"],
  "use_stored_data": false,
  "max_recipes": 3
}
```
✨ **Only uses:**
- What you explicitly specify
- Still enforces allergies for safety

**Benefits:**
- ✅ **Zero typing** - Just request recipes, we handle the rest
- ✅ **Reduces food waste** - Uses your actual leftovers
- ✅ **Practical suggestions** - Based on what you actually bought
- ✅ **Safer** - Allergies are always enforced
- ✅ **Consistent** - Same preferences across all generations
- ✅ **Flexible** - Can still override any default

### 📝 Setting Up Your Data:

**1. Set Your Preferences:**
```bash
PATCH /api/user/me/preferences
{
  "dietary_restrictions": ["vegetarian"],
  "allergies": ["peanuts", "shellfish"],
  "household_size": 4,
  "skill_level": "intermediate"
}
```

**2. Log Your Purchases:**
```bash
POST /api/journal/entries
{
  "type": "purchase",
  "title": "Weekly Grocery Run",
  "store": "Walmart",
  "items": [
    {"name": "Chicken breast", "quantity": "2 lbs", "cost": 12.99},
    {"name": "Rice", "quantity": "5 lbs", "cost": 8.99},
    {"name": "Bell peppers", "quantity": "3 count", "cost": 4.50}
  ]
}
```

**3. Log Leftover Meals:**
```bash
POST /api/journal/entries
{
  "type": "meal",
  "title": "Roasted Chicken",
  "portions": 4,
  "portions_left": 2,
  "status": "leftover"
}
```

**4. Generate Recipes (Zero Config!):**
```bash
POST /api/ai-recipes/generate
{
  "max_recipes": 5
}
```

**Result:** AI suggests recipes using your chicken, rice, bell peppers, and incorporates your leftover roasted chicken!

### 🛒 Minimize Shopping Mode (NEW!)

**Problem:** Want to cook but don't want to go shopping?

**Solution:** Use `minimize_shopping: true`

```bash
POST /api/ai-recipes/generate
{
  "minimize_shopping": true,
  "max_recipes": 5
}
```

**What happens:**
- ✅ AI generates recipes using ONLY your available ingredients
- ✅ Can add common pantry staples: salt, pepper, oil, flour, basic spices
- ❌ NO fresh ingredients you don't have
- ❌ NO specialty or uncommon ingredients
- ❌ NO need to go shopping!

**Use Cases:**
1. **End of week pantry challenge** - Use up what you have before shopping
2. **Lazy Sunday** - Don't feel like going to the store
3. **Budget tight** - Can't spend money on groceries right now
4. **Food waste reduction** - Must use ingredients before they expire

**Example:**

Your available ingredients: Pasta, Eggs, Cheese, Garlic, Tomatoes

```json
{
  "minimize_shopping": true,
  "max_recipes": 3
}
```

**AI suggests:**
- "Garlic Pasta with Tomatoes and Eggs"
- "Cheesy Baked Pasta with Tomatoes"
- "Italian Pasta Frittata"

All recipes use ONLY: pasta, eggs, cheese, garlic, tomatoes + basic pantry items (salt, pepper, olive oil)

---

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install openai
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Add your OpenAI API key to `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Restart Server
```bash
python start_server_debug.py
```

---

## 📡 Available Endpoints

### 1. **Full Recipe Generation** (Recommended)
`POST /api/ai-recipes/generate`

**Features:**
- Specify available ingredients and leftovers
- Set dietary restrictions and cuisine preferences
- Control servings, difficulty, and max recipes
- Optionally save recipes to database

**Example Request:**
```json
{
  "available_ingredients": [
    "chicken breast",
    "rice",
    "bell peppers",
    "onions",
    "garlic"
  ],
  "leftovers": ["roasted vegetables"],
  "servings": 4,
  "difficulty": "easy",
  "dietary_restrictions": ["gluten-free"],
  "cuisine_preferences": ["italian", "mediterranean"],
  "max_recipes": 5,
  "save_to_database": true
}
```

**Required Fields:**
- `available_ingredients` (array of strings)

**Optional Fields:**
- `leftovers` (array of strings)
- `servings` (integer, default: 4)
- `difficulty` (string: "easy", "medium", "hard", default: "medium")
- `dietary_restrictions` (array of strings)
- `cuisine_preferences` (array of strings)
- `max_recipes` (integer, 1-20, default: 5)
- `save_to_database` (boolean, default: false)

---

### 2. **Quick Generation** (Simplified)
`POST /api/ai-recipes/quick-generate?max_recipes=3`

**Features:**
- Simple array of ingredients
- No complex parameters needed
- Fast lightweight generation

**Example Request:**
```json
["pasta", "tomato sauce", "basil", "mozzarella", "olive oil"]
```

**Query Parameters:**
- `max_recipes` (integer, 1-20, default: 3)

---

### 3. **Leftover-Focused Generation**
`POST /api/ai-recipes/leftover-recipes`

**Features:**
- Optimized for using up leftovers
- Minimal food waste
- Combines leftovers with pantry staples

**Example Request:**
```bash
POST /api/ai-recipes/leftover-recipes?max_recipes=3

Query Parameters:
- leftovers=leftover pizza&leftovers=half onion&leftovers=few mushrooms
- pantry_items=eggs&pantry_items=cheese&pantry_items=bread
```

---

## 📋 Response Format

All endpoints return the same structured response:

```json
{
  "count": 3,
  "recipes": [
    {
      "name": "Mediterranean Chicken Rice Bowl",
      "description": "A healthy and flavorful one-bowl meal...",
      "prep_time": "15 minutes",
      "cook_time": "30 minutes",
      "servings": 4,
      "difficulty": "easy",
      "ingredients": [
        "400g chicken breast",
        "2 cups rice",
        "2 bell peppers, diced",
        "1 onion, chopped",
        "3 cloves garlic, minced",
        "2 tbsp olive oil"
      ],
      "steps": [
        "Cook rice according to package instructions",
        "Season and cook chicken breast until golden...",
        "Sauté vegetables in olive oil...",
        "Combine all ingredients and serve hot"
      ],
      "tags": ["chicken", "rice", "healthy", "gluten-free"],
      "uses_leftovers": true,
      "leftover_items_used": ["roasted vegetables"],
      "calories": 450,
      "protein": 35,
      "carbs": 48,
      "fat": 12
    }
  ],
  "model_used": "gpt-4-turbo-preview"
}
```

---

## 🧪 Testing

Run the comprehensive test script:

```bash
python test_ai_recipes.py
```

This will:
1. Login as test user
2. Generate recipes from ingredients
3. Generate recipes using leftovers
4. Test quick generation
5. Test leftover-focused endpoint

---

## 💡 Usage Tips

### For Best Results:

1. **Be Specific with Ingredients**
   - ✅ "chicken breast" instead of "chicken"
   - ✅ "fresh basil" instead of "herbs"
   - ✅ "cheddar cheese" instead of "cheese"

2. **Include Pantry Staples**
   - Add: "olive oil", "salt", "pepper", "garlic"
   - These are commonly needed but often forgotten

3. **Use Dietary Restrictions**
   ```json
   "dietary_restrictions": [
     "vegetarian", 
     "dairy-free", 
     "gluten-free",
     "low-carb"
   ]
   ```

4. **Specify Cuisine for Variety**
   ```json
   "cuisine_preferences": [
     "italian",
     "mexican", 
     "asian",
     "mediterranean"
   ]
   ```

5. **Save Popular Recipes**
   - Set `save_to_database: true` for recipes you want to keep
   - Saved recipes become available to all users

6. **Minimize Shopping Mode** 🆕
   - Set `minimize_shopping: true` when you don't want to buy new ingredients
   - Great for end-of-week cooking or when you can't go shopping
   ```json
   {
     "minimize_shopping": true,
     "max_recipes": 5
   }
   ```

---

## 🎯 Use Cases

### 1. **Zero Food Waste**
Generate recipes that use up leftovers before they spoil:

```json
{
  "available_ingredients": ["eggs", "milk", "flour", "butter"],
  "leftovers": [
    "half roasted chicken",
    "cooked rice from yesterday",
    "steamed broccoli"
  ],
  "max_recipes": 3
}
```

### 2. **Meal Planning**
Generate 20 recipes at once for weekly meal planning:

```json
{
  "available_ingredients": [...],
  "servings": 4,
  "max_recipes": 20,
  "cuisine_preferences": ["varied"],
  "save_to_database": true
}
```

### 3. **Budget-Friendly Meals (No Shopping Required)** 🆕
You have limited ingredients and can't/won't go shopping:

**Without minimize_shopping:**
```json
{
  "available_ingredients": [
    "pasta",
    "eggs",
    "cheese"
  ],
  "max_recipes": 3
}
```
**Result:** "Carbonara" (needs: bacon, parsley), "Pasta Primavera" (needs: fresh vegetables), etc.
❌ Requires shopping for missing ingredients

**With minimize_shopping:**
```json
{
  "available_ingredients": [
    "pasta",
    "eggs",
    "cheese"
  ],
  "minimize_shopping": true,
  "max_recipes": 3
}
```
**Result:** "Simple Pasta Carbonara" (uses: pasta, eggs, cheese, salt, pepper), "Cheese & Egg Pasta Bake" (uses: pasta, eggs, cheese, oil), etc.
✅ NO shopping needed - only uses what you have + pantry staples!

### 4. **Traditional Budget Cooking**
Use simple, cheap ingredients:

```json
{
  "available_ingredients": [
    "pasta",
    "rice",
    "eggs",
    "canned beans",
    "frozen vegetables"
  ],
  "difficulty": "easy",
  "max_recipes": 10
}
```

### 4. **Special Diets**
Generate recipes for specific dietary needs:

```json
{
  "available_ingredients": [...],
  "dietary_restrictions": [
    "vegan",
    "gluten-free",
    "nut-free"
  ],
  "max_recipes": 5
}
```

---

## 🔧 Troubleshooting

### Error: "OpenAI API key not configured"
- Check `.env` file has `OPENAI_API_KEY=sk-...`
- Restart the server after adding the key

### Error: "Rate limit exceeded"
- You've hit OpenAI's rate limit
- Wait a few seconds and try again
- Consider upgrading your OpenAI plan

### Error: "Invalid request"
- Ensure `available_ingredients` is a non-empty array
- Check `max_recipes` is between 1-20
- Verify `difficulty` is one of: "easy", "medium", "hard"

### Recipes Not Saving to Database
- Check `save_to_database: true` is set
- Verify database connection is working
- Check server logs for errors

---

## 📊 Cost Estimation

OpenAI API pricing (as of 2024):
- **GPT-4-Turbo**: ~$0.01 per recipe
- **GPT-3.5-Turbo**: ~$0.001 per recipe

Generating 20 recipes:
- GPT-4: ~$0.20
- GPT-3.5: ~$0.02

To use GPT-3.5 (cheaper), modify [ai_recipes.py](app/api/routes/ai_recipes.py#L100):
```python
model="gpt-3.5-turbo"  # Instead of gpt-4-turbo-preview
```

---

## 🔐 Authentication

All AI recipe endpoints require authentication. Include the bearer token in headers:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

Get token from `/api/auth/login` endpoint.

---

## 📝 Notes

- **Response Time**: Typically 5-15 seconds depending on `max_recipes`
- **Token Limit**: Each request consumes OpenAI tokens
- **Quality**: GPT-4 produces better recipes than GPT-3.5, but costs more
- **Caching**: Consider implementing caching for identical requests
- **Database**: Saved recipes are stored in the `recipes` table

---

## 🎉 Examples from Test Script

See [test_ai_recipes.py](test_ai_recipes.py) for complete working examples including:
- Authentication flow
- Multiple endpoint usage patterns
- Response handling
- Error handling
