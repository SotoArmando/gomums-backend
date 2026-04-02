"""
Seed regional recipes for Dominican Republic and Kansas
Generates culturally-appropriate recipes using local ingredients from CSV data
"""
import psycopg2
import json
import csv
import os
from dotenv import load_dotenv
import time

load_dotenv()

# OpenAI client will be initialized when needed
_openai_client = None


def get_openai_client():
    """Lazy initialization of OpenAI client"""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def read_ingredients_from_csv(csv_path):
    """Read available ingredients from CSV price data"""
    ingredients = []
    
    # List of measurement patterns to remove
    measurements = [
        '(Regular, 1 Liter)', '(1 kg)', '(500 g Loaf)', '(12, Large Size)',
        '(1 Head)', '(1.5 Liter)', '(Mid-Range)', '(0.5 Liter Bottle)',
        '(0.33 Liter Bottle)', '(0.33 Liter)', '(0.5 Liter)',
        '(Pack of 20, Marlboro)', '(Regular Size)', '(Three Courses, Without Drinks)',
        ' or Equivalent Fast-Food Meal', ' or Equivalent Back Leg Red Meat'
    ]
    
    # Items to skip (partial match)
    skip_keywords = ['Meal at', 'Meal for', 'Combo Meal', 'Cigarettes', 'Restaurants', 'Markets']
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            item_name = row.get('Item', '').strip()
            
            # Skip empty rows and specific categories
            if not item_name or any(keyword in item_name for keyword in skip_keywords):
                continue
            
            # Clean up ingredient names (remove quantities, measurements)
            cleaned_name = item_name
            for measurement in measurements:
                cleaned_name = cleaned_name.replace(measurement, '')
            
            cleaned_name = cleaned_name.strip()
            
            # Add cleaned ingredient if valid
            if cleaned_name and len(cleaned_name) > 2:
                ingredients.append(cleaned_name)
    
    return ingredients


def generate_recipes_with_ai(region_name, ingredients, num_recipes=10, batch_size=5):
    """Generate recipes using OpenAI for a specific region"""
    recipes = []
    
    # Define regional cuisine characteristics
    region_prompts = {
        "Dominican Republic": """Dominican cuisine is characterized by its fusion of Spanish, African, and Taíno influences. 
Popular dishes include Mangú, La Bandera, Sancocho, Tostones, Pastelón, Moro de Guandules, and Chicharrón.
Common ingredients include plantains, rice, beans, chicken, pork, beef, yuca (cassava), and tropical fruits.
Dishes often feature sofrito (sautéed aromatics), oregano, cilantro, and lime.""",
        
        "Kansas": """Kansas cuisine reflects Midwestern American cooking with BBQ influences. 
Popular dishes include Kansas City BBQ, chicken fried steak, pot roast, corn casseroles, bierocks, and wheat-based dishes.
Common ingredients include beef, chicken, corn, wheat flour, potatoes, beans, and seasonal vegetables.
Dishes are often hearty, comfort-food style with simple seasoning."""
    }
    
    cuisine_context = region_prompts.get(region_name, f"{region_name} local cuisine")
    
    # Generate recipes in batches
    num_batches = (num_recipes + batch_size - 1) // batch_size
    
    for batch_num in range(num_batches):
        recipes_to_generate = min(batch_size, num_recipes - len(recipes))
        
        prompt = f"""Generate {recipes_to_generate} authentic {region_name} recipes using these locally available ingredients:

{', '.join(ingredients[:50])}  # Limiting to first 50 ingredients to fit within prompt token limits

Regional context: {cuisine_context}

Requirements:
1. Each recipe should be authentic to {region_name} cuisine
2. Use ingredients from the provided list as much as possible
3. Include recipe name, prep time, servings (2-6), difficulty (easy/medium/hard)
4. Provide detailed ingredients list with amounts
5. Provide step-by-step instructions
6. Include nutrition estimates (calories, protein, carbs, fat, fiber)
7. Add relevant category (Breakfast/Lunch/Dinner/Snack)
8. Add appropriate tags
9. Make recipes practical and realistic for home cooking

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Recipe Name",
    "prep_time": "30 minutes",
    "servings": 4,
    "difficulty": "easy",
    "ingredients": ["ingredient 1 with amount", "ingredient 2 with amount"],
    "instructions": ["step 1", "step 2"],
    "calories": 350,
    "protein": "20g",
    "carbs": "45g",
    "fat": "10g",
    "fiber": "5g",
    "category": "Dinner",
    "tags": ["tag1", "tag2"]
  }}
]"""

        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a culinary expert specializing in regional cuisines. Generate authentic, practical recipes in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if content.startswith('```json'):
                content = content.split('```json')[1].split('```')[0].strip()
            elif content.startswith('```'):
                content = content.split('```')[1].split('```')[0].strip()
            
            batch_recipes = json.loads(content)
            
            # Add region-specific tags and metadata
            for recipe in batch_recipes:
                if not recipe.get('tags'):
                    recipe['tags'] = []
                recipe['tags'].append(region_name.lower().replace(' ', '-'))
                recipe['featured'] = False
                recipe['image'] = None
                
            recipes.extend(batch_recipes)
            print(f"✓ Generated batch {batch_num + 1}/{num_batches} ({len(batch_recipes)} recipes)")
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"✗ Error generating batch {batch_num + 1}: {e}")
            continue
    
    return recipes[:num_recipes]  # Return exact number requested


