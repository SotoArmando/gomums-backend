# Recipe API Testing

This document describes how to test the Recipe API endpoints.

## Prerequisites

1. **Database Setup**: Run `seed_recipes.py` to populate the database with sample recipes
   ```bash
   python3 seed_recipes.py
   ```

2. **Server Running**: Start the FastAPI server
   ```bash
   python3 -m uvicorn app.main:app --reload
   ```

## Running Tests

```bash
python3 test_recipes.py
```

## Endpoints Tested

### 1. GET /api/recipes
- Get all recipes with optional filtering
- Filters: category, difficulty, featured, search, tags
- Pagination: limit and offset parameters
- Authentication: Required (Bearer token)

**Test Cases**:
- ✅ Get all recipes (8 recipes)
- ✅ Filter by featured status (4 featured)
- ✅ Filter by category: Dinner (4 recipes)
- ✅ Filter by difficulty: easy (6 recipes)
- ✅ Search by keyword: 'chicken' (1 result)
- ✅ Filter by tags: 'vegetarian' (3 recipes)
- ✅ Pagination (limit=3, offset=0 and offset=3)

### 2. GET /api/recipes/{id}
- Get a single recipe by UUID
- Returns detailed recipe information including ingredients and instructions
- Authentication: Required (Bearer token)

**Test Cases**:
- ✅ Get recipe by ID (Beef Tacos)
- ✅ Includes nutrition info (calories, protein, carbs, fat, fiber)
- ✅ Includes ingredients array (8 items)
- ✅ Includes instructions array (6 steps)

### 3. GET /api/recipes/count/total
- Get total count of recipes matching filters
- Useful for pagination UI
- Authentication: Required (Bearer token)

**Test Cases**:
- ✅ Get total recipe count (8 recipes)

## Sample Recipes

The seed script adds 8 recipes:
1. **Spaghetti Bolognese** (Dinner, Easy, Featured) - Italian pasta
2. **Chicken Stir Fry** (Dinner, Easy, Featured) - Asian quick meal
3. **Fluffy Pancakes** (Breakfast, Easy) - Sweet breakfast
4. **Caesar Salad** (Lunch, Easy) - Light salad
5. **Beef Tacos** (Dinner, Easy, Featured) - Mexican family meal
6. **Vegetable Soup** (Lunch, Easy) - Healthy vegetarian
7. **Chocolate Chip Cookies** (Snack, Medium) - Dessert/baking
8. **Grilled Salmon** (Dinner, Medium, Featured) - High protein

## Filter Examples

```bash
# Get featured recipes
GET /api/recipes/?featured=true

# Get dinner recipes
GET /api/recipes/?category=Dinner

# Get easy recipes
GET /api/recipes/?difficulty=easy

# Search for chicken
GET /api/recipes/?search=chicken

# Get vegetarian recipes
GET /api/recipes/?tags=vegetarian

# Multiple filters
GET /api/recipes/?category=Dinner&difficulty=easy&featured=true

# Pagination
GET /api/recipes/?limit=5&offset=0
GET /api/recipes/?limit=5&offset=5
```

## Expected Results

All tests should pass with:
- ✅ Authentication working
- ✅ All filtering options functional
- ✅ Search returning correct results
- ✅ Pagination working correctly
- ✅ Individual recipe retrieval with full details
- ✅ Recipe count endpoint accurate

## Troubleshooting

### 404 Not Found
- Ensure server is running on port 8000
- Check that recipe router is registered in `main.py`
- Verify router has no duplicate prefix

### No Recipes Found
- Run `seed_recipes.py` to add sample data
- Check database connection
- Verify recipes table exists

### Authentication Errors
- Ensure user is registered and logged in
- Check JWT token is valid and not expired
- Verify Authorization header format: `Bearer <token>`

## Next Steps

After Recipe API is validated:
1. ✅ Phase 4.1 Priority 1 is **COMPLETE**
2. Move to Phase 4.2 Priority 2:
   - Missions endpoints
   - User profile endpoints
   - Advanced Journal features
