"""
Cleanup script for mission cooldown test
Removes the cooldown_test@gomums.com user and all related data
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TEST_EMAIL = "cooldown_test@gomums.com"

def cleanup_test_user():
    """Remove test user and all related data"""
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
        
        print(f"\n🔍 Looking for test user: {TEST_EMAIL}")
        
        # Find user ID
        cursor.execute("SELECT * FROM users WHERE email = %s", (TEST_EMAIL,))
        user = cursor.fetchone()
        
        if not user:
            print(f"ℹ️  Test user not found - nothing to clean up")
            return
        
        user_id = user['id']
        print(f"✓ Found user: {dict(user)}")
        
        # Delete related data in order (respecting foreign keys)
        tables_to_clean = [
            ('user_missions', 'user_id'),
            ('user_stats', 'user_id'),
            ('journal_entries', 'user_id'),
            ('budget_entries', 'user_id'),
            ('budget_settings', 'user_id'),
            ('recipes', 'user_id'),
        ]
        
        for table, column in tables_to_clean:
            cursor.execute(f"DELETE FROM {table} WHERE {column} = %s", (user_id,))
            deleted = cursor.rowcount
            if deleted > 0:
                print(f"✓ Deleted {deleted} record(s) from {table}")
        
        # Finally delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        print(f"✓ Deleted test user")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ Cleanup complete! You can now run test_mission_cooldown.py")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    cleanup_test_user()
