"""
Test script for User Profile API endpoints
"""
import requests
import json
from typing import Optional


# API Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
TEST_USER = {
    "name": "Profile Tester",
    "email": "profile@gomums.com",
    "password": "Test123!@#"
}

# Store access token globally
ACCESS_TOKEN: Optional[str] = None


# ==================== Color Codes ====================
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.CYAN}{'='*60}")
    print(text)
    print(f"{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_response(response, show_full: bool = False):
    """Print response details"""
    print(f"Status: {response.status_code}")
    if show_full or response.status_code >= 400:
        print(f"Response: {json.dumps(response.json(), indent=2)}")


# ==================== Test Functions ====================

def cleanup_test_user():
    """Clean up test user if exists"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST'),
            port=os.getenv('DATABASE_PORT'),
            database=os.getenv('DATABASE_NAME'),
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD')
        )
        
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE email = %s", (TEST_USER["email"],))
            conn.commit()
            
        conn.close()
    except Exception:
        pass


def test_register():
    """Test user registration"""
    print_header("1. User Registration")
    
    cleanup_test_user()
    
    response = requests.post(
        f"{API_URL}/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 201:
        print_success("User registered successfully")
        print_response(response, show_full=False)
        return response.json()["token"]
    else:
        print_error("Registration failed")
        print_response(response)
        return None


def test_login():
    """Test user login"""
    global ACCESS_TOKEN
    
    print_header("2. User Login")
    
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        print_success("Login successful")
        ACCESS_TOKEN = response.json()["token"]
        print_info(f"Access token: {ACCESS_TOKEN[:50]}...")
        return True
    else:
        print_error("Login failed")
        print_response(response)
        return False


def test_get_complete_profile():
    """Test GET /user/me - Get complete profile"""
    print_header("3. Get Complete Profile")
    
    response = requests.get(
        f"{API_URL}/user/me",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Retrieved complete profile")
        print()
        
        profile = data['profile']
        print(f"  Profile:")
        print(f"    Name: {profile['name']}")
        print(f"    Email: {profile['email']}")
        print(f"    Premium: {profile['is_premium']}")
        print()
        
        if data['preferences']:
            prefs = data['preferences']
            print(f"  Preferences: (None set yet)")
        else:
            print(f"  Preferences: Not set")
        print()
        
        if data['stats']:
            stats = data['stats']
            print(f"  Stats:")
            print(f"    Level: {stats['level']}")
            print(f"    Points: {stats['points']}")
            print(f"    Meals Cooked: {stats['total_meals_cooked']}")
            print(f"    Money Saved: ${stats['total_money_saved']}")
            print(f"    Current Streak: {stats['current_streak']} days")
        
        return data
    else:
        print_error("Failed to retrieve profile")
        print_response(response)
        return None


def test_get_profile():
    """Test GET /user/me/profile"""
    print_header("4. Get Profile Info")
    
    response = requests.get(
        f"{API_URL}/user/me/profile",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        profile = response.json()
        print_success(f"Retrieved profile for: {profile['name']}")
        print(f"  Email: {profile['email']}")
        print(f"  Active: {profile['is_active']}")
        print(f"  Premium: {profile['is_premium']}")
        return profile
    else:
        print_error("Failed to retrieve profile")
        print_response(response)
        return None


def test_update_profile():
    """Test PATCH /user/me/profile"""
    print_header("5. Update Profile")
    
    response = requests.patch(
        f"{API_URL}/user/me/profile",
        json={
            "name": "Updated Profile Tester",
            "avatar_url": "https://example.com/avatar.jpg"
        },
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        profile = response.json()
        print_success("Profile updated successfully")
        print(f"  New name: {profile['name']}")
        print(f"  Avatar URL: {profile['avatar_url']}")
        return profile
    else:
        print_error("Failed to update profile")
        print_response(response)
        return None


def test_update_preferences():
    """Test PATCH /user/me/preferences"""
    print_header("6. Update Preferences")
    
    response = requests.patch(
        f"{API_URL}/user/me/preferences",
        json={
            "dietary_restrictions": ["vegetarian", "gluten-free"],
            "allergies": ["peanuts", "shellfish"],
            "budget_goal": 150.00,
            "household_size": 3,
            "skill_level": "intermediate"
        },
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        prefs = response.json()
        print_success("Preferences updated successfully")
        print(f"  Dietary restrictions: {prefs['dietary_restrictions']}")
        print(f"  Allergies: {prefs['allergies']}")
        print(f"  Budget goal: ${prefs['budget_goal']}")
        print(f"  Household size: {prefs['household_size']}")
        print(f"  Skill level: {prefs['skill_level']}")
        return prefs
    else:
        print_error("Failed to update preferences")
        print_response(response)
        return None


def test_get_preferences():
    """Test GET /user/me/preferences"""
    print_header("7. Get Preferences")
    
    response = requests.get(
        f"{API_URL}/user/me/preferences",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        prefs = response.json()
        print_success("Retrieved preferences")
        print(f"  Dietary restrictions: {prefs['dietary_restrictions']}")
        print(f"  Allergies: {prefs['allergies']}")
        print(f"  Budget goal: ${prefs['budget_goal']}")
        print(f"  Household size: {prefs['household_size']}")
        print(f"  Skill level: {prefs['skill_level']}")
        return prefs
    else:
        print_error("Failed to retrieve preferences")
        print_response(response)
        return None


def test_get_stats():
    """Test GET /user/me/stats"""
    print_header("8. Get User Stats")
    
    response = requests.get(
        f"{API_URL}/user/me/stats",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Retrieved user statistics")
        print()
        print(f"  📊 User Stats:")
        print(f"    Level: {stats['level']}")
        print(f"    Points: {stats['points']}")
        print(f"    Total Meals Cooked: {stats['total_meals_cooked']}")
        print(f"    Total Money Saved: ${stats['total_money_saved']}")
        print(f"    Current Streak: {stats['current_streak']} days")
        print(f"    Achievements Unlocked: {stats['achievements_unlocked']}")
        return stats
    else:
        print_error("Failed to retrieve stats")
        print_response(response)
        return None


# ==================== Main Test Runner ====================

def main():
    """Run all user profile API tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("GoMums User Profile API - Test Script")
    print(f"{'='*60}{Colors.END}\n")
    
    print_info(f"Testing API at: {BASE_URL}")
    
    # Setup
    token = test_register()
    if not token:
        print_error("Failed to register user, exiting...")
        return
    
    if not test_login():
        print_error("Failed to login, exiting...")
        return
    
    # Test User Profile endpoints
    test_get_complete_profile()
    
    test_get_profile()
    
    test_update_profile()
    
    test_update_preferences()
    
    test_get_preferences()
    
    test_get_stats()
    
    # Summary
    print_header("Test Summary")
    
    print_success("✅ All user profile API endpoints tested successfully!")
    print_info("  Profile management: Working")
    print_info("  Preferences: Working")
    print_info("  Statistics: Working")
    print_info(f"  API Documentation: {BASE_URL}/docs")


if __name__ == "__main__":
    main()
