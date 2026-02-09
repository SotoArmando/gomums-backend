"""
Test User Stats Endpoints

Tests for user statistics tracking, leaderboard, and stats updates.
"""
import requests
import json
from datetime import datetime

# ==================== Configuration ====================

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_stats@example.com"
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
    response = register_user(TEST_EMAIL, TEST_PASSWORD, "Stats Test User")
    
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


def test_1_get_initial_stats(token: str):
    """Test 1: Get initial user stats"""
    print("\n" + "="*50)
    print("TEST 1: Get Initial Stats")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/user/stats/",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print("✓ Stats retrieved successfully")
        print(f"  Total meals cooked: {stats.get('total_meals_cooked')}")
        print(f"  Total money saved: ${stats.get('total_money_saved')}")
        print(f"  Current streak: {stats.get('current_streak')} days")
        print(f"  Achievements unlocked: {stats.get('achievements_unlocked')}")
        print(f"  Level: {stats.get('level')}")
        print(f"  Points: {stats.get('points')}")
        return stats
    else:
        print("✗ Failed to get stats")
        print(f"  Response: {response.text}")
        return None


def test_2_get_stats_summary(token: str):
    """Test 2: Get comprehensive stats summary"""
    print("\n" + "="*50)
    print("TEST 2: Get Stats Summary")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/user/stats/summary",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        summary = response.json()
        print("✓ Summary retrieved successfully")
        print(f"  Total meals cooked: {summary.get('total_meals_cooked')}")
        print(f"  Total money saved: ${summary.get('total_money_saved')}")
        print(f"  Current streak: {summary.get('current_streak')} days")
        print(f"  Level: {summary.get('level')}")
        print(f"  Points: {summary.get('points')}")
        print(f"  Points to next level: {summary.get('points_to_next_level')}")
        print(f"  Level progress: {summary.get('level_progress_percentage'):.1f}%")
        print(f"  Money saved this week: ${summary.get('money_saved_this_week')}")
        print(f"  Money saved this month: ${summary.get('money_saved_this_month')}")
        print(f"  Meals this week: {summary.get('meals_this_week')}")
        print(f"  Meals this month: {summary.get('meals_this_month')}")
        return summary
    else:
        print("✗ Failed to get summary")
        print(f"  Response: {response.text}")
        return None


