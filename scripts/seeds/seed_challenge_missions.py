"""
Seed script for challenge missions
Adds various cooking and budget challenge missions to the database
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Challenge missions to add
CHALLENGE_MISSIONS = [
    {
        'title': 'Batch Cooking Challenge',
        'description': 'Cook meals in batches to save time. Prepare 3+ portions in a single cooking session.',
        'type': 'weekly',
        'category': 'cooking',
        'difficulty': 'medium',
        'target': 3,  # 3 batch cooking sessions
        'reward_points': 100,
        'kind': 'challenge'
    },
    {
        'title': 'Weekly Savings Challenge',
        'description': 'Save money on groceries this week. Stay under your weekly budget.',
        'type': 'weekly',
        'category': 'budget',
        'difficulty': 'medium',
        'target': 7,  # 7 days under budget
        'reward_points': 150,
        'kind': 'challenge'
    },
    {
        'title': 'No Spend Weekend',
        'description': 'Complete a weekend without spending money on food. Use what you have!',
        'type': 'weekly',
        'category': 'budget',
        'difficulty': 'hard',
        'target': 2,  # 2 days (Saturday & Sunday)
        'reward_points': 200,
        'kind': 'challenge'
    },
    {
        'title': 'Swap Challenge',
        'description': 'Replace expensive ingredients with affordable alternatives in your recipes.',
        'type': 'weekly',
        'category': 'cooking',
        'difficulty': 'medium',
        'target': 5,  # 5 ingredient swaps
        'reward_points': 80,
        'kind': 'challenge'
    },
    {
        'title': 'Swap & Save Challenge',
        'description': 'Make ingredient swaps that reduce your meal costs by at least 20%.',
        'type': 'weekly',
        'category': 'budget',
        'difficulty': 'hard',
        'target': 3,  # 3 cost-reducing swaps
        'reward_points': 120,
        'kind': 'challenge'
    },
    {
        'title': 'One Pot Wonder',
        'description': 'Master one-pot meals! Cook complete meals using only one pot or pan.',
        'type': 'weekly',
        'category': 'cooking',
        'difficulty': 'easy',
        'target': 4,  # 4 one-pot meals
        'reward_points': 70,
        'kind': 'challenge'
    },
    {
        'title': 'Cook Streak',
        'description': 'Build a cooking habit! Cook at home for 5 consecutive days.',
        'type': 'weekly',
        'category': 'cooking',
        'difficulty': 'medium',
        'target': 5,  # 5 days in a row
        'reward_points': 100,
        'kind': 'challenge'
    },
    {
        'title': 'Leftover Makeover',
        'description': 'Transform leftovers into new meals. Create 3 new dishes from yesterday\'s meals.',
        'type': 'weekly',
        'category': 'cooking',
        'difficulty': 'medium',
        'target': 3,  # 3 leftover transformations
        'reward_points': 90,
        'kind': 'challenge'
    },
    {
        'title': 'Batch Prep Master',
        'description': 'Meal prep like a pro! Prepare 10+ portions in one batch cooking session.',
        'type': 'monthly',
        'category': 'cooking',
        'difficulty': 'hard',
        'target': 10,  # 10 portions
        'reward_points': 250,
        'kind': 'challenge'
    },
    {
        'title': 'Zero Waste Week',
        'description': 'Use all your groceries! Complete a week with minimal food waste.',
        'type': 'weekly',
        'category': 'cooking',
        'difficulty': 'hard',
        'target': 7,  # 7 days
        'reward_points': 180,
        'kind': 'challenge'
    }
]


def seed_challenge_missions():
    """Add challenge missions to the database"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database=os.getenv('DATABASE_NAME', 'gomums'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', '7646')
        )
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n" + "="*60)
        print("Seeding Challenge Missions")
        print("="*60)
        
        added_count = 0
        skipped_count = 0
        
        for mission in CHALLENGE_MISSIONS:
            # Check if mission already exists
            cursor.execute(
                "SELECT id FROM missions WHERE title = %s",
                (mission['title'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                print(f"⏭️  Skipped: {mission['title']} (already exists)")
                skipped_count += 1
                continue
            
            # Insert new mission
            mission_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO missions (
                    id, title, description, type, category, 
                    difficulty, target, reward_points, kind
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                mission_id,
                mission['title'],
                mission['description'],
                mission['type'],
                mission['category'],
                mission['difficulty'],
                mission['target'],
                mission['reward_points'],
                mission.get('kind', 'challenge')
            ))
            
            print(f"✅ Added: {mission['title']}")
            print(f"   Type: {mission['type']}, Difficulty: {mission['difficulty']}, Points: {mission['reward_points']}")
            added_count += 1
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print(f"✅ Seeding complete!")
        print(f"   Added: {added_count} new missions")
        print(f"   Skipped: {skipped_count} existing missions")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error seeding missions: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    seed_challenge_missions()
