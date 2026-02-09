"""
Seed Multi-Goal Challenges
Creates comprehensive challenges with multiple objectives
"""

import psycopg2
from app.core.config import settings


challenges_data = [
    {
        "title": "Batch Cooking Master",
        "description": "Master the art of batch cooking to save time and money throughout the week",
        "type": "batch_cooking",
        "duration": 7,  # weekly
        "reward_points": 150,
        "goals": [
            {"description": "Cook 3 meals with 3+ servings each", "target": 3, "order_index": 0},
            {"description": "Freeze 2 meals for later", "target": 2, "order_index": 1},
            {"description": "Use batch-cooked meals 5 times", "target": 5, "order_index": 2}
        ]
    },
    {
        "title": "Weekly Savings Challenge",
        "description": "Save money on groceries while eating delicious homemade meals",
        "type": "budget_savings",
        "duration": 7,
        "reward_points": 200,
        "goals": [
            {"description": "Stay under daily budget 5 days", "target": 5, "order_index": 0},
            {"description": "Save $30 total on groceries", "target": 30, "order_index": 1},
            {"description": "Cook 8 meals at home", "target": 8, "order_index": 2}
        ]
    },
    {
        "title": "Zero Waste Week",
        "description": "Reduce food waste by using every ingredient wisely",
        "type": "zero_waste",
        "duration": 7,
        "reward_points": 180,
        "goals": [
            {"description": "Use leftovers 5 times", "target": 5, "order_index": 0},
            {"description": "Cook with scraps or trimmings 3 times", "target": 3, "order_index": 1},
            {"description": "Freeze meals before they spoil 2 times", "target": 2, "order_index": 2}
        ]
    },
    {
        "title": "Cook Streak Challenge",
        "description": "Build a consistent cooking habit by cooking every day",
        "type": "cooking_streak",
        "duration": 7,
        "reward_points": 100,
        "goals": [
            {"description": "Cook for 5 consecutive days", "target": 5, "order_index": 0},
            {"description": "Try 2 new recipes", "target": 2, "order_index": 1},
            {"description": "Cook breakfast 3 times", "target": 3, "order_index": 2}
        ]
    },
    {
        "title": "Swap & Save Challenge",
        "description": "Replace expensive ingredients with budget-friendly alternatives",
        "type": "ingredient_swap",
        "duration": 7,
        "reward_points": 120,
        "goals": [
            {"description": "Log a meal with a swapped ingredient", "target": 1, "order_index": 0}
        ]
    },
    {
        "title": "Weekend Meal Prep Master",
        "description": "Prepare meals ahead for the busy week",
        "type": "meal_prep",
        "duration": 7,
        "reward_points": 140,
        "goals": [
            {"description": "Prep 4 meals in advance", "target": 4, "order_index": 0},
            {"description": "Batch cook 2 recipes", "target": 2, "order_index": 1},
            {"description": "Use prepped meals 6 times", "target": 6, "order_index": 2}
        ]
    },
    {
        "title": "Leftover Makeover Challenge",
        "description": "Transform leftovers into exciting new meals",
        "type": "leftover_creativity",
        "duration": 7,
        "reward_points": 90,
        "goals": [
            {"description": "Create new meals from leftovers 4 times", "target": 4, "order_index": 0},
            {"description": "Avoid throwing away food for 5 days", "target": 5, "order_index": 1},
            {"description": "Save $15 by using leftovers", "target": 15, "order_index": 2}
        ]
    },
    {
        "title": "One Pot Wonder Week",
        "description": "Simplify cooking with one-pot meals",
        "type": "simple_cooking",
        "duration": 7,
        "reward_points": 70,
        "goals": [
            {"description": "Cook 5 one-pot meals", "target": 5, "order_index": 0},
            {"description": "Save 3 hours on cleanup", "target": 3, "order_index": 1},
            {"description": "Try 2 new simple recipes", "target": 2, "order_index": 2}
        ]
    },
    {
        "title": "No Spend Weekend",
        "description": "Challenge yourself to cook without buying any groceries for the weekend",
        "type": "no_spend",
        "duration": 3,  # weekend
        "reward_points": 80,
        "goals": [
            {"description": "Cook all meals from pantry/fridge items", "target": 6, "order_index": 0},
            {"description": "Use up 5 leftover ingredients", "target": 5, "order_index": 1},
            {"description": "Create 2 creative meals from what you have", "target": 2, "order_index": 2}
        ]
    },
    {
        "title": "Budget Boss Challenge",
        "description": "Master your food budget for an entire month",
        "type": "budget_master",
        "duration": 30,  # monthly
        "reward_points": 300,
        "goals": [
            {"description": "Stay under daily budget 20 days", "target": 20, "order_index": 0},
            {"description": "Save $100 total on groceries", "target": 100, "order_index": 1},
            {"description": "Cook 50 meals at home", "target": 50, "order_index": 2},
            {"description": "Use leftovers 15 times", "target": 15, "order_index": 3}
        ]
    },
    {
        "title": "New Recipe Explorer",
        "description": "Expand your cooking skills by trying new dishes",
        "type": "recipe_exploration",
        "duration": 14,  # bi-weekly
        "reward_points": 110,
        "goals": [
            {"description": "Try 5 new recipes", "target": 5, "order_index": 0},
            {"description": "Cook recipes from 3 different cuisines", "target": 3, "order_index": 1},
            {"description": "Share 2 recipes with friends", "target": 2, "order_index": 2}
        ]
    }
]


def seed_challenges():
    """Seed multi-goal challenges into the database"""
    conn = None
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("🌱 Seeding multi-goal challenges...")
        
        for challenge_data in challenges_data:
            # Insert challenge
            cursor.execute("""
                INSERT INTO challenges 
                (title, description, type, duration, reward_points)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                challenge_data["title"],
                challenge_data["description"],
                challenge_data["type"],
                challenge_data["duration"],
                challenge_data["reward_points"]
            ))
            
            challenge_id = cursor.fetchone()[0]
            
            # Insert goals for this challenge
            for goal in challenge_data["goals"]:
                cursor.execute("""
                    INSERT INTO challenge_goals
                    (challenge_id, description, target, order_index)
                    VALUES (%s, %s, %s, %s)
                """, (
                    challenge_id,
                    goal["description"],
                    goal["target"],
                    goal["order_index"]
                ))
            
            print(f"  ✅ Created: {challenge_data['title']} ({len(challenge_data['goals'])} goals)")
        
        conn.commit()
        
        # Display summary
        cursor.execute("SELECT COUNT(*) FROM challenges")
        challenge_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM challenge_goals")
        goal_count = cursor.fetchone()[0]
        
        print(f"\n✅ Successfully seeded {challenge_count} challenges with {goal_count} total goals")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error seeding challenges: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise


if __name__ == "__main__":
    seed_challenges()
