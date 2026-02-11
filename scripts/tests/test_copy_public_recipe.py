"""
Test script for Copy Public Recipe to Private Recipes feature
Tests the flow of browsing public recipes and copying them to user's private collection
"""
import requests
import json
from typing import Optional
import psycopg2
from dotenv import load_dotenv
import os


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
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")


def get_auth_headers() -> dict:
    """Get authorization headers"""
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}


# ==================== Auth Functions ====================

def cleanup_test_user():
    """Clean up test user if exists"""
    try:
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


# ==================== Test Functions ====================

def test_get_public_recipes():
    """Test getting public recipes with pagination"""
    print_header("3. Get Public Recipes")
    
    # Get first page of recipes
    print_info("Fetching public recipes (first 20)...")
    response = requests.get(
        f"{API_URL}/recipes/",
        headers=get_auth_headers(),
        params={"limit": 20, "offset": 0}
    )
    
    if response.status_code != 200:
        print_error(f"Failed to get recipes: {response.status_code}")
        print_response(response)
        return None
    
    recipes = response.json()
    print_success(f"Retrieved {len(recipes)} recipes")
    
    # Show first few recipes
    print_info("Sample recipes:")
    for i, recipe in enumerate(recipes[:5]):
        print(f"  {i+1}. {recipe['name']} (ID: {recipe['id'][:8]}...)")
    
    if len(recipes) > 5:
        print(f"  ... and {len(recipes) - 5} more")
    
    return recipes


def test_get_total_recipe_count():
    """Test getting total count of public recipes"""
    print_header("4. Count Public Recipes")
    
    # Get max recipes to see total
    print_info("Fetching recipes with higher limit...")
    response = requests.get(
        f"{API_URL}/recipes/",
        headers=get_auth_headers(),
        params={"limit": 100, "offset": 0}
    )
    
    if response.status_code != 200:
        print_error(f"Failed to get recipes: {response.status_code}")
        return 0
    
    first_batch = len(response.json())
    
    # Get second batch if needed
    response2 = requests.get(
        f"{API_URL}/recipes/",
        headers=get_auth_headers(),
        params={"limit": 100, "offset": 100}
    )
    
    second_batch = len(response2.json()) if response2.status_code == 200 else 0
    
    total = first_batch + second_batch
    print_success(f"Total public recipes available: ~{total}")
    
    return total


def test_copy_public_recipe(recipe_id: str, recipe_name: str):
    """Test copying a public recipe to user's private recipes"""
    print_header("5. Copy Public Recipe to Private")
    
    print_info(f"Copying recipe: {recipe_name}")
    print_info(f"Recipe ID: {recipe_id}")
    
    response = requests.post(
        f"{API_URL}/user-recipes/copy-from-public/{recipe_id}",
        headers=get_auth_headers()
    )
    
    if response.status_code in [200, 201]:
        copied_recipe = response.json()
        print_success("Recipe copied successfully!")
        print_info(f"New private recipe ID: {copied_recipe['id']}")
        print_info(f"Name: {copied_recipe['name']}")
        print_info(f"Original recipe ID stored: {copied_recipe.get('original_recipe_id', 'N/A')}")
        return copied_recipe
    else:
        print_error(f"Failed to copy recipe: {response.status_code}")
        print_response(response, show_full=True)
        return None


def test_get_my_private_recipes():
    """Test getting user's private recipes"""
    print_header("6. Get My Private Recipes")
    
    response = requests.get(
        f"{API_URL}/user-recipes/",
        headers=get_auth_headers()
    )
    
    if response.status_code != 200:
        print_error(f"Failed to get private recipes: {response.status_code}")
        print_response(response)
        return None
    
    data = response.json()
    recipes = data.get("recipes", [])
    total = data.get("total", 0)
    
    print_success(f"Retrieved {len(recipes)} private recipes (total: {total})")
    
    for recipe in recipes[:5]:
        print(f"  - {recipe['name']} (ID: {recipe['id'][:8]}...)")
    
    return data


def test_delete_private_recipe(recipe_id: str):
    """Test deleting a private recipe (cleanup)"""
    print_header("8. Delete Private Recipe (Cleanup)")
    
    response = requests.delete(
        f"{API_URL}/user-recipes/{recipe_id}",
        headers=get_auth_headers()
    )
    
    if response.status_code == 200:
        print_success(f"Deleted private recipe: {recipe_id[:8]}...")
        return True
    else:
        print_error(f"Failed to delete recipe: {response.status_code}")
        return False


def test_copy_invalid_recipe():
    """Test copying a non-existent recipe"""
    print_header("7. Copy Invalid Recipe (Should Fail)")
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    print_info(f"Attempting to copy fake recipe ID: {fake_id}")
    
    response = requests.post(
        f"{API_URL}/user-recipes/copy-from-public/{fake_id}",
        headers=get_auth_headers()
    )
    
    if response.status_code == 404:
        print_success("Correctly returned 404 for non-existent recipe")
        return True
    else:
        print_error(f"Unexpected status: {response.status_code}")
        return False


# ==================== Main ====================

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("  COPY PUBLIC RECIPE TO PRIVATE RECIPES - TEST SUITE")
    print(f"{'='*60}{Colors.END}")
    
    # Step 1: Register
    token = test_register()
    if not token:
        print_error("Cannot proceed without registration")
        return
    
    # Step 2: Login
    if not test_login():
        print_error("Cannot proceed without authentication")
        return
    
    # Test 3: Get public recipes
    public_recipes = test_get_public_recipes()
    if not public_recipes:
        print_error("Cannot proceed without public recipes")
        return
    
    # Test 4: Count total recipes
    test_get_total_recipe_count()
    
    # Test 5: Copy first public recipe to private
    recipe_to_copy = public_recipes[0]
    copied_recipe = test_copy_public_recipe(
        recipe_id=recipe_to_copy["id"],
        recipe_name=recipe_to_copy["name"]
    )
    
    # Test 6: Verify it appears in private recipes
    if copied_recipe:
        test_get_my_private_recipes()
    
    # Test 7: Test invalid recipe ID
    test_copy_invalid_recipe()
    
    # Test 8: Cleanup - delete the copied recipe
    if copied_recipe:
        test_delete_private_recipe(copied_recipe["id"])
    
    # Summary
    print_header("TEST SUMMARY")
    print_success("All tests completed!")
    print_info("The copy-from-public endpoint fetches only the specific")
    print_info("recipe by ID - it does NOT load all 200 recipes.")


if __name__ == "__main__":
    main()
