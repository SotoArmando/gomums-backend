#!/usr/bin/env python3
"""
Fix the oauth_provider check constraint in the database
"""

import psycopg2
import os
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
print("Fixing oauth_provider Constraint")
print("="*60)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check current constraint
    print("\n1. Checking current constraint...")
    cursor.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conname = 'users_oauth_provider_check'
    """)
    result = cursor.fetchone()
    
    if result:
        print(f"✓ Current constraint: {result[0]}")
        print(f"  Definition: {result[1]}")
    else:
        print("ℹ No constraint found")
    
    # Drop old constraint
    print("\n2. Dropping old constraint...")
    try:
        cursor.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_oauth_provider_check")
        conn.commit()
        print("✓ Old constraint dropped")
    except Exception as e:
        print(f"ℹ {e}")
        conn.rollback()
    
    # Add new constraint with 'email' included
    print("\n3. Adding new constraint with 'email' support...")
    cursor.execute("""
        ALTER TABLE users 
        ADD CONSTRAINT users_oauth_provider_check 
        CHECK (oauth_provider IN ('google', 'facebook', 'apple', 'email'))
    """)
    conn.commit()
    print("✓ New constraint added")
    
    # Verify
    print("\n4. Verifying new constraint...")
    cursor.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conname = 'users_oauth_provider_check'
    """)
    result = cursor.fetchone()
    
    if result:
        print(f"✓ Constraint verified: {result[0]}")
        print(f"  Definition: {result[1]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Constraint fixed successfully!")
    print("="*60)
    print("\nYou can now:")
    print("1. Restart your server")
    print("2. Run: python3 test_budget.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
