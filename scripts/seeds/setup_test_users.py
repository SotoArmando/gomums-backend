"""
Setup Test Users
Creates test users for all test files
"""
import requests

BASE_URL = "http://localhost:8000/api"

# Test users for different test files
TEST_USERS = [
    {
        "email": "test_stats@example.com",
        "password": "TestPassword123!",
        "name": "Stats Test User"
    },
    {
        "email": "test_achievements@example.com",
        "password": "TestPassword123!",
        "name": "Achievements Test User"
    },
    {
        "email": "test_meal_plans@example.com",
        "password": "TestPassword123!",
        "name": "Meal Plans Test User"
    },
    {
        "email": "test@gomums.com",
        "password": "Test123!@#",
        "name": "Smart Features Test User"
    }
]

def setup_test_users():
    """Create or verify test users exist"""
    print("\n" + "="*70)
    print("SETTING UP TEST USERS")
    print("="*70)
    
    for user in TEST_USERS:
        print(f"\n📧 {user['email']}...")
        
        # Try to register (400 if already exists)
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user
        )
        
        if response.status_code == 201:
            print(f"  ✅ Created new user")
        elif response.status_code == 400:
            print(f"  ℹ️  User already exists")
        else:
            print(f"  ❌ Error: {response.status_code} - {response.text}")
            continue
        
        # Verify login works
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user['email'], "password": user['password']}
        )
        
        if login_response.status_code == 200:
            print(f"  ✅ Login successful")
        else:
            print(f"  ❌ Login failed: {login_response.text}")
    
    print("\n" + "="*70)
    print("✅ Test users setup complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    setup_test_users()
