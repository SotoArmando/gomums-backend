"""
Test All Multi-Goal Challenges
Tests different challenge types and their progression
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

# Test user credentials
TEST_USER = {
    "name": "Challenge Master",
    "email": "challenge_master@gomums.com",
    "password": "TestPass123!"
}


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def register_and_login():
    """Register test user and get access token"""
    print_section("USER REGISTRATION & LOGIN")
    
    # Register user
    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if response.status_code == 201:
        print("✅ User registered successfully")
    elif response.status_code == 400:
        print("ℹ️  User already exists, proceeding to login...")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        return None
    
    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful - User ID: {data['user']['id']}")
        return data["token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None


def get_all_challenges(token):
    """Get all available challenges"""
    print_section("AVAILABLE CHALLENGES")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/challenges/", headers=headers)
    
    if response.status_code == 200:
        challenges = response.json()
        print(f"✅ Found {len(challenges)} total challenges\n")
        
        # Remove duplicates by keeping track of seen titles
        unique_challenges = []
        seen_titles = set()
        
        for challenge in challenges:
            if challenge['title'] not in seen_titles:
                unique_challenges.append(challenge)
                seen_titles.add(challenge['title'])
        
        print(f"📋 {len(unique_challenges)} unique challenges available:\n")
        
        for i, challenge in enumerate(unique_challenges, 1):
            print(f"{i}. {challenge['title']}")
            print(f"   Type: {challenge['type']} | Duration: {challenge['duration']} days | Reward: {challenge['reward_points']} pts")
            print(f"   Goals: {len(challenge['goals'])}")
            for j, goal in enumerate(challenge['goals'], 1):
                print(f"     {j}. {goal['description']} (target: {goal['target']})")
            print()
        
        return unique_challenges
    else:
        print(f"❌ Failed to get challenges: {response.status_code}")
        return []


def select_challenge_from_menu(challenges):
    """Display interactive menu to select a challenge"""
    print_section("SELECT A CHALLENGE TO TEST")
    
    print("Available Challenges:")
    for i, challenge in enumerate(challenges, 1):
        print(f"{i:2}. {challenge['title']} ({challenge['reward_points']} pts)")
    
    print(f"\n{len(challenges) + 1:2}. 🚀 Run ALL Challenges (one by one)")
    print(f"{len(challenges) + 2:2}. Exit")
    
    while True:
        try:
            choice = input(f"\nEnter your choice (1-{len(challenges) + 2}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(challenges) + 2:
                print("👋 Exiting...")
                return None
            
            if choice_num == len(challenges) + 1:
                print("\n✅ Selected: Run ALL Challenges")
                return "ALL"
            
            if 1 <= choice_num <= len(challenges):
                selected = challenges[choice_num - 1]
                print(f"\n✅ Selected: {selected['title']}")
                return selected
            else:
                print(f"❌ Invalid choice. Please enter a number between 1 and {len(challenges) + 2}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            return None


def assign_challenge(token, challenge_id, challenge_title):
    """Assign a specific challenge to the user"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/challenges/assign/{challenge_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Assigned: {challenge_title}")
        print(f"   User Challenge ID: {data['user_challenge_id']}")
        print(f"   Goals: {data['total_goals']} | Reward: {data['reward_points']} points")
        return data["user_challenge_id"]
    elif response.status_code == 409:
        print(f"⚠️  {challenge_title} already assigned")
        return None
    else:
        print(f"❌ Failed to assign {challenge_title}: {response.status_code}")
        print(f"   {response.json()}")
        return None