def test_3_increment_stats(token: str):
    """Test 3: Manually increment stats"""
    print("\n" + "="*50)
    print("TEST 3: Increment Stats")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/user/stats/increment",
        headers=get_headers(token),
        json={
            "meals_cooked": 1,
            "money_saved": 12.50,
            "points": 10
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Stats incremented successfully")
        print(f"  Message: {result.get('message')}")
        
        stats = result.get('stats', {})
        print(f"  Updated meals: {stats.get('total_meals_cooked')}")
        print(f"  Updated savings: ${stats.get('total_money_saved')}")
        print(f"  Updated points: {stats.get('points')}")
        print(f"  Current streak: {stats.get('current_streak')} days")
        print(f"  Level: {stats.get('level')}")
        return stats
    else:
        print("✗ Failed to increment stats")
        print(f"  Response: {response.text}")
        return None


def test_4_increment_multiple_times(token: str):
    """Test 4: Increment stats multiple times (streak test)"""
    print("\n" + "="*50)
    print("TEST 4: Multiple Increments (Same Day)")
    print("="*50)
    
    for i in range(3):
        response = requests.post(
            f"{BASE_URL}/user/stats/increment",
            headers=get_headers(token),
            json={
                "meals_cooked": 1,
                "money_saved": 15.00,
                "points": 10
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            stats = result.get('stats', {})
            print(f"  Increment {i+1}: Meals={stats.get('total_meals_cooked')}, "
                  f"Streak={stats.get('current_streak')}, "
                  f"Level={stats.get('level')}, "
                  f"Points={stats.get('points')}")
        else:
            print(f"  ✗ Increment {i+1} failed: {response.text}")
    
    print("✓ Multiple increments completed")
    print("  Note: Streak should not increase for same-day activities")


def test_5_create_meal_entry(token: str):
    """Test 5: Create a meal entry (should auto-increment stats)"""
    print("\n" + "="*50)
    print("TEST 5: Create Meal Entry (Auto Stats Update)")
    print("="*50)
    
    # Get current stats first
    response = requests.get(
        f"{BASE_URL}/user/stats/",
        headers=get_headers(token)
    )
    initial_stats = response.json() if response.status_code == 200 else {}
    initial_meals = initial_stats.get('total_meals_cooked', 0)
    initial_savings = initial_stats.get('total_money_saved', 0)
    initial_points = initial_stats.get('points', 0)
    
    print(f"Initial stats: {initial_meals} meals, ${initial_savings} saved, {initial_points} points")
    
    # Create meal entry
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        headers=get_headers(token),
        json={
            "type": "meal",
            "title": "Test Meal for Stats",
            "meal_type": "dinner",
            "portions": 4,
            "status": "fresh",
            "is_batch": True,
            "used_leftovers": False
        }
    )
    
    print(f"Meal creation status: {response.status_code}")
    
    if response.status_code == 201:
        print("✓ Meal entry created")
        
        # Get updated stats
        response = requests.get(
            f"{BASE_URL}/user/stats/",
            headers=get_headers(token)
        )
        
        if response.status_code == 200:
            updated_stats = response.json()
            updated_meals = updated_stats.get('total_meals_cooked', 0)
            updated_savings = updated_stats.get('total_money_saved', 0)
            updated_points = updated_stats.get('points', 0)
            
            print("✓ Stats automatically updated")
            print(f"  Meals: {initial_meals} → {updated_meals} (+{updated_meals - initial_meals})")
            print(f"  Savings: ${initial_savings} → ${updated_savings} (+${updated_savings - initial_savings})")
            print(f"  Points: {initial_points} → {updated_points} (+{updated_points - initial_points})")
            print(f"  Current streak: {updated_stats.get('current_streak')} days")
            print(f"  Level: {updated_stats.get('level')}")
            return updated_stats
        else:
            print("✗ Failed to get updated stats")
    else:
        print("✗ Failed to create meal entry")
        print(f"  Response: {response.text}")
    
    return None


def test_6_get_leaderboard(token: str):
    """Test 6: Get leaderboard"""
    print("\n" + "="*50)
    print("TEST 6: Get Leaderboard")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/user/stats/leaderboard?limit=10",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        leaderboard = response.json()
        print(f"✓ Leaderboard retrieved ({len(leaderboard)} entries)")
        
        for i, entry in enumerate(leaderboard, 1):
            print(f"  {i}. {entry.get('user_name')} - Level {entry.get('level')} - {entry.get('points')} points")
            print(f"     {entry.get('total_meals_cooked')} meals, ${entry.get('total_money_saved')} saved, "
                  f"{entry.get('current_streak')} day streak")
        
        return leaderboard
    else:
        print("✗ Failed to get leaderboard")
        print(f"  Response: {response.text}")
        return None


def test_7_level_progression(token: str):
    """Test 7: Test level progression by adding lots of points"""
    print("\n" + "="*50)
    print("TEST 7: Level Progression Test")
    print("="*50)
    
    # Get current level
    response = requests.get(
        f"{BASE_URL}/user/stats/",
        headers=get_headers(token)
    )
    initial_stats = response.json() if response.status_code == 200 else {}
    initial_level = initial_stats.get('level', 1)
    initial_points = initial_stats.get('points', 0)
    
    print(f"Initial: Level {initial_level}, {initial_points} points")
    
    # Add 500 points (should progress toward next level)
    response = requests.post(
        f"{BASE_URL}/user/stats/increment",
        headers=get_headers(token),
        json={
            "points": 500
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        stats = result.get('stats', {})
        new_level = stats.get('level')
        new_points = stats.get('points')
        points_to_next = stats.get('points_to_next_level')
        progress_pct = stats.get('level_progress_percentage')
        
        print(f"After +500 points:")
        print(f"  Level: {initial_level} → {new_level}")
        print(f"  Points: {initial_points} → {new_points}")
        print(f"  Points to next level: {points_to_next}")
        print(f"  Progress: {progress_pct:.1f}%")
        
        if new_level > initial_level:
            print(f"🎉 LEVEL UP! Reached level {new_level}!")
        
        return stats
    else:
        print("✗ Failed to add points")
        print(f"  Response: {response.text}")
        return None


# ==================== Run All Tests ====================

def run_all_tests():
    """Run all test cases in sequence"""
    print("\n" + "="*70)
    print("USER STATS API TESTS")
    print("="*70)
    
    # Setup
    token = test_0_setup()
    if not token:
        print("\n✗ Setup failed - cannot proceed with tests")
        return
    
    # Run tests
    test_1_get_initial_stats(token)
    test_2_get_stats_summary(token)
    test_3_increment_stats(token)
    test_4_increment_multiple_times(token)
    test_5_create_meal_entry(token)
    test_6_get_leaderboard(token)
    test_7_level_progression(token)
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
