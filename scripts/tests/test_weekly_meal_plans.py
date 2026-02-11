"""
Test Weekly Meal Plan Endpoints
Tests /meal-plans/current and /meal-plans/week endpoints
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def login_test_user():
    """Login with test user"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "testrecipes@gomums.com",
            "password": "test123456"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("token") or data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def test_current_week_meal_plan(token: str):
    """Test GET /meal-plans/current"""
    print("\n" + "="*70)
    print("TEST 1: Get Current Week's Meal Plan")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/current",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        meal_plan = response.json()
        print("✅ Current week meal plan retrieved/created")
        print(f"  ID: {meal_plan.get('id')}")
        print(f"  Name: {meal_plan.get('name')}")
        print(f"  Week: {meal_plan.get('start_date')} to {meal_plan.get('end_date')}")
        print(f"  Status: {meal_plan.get('status')}")
        print(f"  Planned Meals: {len(meal_plan.get('planned_meals', []))}")
        print(f"  Shopping Items: {len(meal_plan.get('shopping_list_items', []))}")
        return meal_plan.get('id')
    else:
        print(f"❌ Failed: {response.text}")
        return None


def test_specific_week_meal_plan(token: str, date_str: str):
    """Test GET /meal-plans/week?date=YYYY-MM-DD"""
    print("\n" + "="*70)
    print(f"TEST 2: Get Meal Plan for Week Containing {date_str}")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/week",
        params={"date": date_str},
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        meal_plan = response.json()
        print("✅ Meal plan retrieved/created for specified week")
        print(f"  ID: {meal_plan.get('id')}")
        print(f"  Name: {meal_plan.get('name')}")
        print(f"  Week: {meal_plan.get('start_date')} to {meal_plan.get('end_date')}")
        print(f"  Status: {meal_plan.get('status')}")
        print(f"  Planned Meals: {len(meal_plan.get('planned_meals', []))}")
        print(f"  Shopping Items: {len(meal_plan.get('shopping_list_items', []))}")
        return meal_plan.get('id')
    else:
        print(f"❌ Failed: {response.text}")
        return None


def test_add_meal_to_plan(token: str, meal_plan_id: str, recipe_name: str, date_str: str):
    """Add a meal to a meal plan"""
    print("\n" + "="*70)
    print(f"TEST 3: Add Meal '{recipe_name}' to Plan")
    print("="*70)
    
    response = requests.post(
        f"{BASE_URL}/meal-plans/{meal_plan_id}/meals",
        headers=get_headers(token),
        json={
            "date": date_str,
            "meal_type": "dinner",
            "recipe_name": recipe_name,
            "servings": 2
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        meal = response.json()
        print("✅ Meal added successfully")
        print(f"  ID: {meal.get('id')}")
        print(f"  Recipe: {meal.get('recipe_name')}")
        print(f"  Date: {meal.get('date')}")
        print(f"  Type: {meal.get('meal_type')}")
        print(f"  Servings: {meal.get('servings')}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_current_week_shows_meal(token: str):
    """Verify current week meal plan shows the added meal"""
    print("\n" + "="*70)
    print("TEST 4: Verify Current Week Shows Added Meal")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/meal-plans/current",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        meal_plan = response.json()
        planned_meals = meal_plan.get('planned_meals', [])
        
        if len(planned_meals) > 0:
            print(f"✅ Meal plan has {len(planned_meals)} planned meal(s)")
            for meal in planned_meals:
                print(f"  • {meal.get('date')} - {meal.get('meal_type')}: {meal.get('recipe_name')} ({meal.get('servings')} servings)")
            return True
        else:
            print("⚠️  Meal plan exists but has no planned meals")
            return False
    else:
        print(f"❌ Failed: {response.text}")
        return False


def main():
    print("\n" + "="*70)
    print("🔗 TESTING WEEKLY MEAL PLAN ENDPOINTS")
    print("="*70)
    print(f"Backend: {BASE_URL}")
    print(f"User: testrecipes@gomums.com")
    
    # Login
    print("\n🔑 Logging in...")
    token = login_test_user()
    
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    print("✅ Authenticated")
    
    # Test 1: Get current week
    current_plan_id = test_current_week_meal_plan(token)
    
    if not current_plan_id:
        print("\n❌ Cannot proceed without current week meal plan")
        return
    
    # Test 2: Get next week
    next_week_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    next_week_plan_id = test_specific_week_meal_plan(token, next_week_date)
    
    # Test 3: Add a meal to current week
    today = datetime.now().strftime("%Y-%m-%d")
    if current_plan_id:
        test_add_meal_to_plan(token, current_plan_id, "Chicken Stir-Fry", today)
    
    # Test 4: Verify meal appears in current week
    test_current_week_shows_meal(token)
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70)
    print("\n📋 SUMMARY:")
    print("  • GET /meal-plans/current - Get/create current week's plan")
    print("  • GET /meal-plans/week?date=DATE - Get/create specific week's plan")
    print("  • POST /meal-plans/{id}/meals - Add meals to plans")
    print("\n🎯 USE CASE:")
    print("  Frontend can call GET /meal-plans/current to show 'This Week's Meal Plan'")
    print("  section on home page with actual user data (not mock data).\n")


if __name__ == "__main__":
    main()
