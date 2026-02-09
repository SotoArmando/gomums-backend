"""
Seed sample recipes into the database for testing
"""
import psycopg2
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Sample recipes for testing
SAMPLE_RECIPES = [
    {
        "name": "Spaghetti Bolognese",
        "image": "https://example.com/spaghetti.jpg",
        "prep_time": "45 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": [
            "400g spaghetti",
            "500g ground beef",
            "1 onion, diced",
            "2 cloves garlic, minced",
            "400g crushed tomatoes",
            "2 tbsp tomato paste",
            "1 tsp dried oregano",
            "Salt and pepper to taste",
            "Parmesan cheese for serving"
        ],
        "instructions": [
            "Dice the onion and mince the garlic",
            "Measure out tomato paste and oregano",
            "Cook spaghetti according to package directions",
            "In a large pan, cook ground beef until browned",
            "Add onion and garlic, cook until softened",
            "Add crushed tomatoes, tomato paste, and oregano",
            "Simmer for 20 minutes, season with salt and pepper",
            "Serve over spaghetti with Parmesan cheese"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Dice the onion and mince the garlic", "items": ["1 onion, diced", "2 cloves garlic, minced"]},
            {"order": 2, "phase": "prep", "text": "Measure out tomato paste and oregano", "items": ["2 tbsp tomato paste", "1 tsp dried oregano"]},
            {"order": 3, "phase": "cooking", "text": "Cook spaghetti according to package directions", "items": ["400g spaghetti"]},
            {"order": 4, "phase": "cooking", "text": "In a large pan, cook ground beef until browned", "items": ["500g ground beef"]},
            {"order": 5, "phase": "cooking", "text": "Add onion and garlic, cook until softened", "items": ["1 onion, diced", "2 cloves garlic, minced"]},
            {"order": 6, "phase": "cooking", "text": "Add crushed tomatoes, tomato paste, and oregano", "items": ["400g crushed tomatoes", "2 tbsp tomato paste", "1 tsp dried oregano"]},
            {"order": 7, "phase": "cooking", "text": "Simmer for 20 minutes, season with salt and pepper", "items": ["Salt and pepper to taste"], "time_minutes": 20},
            {"order": 8, "phase": "serve", "text": "Serve over spaghetti with Parmesan cheese", "items": ["Parmesan cheese for serving"]}
        ],
        "calories": 520,
        "protein": "28g",
        "carbs": "65g",
        "fat": "15g",
        "fiber": "5g",
        "featured": True,
        "category": "Dinner",
        "tags": ["pasta", "italian", "family-friendly", "budget-friendly"]
    },
    {
        "name": "Chicken Stir Fry",
        "image": "https://example.com/stirfry.jpg",
        "prep_time": "25 minutes",
        "servings": 3,
        "difficulty": "easy",
        "ingredients": [
            "500g chicken breast, sliced",
            "2 cups mixed vegetables (broccoli, peppers, carrots)",
            "3 tbsp soy sauce",
            "2 tbsp vegetable oil",
            "2 cloves garlic, minced",
            "1 tbsp fresh ginger, grated",
            "1 tbsp cornstarch",
            "Cooked rice for serving"
        ],
        "instructions": [
            "Slice chicken breast into thin strips",
            "Mince garlic and grate ginger",
            "Mix soy sauce with cornstarch in a small bowl",
            "Heat oil in a wok or large pan over high heat",
            "Add chicken and cook until golden",
            "Add garlic and ginger, stir for 30 seconds",
            "Add vegetables and stir fry for 3-4 minutes",
            "Pour soy sauce mixture into pan, stir until sauce thickens",
            "Serve over rice"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Slice chicken breast into thin strips", "items": ["500g chicken breast, sliced"]},
            {"order": 2, "phase": "prep", "text": "Mince garlic and grate ginger", "items": ["2 cloves garlic, minced", "1 tbsp fresh ginger, grated"]},
            {"order": 3, "phase": "prep", "text": "Mix soy sauce with cornstarch in a small bowl", "items": ["3 tbsp soy sauce", "1 tbsp cornstarch"]},
            {"order": 4, "phase": "cooking", "text": "Heat oil in a wok or large pan over high heat", "items": ["2 tbsp vegetable oil"]},
            {"order": 5, "phase": "cooking", "text": "Add chicken and cook until golden", "items": ["500g chicken breast, sliced"], "time_minutes": 5},
            {"order": 6, "phase": "cooking", "text": "Add garlic and ginger, stir for 30 seconds", "items": ["2 cloves garlic, minced", "1 tbsp fresh ginger, grated"]},
            {"order": 7, "phase": "cooking", "text": "Add vegetables and stir fry for 3-4 minutes", "items": ["2 cups mixed vegetables (broccoli, peppers, carrots)"], "time_minutes": 4},
            {"order": 8, "phase": "cooking", "text": "Pour soy sauce mixture into pan, stir until sauce thickens", "items": ["3 tbsp soy sauce", "1 tbsp cornstarch"]},
            {"order": 9, "phase": "serve", "text": "Serve over rice", "items": ["Cooked rice for serving"]}
        ],
        "calories": 380,
        "protein": "35g",
        "carbs": "28g",
        "fat": "12g",
        "fiber": "4g",
        "featured": True,
        "category": "Dinner",
        "tags": ["asian", "quick", "high-protein", "healthy"]
    },
    {
        "name": "Fluffy Pancakes",
        "image": "https://example.com/pancakes.jpg",
        "prep_time": "20 minutes",
        "servings": 6,
        "difficulty": "easy",
        "ingredients": [
            "2 cups all-purpose flour",
            "2 tbsp sugar",
            "2 tsp baking powder",
            "1/2 tsp salt",
            "2 eggs",
            "1 3/4 cups milk",
            "1/4 cup melted butter",
            "Maple syrup and berries for serving"
        ],
        "instructions": [
            "Mix flour, sugar, baking powder, and salt in a bowl",
            "In another bowl, whisk eggs, milk, and melted butter",
            "Pour wet ingredients into dry, mix until just combined",
            "Heat a griddle or pan over medium heat",
            "Pour 1/4 cup batter for each pancake",
            "Cook until bubbles form, flip and cook until golden",
            "Serve warm with maple syrup and berries"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Mix flour, sugar, baking powder, and salt in a bowl", "items": ["2 cups all-purpose flour", "2 tbsp sugar", "2 tsp baking powder", "1/2 tsp salt"]},
            {"order": 2, "phase": "prep", "text": "In another bowl, whisk eggs, milk, and melted butter", "items": ["2 eggs", "1 3/4 cups milk", "1/4 cup melted butter"]},
            {"order": 3, "phase": "prep", "text": "Pour wet ingredients into dry, mix until just combined", "items": []},
            {"order": 4, "phase": "cooking", "text": "Heat a griddle or pan over medium heat", "items": []},
            {"order": 5, "phase": "cooking", "text": "Pour 1/4 cup batter for each pancake", "items": []},
            {"order": 6, "phase": "cooking", "text": "Cook until bubbles form, flip and cook until golden", "items": [], "time_minutes": 3, "tip": "Don't flip until you see bubbles covering the surface"},
            {"order": 7, "phase": "serve", "text": "Serve warm with maple syrup and berries", "items": ["Maple syrup and berries for serving"]}
        ],
        "calories": 280,
        "protein": "8g",
        "carbs": "42g",
        "fat": "9g",
        "fiber": "2g",
        "featured": False,
        "category": "Breakfast",
        "tags": ["breakfast", "sweet", "family-friendly", "vegetarian"]
    },
    {
        "name": "Caesar Salad",
        "image": "https://example.com/caesar.jpg",
        "prep_time": "15 minutes",
        "servings": 4,
        "difficulty": "easy",
        "ingredients": [
            "1 large romaine lettuce, chopped",
            "1 cup croutons",
            "1/2 cup Parmesan cheese, shaved",
            "1/2 cup Caesar dressing",
            "Optional: grilled chicken breast"
        ],
        "instructions": [
            "Wash and chop romaine lettuce",
            "Place lettuce in a large bowl",
            "Add Caesar dressing and toss to coat",
            "Top with croutons and Parmesan cheese",
            "Add grilled chicken if desired",
            "Serve immediately"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Wash and chop romaine lettuce", "items": ["1 large romaine lettuce, chopped"]},
            {"order": 2, "phase": "prep", "text": "Place lettuce in a large bowl", "items": ["1 large romaine lettuce, chopped"]},
            {"order": 3, "phase": "prep", "text": "Add Caesar dressing and toss to coat", "items": ["1/2 cup Caesar dressing"]},
            {"order": 4, "phase": "serve", "text": "Top with croutons and Parmesan cheese", "items": ["1 cup croutons", "1/2 cup Parmesan cheese, shaved"]},
            {"order": 5, "phase": "serve", "text": "Add grilled chicken if desired", "items": ["Optional: grilled chicken breast"]},
            {"order": 6, "phase": "serve", "text": "Serve immediately", "items": []}
        ],
        "calories": 220,
        "protein": "8g",
        "carbs": "12g",
        "fat": "16g",
        "fiber": "3g",
        "featured": False,
        "category": "Lunch",
        "tags": ["salad", "quick", "vegetarian", "light"]
    },
    {
        "name": "Beef Tacos",
        "image": "https://example.com/tacos.jpg",
        "prep_time": "30 minutes",
        "servings": 5,
        "difficulty": "easy",
        "ingredients": [
            "500g ground beef",
            "1 tbsp taco seasoning",
            "8 taco shells",
            "1 cup shredded lettuce",
            "1 cup diced tomatoes",
            "1 cup shredded cheese",
            "1/2 cup sour cream",
            "1/2 cup salsa"
        ],
        "instructions": [
            "Shred lettuce and dice tomatoes",
            "Cook ground beef in a pan until browned",
            "Add taco seasoning and water, simmer 5 minutes",
            "Warm taco shells according to package",
            "Fill shells with beef",
            "Top with lettuce, tomatoes, cheese, sour cream, and salsa",
            "Serve immediately"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Shred lettuce and dice tomatoes", "items": ["1 cup shredded lettuce", "1 cup diced tomatoes"]},
            {"order": 2, "phase": "cooking", "text": "Cook ground beef in a pan until browned", "items": ["500g ground beef"], "time_minutes": 8},
            {"order": 3, "phase": "cooking", "text": "Add taco seasoning and water, simmer 5 minutes", "items": ["1 tbsp taco seasoning"], "time_minutes": 5},
            {"order": 4, "phase": "cooking", "text": "Warm taco shells according to package", "items": ["8 taco shells"]},
            {"order": 5, "phase": "serve", "text": "Fill shells with beef", "items": ["8 taco shells"]},
            {"order": 6, "phase": "serve", "text": "Top with lettuce, tomatoes, cheese, sour cream, and salsa", "items": ["1 cup shredded lettuce", "1 cup diced tomatoes", "1 cup shredded cheese", "1/2 cup sour cream", "1/2 cup salsa"]},
            {"order": 7, "phase": "serve", "text": "Serve immediately", "items": []}
        ],
        "calories": 420,
        "protein": "24g",
        "carbs": "32g",
        "fat": "22g",
        "fiber": "4g",
        "featured": True,
        "category": "Dinner",
        "tags": ["mexican", "quick", "family-friendly", "budget-friendly"]
    },
    {
        "name": "Vegetable Soup",
        "image": "https://example.com/soup.jpg",
        "prep_time": "40 minutes",
        "servings": 6,
        "difficulty": "easy",
        "ingredients": [
            "2 tbsp olive oil",
            "1 onion, diced",
            "2 carrots, diced",
            "2 celery stalks, diced",
            "2 potatoes, cubed",
            "1 can diced tomatoes",
            "6 cups vegetable broth",
            "1 cup frozen green beans",
            "Salt, pepper, herbs to taste"
        ],
        "instructions": [
            "Dice onion, carrots, celery, and cube potatoes",
            "Heat oil in a large pot over medium heat",
            "Add onion, carrots, and celery, cook 5 minutes",
            "Add potatoes, tomatoes, and broth",
            "Bring to a boil, then reduce heat and simmer 20 minutes",
            "Add green beans and cook 5 more minutes",
            "Season with salt, pepper, and herbs",
            "Serve hot with crusty bread"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Dice onion, carrots, celery, and cube potatoes", "items": ["1 onion, diced", "2 carrots, diced", "2 celery stalks, diced", "2 potatoes, cubed"]},
            {"order": 2, "phase": "cooking", "text": "Heat oil in a large pot over medium heat", "items": ["2 tbsp olive oil"]},
            {"order": 3, "phase": "cooking", "text": "Add onion, carrots, and celery, cook 5 minutes", "items": ["1 onion, diced", "2 carrots, diced", "2 celery stalks, diced"], "time_minutes": 5},
            {"order": 4, "phase": "cooking", "text": "Add potatoes, tomatoes, and broth", "items": ["2 potatoes, cubed", "1 can diced tomatoes", "6 cups vegetable broth"]},
            {"order": 5, "phase": "cooking", "text": "Bring to a boil, then reduce heat and simmer 20 minutes", "items": [], "time_minutes": 20},
            {"order": 6, "phase": "cooking", "text": "Add green beans and cook 5 more minutes", "items": ["1 cup frozen green beans"], "time_minutes": 5},
            {"order": 7, "phase": "cooking", "text": "Season with salt, pepper, and herbs", "items": ["Salt, pepper, herbs to taste"]},
            {"order": 8, "phase": "serve", "text": "Serve hot with crusty bread", "items": []}
        ],
        "calories": 180,
        "protein": "5g",
        "carbs": "32g",
        "fat": "5g",
        "fiber": "6g",
        "featured": False,
        "category": "Lunch",
        "tags": ["soup", "vegetarian", "healthy", "batch-cooking"]
    },
    {
        "name": "Chocolate Chip Cookies",
        "image": "https://example.com/cookies.jpg",
        "prep_time": "25 minutes",
        "servings": 24,
        "difficulty": "medium",
        "ingredients": [
            "2 1/4 cups all-purpose flour",
            "1 tsp baking soda",
            "1 tsp salt",
            "1 cup butter, softened",
            "3/4 cup sugar",
            "3/4 cup brown sugar",
            "2 eggs",
            "2 tsp vanilla extract",
            "2 cups chocolate chips"
        ],
        "instructions": [
            "Preheat oven to 375°F (190°C)",
            "Mix flour, baking soda, and salt in a bowl",
            "In another bowl, cream butter and both sugars",
            "Beat in eggs and vanilla",
            "Gradually mix in flour mixture",
            "Stir in chocolate chips",
            "Drop spoonfuls onto baking sheet",
            "Bake 9-11 minutes until golden",
            "Cool on baking sheet 2 minutes, then transfer to wire rack"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Preheat oven to 375°F (190°C)", "items": []},
            {"order": 2, "phase": "prep", "text": "Mix flour, baking soda, and salt in a bowl", "items": ["2 1/4 cups all-purpose flour", "1 tsp baking soda", "1 tsp salt"]},
            {"order": 3, "phase": "prep", "text": "In another bowl, cream butter and both sugars", "items": ["1 cup butter, softened", "3/4 cup sugar", "3/4 cup brown sugar"]},
            {"order": 4, "phase": "prep", "text": "Beat in eggs and vanilla", "items": ["2 eggs", "2 tsp vanilla extract"]},
            {"order": 5, "phase": "prep", "text": "Gradually mix in flour mixture", "items": []},
            {"order": 6, "phase": "prep", "text": "Stir in chocolate chips", "items": ["2 cups chocolate chips"]},
            {"order": 7, "phase": "cooking", "text": "Drop spoonfuls onto baking sheet", "items": []},
            {"order": 8, "phase": "cooking", "text": "Bake 9-11 minutes until golden", "items": [], "time_minutes": 10},
            {"order": 9, "phase": "serve", "text": "Cool on baking sheet 2 minutes, then transfer to wire rack", "items": [], "time_minutes": 2}
        ],
        "calories": 180,
        "protein": "2g",
        "carbs": "24g",
        "fat": "9g",
        "fiber": "1g",
        "featured": False,
        "category": "Snack",
        "tags": ["dessert", "sweet", "baking", "family-friendly"]
    },
    {
        "name": "Grilled Salmon",
        "image": "https://example.com/salmon.jpg",
        "prep_time": "20 minutes",
        "servings": 4,
        "difficulty": "medium",
        "ingredients": [
            "4 salmon fillets (6 oz each)",
            "2 tbsp olive oil",
            "2 cloves garlic, minced",
            "1 lemon, sliced",
            "Fresh dill",
            "Salt and pepper to taste",
            "Asparagus for serving"
        ],
        "instructions": [
            "Preheat grill to medium-high heat",
            "Brush salmon with olive oil and season with salt and pepper",
            "Sprinkle minced garlic over salmon",
            "Place lemon slices and dill on top",
            "Grill skin-side down for 6-8 minutes",
            "Flip and grill 4-6 minutes until cooked through",
            "Serve with grilled asparagus"
        ],
        "steps": [
            {"order": 1, "phase": "prep", "text": "Preheat grill to medium-high heat", "items": []},
            {"order": 2, "phase": "prep", "text": "Brush salmon with olive oil and season with salt and pepper", "items": ["4 salmon fillets (6 oz each)", "2 tbsp olive oil", "Salt and pepper to taste"]},
            {"order": 3, "phase": "prep", "text": "Sprinkle minced garlic over salmon", "items": ["2 cloves garlic, minced"]},
            {"order": 4, "phase": "prep", "text": "Place lemon slices and dill on top", "items": ["1 lemon, sliced", "Fresh dill"]},
            {"order": 5, "phase": "cooking", "text": "Grill skin-side down for 6-8 minutes", "items": [], "time_minutes": 7},
            {"order": 6, "phase": "cooking", "text": "Flip and grill 4-6 minutes until cooked through", "items": [], "time_minutes": 5},
            {"order": 7, "phase": "serve", "text": "Serve with grilled asparagus", "items": ["Asparagus for serving"]}
        ],
        "calories": 320,
        "protein": "38g",
        "carbs": "2g",
        "fat": "18g",
        "fiber": "0g",
        "featured": True,
        "category": "Dinner",
        "tags": ["seafood", "healthy", "high-protein", "low-carb"]
    }
]


