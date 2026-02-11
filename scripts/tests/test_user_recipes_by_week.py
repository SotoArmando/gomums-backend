"""
Test script for User Recipes By Week endpoint
Tests the flow of fetching user private recipes grouped by week (Monday-Sunday)
"""
import requests
import json
from typing import Optional
from datetime import date, timedelta
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


def get_current_week_monday() -> date:
    """Get Monday of the current week"""
    today = date.today()
    return today - timedelta(days=today.weekday())


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

def test_get_by_week_empty():
    """Test getting user recipes by week when no recipes exist"""
    print_header("3. Get User Recipes By Week (Empty)")
    
    week_start = get_current_week_monday()
    print_info(f"Fetching recipes for week starting: {week_start}")
    
    response = requests.get(
        f"{API_URL}/user-recipes/by-week",
        headers=get_auth_headers(),
        params={"week_start": str(week_start)}
    )
    
    if response.status_code != 200:
        print_error(f"Failed to get recipes by week: {response.status_code}")
        print_response(response)
        return False
    
    data = response.json()
    print_success("Successfully fetched week data")
    print_info(f"Week start: {data.get('week_start')}")
    print_info(f"Week end: {data.get('week_end')}")
    print_info(f"Days in response: {len(data.get('recipes_by_day', {}))}")
    
    # Verify structure
    if 'recipes_by_day' not in data:
        print_error("Missing 'recipes_by_day' field in response")
        return False
    
    if len(data['recipes_by_day']) != 7:
        print_error(f"Expected 7 days, got {len(data['recipes_by_day'])}")
        return False
    
    print_success("Response structure is valid (7 days)")
    return True


def test_copy_public_recipe():
    """Copy a public recipe to user's private collection"""
    print_header("4. Copy Public Recipe to Private Collection")
    
    # Get a public recipe first
    print_info("Fetching public recipes...")
    response = requests.get(
        f"{API_URL}/recipes/",
        headers=get_auth_headers(),
        params={"limit": 1}
    )
    
    if response.status_code != 200 or not response.json():
        print_error("Failed to get public recipes")
        print_response(response)
        return None
    
    public_recipe = response.json()[0]
    recipe_id = public_recipe['id']
    recipe_name = public_recipe['name']
    print_info(f"Selected recipe: {recipe_name}")
    
    # Copy to private collection
    print_info("Copying to private collection...")
    response = requests.post(
        f"{API_URL}/user-recipes/copy-from-public/{recipe_id}",
        headers=get_auth_headers()
    )
    
    if response.status_code not in [200, 201]:
        print_error(f"Failed to copy recipe: {response.status_code}")
        print_response(response)
        return None
    
    copied_recipe = response.json()
    print_success(f"Recipe copied successfully!")
    print_info(f"Private recipe ID: {copied_recipe['id']}")
    print_info(f"Name: {copied_recipe['name']}")
    
    return copied_recipe['id']


def test_get_by_week_with_recipes():
    """Test getting user recipes by week after adding a recipe"""
    print_header("5. Get User Recipes By Week (With Recipes)")
    
    week_start = get_current_week_monday()
    print_info(f"Fetching recipes for week starting: {week_start}")
    
    response = requests.get(
        f"{API_URL}/user-recipes/by-week",
        headers=get_auth_headers(),
        params={"week_start": str(week_start)}
    )
    
    if response.status_code != 200:
        print_error(f"Failed to get recipes by week: {response.status_code}")
        print_response(response)
        return False
    
    data = response.json()
    print_success("Successfully fetched week data")
    
    # Count total recipes across all days
    total_recipes = 0
    recipes_by_day = data.get('recipes_by_day', {})
    for day_name, recipes in recipes_by_day.items():
        day_recipes = len(recipes)
        total_recipes += day_recipes
        if day_recipes > 0:
            print_info(f"  {day_name}: {day_recipes} recipe(s)")
    
    print_success(f"Total recipes in week: {total_recipes}")
    
    if total_recipes < 1:
        print_error("Expected at least 1 recipe after copy")
        return False
    
    return True


