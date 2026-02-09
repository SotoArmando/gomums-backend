#!/usr/bin/env python3
"""
Verify budget tables exist and test direct insert
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "database": os.getenv("DATABASE_NAME", "gomums"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "7646")
}

print("="*60)
print("Verifying Budget Tables")
print("="*60)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if tables exist
    print("\n1. Checking if budget tables exist...")
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('budget_entries', 'budget_settings')
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    
    if not tables:
        print("❌ Budget tables do NOT exist!")
        print("\nPlease run: python3 create_budget_tables.py")
    else:
        print(f"✓ Found {len(tables)} budget tables:")
        for table in tables:
            print(f"  - {table['tablename']}")
    
    # Test if we can insert into budget_settings
    print("\n2. Testing budget_settings insert...")
    cursor.execute("SELECT id FROM users LIMIT 1")
    user = cursor.fetchone()
    
    if not user:
        print("❌ No users found. Please create a user first.")
    else:
        user_id = user['id']
        print(f"✓ Using user_id: {user_id}")
        
        # Check if settings already exist
        cursor.execute("SELECT * FROM budget_settings WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"✓ Budget settings already exist: {dict(existing)}")
        else:
            # Try to insert
            cursor.execute("""
                INSERT INTO budget_settings (user_id, weekly_budget, monthly_budget)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (user_id, 150.00, 600.00))
            conn.commit()
            result = cursor.fetchone()
            print(f"✓ Created budget settings: {dict(result)}")
    
    # Test if we can insert into budget_entries
    print("\n3. Testing budget_entries insert...")
    if user:
        cursor.execute("""
            INSERT INTO budget_entries (user_id, date, meal_name, cost, servings, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (user_id, date.today(), "Test Meal", 10.50, 4, "Dinner"))
        conn.commit()
        result = cursor.fetchone()
        print(f"✓ Created budget entry:")
        print(f"  ID: {result['id']}")
        print(f"  Meal: {result['meal_name']}")
        print(f"  Cost: ${result['cost']}")
        print(f"  Cost per serving: ${result['cost_per_serving']}")
        
        # Clean up test entry
        cursor.execute("DELETE FROM budget_entries WHERE id = %s", (result['id'],))
        conn.commit()
        print("✓ Test entry cleaned up")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Budget tables verification complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Restart your server (Ctrl+C and run again)")
    print("2. Run: python3 test_budget.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
