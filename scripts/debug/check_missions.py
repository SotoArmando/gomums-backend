"""
Quick script to check what missions exist in the database
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DATABASE_HOST'),
    port=os.getenv('DATABASE_PORT'),
    database=os.getenv('DATABASE_NAME'),
    user=os.getenv('DATABASE_USER'),
    password=os.getenv('DATABASE_PASSWORD')
)

try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get all missions
        cur.execute("""
            SELECT id, title, type, category, difficulty, target, reward_points
            FROM missions
            ORDER BY type, category, title
        """)
        
        missions = cur.fetchall()
        
        print("\n" + "="*60)
        print("Missions in Database")
        print("="*60)
        
        if not missions:
            print("\n⚠️  No missions found in database!")
            print("Run: python3 seed_missions.py")
        else:
            print(f"\nFound {len(missions)} missions:\n")
            
            for mission in missions:
                print(f"✓ {mission['title']}")
                print(f"  Category: {mission['category']}, Type: {mission['type']}, Target: {mission['target']}")
                print(f"  Difficulty: {mission['difficulty']}, Points: {mission['reward_points']}")
                print(f"  ID: {mission['id']}")
                print()
        
        # Check specifically for "Try a new recipe"
        cur.execute("""
            SELECT * FROM missions 
            WHERE LOWER(title) LIKE '%new recipe%'
        """)
        
        new_recipe = cur.fetchone()
        
        print("="*60)
        if new_recipe:
            print("✅ 'Try a new recipe' mission EXISTS in database")
        else:
            print("❌ 'Try a new recipe' mission NOT FOUND in database")
            print("   Run: python3 seed_missions.py")
        print("="*60)
        
finally:
    conn.close()