def test_get_by_week_auto_monday():
    """Test that non-Monday dates auto-adjust to Monday"""
    print_header("6. Test Auto-Adjust to Monday")
    
    # Use a Wednesday
    today = date.today()
    wednesday = today - timedelta(days=today.weekday()) + timedelta(days=2)  # Get this week's Wednesday
    expected_monday = wednesday - timedelta(days=2)
    
    print_info(f"Requesting with date (Wednesday): {wednesday}")
    print_info(f"Expected Monday: {expected_monday}")
    
    response = requests.get(
        f"{API_URL}/user-recipes/by-week",
        headers=get_auth_headers(),
        params={"week_start": str(wednesday)}
    )
    
    if response.status_code != 200:
        print_error(f"Failed: {response.status_code}")
        print_response(response)
        return False
    
    data = response.json()
    returned_week_start = data.get('week_start')
    
    if returned_week_start == str(expected_monday):
        print_success(f"Auto-adjusted to Monday: {returned_week_start}")
        return True
    else:
        print_error(f"Expected {expected_monday}, got {returned_week_start}")
        return False


def test_get_by_week_different_week():
    """Test getting recipes for a different (older) week"""
    print_header("7. Get Recipes for Previous Week")
    
    last_week_monday = get_current_week_monday() - timedelta(days=7)
    print_info(f"Fetching recipes for week starting: {last_week_monday}")
    
    response = requests.get(
        f"{API_URL}/user-recipes/by-week",
        headers=get_auth_headers(),
        params={"week_start": str(last_week_monday)}
    )
    
    if response.status_code != 200:
        print_error(f"Failed: {response.status_code}")
        print_response(response)
        return False
    
    data = response.json()
    print_success("Successfully fetched last week's data")
    print_info(f"Week: {data.get('week_start')} to {data.get('week_end')}")
    
    # Count recipes (should be 0 for last week since we only added this week)
    recipes_by_day = data.get('recipes_by_day', {})
    total_recipes = sum(len(recipes) for recipes in recipes_by_day.values())
    print_info(f"Recipes in last week: {total_recipes}")
    
    return True


def test_get_by_week_no_auth():
    """Test that endpoint requires authentication"""
    print_header("8. Test Authentication Required")
    
    week_start = get_current_week_monday()
    
    # Call without auth header
    response = requests.get(
        f"{API_URL}/user-recipes/by-week",
        params={"week_start": str(week_start)}
    )
    
    if response.status_code == 401:
        print_success("Correctly rejected unauthenticated request (401)")
        return True
    elif response.status_code == 403:
        print_success("Correctly rejected unauthenticated request (403)")
        return True
    else:
        print_error(f"Expected 401/403, got {response.status_code}")
        print_response(response)
        return False


def cleanup():
    """Clean up test data"""
    print_header("9. Cleanup")
    cleanup_test_user()
    print_success("Cleaned up test user and related data")


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("  USER RECIPES BY-WEEK ENDPOINT TESTS")
    print(f"{'='*60}{Colors.END}")
    
    results = {}
    
    # 1. Register
    token = test_register()
    results['register'] = token is not None
    
    if not token:
        print_error("Cannot continue without registration")
        return
    
    # 2. Login
    results['login'] = test_login()
    
    if not results['login']:
        print_error("Cannot continue without login")
        cleanup()
        return
    
    # 3. Get by week (empty)
    results['by_week_empty'] = test_get_by_week_empty()
    
    # 4. Copy a public recipe
    recipe_id = test_copy_public_recipe()
    results['copy_recipe'] = recipe_id is not None
    
    # 5. Get by week (with recipes)
    results['by_week_with_recipes'] = test_get_by_week_with_recipes()
    
    # 6. Test auto-Monday adjustment
    results['auto_monday'] = test_get_by_week_auto_monday()
    
    # 7. Get different week
    results['different_week'] = test_get_by_week_different_week()
    
    # 8. Test auth required
    results['auth_required'] = test_get_by_week_no_auth()
    
    # 9. Cleanup
    cleanup()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed_test else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}All tests passed!{Colors.END}")
    else:
        print(f"{Colors.RED}Some tests failed{Colors.END}")


if __name__ == "__main__":
    run_all_tests()