def seed_regional_recipes(region_name, csv_path, num_recipes=100):
    """Seed recipes for a specific region"""
    print(f"\n{'='*60}")
    print(f"Generating {num_recipes} recipes for {region_name}")
    print(f"{'='*60}\n")
    
    # Read ingredients from CSV
    print(f"📖 Reading ingredients from {csv_path}...")
    ingredients = read_ingredients_from_csv(csv_path)
    print(f"✓ Found {len(ingredients)} available ingredients")
    
    # Generate recipes using AI
    print(f"\n🤖 Generating recipes with AI...")
    recipes = generate_recipes_with_ai(region_name, ingredients, num_recipes, batch_size=5)
    print(f"✓ Successfully generated {len(recipes)} recipes")
    
    if len(recipes) == 0:
        print("⚠️  No recipes generated. Skipping database insertion.")
        return
    
    # Connect to database
    print(f"\n💾 Inserting recipes into database...")
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    
    try:
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO recipes (
                    name, image, prep_time, servings, difficulty,
                    ingredients, instructions, steps,
                    calories, protein, carbs, fat, fiber,
                    featured, category, tags
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s::jsonb,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
            """
            
            inserted_count = 0
            for recipe in recipes:
                try:
                    cur.execute(insert_query, (
                        recipe.get("name"),
                        recipe.get("image"),
                        recipe.get("prep_time"),
                        recipe.get("servings"),
                        recipe.get("difficulty", "medium"),
                        recipe.get("ingredients", []),
                        recipe.get("instructions", []),
                        json.dumps([]),  # steps - empty for now
                        recipe.get("calories"),
                        recipe.get("protein"),
                        recipe.get("carbs"),
                        recipe.get("fat"),
                        recipe.get("fiber"),
                        recipe.get("featured", False),
                        recipe.get("category"),
                        recipe.get("tags", [])
                    ))
                    inserted_count += 1
                    if inserted_count % 10 == 0:
                        print(f"  Inserted {inserted_count}/{len(recipes)} recipes...")
                except Exception as e:
                    print(f"  ✗ Error inserting recipe '{recipe.get('name')}': {e}")
                    continue
            
            conn.commit()
            print(f"\n✅ Successfully inserted {inserted_count}/{len(recipes)} recipes for {region_name}!")
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()


def main():
    """Main function to seed recipes for both regions"""
    print("\n" + "="*60)
    print("GoMums - Regional Recipe Generation")
    print("="*60)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("Please set OPENAI_API_KEY in your .env file to use AI generation")
        return
    
    # Get the path to CSV files
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dr_csv = os.path.join(base_dir, "excel docs", "Dominican Republic.csv")
    ks_csv = os.path.join(base_dir, "excel docs", "Kansas.csv")
    
    # Check if CSV files exist
    if not os.path.exists(dr_csv):
        print(f"✗ Error: Dominican Republic CSV not found at {dr_csv}")
        return
    if not os.path.exists(ks_csv):
        print(f"✗ Error: Kansas CSV not found at {ks_csv}")
        return
    
    # Ask user what to generate
    print("\nWhat would you like to do?")
    print("1. Generate 100 Dominican Republic recipes")
    print("2. Generate 100 Kansas recipes")
    print("3. Generate both (200 total recipes)")
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        seed_regional_recipes("Dominican Republic", dr_csv, 100)
    elif choice == "2":
        seed_regional_recipes("Kansas", ks_csv, 100)
    elif choice == "3":
        seed_regional_recipes("Dominican Republic", dr_csv, 100)
        seed_regional_recipes("Kansas", ks_csv, 100)
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\n" + "="*60)
    print("✅ Regional recipe generation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
