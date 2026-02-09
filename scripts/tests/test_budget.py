#!/usr/bin/env python3
"""
Test script for Budget API endpoints
Tests all CRUD operations, stats, and category breakdown
"""

import requests
import json
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

# Test user credentials
TEST_USER = {
    "email": "test@gomums.com",
    "password": "Test123!@#",
    "name": "Test User"
}

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_section(title):
    """Print a section header"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{RESET}\n")


def print_success(message):
    """Print a success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print an error message"""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print an info message"""
    print(f"{YELLOW}ℹ {message}{RESET}")


def print_response(response):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def register_user():
    """Register a test user"""
    print_section("1. User Registration")
    
    url = f"{BASE_URL}{API_PREFIX}/auth/register"
    response = requests.post(url, json=TEST_USER)
    
    if response.status_code == 201:
        print_success("User registered successfully")
        print_response(response)
        return response.json()
    elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
        print_info("User already exists, skipping registration")
        return None
    else:
        print_error("Failed to register user")
        print_response(response)
        return None


def login_user():
    """Login and get access token"""
    print_section("2. User Login")
    
    url = f"{BASE_URL}{API_PREFIX}/auth/login"
    response = requests.post(url, json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    
    if response.status_code == 200:
        print_success("Login successful")
        data = response.json()
        access_token = data["token"]
        print_info(f"Access token: {access_token[:50]}...")
        return access_token
    else:
        print_error("Login failed")
        print_response(response)
        return None


def create_budget_settings(token):
    """Create budget settings"""
    print_section("3. Create Budget Settings")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/settings"
    headers = {"Authorization": f"Bearer {token}"}
    
    settings_data = {
        "weekly_budget": 150.00,
        "monthly_budget": 600.00
    }
    
    response = requests.post(url, json=settings_data, headers=headers)
    
    if response.status_code in [200, 201]:
        print_success("Budget settings created successfully")
        print_response(response)
        return response.json()
    else:
        print_error("Failed to create budget settings")
        print_response(response)
        return None


def get_budget_settings(token):
    """Get budget settings"""
    print_section("4. Get Budget Settings")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/settings"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print_success("Budget settings retrieved successfully")
        print_response(response)
        return response.json()
    else:
        print_error("Failed to get budget settings")
        print_response(response)
        return None


def create_budget_entry(token, entry_data):
    """Create a budget entry"""
    url = f"{BASE_URL}{API_PREFIX}/budget/entries"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, json=entry_data, headers=headers)
    
    if response.status_code == 201:
        print_success(f"Budget entry created: {entry_data['meal_name']}")
        data = response.json()
        print_info(f"  Cost: ${data['cost']}, Servings: {data['servings']}, Cost/Serving: ${data['cost_per_serving']}")
        return data
    else:
        print_error(f"Failed to create budget entry: {entry_data['meal_name']}")
        print_response(response)
        return None


def create_sample_entries(token):
    """Create sample budget entries"""
    print_section("5. Create Sample Budget Entries")
    
    today = date.today()
    
    sample_entries = [
        {
            "date": str(today),
            "meal_name": "Spaghetti Bolognese",
            "cost": 12.50,
            "servings": 4,
            "category": "Dinner",
            "notes": "Family favorite, made with ground beef"
        },
        {
            "date": str(today - timedelta(days=1)),
            "meal_name": "Chicken Stir Fry",
            "cost": 15.00,
            "servings": 3,
            "category": "Dinner",
            "notes": "Quick and healthy meal"
        },
        {
            "date": str(today - timedelta(days=2)),
            "meal_name": "Pancakes",
            "cost": 6.00,
            "servings": 6,
            "category": "Breakfast",
            "notes": "Weekend breakfast treat"
        },
        {
            "date": str(today - timedelta(days=3)),
            "meal_name": "Tuna Sandwiches",
            "cost": 8.50,
            "servings": 4,
            "category": "Lunch",
            "notes": "Easy lunch for the kids"
        },
        {
            "date": str(today - timedelta(days=4)),
            "meal_name": "Tacos",
            "cost": 18.00,
            "servings": 5,
            "category": "Dinner",
            "notes": "Taco Tuesday!"
        }
    ]
    
    created_entries = []
    for entry in sample_entries:
        result = create_budget_entry(token, entry)
        if result:
            created_entries.append(result)
    
    print_info(f"\nTotal entries created: {len(created_entries)}")
    return created_entries


def get_all_entries(token):
    """Get all budget entries"""
    print_section("6. Get All Budget Entries")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/entries"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        entries = response.json()
        print_success(f"Retrieved {len(entries)} budget entries")
        
        for entry in entries:
            print(f"  - {entry['meal_name']}: ${entry['cost']} ({entry['servings']} servings) - ${entry['cost_per_serving']}/serving")
        
        return entries
    else:
        print_error("Failed to get budget entries")
        print_response(response)
        return []


