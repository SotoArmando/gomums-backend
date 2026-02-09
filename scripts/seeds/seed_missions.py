"""
Seed sample missions into the database for testing
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Sample missions for testing
SAMPLE_MISSIONS = [
    {
        "title": "Cook 3 meals at home",
        "description": "Prepare and cook 3 meals at home to save money and eat healthier",
        "type": "daily",
        "category": "cooking",
        "difficulty": "easy",
        "target": 3,
        "reward_points": 50
    },
    {
        "title": "Stay under budget",
        "description": "Track your spending and stay within your daily budget",
        "type": "daily",
        "category": "budget",
        "difficulty": "medium",
        "target": 1,
        "reward_points": 30
    },
    {
        "title": "Log your meals",
        "description": "Record all your meals in the journal for the day",
        "type": "daily",
        "category": "tracking",
        "difficulty": "easy",
        "target": 3,
        "reward_points": 20
    },
    {
        "title": "Try a new recipe",
        "description": "Cook a recipe you've never made before",
        "type": "daily",
        "category": "cooking",
        "difficulty": "medium",
        "target": 1,
        "reward_points": 40
    },
    {
        "title": "Meal prep Sunday",
        "description": "Prepare 5 or more meals for the upcoming week",
        "type": "weekly",
        "category": "meal-prep",
        "difficulty": "hard",
        "target": 5,
        "reward_points": 200
    },
    {
        "title": "Cook 15 meals this week",
        "description": "Cook at least 15 meals at home instead of eating out",
        "type": "weekly",
        "category": "cooking",
        "difficulty": "medium",
        "target": 15,
        "reward_points": 150
    },
    {
        "title": "Weekly budget champion",
        "description": "Stay within your weekly budget for 7 consecutive days",
        "type": "weekly",
        "category": "budget",
        "difficulty": "hard",
        "target": 7,
        "reward_points": 180
    },
    {
        "title": "Vegetarian week",
        "description": "Cook 5 vegetarian meals this week",
        "type": "weekly",
        "category": "healthy",
        "difficulty": "medium",
        "target": 5,
        "reward_points": 120
    },
    {
        "title": "Monthly meal master",
        "description": "Cook 60 meals at home this month",
        "type": "monthly",
        "category": "cooking",
        "difficulty": "hard",
        "target": 60,
        "reward_points": 500
    },
    {
        "title": "Save $200 this month",
        "description": "Save at least $200 by cooking at home instead of eating out",
        "type": "monthly",
        "category": "budget",
        "difficulty": "hard",
        "target": 200,
        "reward_points": 400
    },
    {
        "title": "Recipe explorer",
        "description": "Try 10 new recipes this month",
        "type": "monthly",
        "category": "cooking",
        "difficulty": "medium",
        "target": 10,
        "reward_points": 300
    },
    {
        "title": "Perfect journaling",
        "description": "Log meals every single day for a month",
        "type": "monthly",
        "category": "tracking",
        "difficulty": "hard",
        "target": 30,
        "reward_points": 350
    }
]


def seed_missions():
    """Insert sample missions into the database"""
    
    # Connect to database
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    
    try:
        with conn.cursor() as cur:
            # Check if missions already exist
            cur.execute("SELECT COUNT(*) FROM missions")
            count = cur.fetchone()[0]
            
            if count > 0:
                print(f"ℹ  Database already has {count} missions.")
                response = input("Do you want to clear existing missions and add sample data? (yes/no): ")
                if response.lower() == 'yes':
                    cur.execute("DELETE FROM user_missions")
                    cur.execute("DELETE FROM missions")
                    print("✓ Cleared existing missions")
                else:
                    print("⏭  Skipping mission seeding")
                    return
            
            # Insert sample missions
            insert_query = """
                INSERT INTO missions (
                    title, description, type, category, difficulty, target, reward_points
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            for mission in SAMPLE_MISSIONS:
                cur.execute(insert_query, (
                    mission["title"],
                    mission["description"],
                    mission["type"],
                    mission["category"],
                    mission["difficulty"],
                    mission["target"],
                    mission["reward_points"]
                ))
                print(f"✓ Added mission: {mission['title']} ({mission['type']})")
            
            conn.commit()
            print(f"\n✅ Successfully seeded {len(SAMPLE_MISSIONS)} missions!")
            print(f"   - Daily: {sum(1 for m in SAMPLE_MISSIONS if m['type'] == 'daily')}")
            print(f"   - Weekly: {sum(1 for m in SAMPLE_MISSIONS if m['type'] == 'weekly')}")
            print(f"   - Monthly: {sum(1 for m in SAMPLE_MISSIONS if m['type'] == 'monthly')}")
            
    except Exception as e:
        print(f"✗ Error seeding missions: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("="*60)
    print("GoMums - Mission Database Seeding")
    print("="*60)
    seed_missions()
