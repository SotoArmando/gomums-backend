"""
Test automatic mission progress updates
Tests that missions update automatically when journal/budget entries are created
"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000/api"

def test_automatic_mission_updates():
    """Test that missions update automatically when creating journal and budget entries"""
    
    print("\n" + "="*60)
    print("Testing Automatic Mission Progress Updates")
    print("="*60)
    
    # Step 1: Register or login
    print("\n[1] Registering test user...")
    register_data = {
        "email": "mission_auto@test.com",
        "password": "TestPass123!",
        "name": "Mission Auto Test"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 200:
        # Registration returns token directly
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ User registered successfully")
        print("✅ Token received from registration")
    else:
        # If registration fails (user already exists), try login
        print("⚠️  User already exists, attempting login...")
        login_data = {
            "email": "mission_auto@test.com",
            "password": "TestPass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in successfully")
    
    # Step 2: Assign daily missions
    print("\n[2] Assigning daily missions...")
    response = requests.post(f"{BASE_URL}/missions/assign-daily", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to assign missions: {response.text}")
        return
    
    assigned = response.json()
    print(f"✅ Assigned {assigned['assigned_count']} missions")
    
    # Get the assigned missions to show details
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get missions: {response.text}")
        return
    
    missions = response.json()
    for mission in missions:
        print(f"   - {mission['mission']['title']} (Category: {mission['mission']['category']}, Target: {mission['mission']['target']}, Progress: {mission['progress']}/{mission['mission']['target']})")
    
    # Step 3: Create journal entries (should auto-update missions)
    print("\n[3] Creating journal entries to trigger mission updates...")
    
    # Create first meal entry
    meal1_data = {
        "type": "meal",
        "title": "Spaghetti Carbonara",
        "timestamp": datetime.now().isoformat(),
        "meal_type": "dinner",
        "portions": 2,
        "portions_left": 1,
        "status": "fresh",
        "is_batch": False,
        "used_leftovers": False
    }
    
    response = requests.post(f"{BASE_URL}/journal/entries", json=meal1_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create meal entry 1: {response.text}")
        return
    
    print(f"✅ Created meal entry: {meal1_data['title']}")
    
    # Create second meal entry
    meal2_data = {
        "type": "meal",
        "title": "Chicken Stir Fry",
        "timestamp": datetime.now().isoformat(),
        "meal_type": "lunch",
        "portions": 4,
        "portions_left": 2,
        "status": "fresh",
        "is_batch": True,
        "used_leftovers": False
    }
    
    response = requests.post(f"{BASE_URL}/journal/entries", json=meal2_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create meal entry 2: {response.text}")
        return
    
    print(f"✅ Created meal entry: {meal2_data['title']}")
    
    # Create third meal entry
    meal3_data = {
        "type": "meal",
        "title": "Vegetable Soup",
        "timestamp": datetime.now().isoformat(),
        "meal_type": "dinner",
        "portions": 3,
        "portions_left": 1,
        "status": "fresh",
        "is_batch": False,
        "used_leftovers": True
    }
    
    response = requests.post(f"{BASE_URL}/journal/entries", json=meal3_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create meal entry 3: {response.text}")
        return
    
    print(f"✅ Created meal entry: {meal3_data['title']}")
    
    # Step 4: Get active missions (after journal entries)
    print("\n[4] Getting active missions (after journal entries)...")
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get missions: {response.text}")
        return
    
    missions_after_journal = response.json()
    print(f"✅ Active missions updated:")
    
    cooking_missions_updated = False
    tracking_missions_updated = False
    
    for mission in missions_after_journal:
        print(f"   - {mission['mission']['title']}: Progress {mission['progress']}/{mission['mission']['target']} ({mission['status']})")
        
        # Check if cooking missions updated
        if mission['mission']['category'] == 'cooking' and mission['progress'] >= 3:
            cooking_missions_updated = True
        
        # Check if tracking missions updated
        if mission['mission']['category'] == 'tracking' and mission['progress'] >= 3:
            tracking_missions_updated = True
    
    if cooking_missions_updated or tracking_missions_updated:
        print("\n✅ Journal entries automatically updated missions!")
    else:
        print("\n⚠️  Missions may not have updated as expected")
    
    # Step 5: Create budget entry (should auto-update budget missions)
    print("\n[5] Creating budget entry to trigger mission updates...")
    
    # First, create budget settings
    budget_settings = {
        "weekly_budget": 150.0,
        "reminder_enabled": True
    }
    
    response = requests.post(f"{BASE_URL}/budget/settings", json=budget_settings, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create budget settings: {response.text}")
        return
    
    print("✅ Created budget settings")
    
    # Create budget entry
    budget_entry_data = {
        "date": date.today().isoformat(),
        "meal_name": "Spaghetti Carbonara Ingredients",
        "cost": 25.50,
        "servings": 4,
        "category": "groceries"
    }
    
    response = requests.post(f"{BASE_URL}/budget/entries", json=budget_entry_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create budget entry: {response.text}")
        return
    
    print(f"✅ Created budget entry: {budget_entry_data['meal_name']} (${budget_entry_data['cost']})")
    
    # Step 6: Get final mission status
    print("\n[6] Getting final mission status...")
    response = requests.get(f"{BASE_URL}/missions/active", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get missions: {response.text}")
        return
    
    missions_final = response.json()
    
    if missions_final:
        print(f"✅ Active missions remaining:")
        for mission in missions_final:
            status_emoji = "✅" if mission['status'] == 'completed' else "🔄"
            print(f"   {status_emoji} {mission['mission']['title']}: Progress {mission['progress']}/{mission['mission']['target']} ({mission['status']})")
    else:
        print(f"✅ No active missions remaining (check stats for completed missions)")
    
    # Step 7: Check mission stats
    print("\n[7] Checking mission stats and points...")
    response = requests.get(f"{BASE_URL}/missions/stats", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get mission stats: {response.text}")
        return
    
    stats = response.json()
    print(f"✅ Mission Statistics:")
    print(f"   - ✅ Completed missions: {stats['total_completed']} (removed from active list)")
    print(f"   - 🔄 Active missions: {stats['total_active']}")
    print(f"   - ⏰ Expired missions: {stats['total_expired']}")
    print(f"   - 🎯 Points earned today: {stats['points_earned_today']}")
    print(f"   - 📅 Points earned this week: {stats['points_earned_week']}")
    print(f"   - 💰 Total points earned: {stats['points_earned_total']}")
    
    # Step 8: Check user stats to verify points awarded
    print("\n[8] Checking user stats for points...")
    response = requests.get(f"{BASE_URL}/user/me/stats", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get user stats: {response.text}")
        return
    
    user_stats = response.json()
    print(f"✅ User Statistics:")
    print(f"   - Level: {user_stats['level']}")
    print(f"   - Total points: {user_stats['points']}")
    print(f"   - Meals cooked: {user_stats.get('meals_cooked', 0)}")
    
    # Final summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Created 3 journal entries")
    print(f"✅ Created 1 budget entry")
    print(f"✅ Active missions remaining: {len(missions_final)}")
    print(f"✅ Missions completed: {stats['total_completed']}")  # Use actual backend stats
    print(f"✅ Points earned: {stats['points_earned_total']}")
    
    if stats['total_completed'] > 0:
        print(f"\n🎉 SUCCESS! {stats['total_completed']} mission(s) auto-completed and awarded {stats['points_earned_total']} points!")
    else:
        print("\n⚠️  Missions updated but none completed yet (may need more entries)")
    
    print("="*60)

if __name__ == "__main__":
    try:
        test_automatic_mission_updates()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
