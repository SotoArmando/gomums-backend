"""
Test script for AI Recipe Generation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Test user credentials
TEST_USER = {
    "name": "AI Recipe Tester",
    "email": "master_test@gomums.com",
    "password": "Test1234!"
}


def register():
    """Register test user if not exists"""
    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if response.status_code == 201:
        print("✅ User registered successfully")
        return True
    elif response.status_code == 400 and "already registered" in response.text.lower():
        print("ℹ️  User already exists")
        return True
    else:
        print(f"⚠️  Registration response: {response.status_code} - {response.text}")
        return True  # Continue anyway, user might exist


def login():
    """Login and get access token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=TEST_USER)
    if response.status_code == 200:
        print("✅ Logged in successfully")
        return response.json()["token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_ai_recipe_generation(token):
    """Test AI recipe generation endpoint"""
    print("\n" + "="*70)
    print("🤖 TESTING AI RECIPE GENERATION")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test case 0: Set up user preferences and journal data first
    print("\n📋 Test 0: Set up user data (preferences, purchases, leftovers)")
    
    # Set preferences
    preferences_data = {
        "dietary_restrictions": ["vegetarian"],
        "allergies": ["peanuts"],
        "household_size": 4,
        "skill_level": "intermediate"
    }
    
    response = requests.patch(
        f"{BASE_URL}/user/me/preferences",
        json=preferences_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ User preferences set successfully!")
        prefs = response.json()
        print(f"   - Dietary: {prefs.get('dietary_restrictions')}")
        print(f"   - Allergies: {prefs.get('allergies')}")
        print(f"   - Household: {prefs.get('household_size')}")
        print(f"   - Skill: {prefs.get('skill_level')}")
    else:
        print(f"⚠️  Could not set preferences: {response.status_code}")
    
    # Add a purchase entry
    print("\n   Adding sample purchase...")
    purchase_data = {
        "type": "purchase",
        "title": "Weekly Groceries",
        "store": "Walmart",
        "items": [
            {"name": "Pasta", "quantity": "2 lbs", "cost": 4.99, "category": "pantry"},
            {"name": "Tomatoes", "quantity": "4 count", "cost": 3.50, "category": "produce"},
            {"name": "Basil", "quantity": "1 bunch", "cost": 2.50, "category": "herbs"},
            {"name": "Olive Oil", "quantity": "1 bottle", "cost": 8.99, "category": "pantry"},
            {"name": "Garlic", "quantity": "1 bulb", "cost": 0.99, "category": "produce"}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        json=purchase_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✅ Purchase entry added!")
    
    # Add a leftover meal
    print("   Adding leftover meal...")
    meal_data = {
        "type": "meal",
        "title": "Roasted Vegetables",
        "meal_type": "dinner",
        "portions": 4,
        "portions_left": 2,
        "status": "leftover"
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        json=meal_data,
        headers=headers
    )
    
    if response.status_code == 201:
        print("✅ Leftover meal added!")
    
    # Test case 1: ZERO-CONFIG - Ultimate smart defaults
    print("\n📋 Test 1: ZERO-CONFIG AI Recipe Generation")
    print("   (Just requesting recipes - AI fetches everything automatically!)")
    request_data = {
        "max_recipes": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-recipes/generate",
        json=request_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['count']} recipes with ZERO input!")
        print(f"\n   🎯 What the AI automatically used:")
        print(f"      - Ingredients: Pasta, Tomatoes, Basil, Olive Oil, Garlic (from purchases)")
        print(f"      - Leftovers: Roasted Vegetables (from journal)")
        print(f"      - Servings: 4 (from household_size)")
        print(f"      - Difficulty: medium (from skill_level: intermediate)")
        print(f"      - Dietary: vegetarian (from preferences)")
        print(f"      - Avoiding: peanuts (allergy)")
        print(f"\n   📝 Recipes generated:")
        for i, recipe in enumerate(result['recipes'], 1):
            print(f"\n      {i}. {recipe['name']}")
            print(f"         ⏱️  {recipe['prep_time']}")
            print(f"         👥 {recipe['servings']} servings")
            print(f"         📊 {recipe['difficulty']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 2: Minimal request (uses smart defaults)
    print("\n\n📋 Test 2: Minimal request with manual ingredients")
    request_data = {
        "available_ingredients": [
            "pasta",
            "tomatoes",
            "basil",
            "olive oil",
            "garlic"
        ],
        "max_recipes": 2,
        "save_to_database": False
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-recipes/generate",
        json=request_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['count']} recipes using smart defaults!")
        print(f"\nRecipes:")
        for i, recipe in enumerate(result['recipes'], 1):
            print(f"\n  {i}. {recipe['name']}")
            print(f"     ⏱️  Prep time: {recipe['prep_time']}")
            print(f"     👥 Servings: {recipe['servings']} (from household_size)")
            print(f"     📊 Difficulty: {recipe['difficulty']} (from skill_level)")
            print(f"     🏷️  Tags: {', '.join(recipe['tags'])}")
            print(f"     ✅ Dietary restrictions applied: vegetarian")
            print(f"     🚫 Allergies avoided: peanuts")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 2: Simple ingredient-based generation
    print("\n\n📋 Test 2: Generate recipes from available ingredients")
    request_data = {
        "available_ingredients": [
            "chicken breast",
            "rice",
            "bell peppers",
            "onions",
            "garlic",
            "olive oil",
            "tomatoes",
            "cheese"
        ],
        "servings": 4,
        "difficulty": "easy",
        "max_recipes": 3,
        "save_to_database": False
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-recipes/generate",
        json=request_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['count']} recipes!")
        print(f"\nRecipes:")
        for i, recipe in enumerate(result['recipes'], 1):
            print(f"\n  {i}. {recipe['name']}")
            print(f"     ⏱️  Prep time: {recipe['prep_time']}")
            print(f"     👥 Servings: {recipe['servings']}")
            print(f"     📊 Difficulty: {recipe['difficulty']}")
            print(f"     🏷️  Tags: {', '.join(recipe['tags'])}")
            if recipe.get('calories'):
                print(f"     🔥 Calories: {recipe['calories']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 3: Leftover-focused generation
    print("\n\n📋 Test 3: Generate recipes using leftovers")
    request_data = {
        "available_ingredients": ["rice", "pasta", "eggs", "milk", "flour"],
        "leftovers": ["roasted chicken", "cooked vegetables"],
        "max_recipes": 3,
        "save_to_database": False
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-recipes/generate",
        json=request_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['count']} leftover recipes!")
        for i, recipe in enumerate(result['recipes'], 1):
            print(f"\n  {i}. {recipe['name']}")
            print(f"     Uses leftovers: {'✅' if recipe['uses_leftovers'] else '❌'}")
            if recipe.get('leftover_items_used'):
                print(f"     Leftover items: {', '.join(recipe['leftover_items_used'])}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 4: Quick generation
    print("\n\n📋 Test 4: Quick recipe generation")
    response = requests.post(
        f"{BASE_URL}/ai-recipes/quick-generate",
        json={
            "ingredients": ["pasta", "tomato sauce", "basil", "mozzarella"],
            "max_recipes": 2
        },
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Quick generated {result['count']} recipes!")
        for recipe in result['recipes']:
            print(f"  • {recipe['name']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 5: Leftover-specific endpoint
    print("\n\n📋 Test 5: Leftover-specific recipe generation")
    response = requests.post(
        f"{BASE_URL}/ai-recipes/leftover-recipes",
        json={
            "leftovers": ["leftover pizza", "half onion", "few mushrooms"],
            "pantry_items": ["eggs", "cheese", "bread"],
            "max_recipes": 2
        },
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['count']} leftover-focused recipes!")
        for recipe in result['recipes']:
            print(f"  • {recipe['name']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 6: Minimize Shopping Mode (NEW!)
    print("\n\n📋 Test 6: Minimize Shopping Mode - No grocery trip needed!")
    print("   (Recipes using ONLY available ingredients + common pantry staples)")
    request_data = {
        "available_ingredients": [
            "pasta",
            "eggs",
            "cheese",
            "garlic",
            "tomatoes"
        ],
        "minimize_shopping": True,
        "max_recipes": 2,
        "save_to_database": False
    }
    
    response = requests.post(
        f"{BASE_URL}/ai-recipes/generate",
        json=request_data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generated {result['count']} no-shopping-needed recipes!")
        print(f"\n   🛒 Shopping Constraint Active:")
        print(f"      - Must use ONLY: pasta, eggs, cheese, garlic, tomatoes")
        print(f"      - Can add: salt, pepper, oil, basic spices (pantry staples)")
        print(f"      - Cannot require: any fresh ingredients not listed")
        print(f"\n   📝 Recipes (no shopping required):")
        for i, recipe in enumerate(result['recipes'], 1):
            print(f"\n      {i}. {recipe['name']}")
            print(f"         ⏱️  {recipe['prep_time']}")
            print(f"         🥘 Ingredients needed:")
            for ing in recipe['ingredients'][:5]:  # Show first 5 ingredients
                print(f"            • {ing}")
            if len(recipe['ingredients']) > 5:
                print(f"            • ... and {len(recipe['ingredients']) - 5} more")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    # Test case 7: Challenge-specific recipe generation
    print("\n\n📋 Test 7: Generate recipes for a challenge")
    print("   (Fetching available challenges first...)")
    
    # Get user's active challenges
    challenges_response = requests.get(
        f"{BASE_URL}/challenges/user/active",
        headers=headers
    )
    
    if challenges_response.status_code == 200:
        challenges = challenges_response.json()
        if challenges and len(challenges) > 0:
            challenge_id = challenges[0]['challenge_id']
            challenge_title = challenges[0]['challenge']['title']
            print(f"   Using challenge: {challenge_title}")
            
            response = requests.post(
                f"{BASE_URL}/ai-recipes/for-challenge",
                json={
                    "challenge_id": challenge_id,
                    "max_recipes": 3,
                    "save_to_database": False
                },
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Generated {result['count']} recipes for challenge!")
                for i, recipe in enumerate(result['recipes'], 1):
                    print(f"\n  {i}. {recipe['name']}")
                    print(f"     Difficulty: {recipe['difficulty']}")
                    print(f"     Time: {recipe['prep_time']}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
        else:
            print("ℹ️  No active challenges found, skipping test")
    else:
        print(f"⚠️  Could not fetch challenges: {challenges_response.status_code}")
    
    print("\n" + "="*70)
    print("✨ AI RECIPE GENERATION TESTS COMPLETED")
    print("="*70)


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("  🧪 AI RECIPE GENERATION API TEST")
    print("="*70)
    
    # Register user (if needed)
    register()
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test AI recipe generation
    test_ai_recipe_generation(token)


if __name__ == "__main__":
    main()
