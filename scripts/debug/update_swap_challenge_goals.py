"""
Update Swap & Save Challenge goals to require only 1 completion each
Changes target from 4 and 5 to 1 for protein and vegetable goals
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "database": os.getenv("DATABASE_NAME", "gomums"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "7646")
}


def update_goals():
    """Update Swap & Save Challenge to have single simple goal"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔄 Updating Swap & Save Challenge goals...")
        
        # Get the challenge ID
        cursor.execute("""
            SELECT id FROM challenges 
            WHERE title = 'Swap & Save Challenge'
        """)
        
        challenge = cursor.fetchone()
        if not challenge:
            print("⚠️  Swap & Save Challenge not found!")
            return
        
        challenge_id = challenge['id']
        
        # Delete old goals
        cursor.execute("""
            DELETE FROM challenge_goals 
            WHERE challenge_id = %s
        """, (challenge_id,))
        
        deleted_count = cursor.rowcount
        
        # Insert new simple goal
        cursor.execute("""
            INSERT INTO challenge_goals (challenge_id, description, target, order_index)
            VALUES (%s, 'Log a meal with a swapped ingredient', 1, 0)
        """, (challenge_id,))
        
        conn.commit()
        
        print(f"✅ Deleted {deleted_count} old goal(s)")
        print(f"✅ Created 1 new simplified goal")
        print("📊 Goal: Just log any meal with ingredient_swaps data to complete!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise


if __name__ == "__main__":
    print("="*70)
    print("  UPDATE SWAP & SAVE CHALLENGE GOALS")
    print("="*70)
    update_goals()
    print("="*70)
