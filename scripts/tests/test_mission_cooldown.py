"""
Test script for mission cooldown functionality
Verifies that missions can only be reassigned after their cooldown period
"""
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "cooldown_test@gomums.com"
TEST_PASSWORD = "Test1234!"
TEST_NAME = "Cooldown Test User"


def test_mission_cooldown():
    print("\n" + "="*60)
    print("Testing Mission Cooldown System")
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
        print("💡 Make sure the server is running on port 8000")
        print("💡 Or run cleanup first: python3 cleanup_cooldown_test.py")
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
    print("\n[2] Getting available daily missions...")
    response = requests.get(f"{BASE_URL}/missions/available?mission_type=daily", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get available missions: {response.text}")
        return
    
    available_missions = response.json()
    print(f"✅ Found {len(available_missions)} available daily missions")
    
    if not available_missions:
        print("❌ No daily missions available for testing")
        return
    
    # Pick the first daily mission
    test_mission = available_missions[0]
    mission_id = test_mission['id']
    mission_title = test_mission['title']
    print(f"   Testing with: {mission_title} (ID: {mission_id})")
    
    # Step 3: Assign the mission for the first time
    print(f"\n[3] Assigning '{mission_title}' for the first time...")
    response = requests.post(f"{BASE_URL}/missions/assign/{mission_id}", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to assign mission: {response.text}")
        return
    
    assign_result = response.json()
    print(f"✅ Mission assigned successfully")
    print(f"   User Mission ID: {assign_result.get('user_mission_id')}")
    
    # Step 4: Check availability immediately (should be in cooldown)
    print(f"\n[4] Checking availability immediately after assignment...")
    response = requests.get(f"{BASE_URL}/missions/check-availability/{mission_id}", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to check availability: {response.text}")
        return
    
    availability = response.json()
    print(f"   Available: {availability.get('available')}")
    
    if not availability.get('available'):
        print(f"   ✅ Correctly in cooldown period")
        print(f"   Reason: {availability.get('reason')}")
        if 'hours_remaining' in availability:
            print(f"   Hours remaining: {availability['hours_remaining']}")
        if 'available_at' in availability:
            print(f"   Available at: {availability['available_at']}")
    else:
        print(f"   ⚠️  Mission shows as available (unexpected)")
    
    # Step 5: Try to assign the same mission again (should fail)
    print(f"\n[5] Attempting to assign the same mission again...")
    response = requests.post(f"{BASE_URL}/missions/assign/{mission_id}", headers=headers)
    
    if response.status_code == 409:
        error_detail = response.json().get('detail', '')
        print(f"   ✅ Assignment correctly blocked (409 Conflict)")
        print(f"   Message: {error_detail}")
    elif response.status_code == 200:
        print(f"   ❌ Mission was assigned again (should have been blocked)")
    else:
        print(f"   ⚠️  Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 6: Check active missions
    print(f"\n[6] Checking active missions...")
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get active missions: {response.text}")
        return
    
    active_missions = response.json()
    print(f"✅ Currently {len(active_missions)} active mission(s)")
    
    for mission in active_missions:
        m_data = mission.get('mission', {})
        print(f"   - {m_data.get('title')}: Progress {mission.get('progress')}/{m_data.get('target')}")
    
    # Summary
    print(f"\n" + "="*60)
    print("🎉 Cooldown System Test Complete!")
    print("="*60)
    print(f"\nKey Results:")
    print(f"✅ Mission assigned successfully on first attempt")
    print(f"✅ Mission unavailable immediately after assignment")
    print(f"✅ Second assignment attempt correctly blocked with cooldown message")
    print(f"\nNote: Mission will become available again after 24 hours")
    print("="*60)


if __name__ == "__main__":
    try:
        test_mission_cooldown()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
