"""
Test Meal Planning System

Tests for meal plans, planned meals, and shopping lists.
"""
import requests
import json
from datetime import datetime, date, timedelta

# ==================== Configuration ====================

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_mealplan@example.com"
TEST_PASSWORD = "TestPassword123!"


# ==================== Helper Functions ====================

def register_user(email: str, password: str, name: str = "Test User"):
    """Register a new user"""
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name
        }
    )
    return response


def login_user(email: str, password: str):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    return None


def get_headers(token: str):
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# ==================== Tests ====================

def test_0_setup():
    """Setup: Register and login test user"""
    print("\n" + "="*50)
    print("TEST 0: User Setup")
    print("="*50)
    
    # Try to register (might already exist)
    response = register_user(TEST_EMAIL, TEST_PASSWORD, "Meal Plan Test User")
    
    if response.status_code == 201:
        print("✓ New user registered")
    elif response.status_code == 400:
        print("✓ User already exists")
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None
    
    # Login
    token = login_user(TEST_EMAIL, TEST_PASSWORD)
    
    if token:
        print("✓ User logged in successfully")
        print(f"  Token: {token[:20]}...")
        return token
    else:
        print("✗ Login failed")
        return None


def test_1_create_meal_plan(token: str):
    """Test 1: Create a meal plan"""
    print("\n" + "="*50)
    print("TEST 1: Create Meal Plan")
    print("="*50)
    
    # Create meal plan for current week
    today = date.today()
    start_date = today - timedelta(days=today.weekday())  # Monday
    end_date = start_date + timedelta(days=6)  # Sunday
    
    response = requests.post(
        f"{BASE_URL}/meal-plans/",
        headers=get_headers(token),
        json={
            "name": f"Week of {start_date.strftime('%b %d')}",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": "draft"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        meal_plan = response.json()
        print("✓ Meal plan created successfully")
        print(f"  ID: {meal_plan.get('id')}")
        print(f"  Name: {meal_plan.get('name')}")
        print(f"  Dates: {meal_plan.get('start_date')} to {meal_plan.get('end_date')}")
        print(f"  Status: {meal_plan.get('status')}")
        return meal_plan
    else:
        print("✗ Failed to create meal plan")
        print(f"  Response: {response.text}")
        return None


def test_2_add_planned_meals(token: str, meal_plan_id: str):
    """Test 2: Add planned meals to meal plan"""
    print("\n" + "="*50)
    print("TEST 2: Add Planned Meals")
    print("="*50)
    
    today = date.today()
    start_date = today - timedelta(days=today.weekday())
    
    meals_to_add = [
        {
            "date": (start_date + timedelta(days=0)).isoformat(),  # Monday
            "meal_type": "dinner",
            "recipe_name": "Spaghetti Bolognese",
            "servings": 4,
            "is_batch": True
        },
        {
            "date": (start_date + timedelta(days=1)).isoformat(),  # Tuesday
            "meal_type": "lunch",
            "recipe_name": "Leftover Spaghetti",
            "servings": 2,
            "is_leftovers": True
        },
        {
            "date": (start_date + timedelta(days=2)).isoformat(),  # Wednesday
            "meal_type": "dinner",
            "recipe_name": "Chicken Stir Fry",
            "servings": 3
        },
        {
            "date": (start_date + timedelta(days=3)).isoformat(),  # Thursday
            "meal_type": "breakfast",
            "recipe_name": "Overnight Oats",
            "servings": 1
        },
        {
            "date": (start_date + timedelta(days=3)).isoformat(),  # Thursday
            "meal_type": "dinner",
            "recipe_name": "Tacos",
            "servings": 4
        }
    ]
    
    created_meals = []
    
    for meal_data in meals_to_add:
        response = requests.post(
            f"{BASE_URL}/meal-plans/{meal_plan_id}/meals",
            headers=get_headers(token),
            json=meal_data
        )
        
        if response.status_code == 201:
            meal = response.json()
            created_meals.append(meal)
            print(f"  ✓ {meal_data['recipe_name']} - {meal_data['meal_type']} on {meal_data['date']}")
        else:
            print(f"  ✗ Failed to add {meal_data['recipe_name']}: {response.text}")
    
    print(f"\n✓ Added {len(created_meals)} planned meals")
    return created_meals


def test_3_get_calendar_view(token: str, meal_plan_id: str):
    """Test 3: Get calendar view of meal plan"""
    print("\n" + "="*50)
    print("TEST 3: Get Calendar View")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/{meal_plan_id}/calendar",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        calendar = response.json()
        print("✓ Calendar view retrieved")
        print(f"  Plan: {calendar.get('meal_plan_name')}")
        print(f"  Days: {len(calendar.get('days', []))}")
        
        print("\nWeek Overview:")
        for day in calendar.get('days', []):
            day_date = day.get('date')
            breakfast = day.get('breakfast')
            lunch = day.get('lunch')
            dinner = day.get('dinner')
            snacks = day.get('snacks', [])
            
            meals_count = sum([
                1 if breakfast else 0,
                1 if lunch else 0,
                1 if dinner else 0,
                len(snacks)
            ])
            
            print(f"  {day_date}: {meals_count} meal(s)", end="")
            if breakfast:
                print(f" | B: {breakfast.get('recipe_name')}", end="")
            if lunch:
                print(f" | L: {lunch.get('recipe_name')}", end="")
            if dinner:
                print(f" | D: {dinner.get('recipe_name')}", end="")
            print()
        
        return calendar
    else:
        print("✗ Failed to get calendar view")
        print(f"  Response: {response.text}")
        return None


def test_4_add_shopping_items(token: str, meal_plan_id: str):
    """Test 4: Add shopping list items"""
    print("\n" + "="*50)
    print("TEST 4: Add Shopping List Items")
    print("="*50)
    
    shopping_items = [
        {
            "name": "Ground beef",
            "quantity": "2 lbs",
            "category": "Protein",
            "estimated_cost": 12.99
        },
        {
            "name": "Spaghetti pasta",
            "quantity": "1 box",
            "category": "Pantry",
            "estimated_cost": 2.50
        },
        {
            "name": "Tomato sauce",
            "quantity": "2 cans",
            "category": "Canned Goods",
            "estimated_cost": 4.00
        },
        {
            "name": "Chicken breast",
            "quantity": "1.5 lbs",
            "category": "Protein",
            "estimated_cost": 9.99
        },
        {
            "name": "Bell peppers",
            "quantity": "3 peppers",
            "category": "Produce",
            "estimated_cost": 4.50
        },
        {
            "name": "Rolled oats",
            "quantity": "1 container",
            "category": "Pantry",
            "estimated_cost": 5.99
        },
        {
            "name": "Taco shells",
            "quantity": "1 box",
            "category": "Pantry",
            "estimated_cost": 3.99
        }
    ]
    
    created_items = []
    
    for item_data in shopping_items:
        response = requests.post(
            f"{BASE_URL}/meal-plans/{meal_plan_id}/shopping",
            headers=get_headers(token),
            json=item_data
        )
        
        if response.status_code == 201:
            item = response.json()
            created_items.append(item)
            print(f"  ✓ {item_data['name']} - {item_data['quantity']} (${item_data['estimated_cost']})")
        else:
            print(f"  ✗ Failed to add {item_data['name']}: {response.text}")
    
    print(f"\n✓ Added {len(created_items)} shopping items")
    return created_items


def test_5_get_shopping_list(token: str, meal_plan_id: str):
    """Test 5: Get shopping list"""
    print("\n" + "="*50)
    print("TEST 5: Get Shopping List")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/{meal_plan_id}/shopping",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        items = response.json()
        print(f"✓ Retrieved {len(items)} shopping items")
        
        # Group by category
        by_category = {}
        total_cost = 0
        
        for item in items:
            category = item.get('category', 'Uncategorized')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
            
            if item.get('estimated_cost'):
                total_cost += float(item['estimated_cost'])
        
        print("\nShopping List by Category:")
        for category, category_items in by_category.items():
            print(f"  {category}:")
            for item in category_items:
                status = "✓" if item.get('purchased') else "☐"
                print(f"    {status} {item.get('name')} - {item.get('quantity')} (${item.get('estimated_cost')})")
        
        print(f"\nEstimated Total Cost: ${total_cost:.2f}")
        
        return items
    else:
        print("✗ Failed to get shopping list")
        print(f"  Response: {response.text}")
        return None


def test_6_mark_items_purchased(token: str, shopping_items: list):
    """Test 6: Mark items as purchased"""
    print("\n" + "="*50)
    print("TEST 6: Mark Items as Purchased")
    print("="*50)
    
    # Mark first 3 items as purchased
    item_ids = [item['id'] for item in shopping_items[:3]]
    
    response = requests.post(
        f"{BASE_URL}/meal-plans/shopping/bulk-update",
        headers=get_headers(token),
        json={
            "item_ids": item_ids,
            "purchased": True
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Marked {result.get('updated_count')} items as purchased")
        print(f"  Items: {', '.join([shopping_items[i]['name'] for i in range(min(3, len(shopping_items)))])}")
        return result
    else:
        print("✗ Failed to mark items as purchased")
        print(f"  Response: {response.text}")
        return None


def test_7_calculate_cost(token: str, meal_plan_id: str):
    """Test 7: Calculate total cost"""
    print("\n" + "="*50)
    print("TEST 7: Calculate Total Cost")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/meal-plans/{meal_plan_id}/calculate-cost",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Total cost calculated: ${result.get('total_cost')}")
        return result
    else:
        print("✗ Failed to calculate cost")
        print(f"  Response: {response.text}")
        return None


def test_8_get_meal_plan_details(token: str, meal_plan_id: str):
    """Test 8: Get full meal plan details"""
    print("\n" + "="*50)
    print("TEST 8: Get Meal Plan Details")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/{meal_plan_id}/details",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        plan = response.json()
        print("✓ Retrieved complete meal plan")
        print(f"  Name: {plan.get('name')}")
        print(f"  Status: {plan.get('status')}")
        print(f"  Total meals: {len(plan.get('planned_meals', []))}")
        print(f"  Shopping items: {len(plan.get('shopping_list_items', []))}")
        print(f"  Total cost: ${plan.get('total_cost')}")
        return plan
    else:
        print("✗ Failed to get meal plan details")
        print(f"  Response: {response.text}")
        return None


def test_9_update_meal_plan_status(token: str, meal_plan_id: str):
    """Test 9: Update meal plan status to active"""
    print("\n" + "="*50)
    print("TEST 9: Update Meal Plan Status")
    print("="*50)
    
    response = requests.patch(
        f"{BASE_URL}/meal-plans/{meal_plan_id}",
        headers=get_headers(token),
        json={
            "status": "active"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        plan = response.json()
        print(f"✓ Status updated to: {plan.get('status')}")
        return plan
    else:
        print("✗ Failed to update status")
        print(f"  Response: {response.text}")
        return None


def test_10_list_all_meal_plans(token: str):
    """Test 10: List all meal plans"""
    print("\n" + "="*50)
    print("TEST 10: List All Meal Plans")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        plans = response.json()
        print(f"✓ Retrieved {len(plans)} meal plans")
        
        for plan in plans:
            print(f"\n  • {plan.get('name')}")
            print(f"    Status: {plan.get('status')}")
            print(f"    Dates: {plan.get('start_date')} to {plan.get('end_date')}")
            print(f"    Meals: {plan.get('total_meals')}")
            print(f"    Shopping items: {plan.get('total_shopping_items')} ({plan.get('shopping_items_purchased')} purchased)")
            if plan.get('total_cost'):
                print(f"    Total cost: ${plan.get('total_cost')}")
        
        return plans
    else:
        print("✗ Failed to list meal plans")
        print(f"  Response: {response.text}")
        return None


# ==================== Run All Tests ====================

def run_all_tests():
    """Run all test cases in sequence"""
    print("\n" + "="*70)
    print("MEAL PLANNING SYSTEM TESTS")
    print("="*70)
    
    # Setup
    token = test_0_setup()
    if not token:
        print("\n✗ Setup failed - cannot proceed with tests")
        return
    
    # Run tests
    meal_plan = test_1_create_meal_plan(token)
    if not meal_plan:
        print("\n✗ Failed to create meal plan - cannot proceed")
        return
    
    meal_plan_id = meal_plan['id']
    
    planned_meals = test_2_add_planned_meals(token, meal_plan_id)
    test_3_get_calendar_view(token, meal_plan_id)
    shopping_items = test_4_add_shopping_items(token, meal_plan_id)
    test_5_get_shopping_list(token, meal_plan_id)
    
    if shopping_items:
        test_6_mark_items_purchased(token, shopping_items)
    
    test_7_calculate_cost(token, meal_plan_id)
    test_8_get_meal_plan_details(token, meal_plan_id)
    test_9_update_meal_plan_status(token, meal_plan_id)
    test_10_list_all_meal_plans(token)
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
