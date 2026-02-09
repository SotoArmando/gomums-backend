"""
Test script for Journal API endpoints
Run after server is started and authenticated
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        print(response.text if response.text else "No content")
    print()

def main():
    print_section("🧪 Testing Journal API Endpoints")
    
    # First, authenticate to get a token
    print_section("0️⃣  Authentication")
    test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    
    auth_response = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Journal Test User",
        "email": test_email,
        "password": "testpass123"
    })
    
    if auth_response.status_code != 201:
        print("❌ Authentication failed!")
        print_response(auth_response)
        return
    
    token = auth_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated successfully")
    
    # Test 1: Create a meal entry
    print_section("1️⃣  Create Meal Entry")
    meal_response = requests.post(f"{BASE_URL}/journal/entries", headers=headers, json={
        "type": "meal",
        "title": "Chicken Stir Fry",
        "meal_type": "lunch",
        "portions": 4,
        "portions_left": 4,
        "status": "fresh",
        "ingredients_used": ["chicken", "vegetables", "soy sauce"],
        "is_batch": True
    })
    print_response(meal_response)
    
    if meal_response.status_code == 201:
        meal_id = meal_response.json()["id"]
        print(f"✅ Meal created with ID: {meal_id}")
    else:
        print("❌ Failed to create meal")
        return
    
    # Test 2: Create a purchase entry
    print_section("2️⃣  Create Purchase Entry")
    purchase_response = requests.post(f"{BASE_URL}/journal/entries", headers=headers, json={
        "type": "purchase",
        "title": "Walmart Grocery Run",
        "store": "Walmart",
        "items": [
            {
                "name": "Chicken breast",
                "quantity": "2 lbs",
                "cost": 12.99,
                "category": "protein"
            },
            {
                "name": "Mixed vegetables",
                "quantity": "1 bag",
                "cost": 4.50,
                "category": "produce"
            },
            {
                "name": "Soy sauce",
                "quantity": "1 bottle",
                "cost": 3.99,
                "category": "pantry"
            }
        ]
    })
    print_response(purchase_response)
    
    if purchase_response.status_code == 201:
        purchase_id = purchase_response.json()["id"]
        print(f"✅ Purchase created with ID: {purchase_id}")
    else:
        print("❌ Failed to create purchase")
        return
    
    # Test 3: Get all entries
    print_section("3️⃣  Get All Journal Entries")
    all_entries = requests.get(f"{BASE_URL}/journal/entries", headers=headers)
    print_response(all_entries)
    
    if all_entries.status_code == 200:
        count = len(all_entries.json())
        print(f"✅ Retrieved {count} entries")
    else:
        print("❌ Failed to get entries")
    
    # Test 4: Get single entry
    print_section("4️⃣  Get Single Meal Entry")
    single_entry = requests.get(f"{BASE_URL}/journal/entries/{meal_id}", headers=headers)
    print_response(single_entry)
    
    if single_entry.status_code == 200:
        print("✅ Retrieved single entry")
    else:
        print("❌ Failed to get single entry")
    
    # Test 5: Update meal entry
    print_section("5️⃣  Update Meal Entry (Portions Left)")
    update_response = requests.patch(
        f"{BASE_URL}/journal/entries/{meal_id}",
        headers=headers,
        json={
            "portions_left": 2,
            "status": "leftovers"
        }
    )
    print_response(update_response)
    
    if update_response.status_code == 200:
        print("✅ Meal updated successfully")
    else:
        print("❌ Failed to update meal")
    
    # Test 6: Link meal to purchase
    print_section("6️⃣  Link Meal to Purchase")
    link_response = requests.post(
        f"{BASE_URL}/journal/meals/{meal_id}/link-purchase",
        headers=headers,
        json={
            "purchase_id": purchase_id,
            "ingredients_used": ["chicken", "vegetables", "soy sauce"]
        }
    )
    print_response(link_response)
    
    if link_response.status_code == 200:
        print("✅ Meal linked to purchase")
    else:
        print("❌ Failed to link meal to purchase")
    
    # Test 7: Get only meals
    print_section("7️⃣  Get Meals Only")
    meals = requests.get(f"{BASE_URL}/journal/meals", headers=headers)
    print_response(meals)
    
    if meals.status_code == 200:
        count = len(meals.json())
        print(f"✅ Retrieved {count} meals")
    else:
        print("❌ Failed to get meals")
    
    # Test 8: Get only purchases
    print_section("8️⃣  Get Purchases Only")
    purchases = requests.get(f"{BASE_URL}/journal/purchases", headers=headers)
    print_response(purchases)
    
    if purchases.status_code == 200:
        count = len(purchases.json())
        print(f"✅ Retrieved {count} purchases")
    else:
        print("❌ Failed to get purchases")
    
    # Test 9: Filter by type
    print_section("9️⃣  Filter Entries by Type (meal)")
    filtered = requests.get(f"{BASE_URL}/journal/entries?type=meal", headers=headers)
    print_response(filtered)
    
    if filtered.status_code == 200:
        print("✅ Filtered entries successfully")
    else:
        print("❌ Failed to filter entries")
    
    # Test 10: Delete entry
    print_section("🔟 Delete Meal Entry")
    delete_response = requests.delete(f"{BASE_URL}/journal/entries/{meal_id}", headers=headers)
    
    if delete_response.status_code == 204:
        print("✅ Meal deleted successfully")
    else:
        print(f"❌ Failed to delete meal (Status: {delete_response.status_code})")
        print_response(delete_response)
    
    # Summary
    print_section("✨ All Journal Tests Complete!")
    print("Next steps:")
    print("1. Check the API docs: http://localhost:8000/docs")
    print("2. Implement Budget endpoints")
    print("3. Implement Recipes endpoints")
    print()

if __name__ == "__main__":
    main()