def seed_recipes():
    """Insert sample recipes into the database"""
    
    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    
    try:
        with conn.cursor() as cur:
            # Check if recipes already exist
            cur.execute("SELECT COUNT(*) FROM recipes")
            count = cur.fetchone()[0]
            
            if count > 0:
                print(f"ℹ  Database already has {count} recipes.")
                response = input("Do you want to clear existing recipes and add sample data? (yes/no): ")
                if response.lower() == 'yes':
                    cur.execute("DELETE FROM recipes")
                    print("✓ Cleared existing recipes")
                else:
                    print("⏭  Skipping recipe seeding")
                    return
            
            # Insert sample recipes
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
            
            for recipe in SAMPLE_RECIPES:
                cur.execute(insert_query, (
                    recipe["name"],
                    recipe["image"],
                    recipe["prep_time"],
                    recipe["servings"],
                    recipe["difficulty"],
                    recipe["ingredients"],
                    recipe["instructions"],
                    json.dumps(recipe.get("steps", [])),
                    recipe["calories"],
                    recipe["protein"],
                    recipe["carbs"],
                    recipe["fat"],
                    recipe["fiber"],
                    recipe["featured"],
                    recipe["category"],
                    recipe["tags"]
                ))
                print(f"✓ Added recipe: {recipe['name']}")
            
            conn.commit()
            print(f"\n✅ Successfully seeded {len(SAMPLE_RECIPES)} recipes!")
            
    except Exception as e:
        print(f"✗ Error seeding recipes: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("="*60)
    print("GoMums - Recipe Database Seeding")
    print("="*60)
    seed_recipes()
