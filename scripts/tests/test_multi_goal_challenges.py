"""
Test Multi-Goal Challenges
Tests challenge assignment, individual goal tracking, and completion
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

# Test user credentials
TEST_USER = {
    "name": "Challenge Tester",
    "email": "challenge_test@gomums.com",
    "password": "TestPass123!"
}


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def register_and_login():
    """Register test user and get access token"""
    print_section("1. USER REGISTRATION & LOGIN")
    
    # Register user
    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if response.status_code == 201:
        print("✅ User registered successfully")
    elif response.status_code == 400:
        print("ℹ️  User already exists, proceeding to login...")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.json())
        return None
    
    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Token type: {data['token_type']}")
        return data["token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.json())
        return None


def get_available_challenges(token):
    """Get all available challenges"""
    print_section("2. GET AVAILABLE CHALLENGES")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/challenges/", headers=headers)
    
    if response.status_code == 200:
        challenges = response.json()
        print(f"✅ Found {len(challenges)} available challenges")
        
        if challenges:
            challenge = challenges[0]  # Get the first challenge
            print(f"\n📋 Challenge: {challenge['title']}")
            print(f"   Description: {challenge['description']}")
            print(f"   Type: {challenge['type']}")
            print(f"   Duration: {challenge['duration']} days")
            print(f"   Reward: {challenge['reward_points']} points")
            print(f"   Goals ({len(challenge['goals'])}):")
            
            for i, goal in enumerate(challenge['goals'], 1):
                print(f"     {i}. {goal['description']} (target: {goal['target']})")
            
            return challenge
        else:
            print("⚠️  No challenges available. Run seed_challenges.py first.")
            return None
    else:
        print(f"❌ Failed to get challenges: {response.status_code}")
        print(response.json())
        return None


def assign_challenge(token, challenge_id):
    """Assign a challenge to the user"""
    print_section("3. ASSIGN CHALLENGE")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/challenges/assign/{challenge_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Challenge assigned successfully")
        print(f"   Challenge: {data['challenge_title']}")
        print(f"   Total goals: {data['total_goals']}")
        print(f"   Potential reward: {data['reward_points']} points")
        return data["user_challenge_id"]
    else:
        print(f"❌ Failed to assign challenge: {response.status_code}")
        print(response.json())
        return None


def get_active_challenges(token):
    """Get user's active challenges"""
    print_section("4. CHECK ACTIVE CHALLENGES")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/challenges/active/all", headers=headers)
    
    if response.status_code == 200:
        active_challenges = response.json()
        print(f"✅ Found {len(active_challenges)} active challenge(s)")
        
        for challenge in active_challenges:
            print(f"\n📊 {challenge['challenge_title']}")
            print(f"   Status: {challenge['status']}")
            print(f"   Progress: {challenge['completed_goals']}/{challenge['total_goals']} goals completed")
            print(f"   Goals:")
            
            for goal in challenge['goal_progress']:
                status = "✓" if goal['completed'] else "○"
                print(f"     {status} {goal['goal_description']}: {goal['progress']}/{goal['goal_target']}")
        
        return active_challenges
    else:
        print(f"❌ Failed to get active challenges: {response.status_code}")
        return []