def get_active_challenges(token):
    """Get user's active challenges"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/challenges/active/all", headers=headers)
    
    if response.status_code == 200:
        active_challenges = response.json()
        
        if not active_challenges:
            # Try to get completed challenges instead
            print("ℹ️  No active challenges\n")
            completed = get_completed_challenges(token)
            if completed:
                return []
            print()
            return []
        
        print(f"\n✅ Active Challenges: {len(active_challenges)}\n")
        
        for challenge in active_challenges:
            completion = challenge['completed_goals'] / challenge['total_goals'] * 100
            print(f"📊 {challenge['challenge_title']}")
            print(f"   Status: {challenge['status']} | Progress: {challenge['completed_goals']}/{challenge['total_goals']} ({completion:.0f}%)")
            print(f"   Goals:")
            
            for goal in challenge['goal_progress']:
                status = "✓" if goal['completed'] else "○"
                progress_pct = (goal['progress'] / goal['goal_target'] * 100) if goal['goal_target'] > 0 else 0
                print(f"     {status} {goal['goal_description']}: {goal['progress']}/{goal['goal_target']} ({progress_pct:.0f}%)")
            print()
        
        return active_challenges
    else:
        print(f"❌ Failed to get active challenges: {response.status_code}")
        return []


def get_completed_challenges(token):
    """Get user's completed challenges"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/challenges/completed/all", headers=headers)
    
    if response.status_code == 200:
        completed_challenges = response.json()
        
        if not completed_challenges:
            return []
        
        print(f"🏆 Completed Challenges: {len(completed_challenges)}\n")
        
        for challenge in completed_challenges:
            completion = challenge['completed_goals'] / challenge['total_goals'] * 100
            completed_at = challenge.get('completed_at', 'N/A')
            print(f"✅ {challenge['challenge_title']}")
            print(f"   Completed: {completed_at} | Reward: {challenge['reward_points']} points")
            print(f"   Goals: {challenge['completed_goals']}/{challenge['total_goals']} ({completion:.0f}%)")
            
            for goal in challenge['goal_progress']:
                status = "✓" if goal['completed'] else "○"
                progress_pct = (goal['progress'] / goal['goal_target'] * 100) if goal['goal_target'] > 0 else 0
                print(f"     {status} {goal['goal_description']}: {goal['progress']}/{goal['goal_target']} ({progress_pct:.0f}%)")
            print()
        
        return completed_challenges
    else:
        print(f"❌ Failed to get completed challenges: {response.status_code}")
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
        return None


def create_meal_entry(token, meal_data):
    """Create a journal entry for a meal"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        headers=headers,
        json=meal_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"   ⚠️  Failed to create meal entry: {response.status_code}")
        if response.text:
            print(f"   Error: {response.text[:200]}")
        return None


def create_purchase_entry(token, purchase_data):
    """Create a journal entry for a purchase"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/journal/entries",
        headers=headers,
        json=purchase_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"   ⚠️  Failed to create purchase entry: {response.status_code}")
        if response.text:
            print(f"   Error: {response.text[:200]}")
        return None


def set_budget_settings(token, weekly_budget=None, monthly_budget=None):
    """Set user's budget settings"""
    headers = {"Authorization": f"Bearer {token}"}
    
    settings_data = {}
    if weekly_budget is not None:
        settings_data["weekly_budget"] = weekly_budget
    if monthly_budget is not None:
        settings_data["monthly_budget"] = monthly_budget
    
    response = requests.post(
        f"{BASE_URL}/budget/settings",
        headers=headers,
        json=settings_data
    )
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"   ⚠️  Failed to set budget settings: {response.status_code}")
        if response.text:
            print(f"   Error: {response.text[:200]}")
        return None


