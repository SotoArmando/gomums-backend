#!/usr/bin/env python3
"""
Cleanup script to remove test user from database
Run this before running test_budget.py if you encounter issues
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

TEST_EMAIL = "mission_auto@test.com"


def cleanup_test_user():
    """Remove test user and all related data"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"🔍 Looking for test user: {TEST_EMAIL}")
        
        # Check if user exists
        cursor.execute("SELECT id, name, email, oauth_provider FROM users WHERE email = %s", (TEST_EMAIL,))
        user = cursor.fetchone()
        
        if user:
            print(f"✓ Found user: {dict(user)}")
            user_id = user['id']
            
            # Delete user (CASCADE will handle related records)
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            
            print(f"✓ Deleted test user and all related data")
            print(f"  - Budget entries, settings")
            print(f"  - Journal entries")
            print(f"  - Any other related records")
        else:
            print(f"ℹ No test user found with email: {TEST_EMAIL}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Cleanup complete! You can now run test_budget.py")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("="*60)
    print("GoMums - Test User Cleanup Script")
    print("="*60)
    print()
    cleanup_test_user()
