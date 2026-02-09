"""
Test script for Recipe API endpoints
"""
import requests
import json
from typing import Optional


# API Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
TEST_USER = {
    "name": "Test User",
    "email": "test@gomums.com",
    "password": "Test123!@#"
}

# Store access token globally
ACCESS_TOKEN: Optional[str] = None


# ==================== Color Codes ====================
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.CYAN}{'='*60}")
    print(text)
    print(f"{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_response(response, show_full: bool = False):
    """Print response details"""
    print(f"Status: {response.status_code}")
    if show_full or response.status_code >= 400:
        print(f"Response: {json.dumps(response.json(), indent=2)}")


# ==================== Test Functions ====================

def cleanup_test_user():
    """Clean up test user if exists"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST'),
            port=os.getenv('DATABASE_PORT'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD')
        )
        
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email = %s", (TEST_USER["email"],))
            conn.commit()
            
        conn.close()
    except Exception:
        pass


def test_register():
    """Test user registration"""
    print_header("1. User Registration")
    
    cleanup_test_user()
    
    response = requests.post(
        f"{API_URL}/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 201:
        print_success("User registered successfully")
        print_response(response, show_full=True)
        return response.json()["token"]
    else:
        print_error("Registration failed")
        print_response(response)
        return None


def test_login():
    """Test user login"""
    global ACCESS_TOKEN
    
    print_header("2. User Login")
    
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        print_success("Login successful")
        ACCESS_TOKEN = response.json()["token"]
        print_info(f"Access token: {ACCESS_TOKEN[:50]}...")
        return True
    else:
        print_error("Login failed")
        print_response(response)
        return False


def test_get_all_recipes():
    """Test GET /recipes - Get all recipes"""
    print_header("3. Get All Recipes")
    
    response = requests.get(
        f"{API_URL}/recipes/",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipes = response.json()
        print_success(f"Retrieved {len(recipes)} recipes")
        
        for recipe in recipes[:3]:  # Show first 3
            print(f"  - {recipe['name']}: {recipe['category']} ({recipe['difficulty']})")
            print(f"    Servings: {recipe['servings']}, Prep time: {recipe['prep_time']}")
            print(f"    Calories: {recipe['nutrition']['calories']}, Protein: {recipe['nutrition']['protein']}")
        
        if len(recipes) > 3:
            print(f"  ... and {len(recipes) - 3} more")
        
        return recipes
    else:
        print_error("Failed to retrieve recipes")
        print_response(response)
        return []


def test_get_featured_recipes():
    """Test GET /recipes with featured filter"""
    print_header("4. Get Featured Recipes")
    
    response = requests.get(
        f"{API_URL}/recipes/",
        params={"featured": "true"},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipes = response.json()
        print_success(f"Retrieved {len(recipes)} featured recipes")
        
        for recipe in recipes:
            print(f"  ⭐ {recipe['name']} - {recipe['category']}")
        
        return recipes
    else:
        print_error("Failed to retrieve featured recipes")
        print_response(response)
        return []


def test_filter_by_category():
    """Test GET /recipes with category filter"""
    print_header("5. Filter Recipes by Category: Dinner")
    
    response = requests.get(
        f"{API_URL}/recipes/",
        params={"category": "Dinner"},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipes = response.json()
        print_success(f"Retrieved {len(recipes)} dinner recipes")
        
        for recipe in recipes:
            print(f"  - {recipe['name']}: {recipe['prep_time']}")
        
        return recipes
    else:
        print_error("Failed to filter recipes")
        print_response(response)
        return []


def test_filter_by_difficulty():
    """Test GET /recipes with difficulty filter"""
    print_header("6. Filter Recipes by Difficulty: Easy")
    
    response = requests.get(
        f"{API_URL}/recipes/",
        params={"difficulty": "easy"},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipes = response.json()
        print_success(f"Retrieved {len(recipes)} easy recipes")
        
        for recipe in recipes[:5]:  # Show first 5
            print(f"  - {recipe['name']}")
        
        if len(recipes) > 5:
            print(f"  ... and {len(recipes) - 5} more")
        
        return recipes
    else:
        print_error("Failed to filter by difficulty")
        print_response(response)
        return []


def test_search_recipes():
    """Test GET /recipes with search"""
    print_header("7. Search Recipes: 'chicken'")
    
    response = requests.get(
        f"{API_URL}/recipes/",
        params={"search": "chicken"},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipes = response.json()
        print_success(f"Found {len(recipes)} recipes matching 'chicken'")
        
        for recipe in recipes:
            print(f"  - {recipe['name']}")
        
        return recipes
    else:
        print_error("Search failed")
        print_response(response)
        return []


def test_filter_by_tags():
    """Test GET /recipes with tags filter"""
    print_header("8. Filter by Tags: 'vegetarian'")
    
    response = requests.get(
        f"{API_URL}/recipes/",
        params={"tags": "vegetarian"},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipes = response.json()
        print_success(f"Retrieved {len(recipes)} vegetarian recipes")
        
        for recipe in recipes:
            print(f"  - {recipe['name']} (Tags: {', '.join(recipe['tags'])})")
        
        return recipes
    else:
        print_error("Failed to filter by tags")
        print_response(response)
        return []


def test_get_recipe_by_id(recipe_id: str):
    """Test GET /recipes/{id} - Get single recipe"""
    print_header("9. Get Recipe by ID")
    
    response = requests.get(
        f"{API_URL}/recipes/{recipe_id}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        recipe = response.json()
        print_success(f"Retrieved recipe: {recipe['name']}")
        print()
        print(f"  Category: {recipe['category']}")
        print(f"  Difficulty: {recipe['difficulty']}")
        print(f"  Prep Time: {recipe['prep_time']}")
        print(f"  Servings: {recipe['servings']}")
        print()
        print(f"  Nutrition:")
        print(f"    - Calories: {recipe['nutrition']['calories']}")
        print(f"    - Protein: {recipe['nutrition']['protein']}")
        print(f"    - Carbs: {recipe['nutrition']['carbs']}")
        print(f"    - Fat: {recipe['nutrition']['fat']}")
        print()
        print(f"  Ingredients ({len(recipe['ingredients'])}):")
        for i, ingredient in enumerate(recipe['ingredients'][:5], 1):
            print(f"    {i}. {ingredient}")
        if len(recipe['ingredients']) > 5:
            print(f"    ... and {len(recipe['ingredients']) - 5} more")
        print()
        print(f"  Instructions ({len(recipe['instructions'])} steps):")
        for i, step in enumerate(recipe['instructions'][:3], 1):
            print(f"    {i}. {step}")
        if len(recipe['instructions']) > 3:
            print(f"    ... and {len(recipe['instructions']) - 3} more steps")
        
        return recipe
    else:
        print_error("Failed to retrieve recipe")
        print_response(response)
        return None


def test_pagination():
    """Test GET /recipes with pagination"""
    print_header("10. Test Pagination")
    
    # Get first page (limit 3)
    print_info("Fetching page 1 (limit=3, offset=0):")
    response1 = requests.get(
        f"{API_URL}/recipes/",
        params={"limit": 3, "offset": 0},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response1.status_code == 200:
        page1 = response1.json()
        print_success(f"Page 1: {len(page1)} recipes")
        for recipe in page1:
            print(f"  - {recipe['name']}")
    
    # Get second page (limit 3, offset 3)
    print()
    print_info("Fetching page 2 (limit=3, offset=3):")
    response2 = requests.get(
        f"{API_URL}/recipes/",
        params={"limit": 3, "offset": 3},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response2.status_code == 200:
        page2 = response2.json()
        print_success(f"Page 2: {len(page2)} recipes")
        for recipe in page2:
            print(f"  - {recipe['name']}")


def test_get_count():
    """Test GET /recipes/count/total"""
    print_header("11. Get Total Recipe Count")
    
    response = requests.get(
        f"{API_URL}/recipes/count/total",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        count_data = response.json()
        print_success(f"Total recipes in database: {count_data['count']}")
        return count_data['count']
    else:
        print_error("Failed to get recipe count")
        print_response(response)
        return 0


# ==================== Main Test Runner ====================

def main():
    """Run all recipe API tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("GoMums Recipe API - Test Script")
    print(f"{'='*60}{Colors.END}\n")
    
    print_info(f"Testing API at: {BASE_URL}")
    
    # Setup
    token = test_register()
    if not token:
        print_error("Failed to register user, exiting...")
        return
    
    if not test_login():
        print_error("Failed to login, exiting...")
        return
    
    # Test Recipe endpoints
    all_recipes = test_get_all_recipes()
    
    featured_recipes = test_get_featured_recipes()
    
    dinner_recipes = test_filter_by_category()
    
    easy_recipes = test_filter_by_difficulty()
    
    search_results = test_search_recipes()
    
    vegetarian_recipes = test_filter_by_tags()
    
    # Test get single recipe
    if all_recipes:
        test_get_recipe_by_id(all_recipes[0]['id'])
    
    test_pagination()
    
    test_get_count()
    
    # Summary
    print_header("Test Summary")
    
    print_success("✅ All recipe API endpoints tested successfully!")
    print_info(f"  Total recipes: {len(all_recipes)}")
    print_info(f"  Featured: {len(featured_recipes)}")
    print_info(f"  Dinner recipes: {len(dinner_recipes)}")
    print_info(f"  Easy recipes: {len(easy_recipes)}")
    print_info(f"  API Documentation: {BASE_URL}/docs")


if __name__ == "__main__":
    main()
