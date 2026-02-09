# Regional Recipe Generation Guide

This guide explains how to generate 100 recipes for Dominican Republic and Kansas using AI.

## Prerequisites

1. **OpenAI API Key**: You need an OpenAI API key to generate recipes
   - Get your API key from https://platform.openai.com/api-keys
   - Add it to your `.env` file: `OPENAI_API_KEY=your-api-key-here`

2. **Database**: Ensure PostgreSQL is running and the database is set up
   - Database should be configured in `.env` file
   - Run `psql -U postgres -d gomums -f docs/DATABASE_SCHEMA.sql` if not already done

3. **Dependencies**: Install required Python packages
   ```bash
   pip install -r requirements.txt
   ```

## How It Works

The script `scripts/seeds/seed_regional_recipes.py`:

1. **Reads Local Ingredients**: Parses CSV files (`excel docs/Dominican Republic.csv` and `excel docs/Kansas.csv`) to extract locally available ingredients with their prices

2. **Generates AI Recipes**: Uses OpenAI GPT-4o-mini to generate culturally-authentic recipes
   - Dominican recipes: Features traditional dishes like Mangú, La Bandera, Sancocho, Tostones
   - Kansas recipes: Features Midwestern American cuisine with BBQ influences

3. **Seeds Database**: Inserts generated recipes into the PostgreSQL `recipes` table

## Usage

### Option 1: Interactive Mode (Recommended)

Run the script interactively to choose what to generate:

```bash
cd /home/runner/work/gomums-backend/gomums-backend
python scripts/seeds/seed_regional_recipes.py
```

You'll be prompted to choose:
- Generate 100 Dominican Republic recipes
- Generate 100 Kansas recipes
- Generate both (200 total recipes)

### Option 2: Direct Python Import

You can also import and use the functions directly:

```python
from scripts.seeds.seed_regional_recipes import seed_regional_recipes
import os

base_dir = "/home/runner/work/gomums-backend/gomums-backend"
dr_csv = os.path.join(base_dir, "excel docs", "Dominican Republic.csv")

# Generate 100 Dominican Republic recipes
seed_regional_recipes("Dominican Republic", dr_csv, 100)
```

## What Gets Generated

Each recipe includes:
- **Name**: Authentic regional dish name
- **Prep Time**: Cooking time estimate
- **Servings**: Number of servings (typically 2-6)
- **Difficulty**: easy, medium, or hard
- **Ingredients**: List with amounts
- **Instructions**: Step-by-step cooking instructions
- **Nutrition**: Calories, protein, carbs, fat, fiber
- **Category**: Breakfast, Lunch, Dinner, or Snack
- **Tags**: Relevant tags including regional identifier

## Cost Estimate

- Using GPT-4o-mini model
- Each batch generates 5 recipes
- 100 recipes = 20 batches
- Estimated cost: $0.50 - $1.00 per 100 recipes (depending on token usage)
- Total for 200 recipes: approximately $1.00 - $2.00

## Generation Time

- Each batch takes ~3-5 seconds (including rate limiting)
- 100 recipes take approximately 2-3 minutes
- 200 recipes (both regions) take approximately 5-7 minutes

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you have set `OPENAI_API_KEY` in your `.env` file
- Verify the file is in the project root directory

### "Database connection error"
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure the `gomums` database exists

### "CSV file not found"
- Verify the CSV files exist in `excel docs/` directory
- Files should be named exactly:
  - `Dominican Republic.csv`
  - `Kansas.csv`

## Recipe Quality

The AI-generated recipes are:
- ✅ Culturally authentic to their region
- ✅ Use locally available ingredients from the CSV data
- ✅ Include realistic cooking times and difficulty levels
- ✅ Provide detailed, step-by-step instructions
- ✅ Include nutrition information

## Verification

After running the script, verify recipes in the database:

```sql
-- Check total recipes
SELECT COUNT(*) FROM recipes;

-- Check Dominican Republic recipes
SELECT COUNT(*) FROM recipes WHERE 'dominican-republic' = ANY(tags);

-- Check Kansas recipes
SELECT COUNT(*) FROM recipes WHERE 'kansas' = ANY(tags);

-- View sample recipes
SELECT name, category, difficulty FROM recipes 
WHERE 'dominican-republic' = ANY(tags) 
LIMIT 10;
```

Or use the API:

```bash
# Get all recipes
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/recipes

# Filter by Dominican Republic
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/recipes?tags=dominican-republic&limit=100"

# Filter by Kansas
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/recipes?tags=kansas&limit=100"
```

## Next Steps

After generating the recipes, you can:
1. Test them through the API endpoints
2. Use them in meal planning features
3. Display them in the mobile app
4. Allow users to save favorites
5. Generate more recipes as needed
