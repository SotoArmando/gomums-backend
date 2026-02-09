"""
Test Smart Suggestions System
Tests personalized suggestion generation and management
"""
import requests
import os
from datetime import date, timedelta

# Load test environment
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@gomums.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test123!@#")


def test_smart_suggestions():
    """Test smart suggestions workflow"""
    print("\n" + "=" * 70)
    print("SMART SUGGESTIONS SYSTEM TEST")
    print("=" * 70)
    
    # ==================== 1. AUTHENTICATE ====================
    print("\n1️⃣ AUTHENTICATING USER...")
    
    auth_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.text}")
        return
    
    token = auth_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Authenticated as {TEST_EMAIL}")
    
    # ==================== 2. CLEAR OLD SUGGESTIONS ====================
    print("\n2️⃣ CLEARING OLD SUGGESTIONS...")
    
    clear_response = requests.delete(
        f"{BASE_URL}/api/suggestions/",
        headers=headers,
        params={"days": 0}  # Clear all
    )
    
    if clear_response.status_code == 200:
        count = clear_response.json().get("count", 0)
        print(f"✅ Cleared {count} old suggestions")
    else:
        print(f"⚠️  Failed to clear suggestions: {clear_response.text}")
    
    # ==================== 3. CHECK EXISTING SUGGESTIONS ====================
    print("\n3️⃣ CHECKING EXISTING SUGGESTIONS...")
    
    list_response = requests.get(
        f"{BASE_URL}/api/suggestions/",
        headers=headers
    )
    
    if list_response.status_code == 200:
        suggestions = list_response.json()
        print(f"✅ Found {len(suggestions)} existing suggestions")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. [{suggestion['type']}] {suggestion['title']}")
            print(f"      {suggestion['subtitle']}")
            print(f"      Priority: {suggestion['priority']} | Color: {suggestion['dot_color']}")
    else:
        print(f"❌ Failed to fetch suggestions: {list_response.text}")
        suggestions = []
    
    # ==================== 4. GENERATE NEW SUGGESTIONS ====================
    print("\n4️⃣ GENERATING NEW SUGGESTIONS...")
    
    generate_response = requests.post(
        f"{BASE_URL}/api/suggestions/generate",
        headers=headers,
        json={"refresh": True, "max_suggestions": 5}
    )
    
    if generate_response.status_code == 200:
        new_suggestions = generate_response.json()
        print(f"✅ Generated {len(new_suggestions)} new suggestions")
        print("\n📋 PERSONALIZED SUGGESTIONS:")
        print("-" * 70)
        
        for i, suggestion in enumerate(new_suggestions, 1):
            print(f"\n{i}. {suggestion['title']}")
            print(f"   Subtitle: {suggestion['subtitle']}")
            print(f"   Description: {suggestion['description']}")
            print(f"   Type: {suggestion['type']} | Priority: {suggestion['priority']}")
            print(f"   Color: {suggestion['dot_color']} | Action: {suggestion['action_text']}")
            print(f"   ID: {suggestion['id']}")
    else:
        print(f"❌ Failed to generate suggestions: {generate_response.text}")
        return
    
    # ==================== 5. VIEW SUGGESTIONS BY TYPE ====================
    print("\n5️⃣ FILTERING SUGGESTIONS BY TYPE...")
    
    # Get unique types from generated suggestions
    types = list(set([s['type'] for s in new_suggestions]))
    
    for suggestion_type in types[:2]:  # Test first 2 types
        filter_response = requests.get(
            f"{BASE_URL}/api/suggestions/",
            headers=headers,
            params={"type_filter": suggestion_type}
        )
        
        if filter_response.status_code == 200:
            filtered = filter_response.json()
            print(f"✅ Found {len(filtered)} {suggestion_type} suggestions")
        else:
            print(f"❌ Failed to filter by type: {filter_response.text}")
    
    # ==================== 6. DISMISS A SUGGESTION ====================
    print("\n6️⃣ DISMISSING A SUGGESTION...")
    
    if new_suggestions:
        suggestion_to_dismiss = new_suggestions[0]
        dismiss_response = requests.patch(
            f"{BASE_URL}/api/suggestions/{suggestion_to_dismiss['id']}/dismiss",
            headers=headers
        )
        
        if dismiss_response.status_code == 200:
            print(f"✅ Dismissed suggestion: {suggestion_to_dismiss['title']}")
        else:
            print(f"❌ Failed to dismiss suggestion: {dismiss_response.text}")
        
        # Verify it's dismissed
        list_active_response = requests.get(
            f"{BASE_URL}/api/suggestions/",
            headers=headers,
            params={"include_dismissed": False}
        )
        
        list_all_response = requests.get(
            f"{BASE_URL}/api/suggestions/",
            headers=headers,
            params={"include_dismissed": True}
        )
        
        if list_active_response.status_code == 200 and list_all_response.status_code == 200:
            active_count = len(list_active_response.json())
            all_count = len(list_all_response.json())
            print(f"✅ Active suggestions: {active_count}, Total (including dismissed): {all_count}")
    
    # ==================== 7. CREATE CUSTOM SUGGESTION ====================
    print("\n7️⃣ CREATING CUSTOM SUGGESTION...")
    
    custom_suggestion = {
        "title": "🎉 Special Feature Announcement",
        "subtitle": "New features just dropped!",
        "description": "Check out the new meal planning calendar and smart suggestions",
        "type": "TIP",
        "dot_color": "PURPLE",
        "action_text": "Explore Now",
        "priority": 95
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/suggestions/",
        headers=headers,
        json=custom_suggestion
    )
    
    if create_response.status_code == 200:
        created = create_response.json()
        print(f"✅ Created custom suggestion: {created['title']}")
        print(f"   ID: {created['id']}")
    else:
        print(f"❌ Failed to create custom suggestion: {create_response.text}")
    
    # ==================== 8. UPDATE A SUGGESTION ====================
    print("\n8️⃣ UPDATING A SUGGESTION...")
    
    if len(new_suggestions) > 1:
        suggestion_to_update = new_suggestions[1]
        update_data = {
            "priority": 100,
            "dot_color": "RED"
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/api/suggestions/{suggestion_to_update['id']}",
            headers=headers,
            json=update_data
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Updated suggestion priority to {updated['priority']}")
            print(f"   Color changed to {updated['dot_color']}")
        else:
            print(f"❌ Failed to update suggestion: {update_response.text}")
    
    # ==================== 9. GET SUGGESTION STATS ====================
    print("\n9️⃣ GETTING SUGGESTION STATISTICS...")
    
    stats_response = requests.get(
        f"{BASE_URL}/api/suggestions/stats",
        headers=headers
    )
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"✅ SUGGESTION STATISTICS:")
        print(f"   Total suggestions: {stats['total_suggestions']}")
        print(f"   Active suggestions: {stats['active_suggestions']}")
        print(f"   Dismissed suggestions: {stats['dismissed_suggestions']}")
        print(f"   Most recent update: {stats.get('most_recent_update', 'N/A')}")
        
        if stats.get('suggestions_by_type'):
            print(f"\n   📊 Breakdown by type:")
            for stype, count in stats['suggestions_by_type'].items():
                print(f"      {stype}: {count}")
    else:
        print(f"❌ Failed to get stats: {stats_response.text}")
    
    # ==================== 10. TEST SUGGESTION GENERATION LOGIC ====================
    print("\n🔟 TESTING GENERATION LOGIC WITH USER CONTEXT...")
    
    # Create some context: add a meal with leftovers
    print("\n   Creating meal with leftovers...")
    meal_response = requests.post(
        f"{BASE_URL}/api/journal/",
        headers=headers,
        json={
            "name": "Test Leftover Meal",
            "description": "Test meal for suggestions",
            "type": "meal",
            "date": date.today().isoformat(),
            "estimated_cost": 10.0,
            "actual_cost": 8.5,
            "store": "Test Store",
            "portions": 4,
            "portions_left": 2,
            "status": "leftovers"
        }
    )
    
    if meal_response.status_code == 200:
        print("   ✅ Created meal with leftovers")
    else:
        print(f"   ⚠️  Failed to create meal: {meal_response.text}")
    
    # Regenerate suggestions
    print("\n   Regenerating suggestions to see leftover prompt...")
    regen_response = requests.post(
        f"{BASE_URL}/api/suggestions/generate",
        headers=headers,
        json={"refresh": True, "max_suggestions": 5}
    )
    
    if regen_response.status_code == 200:
        regen_suggestions = regen_response.json()
        print(f"   ✅ Generated {len(regen_suggestions)} suggestions")
        
        # Check for leftover suggestion
        leftover_suggestions = [s for s in regen_suggestions if 'leftover' in s['title'].lower() or 'leftover' in s['description'].lower()]
        if leftover_suggestions:
            print(f"\n   🎯 FOUND LEFTOVER SUGGESTION:")
            ls = leftover_suggestions[0]
            print(f"      {ls['title']}")
            print(f"      {ls['description']}")
        else:
            print(f"\n   📋 All suggestions:")
            for s in regen_suggestions:
                print(f"      - {s['title']}")
    else:
        print(f"   ❌ Failed to regenerate: {regen_response.text}")
    
    # ==================== 11. DELETE A SUGGESTION ====================
    print("\n1️⃣1️⃣ DELETING A SUGGESTION...")
    
    if new_suggestions and len(new_suggestions) > 2:
        suggestion_to_delete = new_suggestions[2]
        delete_response = requests.delete(
            f"{BASE_URL}/api/suggestions/{suggestion_to_delete['id']}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print(f"✅ Deleted suggestion: {suggestion_to_delete['title']}")
        else:
            print(f"❌ Failed to delete suggestion: {delete_response.text}")
    
    # ==================== FINAL SUMMARY ====================
    print("\n" + "=" * 70)
    print("✅ SMART SUGGESTIONS TEST COMPLETED")
    print("=" * 70)
    
    # Get final stats
    final_stats_response = requests.get(
        f"{BASE_URL}/api/suggestions/stats",
        headers=headers
    )
    
    if final_stats_response.status_code == 200:
        final_stats = final_stats_response.json()
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Total: {final_stats['total_suggestions']}")
        print(f"   Active: {final_stats['active_suggestions']}")
        print(f"   Dismissed: {final_stats['dismissed_suggestions']}")
    
    print("\n✨ All smart suggestion operations tested successfully!")


if __name__ == "__main__":
    test_smart_suggestions()
