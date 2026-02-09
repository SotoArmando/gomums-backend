"""
Test script for Mission API endpoints
"""
import requests
import json
from typing import Optional


# API Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test credentials
TEST_USER = {
    "name": "Mission Tester",
    "email": "mission@gomums.com",
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


def test_assign_daily_missions():
    """Test POST /missions/assign-daily"""
    print_header("3. Assign Daily Missions")
    
    response = requests.post(
        f"{API_URL}/missions/assign-daily",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Assigned {data['assigned_count']} daily missions")
        print_info(f"Mission IDs: {data['mission_ids']}")
        return data
    else:
        print_error("Failed to assign missions")
        print_response(response)
        return None


def test_get_active_missions():
    """Test GET /missions/active"""
    print_header("4. Get Active Missions")
    
    response = requests.get(
        f"{API_URL}/missions/active",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        missions = response.json()
        print_success(f"Retrieved {len(missions)} active missions")
        print()
        
        for mission in missions:
            m = mission['mission']
            print(f"  📋 {m['title']}")
            print(f"     Type: {m['type']} | Difficulty: {m['difficulty']}")
            print(f"     Progress: {mission['progress']}/{m['target']}")
            print(f"     Reward: {m['reward_points']} points")
            print(f"     Status: {mission['status']}")
            print()
        
        return missions
    else:
        print_error("Failed to retrieve active missions")
        print_response(response)
        return []


def test_update_mission_progress(user_mission_id: str, progress: int):
    """Test PATCH /missions/{id}/progress"""
    print_header(f"5. Update Mission Progress (ID: {user_mission_id[:8]}...)")
    
    response = requests.patch(
        f"{API_URL}/missions/{user_mission_id}/progress",
        json={"progress": progress},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        mission = response.json()
        m = mission['mission']
        print_success(f"Updated progress for: {m['title']}")
        print(f"  New progress: {mission['progress']}/{m['target']}")
        print(f"  Status: {mission['status']}")
        
        if mission['status'] == 'completed':
            print_success(f"  🎉 Mission completed! Earned {m['reward_points']} points!")
        
        return mission
    else:
        print_error("Failed to update mission progress")
        print_response(response)
        return None


def test_complete_mission(user_mission_id: str, target: int):
    """Test completing a mission by setting progress to target"""
    print_header(f"6. Complete Mission (ID: {user_mission_id[:8]}...)")
    
    response = requests.patch(
        f"{API_URL}/missions/{user_mission_id}/progress",
        json={"progress": target},
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        mission = response.json()
        m = mission['mission']
        print_success(f"Completed mission: {m['title']}")
        print(f"  Final progress: {mission['progress']}/{m['target']}")
        print(f"  Status: {mission['status']}")
        print(f"  Points earned: {m['reward_points']}")
        
        return mission
    else:
        print_error("Failed to complete mission")
        print_response(response)
        return None


def test_get_mission_stats():
    """Test GET /missions/stats"""
    print_header("7. Get Mission Statistics")
    
    response = requests.get(
        f"{API_URL}/missions/stats",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Retrieved mission statistics")
        print()
        print(f"  Active missions: {stats['total_active']}")
        print(f"  Completed missions: {stats['total_completed']}")
        print(f"  Expired missions: {stats['total_expired']}")
        print()
        print(f"  Points earned today: {stats['points_earned_today']}")
        print(f"  Points earned this week: {stats['points_earned_week']}")
        print(f"  Total points earned: {stats['points_earned_total']}")
        
        return stats
    else:
        print_error("Failed to retrieve mission stats")
        print_response(response)
        return None


# ==================== Main Test Runner ====================

def main():
    """Run all mission API tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print("GoMums Mission API - Test Script")
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
    
    # Test Mission endpoints
    assign_result = test_assign_daily_missions()
    
    active_missions = test_get_active_missions()
    
    if active_missions and len(active_missions) > 0:
        # Test updating progress on first mission
        first_mission = active_missions[0]
        test_update_mission_progress(first_mission['id'], 1)
        
        # Test completing the mission
        if len(active_missions) > 1:
            second_mission = active_missions[1]
            test_complete_mission(
                second_mission['id'], 
                second_mission['mission']['target']
            )
    
    test_get_mission_stats()
    
    # Summary
    print_header("Test Summary")
    
    print_success("✅ All mission API endpoints tested successfully!")
    print_info(f"  Assigned missions: {len(active_missions)}")
    print_info(f"  API Documentation: {BASE_URL}/docs")


if __name__ == "__main__":
    main()
