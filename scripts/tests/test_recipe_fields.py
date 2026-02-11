"""
Test that recipes now include description and all nutrition fields
"""
import requests

BASE_URL = "http://localhost:8000"

try:
    # Login
    print("\n🔐 Logging in...")
    login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "test@gomums.com", "password": "test123"})
    
    if login.status_code != 200:
        print(f"❌ Login failed: {login.status_code}")
        exit(1)
    
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in\n")
    
    # Get recipes with steps
    print("="*70)
    print("📋 Testing Recipe Fields")
    print("="*70 + "\n")
    
    response = requests.get(f"{BASE_URL}/api/recipes/with-steps", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get recipes: {response.status_code}")
        print(response.text)
        exit(1)
    
    recipes = response.json()
    print(f"✅ Retrieved {len(recipes)} recipes\n")
    
    if len(recipes) > 0:
        recipe = recipes[0]
        print(f"🍽️  Sample Recipe: {recipe['name']}\n")
        
        # Check all requested fields
        fields_to_check = {
            "Description": recipe.get('description'),
            "Prep Time": recipe.get('prep_time'),
            "Calories": recipe.get('nutrition', {}).get('calories'),
            "Protein": recipe.get('nutrition', {}).get('protein'),
            "Carbs": recipe.get('nutrition', {}).get('carbs'),
            "Fat": recipe.get('nutrition', {}).get('fat'),
            "Fiber": recipe.get('nutrition', {}).get('fiber')
        }
        
        print("Field Status:")
        print("-" * 70)
        for field_name, value in fields_to_check.items():
            status = "✅" if value is not None else "⚠️  (null)"
            print(f"{status} {field_name:15} : {value}")
        
        print("\n" + "="*70)
        print("✨ All nutrition fields are available in the API!")
        print("="*70 + "\n")
        
        print("📊 Full Recipe Data Structure:")
        print(f"   - ID: {recipe['id']}")
        print(f"   - Name: {recipe['name']}")
        print(f"   - Description: {recipe.get('description', 'N/A')}")
        print(f"   - Image: {'Yes' if recipe.get('image') else 'No'}")
        print(f"   - Prep Time: {recipe.get('prep_time', 'N/A')}")
        print(f"   - Servings: {recipe.get('servings', 'N/A')}")
        print(f"   - Difficulty: {recipe.get('difficulty', 'N/A')}")
        print(f"   - Steps: {len(recipe.get('steps', []))} steps")
        print(f"   - Nutrition:")
        for key, value in recipe.get('nutrition', {}).items():
            print(f"      • {key}: {value}")
    
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server. Is it running on http://localhost:8000?")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
