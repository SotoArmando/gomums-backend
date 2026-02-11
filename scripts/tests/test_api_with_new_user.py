"""
Register test user and verify API descriptions
"""
import requests

BASE_URL = "http://localhost:8000"

try:
    print("\n" + "="*70)
    print("Setting up test user and verifying API")
    print("="*70 + "\n")
    
    # Try to register a new test user
    print("1️⃣  Creating test user...")
    register_data = {
        "name": "Recipe Tester",
        "email": "testrecipes@gomums.com",
        "password": "test123456"
    }
    
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    
    if register_response.status_code == 200:
        print("✅ Test user created successfully\n")
    elif register_response.status_code == 400 and "already registered" in register_response.text.lower():
        print("ℹ️  Test user already exists, proceeding to login\n")
    else:
        print(f"⚠️  Registration status: {register_response.status_code}")
        print(f"    {register_response.text[:100]}\n")
    
    # Login
    print("2️⃣  Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "testrecipes@gomums.com",
            "password": "test123456"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        exit(1)
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully\n")
    
    # Get recipes with steps
    print("3️⃣  Testing /api/recipes/with-steps endpoint...")
    print("-"*70)
    
    response = requests.get(f"{BASE_URL}/api/recipes/with-steps", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        exit(1)
    
    recipes = response.json()
    print(f"✅ Retrieved {len(recipes)} recipes\n")
    
    # Check each recipe
    print("📋 Recipe Details:")
    print("-"*70)
    
    for i, recipe in enumerate(recipes, 1):
        description = recipe.get('description')
        has_desc = "✅" if description else "❌"
        
        print(f"\n{i}. {recipe['name']}")
        print(f"   Description: {has_desc}")
        if description:
            print(f"   Preview: {description[:80]}...")
        print(f"   Image: {'✅' if recipe.get('image') else '❌'}")
        print(f"   Nutrition: {'✅' if recipe.get('nutrition', {}).get('calories') else '❌'}")
        print(f"   Steps: {len(recipe.get('steps', []))} steps")
    
    # Summary
    has_description = sum(1 for r in recipes if r.get('description'))
    
    print("\n" + "="*70)
    print(f"📊 RESULTS: {has_description}/{len(recipes)} recipes have descriptions")
    print("="*70)
    
    if has_description == len(recipes):
        print("\n✨ SUCCESS! All recipes now include descriptions in the API!")
        print("   The fix is working correctly! 🎉\n")
    else:
        missing = len(recipes) - has_description
        print(f"\n⚠️  WARNING: {missing} recipe(s) still missing descriptions")
        print("   The server may need to be restarted to pick up code changes.\n")
    
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to server.")
    print("   Make sure FastAPI is running on http://localhost:8000")
    print("   Run: python -m uvicorn app.main:app --reload\n")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
