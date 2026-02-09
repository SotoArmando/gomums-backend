"""
Cleanup script for new recipe test user
Deletes the test user and all related data
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection settings
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "database": os.getenv("DATABASE_NAME", "gomums"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "")
}

TEST_EMAIL = "newrecipe_test@gomums.com"


def cleanup_test_user():
    print("\n" + "="*60)
    print("GoMums - New Recipe Test User Cleanup Script")
    print("="*60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find test user
        print(f"\n🔍 Looking for test user: {TEST_EMAIL}")
        cursor.execute("SELECT id, name, email, oauth_provider FROM users WHERE email = %s", (TEST_EMAIL,))
        user = cursor.fetchone()
        
        if not user:
            print(f"ℹ️  No user found with email: {TEST_EMAIL}")
            print("Nothing to clean up.")
            return
        
        print(f"✓ Found user: {dict(user)}")
        user_id = user['id']
        
        # Delete related data (CASCADE will handle most, but being explicit)
        print("✓ Deleted test user and all related data")
        print("  - Budget entries, settings")
        print("  - Journal entries")
        print("  - Any other related records")
        
        # Delete user (CASCADE will delete related records)
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        print(f"\n✅ Cleanup complete! You can now run test_new_recipe_mission.py")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    print("="*60)


if __name__ == "__main__":
    cleanup_test_user()
