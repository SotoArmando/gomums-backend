"""
Test Achievement System

Tests for achievements endpoints and auto-unlock functionality.
"""
import requests
import json
from datetime import datetime

# ==================== Configuration ====================

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test_achievements@example.com"
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
    response = register_user(TEST_EMAIL, TEST_PASSWORD, "Achievement Test User")
    
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


def test_1_seed_achievements(token: str):
    """Test 1: Seed predefined achievements"""
    print("\n" + "="*50)
    print("TEST 1: Seed Achievements")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/achievements/seed",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Achievements seeded successfully")
        print(f"  Total predefined: {result.get('total_predefined')}")
        print(f"  Created: {result.get('created')}")
        print(f"  Skipped (already exist): {result.get('skipped')}")
        return result
    else:
        print("✗ Failed to seed achievements")
        print(f"  Response: {response.text}")
        return None


def test_2_get_all_achievements(token: str):
    """Test 2: Get all available achievements"""
    print("\n" + "="*50)
    print("TEST 2: Get All Achievements")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/achievements/",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        achievements = response.json()
        print(f"✓ Retrieved {len(achievements)} achievements")
        
        # Group by category
        by_category = {}
        for achievement in achievements:
            category = achievement.get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(achievement)
        
        print("\nAchievements by Category:")
        for category, items in by_category.items():
            print(f"  {category}: {len(items)} achievements")
            for item in items[:2]:  # Show first 2
                print(f"    - {item.get('icon')} {item.get('title')} (Target: {item.get('target')}, Points: {item.get('points')})")
        
        return achievements
    else:
        print("✗ Failed to get achievements")
        print(f"  Response: {response.text}")
        return None


def test_3_get_my_achievements(token: str):
    """Test 3: Get user's achievements with progress"""
    print("\n" + "="*50)
    print("TEST 3: Get My Achievements")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/achievements/mine",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        achievements = response.json()
        print(f"✓ Retrieved {len(achievements)} user achievements")
        
        unlocked = [a for a in achievements if a.get('is_unlocked')]
        locked = [a for a in achievements if not a.get('is_unlocked')]
        
        print(f"  Unlocked: {len(unlocked)}")
        print(f"  Locked: {len(locked)}")
        
        if unlocked:
            print("\nUnlocked Achievements:")
            for achievement in unlocked[:5]:
                print(f"  {achievement.get('achievement_icon')} {achievement.get('achievement_title')} "
                      f"({achievement.get('achievement_points')} points)")
        
        if locked:
            print("\nLocked Achievements (showing progress):")
            for achievement in locked[:5]:
                print(f"  {achievement.get('achievement_icon')} {achievement.get('achievement_title')} - "
                      f"{achievement.get('progress')}/{achievement.get('achievement_target')} "
                      f"({achievement.get('progress_percentage'):.1f}%)")
        
        return achievements
    else:
        print("✗ Failed to get user achievements")
        print(f"  Response: {response.text}")
        return None


