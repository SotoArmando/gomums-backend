"""
Migration: Add structured steps column to recipes table
Steps have phases (prep, cooking, serve) and reference specific ingredients/items

Run: python apply_recipe_steps_migration.py
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def apply_migration():
    """Add steps JSONB column to recipes and backfill from instructions"""
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )

    try:
        with conn.cursor() as cur:
            # 1. Add steps column
            print("Adding 'steps' JSONB column to recipes table...")
            cur.execute("""
                ALTER TABLE recipes
                ADD COLUMN IF NOT EXISTS steps JSONB DEFAULT '[]'::jsonb
            """)
            print("  ✓ Column added")

            # 2. Add GIN index for efficient JSONB queries
            print("Adding GIN index on steps column...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipes_steps
                ON recipes USING gin (steps)
            """)
            print("  ✓ Index created")

            # 3. Backfill existing instructions as "cooking" phase steps
            print("Backfilling existing instructions into steps...")
            cur.execute("""
                UPDATE recipes
                SET steps = (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'order', ordinality,
                            'phase', 'cooking',
                            'text', instruction,
                            'items', '[]'::jsonb,
                            'time_minutes', NULL,
                            'tip', NULL
                        )
                    )
                    FROM unnest(instructions) WITH ORDINALITY AS t(instruction, ordinality)
                )
                WHERE instructions IS NOT NULL
                  AND array_length(instructions, 1) > 0
                  AND (steps IS NULL OR steps = '[]'::jsonb)
            """)
            backfilled = cur.rowcount
            print(f"  ✓ Backfilled {backfilled} recipes")

            conn.commit()
            print("\n✅ Migration complete!")
            print("   - Added 'steps' JSONB column to recipes")
            print("   - Created GIN index for efficient queries")
            print(f"   - Backfilled {backfilled} existing recipes with default 'cooking' phase")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    apply_migration()
