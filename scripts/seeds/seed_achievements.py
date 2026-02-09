"""
Seed Achievements

Seeds predefined achievements into the database.
Run this after database setup to populate achievements.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "gomums_db"),
    "user": os.getenv("DB_USER", "gomums_user"),
    "password": os.getenv("DB_PASSWORD")
}


# Predefined achievements
ACHIEVEMENTS = [
    # Cooking Milestones
    {
        "title": "First Steps",
        "description": "Cook your first meal at home",
        "icon": "🍳",
        "category": "cooking",
        "target": 1,
        "points": 10
    },
    {
        "title": "Getting Started",
        "description": "Cook 5 meals at home",
        "icon": "👨‍🍳",
        "category": "cooking",
        "target": 5,
        "points": 25
    },
    {
        "title": "Home Chef",
        "description": "Cook 25 meals at home",
        "icon": "👩‍🍳",
        "category": "cooking",
        "target": 25,
        "points": 50
    },
    {
        "title": "Master Chef",
        "description": "Cook 50 meals at home",
        "icon": "🏆",
        "category": "cooking",
        "target": 50,
        "points": 100
    },
    {
        "title": "Century Club",
        "description": "Cook 100 meals at home",
        "icon": "💯",
        "category": "cooking",
        "target": 100,
        "points": 250
    },
    
    # Savings Milestones
    {
        "title": "Penny Pincher",
        "description": "Save $50 by cooking at home",
        "icon": "💰",
        "category": "savings",
        "target": 50,
        "points": 25
    },
    {
        "title": "Money Saver",
        "description": "Save $100 by cooking at home",
        "icon": "💵",
        "category": "savings",
        "target": 100,
        "points": 50
    },
    {
        "title": "Budget Boss",
        "description": "Save $500 by cooking at home",
        "icon": "💸",
        "category": "savings",
        "target": 500,
        "points": 100
    },
    {
        "title": "Savings Star",
        "description": "Save $1000 by cooking at home",
        "icon": "⭐",
        "category": "savings",
        "target": 1000,
        "points": 200
    },
    
    # Streak Achievements
    {
        "title": "Consistency",
        "description": "Maintain a 3-day cooking streak",
        "icon": "🔥",
        "category": "streak",
        "target": 3,
        "points": 15
    },
    {
        "title": "Week Warrior",
        "description": "Maintain a 7-day cooking streak",
        "icon": "📅",
        "category": "streak",
        "target": 7,
        "points": 50
    },
    {
        "title": "Streak Master",
        "description": "Maintain a 30-day cooking streak",
        "icon": "🎯",
        "category": "streak",
        "target": 30,
        "points": 150
    },
    {
        "title": "Unstoppable",
        "description": "Maintain a 100-day cooking streak",
        "icon": "🚀",
        "category": "streak",
        "target": 100,
        "points": 500
    },
    
    # Challenge Achievements
    {
        "title": "Challenge Accepted",
        "description": "Complete your first challenge",
        "icon": "🎪",
        "category": "challenges",
        "target": 1,
        "points": 20
    },
    {
        "title": "Challenge Champion",
        "description": "Complete 5 challenges",
        "icon": "🏅",
        "category": "challenges",
        "target": 5,
        "points": 75
    },
    {
        "title": "Challenge Master",
        "description": "Complete 10 challenges",
        "icon": "👑",
        "category": "challenges",
        "target": 10,
        "points": 200
    },
    
    # Mission Achievements
    {
        "title": "Mission Starter",
        "description": "Complete your first mission",
        "icon": "📋",
        "category": "missions",
        "target": 1,
        "points": 10
    },
    {
        "title": "Mission Runner",
        "description": "Complete 10 missions",
        "icon": "🎖️",
        "category": "missions",
        "target": 10,
        "points": 50
    },
    {
        "title": "Mission Expert",
        "description": "Complete 50 missions",
        "icon": "⚡",
        "category": "missions",
        "target": 50,
        "points": 150
    },
    
    # Special Achievements
    {
        "title": "Early Adopter",
        "description": "Join GoMums in the early days",
        "icon": "🌟",
        "category": "special",
        "target": 1,
        "points": 50
    },
    {
        "title": "Batch Cooking Pro",
        "description": "Cook 10 batch meals",
        "icon": "🍲",
        "category": "special",
        "target": 10,
        "points": 75
    },
    {
        "title": "Zero Waste Hero",
        "description": "Use leftovers in 20 meals",
        "icon": "♻️",
        "category": "special",
        "target": 20,
        "points": 100
    }
]


def seed_achievements():
    """Seed achievements into database"""
    print("\n" + "="*50)
    print("SEEDING ACHIEVEMENTS")
    print("="*50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"\n✓ Connected to database: {DB_CONFIG['database']}")
        
        created = 0
        skipped = 0
        
        for achievement in ACHIEVEMENTS:
            # Check if already exists
            cursor.execute("""
                SELECT id FROM achievements WHERE title = %s
            """, (achievement['title'],))
            
            if cursor.fetchone():
                print(f"  ⊘ {achievement['icon']} {achievement['title']} (already exists)")
                skipped += 1
                continue
            
            # Insert achievement
            cursor.execute("""
                INSERT INTO achievements (title, description, icon, category, target, points)
                VALUES (%(title)s, %(description)s, %(icon)s, %(category)s, %(target)s, %(points)s)
            """, achievement)
            
            print(f"  ✓ {achievement['icon']} {achievement['title']} - {achievement['points']} points (target: {achievement['target']})")
            created += 1
        
        conn.commit()
        
        print("\n" + "="*50)
        print(f"✓ Seeding complete!")
        print(f"  Created: {created}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {len(ACHIEVEMENTS)}")
        print("="*50 + "\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error seeding achievements: {e}")


if __name__ == "__main__":
    seed_achievements()
