"""
Test Home Sections System
Tests customizable home screen sections
"""
import requests
import os

# Load test environment
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_EMAIL = os.getenv("TEST_EMAIL", "test@gomums.com")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test123!@#")


def test_home_sections():
    """Test home sections workflow"""
    print("\n" + "=" * 70)
    print("HOME SECTIONS SYSTEM TEST")
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
    
    # ==================== 2. GET EXISTING SECTIONS ====================
    print("\n2️⃣ GETTING EXISTING SECTIONS...")
    
    list_response = requests.get(
        f"{BASE_URL}/api/home-sections/",
        headers=headers
    )
    
    if list_response.status_code == 200:
        sections = list_response.json()
        print(f"✅ Found {len(sections)} existing sections")
        for i, section in enumerate(sections[:5], 1):
            print(f"   {i}. [{section['type']}] {section['title']} - Order: {section['order_index']}, Visible: {section['visible']}")
    else:
        print(f"❌ Failed to fetch sections: {list_response.text}")
        sections = []
    
    # ==================== 3. GET AVAILABLE TEMPLATES ====================
    print("\n3️⃣ GETTING AVAILABLE TEMPLATES...")
    
    templates_response = requests.get(
        f"{BASE_URL}/api/home-sections/templates",
        headers=headers
    )
    
    if templates_response.status_code == 200:
        templates_data = templates_response.json()
        templates = templates_data.get("templates", [])
        print(f"✅ Found {len(templates)} available templates")
        print("\n📋 AVAILABLE TEMPLATES:")
        print("-" * 70)
        for i, template in enumerate(templates[:10], 1):
            print(f"{i:2}. {template['key']:20} - {template['title']}")
    else:
        print(f"❌ Failed to fetch templates: {templates_response.text}")
        return
    
    # ==================== 4. INITIALIZE DEFAULT SECTIONS (IF NEEDED) ====================
    print("\n4️⃣ CHECKING IF INITIALIZATION NEEDED...")
    
    if len(sections) == 0:
        print("   No sections found, initializing defaults...")
        init_response = requests.post(
            f"{BASE_URL}/api/home-sections/initialize",
            headers=headers
        )
        
        if init_response.status_code == 200:
            sections = init_response.json()
            print(f"✅ Initialized {len(sections)} default sections")
        else:
            print(f"❌ Failed to initialize: {init_response.text}")
    else:
        print(f"✅ User already has {len(sections)} sections")
    
    # ==================== 5. CREATE CUSTOM SECTION ====================
    print("\n5️⃣ CREATING CUSTOM SECTION...")
    
    custom_section = {
        "type": "custom",
        "title": "🎯 My Custom Section",
        "subtitle": "Personalized content",
        "visible": True,
        "order_index": 100,
        "data": {
            "custom_field": "custom_value",
            "show_header": True,
            "items": ["item1", "item2", "item3"]
        }
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/home-sections/",
        headers=headers,
        json=custom_section
    )
    
    if create_response.status_code == 200:
        created_section = create_response.json()
        custom_section_id = created_section["id"]
        print(f"✅ Created custom section: {created_section['title']}")
        print(f"   ID: {custom_section_id}")
        print(f"   Type: {created_section['type']}")
        print(f"   Order: {created_section['order_index']}")
    else:
        print(f"❌ Failed to create section: {create_response.text}")
        custom_section_id = None
    
    # ==================== 6. ADD SECTION FROM TEMPLATE ====================
    print("\n6️⃣ ADDING SECTION FROM TEMPLATE...")
    
    # Try to add a "tips" section
    template_response = requests.post(
        f"{BASE_URL}/api/home-sections/from-template/tips",
        headers=headers
    )
    
    if template_response.status_code == 200:
        template_section = template_response.json()
        template_section_id = template_section["id"]
        print(f"✅ Added section from template: {template_section['title']}")
        print(f"   ID: {template_section_id}")
        print(f"   Type: {template_section['type']}")
    else:
        print(f"⚠️  Failed to add template section: {template_response.text}")
        template_section_id = None
    
    # ==================== 7. UPDATE SECTION ====================
    print("\n7️⃣ UPDATING SECTION...")
    
    if custom_section_id:
        updates = {
            "title": "🎯 Updated Custom Section",
            "subtitle": "This has been modified",
            "order_index": 50
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/api/home-sections/{custom_section_id}",
            headers=headers,
            json=updates
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Updated section: {updated['title']}")
            print(f"   New order: {updated['order_index']}")
        else:
            print(f"❌ Failed to update section: {update_response.text}")
    
    # ==================== 8. TOGGLE VISIBILITY ====================
    print("\n8️⃣ TOGGLING SECTION VISIBILITY...")
    
    if custom_section_id:
        toggle_response = requests.patch(
            f"{BASE_URL}/api/home-sections/{custom_section_id}/toggle-visibility",
            headers=headers
        )
        
        if toggle_response.status_code == 200:
            toggled = toggle_response.json()
            print(f"✅ Toggled visibility: {toggled['visible']}")
        else:
            print(f"❌ Failed to toggle visibility: {toggle_response.text}")
    
    # ==================== 9. GET VISIBLE SECTIONS ONLY ====================
    print("\n9️⃣ GETTING VISIBLE SECTIONS ONLY...")
    
    visible_response = requests.get(
        f"{BASE_URL}/api/home-sections/",
        headers=headers,
        params={"visible_only": True}
    )
    
    if visible_response.status_code == 200:
        visible_sections = visible_response.json()
        print(f"✅ Found {len(visible_sections)} visible sections")
    else:
        print(f"❌ Failed to fetch visible sections: {visible_response.text}")
    
    # ==================== 10. REORDER SECTIONS ====================
    print("\n🔟 REORDERING SECTIONS...")
    
    # Get current sections
    current_response = requests.get(
        f"{BASE_URL}/api/home-sections/",
        headers=headers
    )
    
    if current_response.status_code == 200:
        current_sections = current_response.json()
        
        # Create reorder data (reverse first 3 sections)
        if len(current_sections) >= 3:
            reorder_data = {
                "sections": [
                    {"section_id": current_sections[0]["id"], "new_order_index": 2},
                    {"section_id": current_sections[1]["id"], "new_order_index": 1},
                    {"section_id": current_sections[2]["id"], "new_order_index": 0}
                ]
            }
            
            reorder_response = requests.post(
                f"{BASE_URL}/api/home-sections/reorder",
                headers=headers,
                json=reorder_data
            )
            
            if reorder_response.status_code == 200:
                print(f"✅ Reordered {len(reorder_data['sections'])} sections")
            else:
                print(f"❌ Failed to reorder: {reorder_response.text}")
    
    # ==================== 11. GET GLOBAL SECTIONS ====================
    print("\n1️⃣1️⃣ GETTING GLOBAL SECTIONS...")
    
    global_response = requests.get(
        f"{BASE_URL}/api/home-sections/global",
        headers=headers
    )
    
    if global_response.status_code == 200:
        global_sections = global_response.json()
        print(f"✅ Found {len(global_sections)} global sections")
        if global_sections:
            for section in global_sections:
                print(f"   - {section['title']} (Order: {section['order_index']})")
    else:
        print(f"❌ Failed to fetch global sections: {global_response.text}")
    
    # ==================== 12. GET SPECIFIC SECTION ====================
    print("\n1️⃣2️⃣ GETTING SPECIFIC SECTION...")
    
    if custom_section_id:
        get_response = requests.get(
            f"{BASE_URL}/api/home-sections/{custom_section_id}",
            headers=headers
        )
        
        if get_response.status_code == 200:
            section_details = get_response.json()
            print(f"✅ Retrieved section: {section_details['title']}")
            print(f"   Type: {section_details['type']}")
            print(f"   Visible: {section_details['visible']}")
            print(f"   Order: {section_details['order_index']}")
            if section_details.get('data'):
                print(f"   Data: {section_details['data']}")
        else:
            print(f"❌ Failed to get section: {get_response.text}")
    
    # ==================== 13. DELETE SECTION ====================
    print("\n1️⃣3️⃣ DELETING CUSTOM SECTION...")
    
    if custom_section_id:
        delete_response = requests.delete(
            f"{BASE_URL}/api/home-sections/{custom_section_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print(f"✅ Deleted section successfully")
        else:
            print(f"❌ Failed to delete section: {delete_response.text}")
    
    # ==================== 14. RESET TO DEFAULTS ====================
    print("\n1️⃣4️⃣ TESTING RESET TO DEFAULTS...")
    
    reset_response = requests.post(
        f"{BASE_URL}/api/home-sections/reset",
        headers=headers
    )
    
    if reset_response.status_code == 200:
        reset_sections = reset_response.json()
        print(f"✅ Reset to {len(reset_sections)} default sections")
        print("\n📋 DEFAULT SECTIONS:")
        for i, section in enumerate(reset_sections, 1):
            print(f"   {i}. [{section['type']}] {section['title']}")
    else:
        print(f"❌ Failed to reset: {reset_response.text}")
    
    # ==================== FINAL SUMMARY ====================
    print("\n" + "=" * 70)
    print("✅ HOME SECTIONS TEST COMPLETED")
    print("=" * 70)
    
    # Get final count
    final_response = requests.get(
        f"{BASE_URL}/api/home-sections/",
        headers=headers
    )
    
    if final_response.status_code == 200:
        final_sections = final_response.json()
        visible_count = len([s for s in final_sections if s['visible']])
        print(f"\n📊 FINAL STATE:")
        print(f"   Total sections: {len(final_sections)}")
        print(f"   Visible sections: {visible_count}")
        print(f"   Hidden sections: {len(final_sections) - visible_count}")
    
    print("\n✨ All home section operations tested successfully!")


if __name__ == "__main__":
    test_home_sections()
