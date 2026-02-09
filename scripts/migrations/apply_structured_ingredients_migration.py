"""
Apply the structured_ingredients column migration to the recipes table.

Usage:
    python apply_structured_ingredients_migration.py
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "gomums"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}


def apply_migration():
    """Add structured_ingredients column to recipes table"""
    sql_path = os.path.join(os.path.dirname(__file__), "..", "..", "alembic", "add_structured_ingredients.sql")

    with open(sql_path, "r") as f:
        sql = f.read()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        print("✅ structured_ingredients column added to recipes table")
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    apply_migration()
