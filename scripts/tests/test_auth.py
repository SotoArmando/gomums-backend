"""
Quick authentication test script
Run this after starting your server to test all auth endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

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
    print_section("🧪 Testing GoMums Authentication API")
    
    # Test data
    test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    test_password = "testpass123"
    test_name = "Test User"
    
    print(f"📧 Test Email: {test_email}")
    print(f"🔐 Test Password: {test_password}")
    
    # 1. Health Check
    print_section("1️⃣  Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the server is running: python -m uvicorn app.main:app --reload --port 8000")
        return
    
    # 2. Register
    print_section("2️⃣  Register New User")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": test_name,
            "email": test_email,
            "password": test_password
        })
        print_response(response)
        
        if response.status_code == 201:
            data = response.json()
            token = data["token"]
            refresh_token = data["refresh_token"]
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Login
    print_section("3️⃣  Login")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        print_response(response)
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Get Current User (Protected Route)
    print_section("4️⃣  Get Current User (Protected)")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            print("✅ Protected route access successful!")
        else:
            print("❌ Protected route access failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Refresh Token
    print_section("5️⃣  Refresh Token")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        print_response(response)
        
        if response.status_code == 200:
            new_data = response.json()
            token = new_data["access_token"]
            print("✅ Token refresh successful!")
        else:
            print("❌ Token refresh failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Test Invalid Login
    print_section("6️⃣  Test Invalid Login (Should Fail)")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "wrongpassword"
        })
        print_response(response)
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid credentials!")
        else:
            print("❌ Should have rejected invalid credentials!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 7. Logout
    print_section("7️⃣  Logout")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        print_response(response)
        
        if response.status_code == 204:
            print("✅ Logout successful!")
        else:
            print("❌ Logout failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Summary
    print_section("✨ All Tests Complete!")
    print("Next steps:")
    print("1. Check the API docs: http://localhost:8000/docs")
    print("2. Implement journal endpoints")
    print("3. Implement budget endpoints")
    print("4. Implement recipes endpoints")
    print()

if __name__ == "__main__":
    main()
