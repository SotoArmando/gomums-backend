#!/usr/bin/env python3
"""
Migration: Add has_leftovers field to journal_entries
This field indicates when a meal wasn't fully consumed and leftovers remain
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


def apply_migration():
    """Add has_leftovers column to journal_entries table"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔄 Applying migration: Add has_leftovers to journal_entries")
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'journal_entries' 
            AND column_name = 'has_leftovers'
        """)
        
        if cursor.fetchone():
            print("⚠️  Column 'has_leftovers' already exists. Skipping migration.")
            cursor.close()
            conn.close()
            return
        
        # Add the column
        cursor.execute("""
            ALTER TABLE journal_entries 
            ADD COLUMN has_leftovers BOOLEAN DEFAULT FALSE
        """)
        
        # Add comment for documentation
        cursor.execute("""
            COMMENT ON COLUMN journal_entries.has_leftovers 
            IS 'Indicates meal was not fully consumed and leftovers remain'
        """)
        
        # Optionally: Update existing records where portions_left > 0
        cursor.execute("""
            UPDATE journal_entries 
            SET has_leftovers = TRUE 
            WHERE type = 'meal' AND portions_left > 0
        """)
        
        updated_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Migration applied successfully!")
        print(f"   - Column 'has_leftovers' added to journal_entries")
        print(f"   - Updated {updated_count} existing meal entries with leftovers")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    apply_migration()