def test_4_get_achievement_summary(token: str):
    """Test 4: Get achievement summary"""
    print("\n" + "="*50)
    print("TEST 4: Get Achievement Summary")
    print("="*50)
    
    response = requests.get(
        f"{BASE_URL}/achievements/summary",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        summary = response.json()
        print("✓ Summary retrieved successfully")
        print(f"  Total achievements: {summary.get('total_achievements')}")
        print(f"  Unlocked: {summary.get('unlocked_achievements')}")
        print(f"  Locked: {summary.get('locked_achievements')}")
        print(f"  Total points earned: {summary.get('total_points_earned')}")
        
        print("\nBy Category:")
        for category, data in summary.get('achievements_by_category', {}).items():
            print(f"  {category}: {data.get('unlocked')}/{data.get('total')}")
        
        recent = summary.get('recent_unlocks', [])
        if recent:
            print(f"\nRecent Unlocks ({len(recent)}):")
            for achievement in recent:
                print(f"  {achievement.get('achievement_icon')} {achievement.get('achievement_title')} "
                      f"- {achievement.get('unlocked_date')}")
        
        return summary
    else:
        print("✗ Failed to get summary")
        print(f"  Response: {response.text}")
        return None


def test_5_create_meals_and_check(token: str):
    """Test 5: Create meals and trigger achievement check"""
    print("\n" + "="*50)
    print("TEST 5: Create Meals & Auto-Unlock")
    print("="*50)
    
    # Create 3 meals to unlock "First Steps" and maybe more
    meals_to_create = [
        {
            "type": "meal",
            "title": "Achievement Test Meal 1",
            "meal_type": "dinner",
            "portions": 4,
            "status": "fresh"
        },
        {
            "type": "meal",
            "title": "Achievement Test Meal 2 (Batch)",
            "meal_type": "lunch",
            "portions": 6,
            "status": "fresh",
            "is_batch": True
        },
        {
            "type": "meal",
            "title": "Achievement Test Meal 3 (Leftovers)",
            "meal_type": "dinner",
            "portions": 2,
            "status": "leftovers",
            "used_leftovers": True
        }
    ]
    
    print(f"Creating {len(meals_to_create)} meals...")
    
    for i, meal_data in enumerate(meals_to_create, 1):
        response = requests.post(
            f"{BASE_URL}/journal/entries",
            headers=get_headers(token),
            json=meal_data
        )
        
        if response.status_code == 201:
            print(f"  ✓ Meal {i} created: {meal_data['title']}")
        else:
            print(f"  ✗ Meal {i} failed: {response.text}")
    
    # Get updated achievements
    print("\nChecking for unlocked achievements...")
    response = requests.get(
        f"{BASE_URL}/achievements/mine",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        achievements = response.json()
        unlocked = [a for a in achievements if a.get('is_unlocked')]
        
        print(f"✓ Now have {len(unlocked)} achievements unlocked")
        
        if unlocked:
            print("\nUnlocked Achievements:")
            for achievement in unlocked:
                print(f"  {achievement.get('achievement_icon')} {achievement.get('achievement_title')} "
                      f"({achievement.get('achievement_points')} points)")
        
        return unlocked
    else:
        print("✗ Failed to check achievements")
        return None


def test_6_manual_check_achievements(token: str):
    """Test 6: Manually trigger achievement check"""
    print("\n" + "="*50)
    print("TEST 6: Manual Achievement Check")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/achievements/check",
        headers=get_headers(token)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Achievement check completed")
        print(f"  Newly unlocked: {result.get('count')}")
        print(f"  Points awarded: {result.get('points_awarded')}")
        
        newly_unlocked = result.get('newly_unlocked', [])
        if newly_unlocked:
            print("\nNewly Unlocked:")
            for achievement in newly_unlocked:
                print(f"  {achievement.get('title')} (+{achievement.get('points')} points)")
        else:
            print("  No new achievements unlocked")
        
        # Show updated stats
        updated_stats = result.get('updated_stats', {})
        if updated_stats:
            print(f"\nUpdated Stats:")
            print(f"  Level: {updated_stats.get('level')}")
            print(f"  Points: {updated_stats.get('points')}")
            print(f"  Achievements unlocked: {updated_stats.get('achievements_unlocked')}")
        
        return result
    else:
        print("✗ Failed to check achievements")
        print(f"  Response: {response.text}")
        return None


def test_7_filter_by_category(token: str):
    """Test 7: Filter achievements by category"""
    print("\n" + "="*50)
    print("TEST 7: Filter by Category")
    print("="*50)
    
    categories = ['cooking', 'savings', 'streak']
    
    for category in categories:
        response = requests.get(
            f"{BASE_URL}/achievements/mine?category={category}",
            headers=get_headers(token)
        )
        
        if response.status_code == 200:
            achievements = response.json()
            print(f"✓ {category.capitalize()}: {len(achievements)} achievements")
            
            for achievement in achievements[:3]:
                print(f"  {achievement.get('achievement_icon')} {achievement.get('achievement_title')} - "
                      f"{achievement.get('progress')}/{achievement.get('achievement_target')} "
                      f"({'UNLOCKED' if achievement.get('is_unlocked') else 'locked'})")
        else:
            print(f"✗ Failed to get {category} achievements")


# ==================== Run All Tests ====================

def run_all_tests():
    """Run all test cases in sequence"""
    print("\n" + "="*70)
    print("ACHIEVEMENT SYSTEM TESTS")
    print("="*70)
    
    # Setup
    token = test_0_setup()
    if not token:
        print("\n✗ Setup failed - cannot proceed with tests")
        return
    
    # Run tests
    test_1_seed_achievements(token)
    test_2_get_all_achievements(token)
    test_3_get_my_achievements(token)
    test_4_get_achievement_summary(token)
    test_5_create_meals_and_check(token)
    test_6_manual_check_achievements(token)
    test_7_filter_by_category(token)
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
