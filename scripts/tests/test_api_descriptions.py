"""
Quick test to verify recipe descriptions are returned in API
"""
import requests
import json

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
    print("✅ Logged in\n")
    
    # Get recipes with steps
    print("="*70)
    print("Testing /api/recipes/with-steps - Description Field")
    print("="*70 + "\n")
    
    response = requests.get(f"{BASE_URL}/api/recipes/with-steps", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        exit(1)
    
    recipes = response.json()
    print(f"✅ Retrieved {len(recipes)} recipes\n")
    
    # Check first 3 recipes
    for i, recipe in enumerate(recipes[:3], 1):
        print(f"{i}. {recipe['name']}")
        
        description = recipe.get('description')
        if description:
            print(f"   ✅ Description: {description[:80]}...")
        else:
            print(f"   ❌ Description: NULL")
        
        print(f"   Image: {recipe.get('image', 'N/A')[:50]}...")
        print(f"   Steps: {len(recipe.get('steps', []))} steps")
        print(f"   Nutrition: {recipe.get('nutrition', {}).get('calories')} cal\n")
    
    # Summary
    has_description = sum(1 for r in recipes if r.get('description'))
    print("="*70)
    print(f"📊 Summary: {has_description}/{len(recipes)} recipes have descriptions")
    
    if has_description == len(recipes):
        print("✨ SUCCESS! All recipes now have descriptions in the API!")
    else:
        print(f"⚠️  {len(recipes) - has_description} recipes still missing descriptions")
    print("="*70 + "\n")
    
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server. Is it running on http://localhost:8000?")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