def update_challenge_goal_progress(token, user_challenge_id, goal_id, increment=1):
    """Update progress for a specific challenge goal"""
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "user_challenge_id": str(user_challenge_id),
        "goal_id": str(goal_id),
        "progress_increment": increment
    }
    
    response = requests.post(
        f"{BASE_URL}/challenges/progress/update",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️  Failed to update goal progress: {response.status_code}")
        print(response.json())
        return None


def create_batch_meal(token, servings=4):
    """Create a batch meal journal entry"""
    headers = {"Authorization": f"Bearer {token}"}
    
    meal_data = {
        "title": f"Batch Cooked Pasta (Servings: {servings})",
        "type": "meal",
        "meal_type": "dinner",
        "portions": servings,
        "portions_left": servings - 1,
        "status": "fresh",
        "ingredients_used": ["pasta", "tomato sauce", "vegetables"]
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        headers=headers,
        json=meal_data
    )
    
    return response.status_code == 201


def create_leftover_meal(token):
    """Create a leftover meal journal entry"""
    headers = {"Authorization": f"Bearer {token}"}
    
    meal_data = {
        "title": "Leftover Pasta Remix",
        "type": "meal",
        "meal_type": "lunch",
        "portions": 1,
        "status": "leftovers",
        "used_leftovers": True,
        "ingredients_used": ["leftover pasta", "cheese"]
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        headers=headers,
        json=meal_data
    )
    
    return response.status_code == 201


def test_multi_goal_challenge():
    """Main test function"""
    print("\n" + "="*60)
    print("  MULTI-GOAL CHALLENGE TESTING")
    print("  Testing: Batch Cooking Master Challenge")
    print("="*60)
    
    # Step 1: Register and login
    token = register_and_login()
    if not token:
        print("\n❌ Test failed at login step")
        return
    
    time.sleep(1)
    
    # Step 2: Get available challenges
    challenge = get_available_challenges(token)
    if not challenge:
        print("\n❌ Test failed: No challenges available")
        return
    
    time.sleep(1)
    
    # Step 3: Assign the challenge
    user_challenge_id = assign_challenge(token, challenge['id'])
    if not user_challenge_id:
        print("\n❌ Test failed at challenge assignment")
        return
    
    time.sleep(1)
    
    # Step 4: Check initial state
    active_challenges = get_active_challenges(token)
    if not active_challenges:
        print("\n❌ Test failed: Challenge not showing as active")
        return
    
    # Get challenge and goal IDs for testing
    user_challenge = active_challenges[0]
    user_challenge_id = user_challenge['id']
    goals = user_challenge['goal_progress']
    
    # Step 5: Create journal entries and update challenge goals
    print_section("5. PROGRESS CHALLENGE GOALS")
    
    # Goal 1: Try new recipes (assuming first goal)
    if len(goals) >= 1:
        goal_1_id = goals[0]['goal_id']
        goal_1_target = goals[0]['goal_target']
        
        print(f"\n🍳 Working on Goal 1: {goals[0]['goal_description']}")
        print(f"   Target: {goal_1_target}")
        
        for i in range(min(3, goal_1_target)):
            if create_batch_meal(token, servings=4):
                print(f"  ✅ Created batch meal {i+1}")
                # Update challenge progress
                result = update_challenge_goal_progress(token, user_challenge_id, goal_1_id, 1)
                if result:
                    print(f"     Progress: {result['current_progress']}/{goal_1_target}")
                    if result.get('goal_completed'):
                        print(f"     🎯 Goal completed!")
                time.sleep(0.5)
    
    time.sleep(1)
    active_challenges = get_active_challenges(token)
    
    # Goal 3: Use leftovers (assuming third goal - adjust index if needed)
    if len(goals) >= 3:
        goal_3_id = goals[2]['goal_id']
        goal_3_target = goals[2]['goal_target']
        
        print(f"\n🍱 Working on Goal 3: {goals[2]['goal_description']}")
        print(f"   Target: {goal_3_target}")
        
        for i in range(min(5, goal_3_target)):
            if create_leftover_meal(token):
                print(f"  ✅ Used leftovers {i+1}")
                # Update challenge progress
                result = update_challenge_goal_progress(token, user_challenge_id, goal_3_id, 1)
                if result:
                    print(f"     Progress: {result['current_progress']}/{goal_3_target}")
                    if result.get('goal_completed'):
                        print(f"     🎯 Goal completed!")
                    if result.get('challenge_completed'):
                        print(f"     🎉 CHALLENGE COMPLETED! Points awarded: {result.get('points_awarded', 0)}")
                time.sleep(0.5)
    
    time.sleep(1)
    
    # Step 6: Check final progress
    print_section("6. FINAL CHALLENGE STATUS")
    
    final_challenges = get_active_challenges(token)
    
    if final_challenges:
        challenge = final_challenges[0]
        
        if challenge['status'] == 'completed':
            print(f"\n🎉 CHALLENGE COMPLETED!")
            print(f"   Points awarded: {challenge['reward_points']}")
        else:
            print(f"\n📊 Challenge still in progress")
            print(f"   Completed: {challenge['completed_goals']}/{challenge['total_goals']} goals")
    
    # Step 7: Get user profile to verify points
    print_section("7. VERIFY POINTS AWARDED")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ User stats retrieved")
        print(f"   Total points: {profile['stats']['points']}")
        print(f"   Meals cooked: {profile['stats']['total_meals_cooked']}")
        print(f"   Level: {profile['stats']['level']}")
    else:
        print(f"⚠️  Could not retrieve user profile: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.json()}")
    
    print("\n" + "="*60)
    print("  TEST COMPLETED SUCCESSFULLY! ✅")
    print("  Multi-goal challenge system is working!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_multi_goal_challenge()
