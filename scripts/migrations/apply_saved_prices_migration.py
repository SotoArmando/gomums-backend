"""
Apply the saved_ingredient_prices table migration.

Usage:
    python apply_saved_prices_migration.py
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('DATABASE_USER', 'postgres')}:{os.getenv('DATABASE_PASSWORD', 'postgres')}"
    f"@{os.getenv('DATABASE_HOST', 'localhost')}:{os.getenv('DATABASE_PORT', '5432')}"
    f"/{os.getenv('DATABASE_NAME', 'gomums')}",
)


def apply_migration():
    """Run the SQL migration file"""
    sql_path = os.path.join(os.path.dirname(__file__), "..", "..", "alembic", "create_saved_ingredient_prices.sql")

    with open(sql_path, "r") as f:
        sql = f.read()

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("✓ saved_ingredient_prices table created successfully")
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    apply_migration()
