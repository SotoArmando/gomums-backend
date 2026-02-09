"""
Test script to verify automatic challenge goal tracking from journal entries
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# Test credentials (same as test_multi_goal_challenges.py)
EMAIL = "challenge_test@gomums.com"
PASSWORD = "TestPass123!"

def register_user():
    """Register test user"""
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "name": "Challenge Tester",
            "email": EMAIL,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 201:
        print("✅ User registered successfully")
        return True
    elif response.status_code == 400 and "already registered" in response.text:
        print("ℹ️ User already exists")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return False

def login():
    """Login and get auth token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        token = response.json()["token"]
        print("✅ Logged in successfully")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def register_and_login():
    """Register user if needed and login"""
    # Try to register first (will succeed or say user exists)
    register_user()
    
    # Then login
    return login()

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def get_challenges(token):
    """Get all available challenges"""
    response = requests.get(
        f"{BASE_URL}/challenges/",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        challenges = response.json()
        
        # Remove duplicates
        unique_challenges = {}
        for challenge in challenges:
            if challenge['title'] not in unique_challenges:
                unique_challenges[challenge['title']] = challenge
        
        print(f"\n📋 Found {len(unique_challenges)} unique challenges")
        return list(unique_challenges.values())
    else:
        print(f"❌ Failed to get challenges: {response.status_code}")
        return []

def display_challenges_menu(challenges):
    """Display challenges menu and let user select"""
    print("\n" + "="*70)
    print("  SELECT A CHALLENGE TO TEST")
    print("="*70)
    
    print("\nAvailable Challenges:\n")
    for i, challenge in enumerate(challenges, 1):
        print(f"{i:2}. {challenge['title']}")
        print(f"    Type: {challenge['type']} | Duration: {challenge['duration']} days | Reward: {challenge['reward_points']} pts")
        print(f"    Goals: {len(challenge['goals'])}")
        for j, goal in enumerate(challenge['goals'], 1):
            print(f"      {j}. {goal['description']} (target: {goal['target']})")
        print()
    
    print(f"{len(challenges) + 1:2}. Exit")
    
    while True:
        try:
            choice = input(f"\nEnter your choice (1-{len(challenges) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(challenges) + 1:
                print("👋 Exiting...")
                return None
            
            if 1 <= choice_num <= len(challenges):
                selected = challenges[choice_num - 1]
                print(f"\n✅ Selected: {selected['title']}")
                return selected
            else:
                print(f"❌ Invalid choice. Please enter a number between 1 and {len(challenges) + 1}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            return None

def assign_challenge(token, challenge_id):
    """Assign a challenge to the user"""
    response = requests.post(
        f"{BASE_URL}/challenges/assign/{challenge_id}",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        print(f"✅ Challenge assigned successfully")
        return True
    elif response.status_code == 409:
        print(f"⚠️ Challenge already assigned")
        return True
    else:
        print(f"❌ Failed to assign challenge: {response.status_code}")
        print(response.text)
        return False

def get_active_challenges(token):
    """Get user's active challenges"""
    response = requests.get(
        f"{BASE_URL}/challenges/active/all",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get active challenges: {response.status_code}")
        return []

def create_meal_entry(token, title, meal_type, portions, status=None, used_leftovers=False):
    """Create a meal journal entry"""
    entry_data = {
        "type": "meal",
        "title": title,
        "meal_type": meal_type,
        "portions": portions,
        "status": status or "fresh",
        "used_leftovers": used_leftovers,
        "is_batch": portions >= 3,
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        headers=get_headers(token),
        json=entry_data
    )
    
    if response.status_code == 201:
        print(f"✅ Meal entry created: {title}")
        return response.json()
    else:
        print(f"❌ Failed to create meal entry: {response.status_code}")
        print(response.text)
        return None

def display_challenge_progress(challenges):
    """Display challenge progress"""
    print("\n" + "="*60)
    print("📊 Current Challenge Progress")
    print("="*60)
    
    for challenge in challenges:
        print(f"\n🎯 {challenge['challenge_title']} ({challenge['reward_points']} points)")
        print(f"   Type: {challenge['challenge_type']}")
        print(f"   Status: {challenge['status']}")
        
        if 'goal_progress' in challenge:
            completed_count = sum(1 for goal in challenge['goal_progress'] if goal['completed'])
            total_goals = len(challenge['goal_progress'])
            
            print(f"   Progress: {completed_count}/{total_goals} goals completed\n")
            
            for i, goal in enumerate(challenge['goal_progress'], 1):
                progress = goal['progress']
                target = goal['goal_target']
                percentage = (progress / target * 100) if target > 0 else 0
                status_icon = "✓" if goal['completed'] else "○"
                
                print(f"   {status_icon} Goal {i}: {progress}/{target} ({percentage:.0f}%)")
    
    print("\n" + "="*60)

def run_challenge_tests(token, challenge):
    """Run automated tests based on challenge type"""
    challenge_type = challenge['type']
    
    print("\n" + "="*70)
    print(f"  🧪 RUNNING AUTOMATED TESTS FOR: {challenge['title']}")
    print("="*70)
    
    # Get initial progress
    print("\n📊 Initial Progress:")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    if challenge_type == 'batch_cooking':
        run_batch_cooking_tests(token)
    elif challenge_type == 'zero_waste':
        run_zero_waste_tests(token)
    elif challenge_type == 'budget_savings':
        run_budget_tests(token)
    elif challenge_type == 'cooking_streak':
        run_streak_tests(token)
    elif 'leftover' in challenge_type:
        run_leftover_tests(token)
    elif 'new_recipe' in challenge['title'].lower() or 'recipe' in challenge_type:
        run_recipe_tests(token)
    else:
        run_generic_meal_tests(token)
    
    # Final progress
    print("\n" + "="*70)
    print("  📊 FINAL PROGRESS")
    print("="*70)
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_batch_cooking_tests(token):
    """Test batch cooking challenge"""
    print("\n" + "="*60)
    print("🍳 TEST 1: Creating batch meal with 4 portions")
    print("   Expected: Batch cooking goals should increment")
    print("="*60)
    
    create_meal_entry(token, "Chicken Stir Fry", "dinner", 4, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 2: Creating batch meal with 5 portions")
    print("   Expected: Batch cooking goals should increment again")
    print("="*60)
    
    create_meal_entry(token, "Beef Chili", "dinner", 5, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 3: Using leftovers from batch meal")
    print("   Expected: Leftover goals should increment")
    print("="*60)
    
    create_meal_entry(token, "Leftover Chili", "lunch", 1, "leftovers", used_leftovers=True)
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 4: Freezing a batch meal")
    print("   Expected: Freeze goals should increment")
    print("="*60)
    
    create_meal_entry(token, "Frozen Pasta Sauce", "dinner", 6, "frozen")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_leftover_tests(token):
    """Test leftover-focused challenges"""
    print("\n" + "="*60)
    print("🍳 TEST 1: Using leftovers")
    print("   Expected: Leftover usage goals increment")
    print("="*60)
    
    create_meal_entry(token, "Leftover Stir Fry", "lunch", 1, "leftovers", used_leftovers=True)
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 2: Another leftover meal")
    print("="*60)
    
    create_meal_entry(token, "Leftover Soup", "dinner", 2, "leftovers", used_leftovers=True)
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_recipe_tests(token):
    """Test new recipe challenges"""
    print("\n" + "="*60)
    print("🍳 TEST 1: Trying new recipe")
    print("   Expected: New recipe goals increment")
    print("="*60)
    
    create_meal_entry(token, "Thai Green Curry", "dinner", 3, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 2: Another new recipe")
    print("="*60)
    
    create_meal_entry(token, "Moroccan Tagine", "dinner", 4, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_zero_waste_tests(token):
    """Test zero waste challenges"""
    print("\n" + "="*60)
    print("🍳 TEST 1: Using leftovers (reduce waste)")
    print("="*60)
    
    create_meal_entry(token, "Leftover Casserole", "dinner", 3, "leftovers", used_leftovers=True)
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 2: Freezing meal to prevent waste")
    print("="*60)
    
    create_meal_entry(token, "Frozen Soup", "lunch", 4, "frozen")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_budget_tests(token):
    """Test budget-related challenges"""
    print("\n" + "="*60)
    print("🍳 TEST: Creating affordable home meals")
    print("   Note: Budget tracking requires budget entries")
    print("="*60)
    
    create_meal_entry(token, "Budget Pasta", "dinner", 3, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_streak_tests(token):
    """Test streak challenges"""
    print("\n" + "="*60)
    print("🍳 TEST: Creating daily meals")
    print("   Note: Streak challenges require consecutive days")
    print("="*60)
    
    create_meal_entry(token, "Today's Breakfast", "breakfast", 1, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def run_generic_meal_tests(token):
    """Run generic meal tests when type is unknown"""
    print("\n" + "="*60)
    print("🍳 TEST 1: Creating regular meal")
    print("="*60)
    
    create_meal_entry(token, "Home Cooked Meal", "dinner", 2, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)
    
    print("\n" + "="*60)
    print("🍳 TEST 2: Creating batch meal")
    print("="*60)
    
    create_meal_entry(token, "Big Batch Meal", "dinner", 4, "fresh")
    active_challenges = get_active_challenges(token)
    display_challenge_progress(active_challenges)

def main():
    print("🧪 Testing Automatic Challenge Goal Tracking")
    print("="*60)
    
    # Register and login
    token = register_and_login()
    if not token:
        return
    
    # Get all challenges
    all_challenges = get_challenges(token)
    if not all_challenges:
        print("❌ No challenges available")
        return
    
    # Display menu and let user select
    selected_challenge = display_challenges_menu(all_challenges)
    if not selected_challenge:
        return
    
    # Assign the selected challenge
    if not assign_challenge(token, selected_challenge['id']):
        return
    
    # Run automated tests for the selected challenge
    run_challenge_tests(token, selected_challenge)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
