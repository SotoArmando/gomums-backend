#!/usr/bin/env python3
"""
Create budget tables in the database
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
print("Creating Budget Tables")
print("="*60)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check existing tables
    print("\n1. Checking existing tables...")
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('budget_entries', 'budget_settings')
    """)
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"   Existing budget tables: {existing_tables if existing_tables else 'None'}")
    
    # Create budget_entries table
    print("\n2. Creating budget_entries table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            meal_name VARCHAR(255) NOT NULL,
            cost DECIMAL(10, 2) NOT NULL,
            servings INTEGER NOT NULL,
            cost_per_serving DECIMAL(10, 2) GENERATED ALWAYS AS (cost / NULLIF(servings, 0)) STORED,
            category VARCHAR(100),
            notes TEXT,
            journal_entry_id UUID REFERENCES journal_entries(id) ON DELETE SET NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)
    print("   ✓ budget_entries table created/verified")
    
    # Create index on user_id and date
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_budget_entries_user_date 
        ON budget_entries(user_id, date DESC)
    """)
    print("   ✓ Index on user_id and date created")
    
    # Create budget_settings table
    print("\n3. Creating budget_settings table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            weekly_budget DECIMAL(10, 2),
            monthly_budget DECIMAL(10, 2),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(user_id)
        )
    """)
    print("   ✓ budget_settings table created/verified")
    
    # Commit changes
    conn.commit()
    
    # Verify tables
    print("\n4. Verifying tables...")
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('budget_entries', 'budget_settings')
    """)
    final_tables = [row[0] for row in cursor.fetchall()]
    print(f"   Budget tables: {final_tables}")
    
    # Show table structures
    print("\n5. Table structures:")
    for table in ['budget_entries', 'budget_settings']:
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """)
        print(f"\n   {table}:")
        for col in cursor.fetchall():
            print(f"     - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Budget tables created successfully!")
    print("="*60)
    print("\nYou can now:")
    print("1. Restart your server")
    print("2. Run: python3 test_budget.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
