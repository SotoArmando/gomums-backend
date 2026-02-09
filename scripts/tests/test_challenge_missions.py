"""
Test script for challenge missions
Tests various cooking and budget challenge missions
"""
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "challenge_test@gomums.com"
TEST_PASSWORD = "Test1234!"
TEST_NAME = "Challenge Test User"

# Challenges to test
CHALLENGE_TESTS = [
    {
        'title': 'Batch Cooking Challenge',
        'test_type': 'batch_cooking',
        'entries': 3,  # Create 3 batch meals
        'description': 'Cook 3 meals with 3+ portions each'
    },
    {
        'title': 'Weekly Savings Challenge',
        'test_type': 'budget_tracking',
        'entries': 7,  # Track 7 days under budget
        'description': 'Stay under budget for 7 days'
    },
    {
        'title': 'No Spend Weekend',
        'test_type': 'no_spend',
        'entries': 2,  # 2 days without spending
        'description': 'Complete weekend without food spending'
    },
    {
        'title': 'Cook Streak',
        'test_type': 'cooking_streak',
        'entries': 5,  # 5 consecutive cooking days
        'description': 'Cook at home for 5 days straight'
    },
    {
        'title': 'Leftover Makeover',
        'test_type': 'leftover_meals',
        'entries': 3,  # 3 leftover transformations
        'description': 'Create 3 new meals from leftovers'
    }
]


def test_challenge_missions():
    print("\n" + "="*70)
    print("Testing Challenge Missions")
    print("="*70)
    
    # Step 1: Register and login
    print("\n[1] Registering test user...")
    register_data = {
        "name": TEST_NAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    # If user exists, try login instead
    if response.status_code == 400:
        print("⚠️  User already exists, attempting login...")
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to authenticate: {response.text}")
        print("💡 Make sure the server is running on port 8000")
        print("💡 Or run cleanup first: python3 cleanup_challenge_test.py")
        return
    
    response_data = response.json()
    
    # Handle different response formats
    if "access_token" in response_data:
        token = response_data["access_token"]
    elif "token" in response_data:
        token = response_data["token"]
    else:
        print(f"❌ Unexpected response structure: {response_data}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Step 2: Get available missions
    print("\n[2] Fetching available weekly missions...")
    response = requests.get(f"{BASE_URL}/missions/available?mission_type=weekly", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get available missions: {response.text}")
        return
    
    available_missions = response.json()
    print(f"✅ Found {len(available_missions)} available weekly missions")
    
    # Step 3: Test each challenge
    tested_count = 0
    for challenge in CHALLENGE_TESTS:
        print(f"\n{'='*70}")
        print(f"Testing: {challenge['title']}")
        print(f"{'='*70}")
        
        # Find the mission
        mission = None
        for m in available_missions:
            if challenge['title'].lower() in m.get('title', '').lower():
                mission = m
                break
        
        if not mission:
            print(f"⚠️  Mission '{challenge['title']}' not found in database")
            print("   Run: python3 seed_challenge_missions.py")
            continue
        
        mission_id = mission['id']
        mission_target = mission['target']
        mission_points = mission['reward_points']
        
        print(f"📋 Mission: {mission['title']}")
        print(f"   Target: {mission_target}")
        print(f"   Difficulty: {mission['difficulty']}")
        print(f"   Reward: {mission_points} points")
        print(f"   Description: {mission['description']}")
        
        # Check availability
        print(f"\n   Checking availability...")
        response = requests.get(f"{BASE_URL}/missions/check-availability/{mission_id}", headers=headers)
        if response.status_code == 200:
            availability = response.json()
            if availability.get('available'):
                print(f"   ✅ Mission is available")
            else:
                print(f"   ⏳ Mission in cooldown: {availability.get('reason')}")
                if 'hours_remaining' in availability:
                    print(f"      Available in: {availability['hours_remaining']} hours")
                continue
        
        # Assign the mission
        print(f"\n   Assigning mission...")
        response = requests.post(f"{BASE_URL}/missions/assign/{mission_id}", headers=headers)
        
        if response.status_code == 409:
            print(f"   ⏳ Mission in cooldown: {response.json().get('detail')}")
            continue
        elif response.status_code != 200:
            print(f"   ❌ Failed to assign: {response.text}")
            continue
        
        print(f"   ✅ Mission assigned successfully")
        tested_count += 1
        
        # Get mission details
        response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
        if response.status_code == 200:
            active_missions = response.json()
            assigned_mission = next(
                (m for m in active_missions if m.get('mission', {}).get('id') == mission_id),
                None
            )
            if assigned_mission:
                progress = assigned_mission.get('progress', 0)
                print(f"   Progress: {progress}/{mission_target}")
        
        print(f"\n   💡 Test scenario: {challenge['description']}")
        print(f"   💡 To complete: Perform {challenge['entries']} actions for this mission")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Test Summary")
    print(f"{'='*70}")
    print(f"✅ Successfully assigned: {tested_count} missions")
    print(f"💡 Note: These missions require specific actions to complete")
    print(f"   - Track progress via GET /api/missions/active")
    print(f"   - Missions auto-update based on journal/budget entries")
    print("="*70)


if __name__ == "__main__":
    try:
        test_challenge_missions()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
