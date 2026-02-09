"""
Migration: Add ingredient_swaps column to journal_entries table
Adds JSONB column to track ingredient substitutions for challenge tracking
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
    """Add ingredient_swaps column to journal_entries"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔄 Checking if ingredient_swaps column exists...")
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'journal_entries' 
            AND column_name = 'ingredient_swaps'
        """)
        
        exists = cursor.fetchone()
        
        if exists:
            print("⚠️  Column 'ingredient_swaps' already exists. Skipping migration.")
            cursor.close()
            conn.close()
            return
        
        print("📝 Adding ingredient_swaps column to journal_entries...")
        
        # Add ingredient_swaps column
        cursor.execute("""
            ALTER TABLE journal_entries
            ADD COLUMN ingredient_swaps JSONB;
        """)
        
        # Add comment
        cursor.execute("""
            COMMENT ON COLUMN journal_entries.ingredient_swaps IS 
            'Array of ingredient swaps: [{recipe_id, original_ingredient, swapped_ingredient}]';
        """)
        
        conn.commit()
        
        print("✅ Successfully added ingredient_swaps column")
        print("📊 Column structure: JSONB - stores array of swap objects")
        print("   Example: [{\"recipe_id\": \"uuid-here\", \"original_ingredient\": \"bacon\", \"swapped_ingredient\": \"beans\"}]")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise


if __name__ == "__main__":
    print("="*70)
    print("  INGREDIENT SWAPS MIGRATION")
    print("="*70)
    apply_migration()
    print("="*70)
