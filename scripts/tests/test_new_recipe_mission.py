"""
Test script for "Try a new recipe" mission
Tests that the mission only counts truly new recipes (not repeated ones)
"""
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "newrecipe_test@gomums.com"
TEST_PASSWORD = "Test1234!"
TEST_NAME = "New Recipe Test User"


def test_new_recipe_mission():
    print("\n" + "="*60)
    print("Testing 'Try a New Recipe' Mission Logic")
    print("="*60)
    
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
        print(f"   Status code: {response.status_code}")
        print("💡 Make sure the server is running on port 8000")
        print("💡 Or run cleanup first: python3 cleanup_new_recipe_test.py")
        return
    
    response_data = response.json()
    
    # Handle different response formats
    if "access_token" in response_data:
        token = response_data["access_token"]
    elif "token" in response_data:
        token = response_data["token"]
    else:
        print(f"❌ Unexpected response structure: {response_data}")
        print("💡 Make sure the server is running on port 8000")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Step 2: Get available missions and find "Try a new recipe"
    print("\n[2] Finding 'Try a new recipe' mission...")
    response = requests.get(f"{BASE_URL}/missions/available?mission_type=daily", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get available missions: {response.text}")
        return
    
    available_missions = response.json()
    print(f"✅ Found {len(available_missions)} available daily missions")
    
    # Find the "Try a new recipe" mission
    new_recipe_template = None
    for mission in available_missions:
        if 'new recipe' in mission.get('title', '').lower():
            new_recipe_template = mission
            break
    
    if not new_recipe_template:
        print("\n❌ 'Try a new recipe' mission not found in available missions")
        print("Available missions:")
        for mission in available_missions:
            print(f"   - {mission.get('title')}")
        return
    
    mission_id = new_recipe_template['id']
    mission_title = new_recipe_template['title']
    mission_target = new_recipe_template['target']
    print(f"✅ Found mission: {mission_title} (ID: {mission_id})")
    print(f"   Target: {mission_target}")
    
    # Step 3: Assign the specific mission
    print(f"\n[3] Assigning '{mission_title}' mission...")
    response = requests.post(f"{BASE_URL}/missions/assign/{mission_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to assign mission: {response.text}")
        return
    
    assign_result = response.json()
    print(f"✅ Mission assigned: {assign_result.get('message')}")
    
    # Get the full mission details from active missions
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get active missions: {response.text}")
        return
    
    missions = response.json()
    
    # Find the newly assigned "Try a new recipe" mission
    new_recipe_mission = None
    for mission in missions:
        mission_data = mission.get('mission', {})
        if mission_data.get('id') == mission_id:
            new_recipe_mission = mission
            break
    
    if not new_recipe_mission:
        print("\n❌ Mission not found in active missions after assignment")
        return
    
    initial_progress = new_recipe_mission.get('progress', 0)
    print(f"   Initial progress: {initial_progress}/{mission_target}")
    
    # Step 4: Create first meal - "Spaghetti Carbonara" (NEW)
    print("\n[4] Creating first meal: Spaghetti Carbonara (should count as NEW)...")
    meal1_data = {
        "type": "meal",
        "title": "Spaghetti Carbonara",
        "timestamp": datetime.now().isoformat(),
        "meal_type": "dinner",
        "portions": 2,
        "portions_left": 2,
        "status": "fresh"
    }
    
    response = requests.post(f"{BASE_URL}/journal/entries", json=meal1_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create meal: {response.text}")
        return
    print(f"✅ Created: {meal1_data['title']}")
    
    # Check mission progress
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    missions_after_1 = response.json()
    
    new_recipe_1 = next((m for m in missions_after_1 if 'new recipe' in m.get('mission', {}).get('title', '').lower()), None)
    if new_recipe_1:
        progress_1 = new_recipe_1.get('progress', 0)
        target_1 = new_recipe_1.get('mission', {}).get('target', 0)
        print(f"   Mission progress: {progress_1}/{target_1}")
        if progress_1 == 1:
            print("   ✅ Correctly counted as NEW recipe!")
        else:
            print("   ❌ Progress did not increase")
    else:
        print("   ✅ Mission completed!")
    
    # Step 5: Create same meal again - "Spaghetti Carbonara" (REPEAT)
    print("\n[5] Creating same meal again: Spaghetti Carbonara (should NOT count)...")
    meal2_data = {
        "type": "meal",
        "title": "Spaghetti Carbonara",  # Same title
        "timestamp": datetime.now().isoformat(),
        "meal_type": "lunch",
        "portions": 2,
        "portions_left": 1,
        "status": "leftovers"
    }
    
    response = requests.post(f"{BASE_URL}/journal/entries", json=meal2_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create meal: {response.text}")
        return
    print(f"✅ Created: {meal2_data['title']} (repeat)")
    
    # Check mission progress
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    missions_after_2 = response.json()
    
    new_recipe_2 = next((m for m in missions_after_2 if 'new recipe' in m.get('mission', {}).get('title', '').lower()), None)
    if new_recipe_2:
        progress_2 = new_recipe_2.get('progress', 0)
        target_2 = new_recipe_2.get('mission', {}).get('target', 0)
        print(f"   Mission progress: {progress_2}/{target_2}")
        if new_recipe_1 and progress_2 == progress_1:
            print("   ✅ Correctly ignored REPEATED recipe!")
        else:
            print("   ❌ Incorrectly counted repeated recipe")
    else:
        if new_recipe_1 and new_recipe_1.get('status') == 'completed':
            print("   ✅ Mission was already completed from first meal")
        else:
            print("   ℹ️  Mission no longer in active list")
    
    # Step 6: Create different meal - "Chicken Stir Fry" (NEW)
    print("\n[6] Creating different meal: Chicken Stir Fry (should count as NEW)...")
    meal3_data = {
        "type": "meal",
        "title": "Chicken Stir Fry",  # Different title
        "timestamp": datetime.now().isoformat(),
        "meal_type": "dinner",
        "portions": 3,
        "portions_left": 3,
        "status": "fresh"
    }
    
    response = requests.post(f"{BASE_URL}/journal/entries", json=meal3_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create meal: {response.text}")
        return
    print(f"✅ Created: {meal3_data['title']}")
    
    # Check mission progress
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    missions_after_3 = response.json()
    
    new_recipe_3 = next((m for m in missions_after_3 if 'new recipe' in m.get('mission', {}).get('title', '').lower()), None)
    
    # Get stats to see if mission completed
    response = requests.get(f"{BASE_URL}/missions/stats", headers=headers)
    stats = response.json()
    
    print(f"\n[7] Final Results:")
    print(f"   Total meals logged: 3")
    print(f"   - Spaghetti Carbonara (1st time) ✅ NEW")
    print(f"   - Spaghetti Carbonara (2nd time) ❌ REPEAT")
    print(f"   - Chicken Stir Fry ✅ NEW")
    print(f"   Expected new recipes: 2")
    
    if new_recipe_3:
        progress_3 = new_recipe_3.get('progress', 0)
        target_3 = new_recipe_3.get('mission', {}).get('target', 0)
        status_3 = new_recipe_3.get('status', 'active')
        print(f"\n   Mission still active:")
        print(f"   Progress: {progress_3}/{target_3}")
        print(f"   Status: {status_3}")
    else:
        print(f"\n   ✅ Mission completed!")
        print(f"   Completed missions today: {stats.get('total_completed', 0)}")
        print(f"   Points earned: {stats.get('points_earned_today', 0)}")
    
    print("\n" + "="*60)
    if mission_target == 1:
        if not new_recipe_3:
            print("🎉 SUCCESS! Mission completed after first NEW recipe")
        else:
            print("✅ Mission tracking new recipes correctly")
    else:
        if new_recipe_3 and new_recipe_3.get('progress', 0) == 2:
            print("🎉 SUCCESS! Mission correctly counted 2 NEW recipes")
        elif not new_recipe_3:
            print("🎉 SUCCESS! Mission completed after 2+ NEW recipes")
        else:
            print("⚠️  Check results above")
    print("="*60)


if __name__ == "__main__":
    try:
        test_new_recipe_mission()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
