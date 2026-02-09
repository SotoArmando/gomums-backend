"""
Apply mission kind migration and seed challenges
Run this to add the 'kind' distinction between missions and challenges
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def apply_migration():
    """Apply the mission kind migration"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database=os.getenv('DATABASE_NAME', 'gomums'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', '7646')
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("Applying Mission Kind Migration")
        print("="*60)
        
        # Read migration file
        sql_path = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic', 'add_mission_kind.sql')
        with open(sql_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        
        print("\n✅ Migration applied successfully!")
        print("   - Added 'kind' column to missions table")
        print("   - Updated existing challenges with kind='challenge'")
        print("   - Created index on kind column")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("Migration Complete!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    apply_migration()
