"""
Apply Mission Goals Tables Migration
Adds multi-goal support to missions system
"""

import psycopg2
import os
from app.core.config import settings

def apply_migration():
    """Apply the mission goals tables migration"""
    conn = None
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("📊 Applying mission goals tables migration...")
        print("   (Tables may already exist - will create if missing)")
        
        # Read migration file
        sql_path = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic', 'add_mission_goals_tables.sql')
        with open(sql_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration applied successfully!")
        print("\nTables created:")
        print("  - mission_goals")
        print("  - user_mission_goals")
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('mission_goals', 'user_mission_goals')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Verified {len(tables)} tables exist")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    apply_migration()
