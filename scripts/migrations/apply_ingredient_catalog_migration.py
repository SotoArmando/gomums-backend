"""
Apply the ingredient_catalog table migration.

Usage:
    python apply_ingredient_catalog_migration.py
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
    """Create the ingredient_catalog table"""
    sql_path = os.path.join(os.path.dirname(__file__), "..", "..", "alembic", "create_ingredient_catalog.sql")

    with open(sql_path, "r") as f:
        sql = f.read()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        print("✅ ingredient_catalog table created successfully")
    except Exception as e:
        print(f"❌ Error creating ingredient_catalog table: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    apply_migration()
