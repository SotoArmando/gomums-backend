"""
Test script for Meal-Purchase Linking Flow
Tests: Log a purchase → Log a meal with shared ingredients → Link them together

This simulates the real user flow:
1. User goes grocery shopping and logs the purchase
2. User cooks a meal using those ingredients
3. System links them to track ingredient usage
"""
import requests
import json
from typing import Optional
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import os


# API Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
TEST_USER = {
    "name": "Meal Link Test User",
    "email": "meallink_test@gomums.com",
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

def test_create_purchase():
    """Create a purchase log with grocery items"""
    print_header("3. Log a Grocery Purchase")
    
    purchase_data = {
        "type": "purchase",
        "title": "Weekly Grocery Shopping",
        "store": "Walmart",
        "items": [
            {"name": "Chicken breast", "quantity": "2 lb", "cost": 8.99, "category": "proteins"},
            {"name": "Broccoli", "quantity": "2 heads", "cost": 2.50, "category": "vegetables"},
            {"name": "Soy sauce", "quantity": "1 bottle", "cost": 3.99, "category": "pantry"},
            {"name": "Rice", "quantity": "5 lb bag", "cost": 4.99, "category": "grains"},
            {"name": "Garlic", "quantity": "1 head", "cost": 0.50, "category": "vegetables"}
        ]
    }
    
    print_info("Creating purchase entry...")
    print_info(f"Store: {purchase_data['store']}")
    print_info(f"Items: {len(purchase_data['items'])}")
    
    response = requests.post(
        f"{API_URL}/journal/entries",
        headers=get_auth_headers(),
        json=purchase_data
    )
    
    if response.status_code == 201:
        purchase = response.json()
        print_success(f"Purchase created!")
        print_info(f"Purchase ID: {purchase['id']}")
        print_info(f"Total items: {len(purchase.get('items', []))}")
        return purchase['id']
    else:
        print_error(f"Failed to create purchase: {response.status_code}")
        print_response(response)
        return None


def test_create_meal_with_shared_ingredients(purchase_id: str):
    """Create a meal log using ingredients from the purchase"""
    print_header("4. Log a Meal (Using Purchased Ingredients)")
    
    # These ingredients match items from the purchase
    meal_data = {
        "type": "meal",
        "title": "Chicken Stir Fry",
        "meal_type": "dinner",
        "portions": 4,
        "status": "fresh",
        "ingredients_used": ["Chicken breast", "Broccoli", "Soy sauce", "Garlic"],
        "is_batch": False,
        "used_leftovers": False,
        "has_leftovers": True
    }
    
    print_info(f"Meal: {meal_data['title']}")
    print_info(f"Meal type: {meal_data['meal_type']}")
    print_info(f"Ingredients used: {meal_data['ingredients_used']}")
    
    response = requests.post(
        f"{API_URL}/journal/entries",
        headers=get_auth_headers(),
        json=meal_data
    )
    
    if response.status_code == 201:
        meal = response.json()
        print_success(f"Meal logged!")
        print_info(f"Meal ID: {meal['id']}")
        print_info(f"Portions: {meal.get('portions', 'N/A')}")
        print_info(f"Has leftovers: {meal.get('has_leftovers', False)}")
        return meal['id']
    else:
        print_error(f"Failed to create meal: {response.status_code}")
        print_response(response)
        return None


def test_link_meal_to_purchase(meal_id: str, purchase_id: str):
    """Link the meal to the purchase with matched ingredients"""
    print_header("5. Link Meal to Purchase")
    
    # These are the ingredients that match between meal and purchase
    matched_ingredients = ["Chicken breast", "Broccoli", "Soy sauce", "Garlic"]
    
    link_data = {
        "purchase_id": purchase_id,
        "ingredients_used": matched_ingredients
    }
    
    print_info(f"Linking meal {meal_id[:8]}... to purchase {purchase_id[:8]}...")
    print_info(f"Matched ingredients: {matched_ingredients}")
    
    response = requests.post(
        f"{API_URL}/journal/meals/{meal_id}/link-purchase",
        headers=get_auth_headers(),
        json=link_data
    )
    
    if response.status_code == 200:
        meal = response.json()
        print_success("Meal linked to purchase!")
        print_info(f"Meal now has purchase_id: {meal.get('purchase_id', 'None')}")
        return True
    else:
        print_error(f"Failed to link: {response.status_code}")
        print_response(response)
        return False


def test_verify_linkage(meal_id: str, purchase_id: str):
    """Verify the meal is properly linked to the purchase"""
    print_header("6. Verify Meal-Purchase Linkage")
    
    # Get the meal and check its purchase_id
    response = requests.get(
        f"{API_URL}/journal/entries/{meal_id}",
        headers=get_auth_headers()
    )
    
    if response.status_code != 200:
        print_error(f"Failed to fetch meal: {response.status_code}")
        return False
    
    meal = response.json()
    linked_purchase_id = meal.get('purchase_id')
    
    print_info(f"Meal ID: {meal['id']}")
    print_info(f"Meal Title: {meal['title']}")
    print_info(f"Linked Purchase ID: {linked_purchase_id}")
    
    if linked_purchase_id == purchase_id:
        print_success("✓ Meal is correctly linked to purchase!")
        return True
    else:
        print_error(f"Linkage mismatch! Expected {purchase_id}, got {linked_purchase_id}")
        return False


def test_get_all_entries():
    """Get all journal entries to see the full picture"""
    print_header("7. View All Journal Entries")
    
    response = requests.get(
        f"{API_URL}/journal/entries",
        headers=get_auth_headers()
    )
    
    if response.status_code != 200:
        print_error(f"Failed to fetch entries: {response.status_code}")
        return False
    
    entries = response.json()
    print_success(f"Total entries: {len(entries)}")
    
    for entry in entries:
        entry_type = entry.get('type', 'unknown')
        title = entry.get('title', 'Untitled')
        
        if entry_type == 'meal':
            purchase_link = entry.get('purchase_id')
            link_status = f"Linked to {purchase_link[:8]}..." if purchase_link else "Not linked"
            print_info(f"  🍽️ MEAL: {title} - {link_status}")
        elif entry_type == 'purchase':
            items_count = len(entry.get('items', []))
            print_info(f"  🛒 PURCHASE: {title} ({items_count} items)")
    
    return True


def cleanup():
    """Clean up test data"""
    print_header("8. Cleanup")
    cleanup_test_user()
    print_success("Cleaned up test user and related data")


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("  MEAL-PURCHASE LINKING FLOW TESTS")
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
    
    # 3. Create purchase
    purchase_id = test_create_purchase()
    results['create_purchase'] = purchase_id is not None
    
    if not purchase_id:
        print_error("Cannot continue without purchase")
        cleanup()
        return
    
    # 4. Create meal with shared ingredients
    meal_id = test_create_meal_with_shared_ingredients(purchase_id)
    results['create_meal'] = meal_id is not None
    
    if not meal_id:
        print_error("Cannot continue without meal")
        cleanup()
        return
    
    # 5. Link meal to purchase
    results['link_meal_purchase'] = test_link_meal_to_purchase(meal_id, purchase_id)
    
    # 6. Verify linkage
    results['verify_linkage'] = test_verify_linkage(meal_id, purchase_id)
    
    # 7. View all entries
    results['view_entries'] = test_get_all_entries()
    
    # 8. Cleanup
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
