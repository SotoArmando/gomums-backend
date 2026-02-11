"""
Test script for AUTOMATIC Meal-Purchase Linking

Tests: Log a purchase → Log a meal with matching ingredients → Verify auto-link

This verifies the NEW auto-linking behavior:
- When a meal is created with ingredients_used
- The system automatically finds recent purchases with matching items
- Links them together WITHOUT requiring a separate API call
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
    "name": "Auto Link Test User",
    "email": "autolink_test@gomums.com",
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
    print(f"\n{Colors.CYAN}{'='*60}")
    print(text)
    print(f"{'='*60}{Colors.END}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def get_auth_headers() -> dict:
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


def setup_user():
    """Register and login test user"""
    global ACCESS_TOKEN
    
    print_header("1. Setup Test User")
    
    cleanup_test_user()
    
    # Register
    response = requests.post(f"{API_URL}/auth/register", json=TEST_USER)
    
    if response.status_code == 201:
        print_success("User registered")
        ACCESS_TOKEN = response.json()["token"]
        return True
    else:
        print_error(f"Registration failed: {response.status_code}")
        return False


# ==================== Test Functions ====================

def test_create_purchase():
    """Step 1: Log a grocery purchase with quantities in names"""
    print_header("2. Log a Grocery Purchase")
    
    # Items have quantities/units in names - should still match simplified ingredient names
    purchase_data = {
        "type": "purchase",
        "title": "Grocery Run",
        "store": "Walmart",
        "items": [
            {"name": "2 lb Chicken breast", "quantity": "2 lb", "cost": 8.99, "category": "proteins"},
            {"name": "Fresh Broccoli (2 heads)", "quantity": "2 heads", "cost": 2.50, "category": "vegetables"},
            {"name": "1 bottle Soy sauce", "quantity": "1 bottle", "cost": 3.99, "category": "pantry"},
            {"name": "Garlic cloves", "quantity": "1 head", "cost": 0.50, "category": "vegetables"}
        ]
    }
    
    response = requests.post(
        f"{API_URL}/journal/entries",
        headers=get_auth_headers(),
        json=purchase_data
    )
    
    if response.status_code == 201:
        purchase = response.json()
        print_success(f"Purchase logged!")
        print_info(f"Purchase ID: {purchase['id']}")
        print_info(f"Items (with quantities): {[item['name'] for item in purchase.get('items', [])]}")
        return purchase['id']
    else:
        print_error(f"Failed: {response.status_code}")
        print(response.text)
        return None


def test_create_meal_auto_link():
    """Step 2: Log a meal with simplified ingredients - should AUTO-LINK"""
    print_header("3. Log a Meal (Should Auto-Link)")
    
    # These are SIMPLIFIED ingredient names - no quantities
    # Should still match: "Chicken" → "2 lb Chicken breast"
    meal_data = {
        "type": "meal",
        "title": "Chicken Stir Fry",
        "meal_type": "dinner",
        "portions": 4,
        "status": "fresh",
        "ingredients_used": ["Chicken", "Broccoli", "Soy sauce", "Garlic"],
        "has_leftovers": True
    }
    
    print_info(f"Creating meal with SIMPLIFIED ingredients: {meal_data['ingredients_used']}")
    print_info("(Should match purchase items with quantities stripped)")
    print_info("(No purchase_id provided - should auto-link)")
    
    response = requests.post(
        f"{API_URL}/journal/entries",
        headers=get_auth_headers(),
        json=meal_data
    )
    
    if response.status_code == 201:
        meal = response.json()
        print_success(f"Meal logged!")
        print_info(f"Meal ID: {meal['id']}")
        
        # Check if it was auto-linked
        purchase_id = meal.get('purchase_id')
        if purchase_id:
            print_success(f"🔗 AUTO-LINKED to purchase: {purchase_id[:8]}...")
            return meal['id'], purchase_id
        else:
            print_error("Meal was NOT auto-linked (purchase_id is null)")
            return meal['id'], None
    else:
        print_error(f"Failed: {response.status_code}")
        print(response.text)
        return None, None


def test_verify_link_in_database(meal_id: str, expected_purchase_id: str):
    """Step 3: Verify the link exists"""
    print_header("4. Verify Link in Database")
    
    # Fetch the meal entry directly
    response = requests.get(
        f"{API_URL}/journal/entries/{meal_id}",
        headers=get_auth_headers()
    )
    
    if response.status_code != 200:
        print_error(f"Failed to fetch meal: {response.status_code}")
        return False
    
    meal = response.json()
    actual_purchase_id = meal.get('purchase_id')
    
    print_info(f"Meal: {meal['title']}")
    print_info(f"Expected purchase_id: {expected_purchase_id[:8] if expected_purchase_id else 'None'}...")
    print_info(f"Actual purchase_id: {actual_purchase_id[:8] if actual_purchase_id else 'None'}...")
    
    if actual_purchase_id == expected_purchase_id:
        print_success("✓ Link verified correctly!")
        return True
    else:
        print_error("Link mismatch!")
        return False


def test_no_match_case():
    """Test that meals without matching ingredients don't get linked"""
    print_header("5. Test No-Match Case")
    
    meal_data = {
        "type": "meal",
        "title": "Mystery Soup",
        "meal_type": "lunch",
        "portions": 2,
        "ingredients_used": ["unicorn horn", "dragon scales", "pixie dust"]
    }
    
    print_info(f"Creating meal with non-matching ingredients: {meal_data['ingredients_used']}")
    
    response = requests.post(
        f"{API_URL}/journal/entries",
        headers=get_auth_headers(),
        json=meal_data
    )
    
    if response.status_code == 201:
        meal = response.json()
        purchase_id = meal.get('purchase_id')
        
        if purchase_id:
            print_error(f"Unexpected link to: {purchase_id}")
            return False
        else:
            print_success("Correctly NOT linked (no matching ingredients)")
            return True
    else:
        print_error(f"Failed: {response.status_code}")
        return False


def cleanup():
    print_header("6. Cleanup")
    cleanup_test_user()
    print_success("Cleaned up test data")


def run_all_tests():
    print(f"\n{Colors.BOLD}{'='*60}")
    print("  AUTOMATIC MEAL-PURCHASE LINKING TESTS")
    print(f"{'='*60}{Colors.END}")
    
    results = {}
    
    # Setup
    if not setup_user():
        print_error("Setup failed, aborting")
        return
    results['setup'] = True
    
    # Create purchase
    purchase_id = test_create_purchase()
    results['create_purchase'] = purchase_id is not None
    
    if not purchase_id:
        cleanup()
        return
    
    # Create meal (should auto-link)
    meal_id, linked_purchase_id = test_create_meal_auto_link()
    results['create_meal'] = meal_id is not None
    results['auto_link'] = linked_purchase_id == purchase_id
    
    # Verify link
    if meal_id and linked_purchase_id:
        results['verify_link'] = test_verify_link_in_database(meal_id, purchase_id)
    else:
        results['verify_link'] = False
    
    # Test no-match case
    results['no_match'] = test_no_match_case()
    
    # Cleanup
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
        print(f"{Colors.GREEN}All tests passed! Auto-linking works!{Colors.END}")
    else:
        print(f"{Colors.RED}Some tests failed{Colors.END}")


if __name__ == "__main__":
    run_all_tests()