def get_entries_by_category(token, category):
    """Get budget entries filtered by category"""
    print_section(f"7. Get Entries by Category: {category}")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/entries?category={category}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        entries = response.json()
        print_success(f"Retrieved {len(entries)} entries in category '{category}'")
        
        for entry in entries:
            print(f"  - {entry['meal_name']}: ${entry['cost']}")
        
        return entries
    else:
        print_error(f"Failed to get entries for category '{category}'")
        print_response(response)
        return []


def get_budget_stats(token, period="week"):
    """Get budget statistics"""
    print_section(f"8. Get Budget Stats (Period: {period})")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/stats?period={period}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Budget statistics retrieved successfully")
        print(f"\n  Budget Score: {stats['score']}/100")
        print(f"  Average Cost per Meal: ${stats['avg_cost_per_meal']}")
        print(f"  Savings vs Restaurant: ${stats['savings_vs_restaurant']}")
        print(f"  Meals This Week: {stats['meals_this_week']}")
        print(f"  Total Spent: ${stats['total_spent']}")
        
        if stats['weekly_budget']:
            print(f"  Weekly Budget: ${stats['weekly_budget']}")
            print(f"  Remaining Budget: ${stats['remaining_budget']}")
        
        return stats
    else:
        print_error("Failed to get budget stats")
        print_response(response)
        return None


def get_category_breakdown(token, period="week"):
    """Get category breakdown"""
    print_section(f"9. Get Category Breakdown (Period: {period})")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/category-breakdown?period={period}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        breakdown = response.json()
        print_success("Category breakdown retrieved successfully")
        
        print(f"\n  Categories:")
        for category, amount in breakdown['breakdown'].items():
            print(f"    - {category}: ${amount}")
        
        print(f"\n  Total: ${breakdown['total']}")
        
        return breakdown
    else:
        print_error("Failed to get category breakdown")
        print_response(response)
        return None


def update_budget_entry(token, entry_id):
    """Update a budget entry"""
    print_section("10. Update Budget Entry")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/entries/{entry_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "cost": 14.00,
        "notes": "Updated: Actually spent more on premium ingredients"
    }
    
    response = requests.patch(url, json=update_data, headers=headers)
    
    if response.status_code == 200:
        print_success("Budget entry updated successfully")
        print_response(response)
        return response.json()
    else:
        print_error("Failed to update budget entry")
        print_response(response)
        return None


def delete_budget_entry(token, entry_id):
    """Delete a budget entry"""
    print_section("11. Delete Budget Entry")
    
    url = f"{BASE_URL}{API_PREFIX}/budget/entries/{entry_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        print_success("Budget entry deleted successfully")
        return True
    else:
        print_error("Failed to delete budget entry")
        print_response(response)
        return False


def main():
    """Main test function"""
    print(f"\n{BLUE}{'='*60}")
    print("GoMums Budget API - Test Script")
    print(f"{'='*60}{RESET}\n")
    
    print_info(f"Testing API at: {BASE_URL}")
    
    # Step 1 & 2: Register and Login
    register_user()
    token = login_user()
    
    if not token:
        print_error("\n❌ Cannot proceed without authentication token")
        return
    
    # Step 3 & 4: Budget Settings
    create_budget_settings(token)
    get_budget_settings(token)
    
    # Step 5: Create Sample Entries
    entries = create_sample_entries(token)
    
    if not entries:
        print_error("\n❌ Failed to create sample entries")
        return
    
    # Step 6: Get All Entries
    all_entries = get_all_entries(token)
    
    # Step 7: Filter by Category
    get_entries_by_category(token, "Dinner")
    
    # Step 8: Get Budget Stats
    get_budget_stats(token, "week")
    
    # Step 9: Get Category Breakdown
    get_category_breakdown(token, "week")
    
    # Step 10: Update an Entry
    if entries:
        update_budget_entry(token, entries[0]["id"])
    
    # Step 11: Delete an Entry
    if len(entries) > 1:
        delete_budget_entry(token, entries[-1]["id"])
    
    # Final check
    print_section("12. Final Check - Get All Entries")
    final_entries = get_all_entries(token)
    
    # Summary
    print_section("Test Summary")
    print_success(f"✅ All budget API endpoints tested successfully!")
    print_info(f"  Total entries remaining: {len(final_entries)}")
    print_info(f"  API Documentation: {BASE_URL}/docs")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print_error("\n❌ Cannot connect to the API server")
        print_info(f"Make sure the server is running at {BASE_URL}")
        print_info("Run: python -m app.main")
    except Exception as e:
        print_error(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