def create_budget_entry(token, amount, category="groceries"):
    """Create a budget entry"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Budget entries need meal_name, cost, servings, date
    budget_data = {
        "date": time.strftime("%Y-%m-%d"),
        "meal_name": f"{category.title()} Purchase",
        "cost": amount,
        "servings": 4,
        "category": category,
        "notes": "Test budget entry"
    }
    
    response = requests.post(
        f"{BASE_URL}/budget/entries",
        headers=headers,
        json=budget_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"   Budget entry failed: {response.status_code} - {response.text[:100]}")
        return None


def simulate_progress(token, challenge):
    """Simulate progress by creating appropriate journal entries"""
    print_section("SIMULATING CHALLENGE PROGRESS")
    
    print(f"\n🎯 Testing: {challenge['title']}")
    print(f"📝 Creating journal entries to trigger automatic goal tracking...\n")
    
    # Get current state
    active = get_active_challenges(token)
    current = next((c for c in active if str(c['id']) == str(challenge['id'])), None)
    if not current:
        print(f"   ⚠️  Challenge not found in active challenges")
        return
    
    # Analyze goals and create appropriate entries
    goals_text = " ".join([g['goal_description'].lower() for g in current['goal_progress']])
    challenge_title = challenge['title'].lower()
    
    meal_counter = 1
    purchase_counter = 0
    
    # Swap & Save Challenge - create ingredient swap examples
    if "swap" in challenge_title and "save" in challenge_title:
        print("🔄 Creating ingredient swap meal example...")
        print("   Step 1: Logging grocery purchases with costs...\n")
        
        # Create purchase log showing what was bought
        purchase_data = {
            "type": "purchase",
            "title": "Grocery Shopping - Budget Ingredients",
            "store": "Local Market",
            "items": [
                {
                    "name": "beans (canned)",
                    "quantity": "1 can",
                    "cost": 1.99,
                    "category": "protein"
                },
                {
                    "name": "nutritional yeast",
                    "quantity": "1 container",
                    "cost": 3.99,
                    "category": "seasoning"
                },
                {
                    "name": "pasta",
                    "quantity": "1 lb",
                    "cost": 1.50,
                    "category": "carbs"
                },
                {
                    "name": "vegetables",
                    "quantity": "mixed",
                    "cost": 2.00,
                    "category": "produce"
                }
            ]
        }
        
        purchase_result = create_purchase_entry(token, purchase_data)
        if purchase_result:
            purchase_counter += 1
            total_cost = sum(item['cost'] for item in purchase_data['items'])
            print(f"   ✅ Purchase logged: {purchase_data['store']}")
            print(f"      📦 {len(purchase_data['items'])} items purchased")
            print(f"      💰 Total spent: ${total_cost:.2f}")
            for item in purchase_data['items']:
                print(f"         • {item['name']} - ${item['cost']:.2f}")
            
            # Show comparison with original recipe ingredients
            print(f"\n   💡 Original recipe would have cost:")
            print(f"      • bacon - $5.99")
            print(f"      • parmesan - $6.49")
            print(f"      • pasta - $1.50")
            print(f"      • vegetables - $2.00")
            print(f"      Total: $15.98")
            print(f"\n   ✨ By swapping ingredients, saved: $6.50!")
        
        print(f"\n   Step 2: Logging meal with ingredient swaps...\n")
        
        # Just need ONE meal with swaps to complete the challenge
        meal_data = {
            "type": "meal",
            "title": "Budget Pasta",
            "meal_type": "dinner",
            "portions": 3,
            "portions_left": 1,
            "status": "fresh",
            "is_batch": False,
            "used_leftovers": False,
            "has_leftovers": True,
            "ingredient_swaps": [
                {
                    "recipe_id": "recipe-001", 
                    "original_ingredient": "bacon", 
                    "original_cost": 5.99,
                    "swapped_ingredient": "beans",
                    "swapped_cost": 1.99,
                    "savings": 4.00
                },
                {
                    "recipe_id": "recipe-001", 
                    "original_ingredient": "parmesan", 
                    "original_cost": 6.49,
                    "swapped_ingredient": "nutritional yeast",
                    "swapped_cost": 3.99,
                    "savings": 2.50
                }
            ]
        }
        result = create_meal_entry(token, meal_data)
        if result:
            print(f"   ✅ Meal logged: Budget Pasta")
            print(f"      🍝 3 portions made, 1 saved for later")
            print(f"      🔄 Ingredient swaps tracked:")
            print(f"         • bacon ($5.99) → beans ($1.99) - saved $4.00")
            print(f"         • parmesan ($6.49) → nutritional yeast ($3.99) - saved $2.50")
            print(f"      💰 Total savings from swaps: $6.50")
            meal_counter += 1
        
        print(f"\n   🎯 Goal: Complete with just 1 meal containing swapped ingredients!")
    
    # Batch cooking challenge
    elif "batch" in goals_text or "meal prep" in goals_text:
        print("🍲 Creating batch cooking entries...")
        for i in range(3):
            meal_data = {
                "type": "meal",
                "title": f"Batch Cooked Meal {meal_counter}",
                "meal_type": "lunch",
                "portions": 6,
                "portions_left": 4,
                "status": "fresh",
                "is_batch": True,
                "used_leftovers": False,
                "has_leftovers": True
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"   ✅ Created batch meal entry #{meal_counter}")
                meal_counter += 1
                time.sleep(0.2)
    
    # Budget Boss Challenge - comprehensive budget tracking
    elif "budget boss" in challenge_title or ("budget" in goals_text and "daily" in goals_text):
        print("\n💰 Creating Budget Boss Challenge entries...")
        
        # Set weekly budget first (this enables budget tracking)
        print("   📊 Setting weekly budget: $150/week (~$21.43/day)")
        budget_result = set_budget_settings(token, weekly_budget=150.0)
        if budget_result:
            print(f"      ✅ Budget settings saved")
        else:
            print(f"      ⚠️  Failed to set budget - budget goals won't track")
        
        # Create purchase entries on different days, all under daily budget
        print("\n   🛒 Creating purchase entries (20 days under budget)...")
        from datetime import datetime, timedelta
        base_date = datetime.now()
        total_savings = 0
        
        for day in range(20):
            # Create purchase entry for each day, staying under $21.43
            purchase_date = base_date - timedelta(days=day)
            purchase_amount = 15.0 + (day % 5)  # $15-19 each day
            
            # Every 5th purchase includes ingredient swaps with savings
            purchase_data = {
                "type": "purchase",
                "title": f"Day {day + 1} Groceries",
                "store": "Budget Mart",
                "timestamp": purchase_date.isoformat(),
                "items": [
                    {"name": "Groceries", "cost": purchase_amount, "quantity": "1 bag"}
                ]
            }
            
            # Add ingredient swaps every 5th purchase
            if day % 5 == 0:
                purchase_data["ingredient_swaps"] = [
                    {
                        "original_ingredient": "Premium Item",
                        "original_cost": 8.99,
                        "swapped_ingredient": "Budget Item",
                        "swapped_cost": 4.99,
                        "savings": 4.0
                    }
                ]
                total_savings += 4.0
            
            result = create_purchase_entry(token, purchase_data)
            if result and day % 5 == 0:
                savings_note = " (swaps saved $4.00)" if day % 5 == 0 else ""
                print(f"      ✅ Day {day + 1}: ${purchase_amount:.2f}{savings_note}")
            time.sleep(0.1)
        
        print(f"\n   💵 Total savings from swaps: ${total_savings:.2f}")
        
        # Create leftover meals to progress that goal
        print("\n   🥡 Creating leftover usage entries...")
        for i in range(15):
            meal_data = {
                "type": "meal",
                "title": f"Leftover Meal {meal_counter}",
                "meal_type": "dinner",
                "portions": 2,
                "portions_left": 0,
                "status": "leftovers",
                "is_batch": False,
                "used_leftovers": True,
                "has_leftovers": False
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"      ✅ Leftover meal #{i + 1}")
                meal_counter += 1
                time.sleep(0.1)
        
        # Create home-cooked meals to progress that goal
        print("\n   🍽️ Creating home-cooked meal entries...")
        for i in range(50):
            meal_data = {
                "type": "meal",
                "title": f"Home Cooked Meal {meal_counter}",
                "meal_type": ["breakfast", "lunch", "dinner"][i % 3],
                "portions": 2,
                "portions_left": 1,
                "status": "fresh",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": True
            }
            result = create_meal_entry(token, meal_data)
            if result and i % 10 == 0:
                print(f"      ✅ Home meal #{i + 1}/50")
                meal_counter += 1
            elif result:
                meal_counter += 1
            time.sleep(0.05)
        
        print("\n   🎯 All Budget Boss goals should now track automatically!")
    
    # Leftover challenge
    elif "leftover" in goals_text:
        print("\n🥡 Creating leftover usage entries...")
        for i in range(4):
            meal_data = {
                "type": "meal",
                "title": f"Leftover Meal {meal_counter}",
                "meal_type": "dinner",
                "portions": 2,
                "portions_left": 0,
                "status": "leftovers",
                "is_batch": False,
                "used_leftovers": True,
                "has_leftovers": False
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"   ✅ Created leftover meal entry #{meal_counter}")
                meal_counter += 1
                time.sleep(0.2)
    
    # Cook Streak Challenge - needs consecutive days + breakfast meals + new recipes
    elif "consecutive" in goals_text or "streak" in goals_text or ("breakfast" in goals_text and "recipe" in goals_text):
        print("\n🔥 Creating cooking streak entries...")
        print("   Simulating meals across multiple days...\n")
        
        from datetime import datetime, timedelta
        
        # Create breakfast meals (3 needed)
        print("   🌅 Day 1-3: Breakfast meals with new recipes")
        for day in range(3):
            meal_data = {
                "type": "meal",
                "title": f"New Breakfast: {['Avocado Toast', 'Smoothie Bowl', 'Oatmeal Delight'][day]}",
                "meal_type": "breakfast",
                "portions": 1,
                "portions_left": 0,
                "status": "completed",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": False,
                "timestamp": (datetime.now() - timedelta(days=4-day)).isoformat()
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"      ✅ Day {day + 1}: {meal_data['title']}")
                meal_counter += 1
                time.sleep(0.2)
        
        # Create lunch/dinner for remaining days to complete 5 consecutive days
        print("\n   🍽️ Day 4-5: Additional meals to complete streak")
        for day in range(3, 5):
            meal_data = {
                "type": "meal",
                "title": f"Home Cooked Meal Day {day + 1}",
                "meal_type": "dinner" if day % 2 == 0 else "lunch",
                "portions": 3,
                "portions_left": 1,
                "status": "fresh",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": True,
                "timestamp": (datetime.now() - timedelta(days=4-day)).isoformat()
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"      ✅ Day {day + 1}: {meal_data['title']}")
                meal_counter += 1
                time.sleep(0.2)
        
        print(f"\n   🎯 Goals covered:")
        print(f"      • 5 consecutive days of cooking")
        print(f"      • 3 breakfast meals")
        print(f"      • 2+ new recipes")
    
    # Recipe challenge
    elif "recipe" in goals_text or "new dish" in goals_text:
        print("\n📖 Creating recipe-based entries...")
        for i in range(3):
            meal_data = {
                "type": "meal",
                "title": f"New Recipe: Dish {meal_counter}",
                "meal_type": "dinner",
                "portions": 4,
                "portions_left": 1,
                "status": "fresh",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": True
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"   ✅ Created recipe meal entry #{meal_counter}")
                meal_counter += 1
                time.sleep(0.2)
    
    # Budget challenge
    elif "budget" in goals_text or "save" in goals_text or "spend" in goals_text:
        print("\n💰 Creating budget entries...")
        for i in range(3):
            amount = 15.00 + (i * 5)
            result = create_budget_entry(token, amount, "groceries")
            if result:
                print(f"   ✅ Created budget entry: ${amount:.2f}")
                time.sleep(0.2)
    
    # Zero waste / no leftovers challenge
    elif "zero waste" in goals_text or "no leftover" in goals_text:
        print("\n♻️ Creating zero-waste meal entries...")
        for i in range(3):
            meal_data = {
                "type": "meal",
                "title": f"Zero Waste Meal {meal_counter}",
                "meal_type": "dinner",
                "portions": 2,
                "portions_left": 0,
                "status": "fresh",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": False
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"   ✅ Created zero-waste meal entry #{meal_counter}")
                meal_counter += 1
                time.sleep(0.2)
    
    # One-pot / simple meals
    elif "one-pot" in goals_text or "simple" in goals_text or "easy" in goals_text:
        print("\n🍳 Creating one-pot meal entries...")
        for i in range(3):
            meal_data = {
                "type": "meal",
                "title": f"One-Pot Meal {meal_counter}",
                "meal_type": "dinner",
                "portions": 3,
                "portions_left": 1,
                "status": "fresh",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": True
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"   ✅ Created one-pot meal entry #{meal_counter}")
                meal_counter += 1
                time.sleep(0.2)
    
    # Home cooking / meal prep (fallback for general cooking goals)
    else:
        print("\n🏠 Creating home-cooked meal entries...")
        for i in range(5):
            meal_data = {
                "type": "meal",
                "title": f"Home Cooked Meal {meal_counter}",
                "meal_type": ["breakfast", "lunch", "dinner"][i % 3],
                "portions": 2,
                "portions_left": 0,
                "status": "fresh",
                "is_batch": False,
                "used_leftovers": False,
                "has_leftovers": False
            }
            result = create_meal_entry(token, meal_data)
            if result:
                print(f"   ✅ Created home meal entry #{meal_counter}")
                meal_counter += 1
                time.sleep(0.2)
    
    total_entries = (meal_counter - 1) + purchase_counter
    if purchase_counter > 0:
        print(f"\n✨ Created {total_entries} journal entries ({purchase_counter} purchase, {meal_counter - 1} meal)")
    else:
        print(f"\n✨ Created {meal_counter - 1} journal entries")
    print("⏳ Waiting for automatic goal tracking to process...")
    time.sleep(1)


def test_all_challenges():
    """Main test function"""
    print("\n" + "="*70)
    print("  🎮 MULTI-GOAL CHALLENGE INTERACTIVE TESTER")
    print("="*70)
    
    # Step 1: Login
    token = register_and_login()
    if not token:
        print("\n❌ Test failed at login step")
        return
    
    time.sleep(0.5)
    
    # Step 2: Get all challenges
    challenges = get_all_challenges(token)
    if not challenges:
        print("\n❌ No challenges available - run seed_challenges.py first")
        return
    
    time.sleep(0.5)
    
    # Step 3: Show current active challenges
    print_section("YOUR ACTIVE CHALLENGES")
    active = get_active_challenges(token)
    
    time.sleep(0.5)
    
    # Step 4: Select challenge from menu
    selected_challenge = select_challenge_from_menu(challenges)
    
    if not selected_challenge:
        print("\n👋 No challenge selected. Exiting...")
        return
    
    time.sleep(0.5)
    
    # Check if user wants to run all challenges
    if selected_challenge == "ALL":
        print_section("RUNNING ALL CHALLENGES")
        print(f"\n🚀 Testing all {len(challenges)} challenges sequentially...\n")
        
        for idx, challenge in enumerate(challenges, 1):
            print(f"\n{'='*70}")
            print(f"  📋 Testing Challenge {idx}/{len(challenges)}: {challenge['title']}")
            print(f"{'='*70}\n")
            
            # Assign challenge
            user_challenge_id = assign_challenge(token, challenge['id'], challenge['title'])
            
            if not user_challenge_id:
                active = get_active_challenges(token)
                existing = next((c for c in active if c['challenge_title'] == challenge['title']), None)
                
                if existing:
                    user_challenge_id = existing['id']
                    challenge['id'] = user_challenge_id
                else:
                    print(f"⚠️ Could not assign challenge '{challenge['title']}', skipping...")
                    continue
            else:
                challenge['id'] = user_challenge_id
            
            time.sleep(0.3)
            
            # Show initial state
            get_active_challenges(token)
            time.sleep(0.3)
            
            # Simulate progress
            simulate_progress(token, challenge)
            time.sleep(0.3)
            
            # Show final status for this challenge
            final_active = get_active_challenges(token)
            final_challenge = next((c for c in final_active if str(c['id']) == str(challenge['id'])), None)
            
            if final_challenge:
                if final_challenge['status'] == 'completed':
                    print(f"\n✅ Challenge '{final_challenge['challenge_title']}' COMPLETED!")
                    print(f"💰 Reward: {final_challenge['reward_points']} points")
                else:
                    completion_pct = (final_challenge['completed_goals'] / final_challenge['total_goals'] * 100)
                    print(f"\n📊 Challenge '{final_challenge['challenge_title']}' - {completion_pct:.0f}% complete")
            
            if idx < len(challenges):
                time.sleep(1)
        
        print("\n" + "="*70)
        print(f"  🎊 ALL {len(challenges)} CHALLENGES TESTED!")
        print("="*70 + "\n")
        return
    
    # Single challenge flow
    # Step 5: Assign the selected challenge
    print_section(f"ASSIGNING: {selected_challenge['title']}")
    
    user_challenge_id = assign_challenge(token, selected_challenge['id'], selected_challenge['title'])
    
    if not user_challenge_id:
        # Check if already assigned
        active = get_active_challenges(token)
        existing = next((c for c in active if c['challenge_title'] == selected_challenge['title']), None)
        
        if existing:
            print(f"\n💡 This challenge is already active. Let's work on it!")
            user_challenge_id = existing['id']
            selected_challenge['id'] = user_challenge_id
        else:
            print(f"\n❌ Could not assign challenge")
            return
    else:
        selected_challenge['id'] = user_challenge_id
    
    time.sleep(0.5)
    
    # Step 6: Show initial state
    print_section(f"CHALLENGE STATUS: {selected_challenge['title']}")
    get_active_challenges(token)
    
    time.sleep(0.5)
    
    # Step 7: Automated progress via journal entries
    simulate_progress(token, selected_challenge)
    
    time.sleep(0.5)
    
    # Step 8: Show final status
    print_section("FINAL STATUS")
    final_active = get_active_challenges(token)
    
    final_challenge = next((c for c in final_active if str(c['id']) == str(selected_challenge['id'])), None)
    
    if final_challenge:
        if final_challenge['status'] == 'completed':
            print(f"\n🎊 🎉 CONGRATULATIONS! 🎉 🎊")
            print(f"Challenge '{final_challenge['challenge_title']}' is COMPLETE!")
            print(f"💰 Reward: {final_challenge['reward_points']} points earned!")
        else:
            completion_pct = (final_challenge['completed_goals'] / final_challenge['total_goals'] * 100)
            print(f"\n📊 Progress Summary:")
            print(f"Challenge: {final_challenge['challenge_title']}")
            print(f"Status: {final_challenge['status']}")
            print(f"Completion: {final_challenge['completed_goals']}/{final_challenge['total_goals']} goals ({completion_pct:.0f}%)")
            print(f"Potential Reward: {final_challenge['reward_points']} points")
    
    print("\n" + "="*70)
    print("  ✨ TEST SESSION COMPLETED!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_all_challenges()
