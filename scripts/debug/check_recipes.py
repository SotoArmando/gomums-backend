"""
Simple utility to check recipe counts in the database
Useful for verifying recipe generation results
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def check_recipe_counts():
    """Display recipe counts by region and category"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database=os.getenv('DATABASE_NAME', 'gomums'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', '')
        )
        
        print("\n" + "=" * 60)
        print("Recipe Database Statistics")
        print("=" * 60 + "\n")
        
        with conn.cursor() as cur:
            # Total recipes
            cur.execute("SELECT COUNT(*) FROM recipes")
            total = cur.fetchone()[0]
            print(f"📊 Total Recipes: {total}")
            
            # Dominican Republic recipes
            cur.execute("SELECT COUNT(*) FROM recipes WHERE 'dominican-republic' = ANY(tags)")
            dr_count = cur.fetchone()[0]
            print(f"🇩🇴 Dominican Republic: {dr_count} recipes")
            
            # Kansas recipes
            cur.execute("SELECT COUNT(*) FROM recipes WHERE 'kansas' = ANY(tags)")
            ks_count = cur.fetchone()[0]
            print(f"🌾 Kansas: {ks_count} recipes")
            
            # Other recipes
            other_count = total - dr_count - ks_count
            print(f"🍽️  Other Regions: {other_count} recipes")
            
            print("\n" + "-" * 60)
            print("Recipes by Category")
            print("-" * 60 + "\n")
            
            # By category
            cur.execute("""
                SELECT category, COUNT(*) as count 
                FROM recipes 
                WHERE category IS NOT NULL
                GROUP BY category 
                ORDER BY count DESC
            """)
            
            for row in cur.fetchall():
                category, count = row
                print(f"  {category}: {count}")
            
            print("\n" + "-" * 60)
            print("Recipes by Difficulty")
            print("-" * 60 + "\n")
            
            # By difficulty
            cur.execute("""
                SELECT difficulty, COUNT(*) as count 
                FROM recipes 
                WHERE difficulty IS NOT NULL
                GROUP BY difficulty 
                ORDER BY count DESC
            """)
            
            for row in cur.fetchall():
                difficulty, count = row
                print(f"  {difficulty.capitalize()}: {count}")
            
            print("\n" + "-" * 60)
            print("Featured Recipes")
            print("-" * 60 + "\n")
            
            # Featured recipes
            cur.execute("SELECT COUNT(*) FROM recipes WHERE featured = TRUE")
            featured = cur.fetchone()[0]
            print(f"  ⭐ Featured: {featured}")
            
            print("\n" + "-" * 60)
            print("Sample Dominican Republic Recipes")
            print("-" * 60 + "\n")
            
            # Sample DR recipes
            cur.execute("""
                SELECT name, category, difficulty 
                FROM recipes 
                WHERE 'dominican-republic' = ANY(tags)
                LIMIT 5
            """)
            
            for i, row in enumerate(cur.fetchall(), 1):
                name, category, difficulty = row
                print(f"  {i}. {name} ({category}, {difficulty})")
            
            print("\n" + "-" * 60)
            print("Sample Kansas Recipes")
            print("-" * 60 + "\n")
            
            # Sample KS recipes
            cur.execute("""
                SELECT name, category, difficulty 
                FROM recipes 
                WHERE 'kansas' = ANY(tags)
                LIMIT 5
            """)
            
            for i, row in enumerate(cur.fetchall(), 1):
                name, category, difficulty = row
                print(f"  {i}. {name} ({category}, {difficulty})")
        
        conn.close()
        print("\n" + "=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Please ensure PostgreSQL is running and .env is configured correctly.\n")


if __name__ == "__main__":
    check_recipe_counts()
