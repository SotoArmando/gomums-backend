"""
Quick test to verify Step-by-Step Recipes section is accessible
"""
import requests

BASE_URL = "http://localhost:8000"

try:
    # Login
    print("\n🔐 Logging in...")
    login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "test@gomums.com", "password": "test123"})
    
    if login.status_code != 200:
        print(f"❌ Login failed: {login.status_code}")
        print(login.text)
        exit(1)
    
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully\n")
    
    # Get home sections
    print("="*70)
    print("🏠 Home Sections")
    print("="*70 + "\n")
    
    sections = requests.get(f"{BASE_URL}/api/home-sections/", headers=headers, params={"include_global": True}).json()
    
    print(f"Found {len(sections)} sections:\n")
    
    found_steps = False
    for section in sections:
        scope = "🌍 Global" if not section.get("user_id") else "👤 User"
        print(f"[{section['order_index']}] {scope} - {section['title']}")
        if section['title'] == "Step-by-Step Recipes":
            found_steps = True
            print(f"    ✅ This section uses: /api/recipes/with-steps")
            print(f"    📊 Filter: {section['data'].get('filter')}")
            print(f"    📱 Layout: {section['data'].get('layout')}")
            print(f"    🔢 Limit: {section['data'].get('limit')} recipes")
    
    print("\n" + "="*70)
    if found_steps:
        print("✨ YES! 'Step-by-Step Recipes' is ALREADY on your home page!")
    else:
        print("❌ 'Step-by-Step Recipes' section not found")
    print("="*70 + "\n")
    
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server. Is it running on http://localhost:8000?")
except Exception as e:
    print(f"❌ Error: {e}")
