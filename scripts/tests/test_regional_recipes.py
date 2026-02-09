"""
Test script to validate regional recipe generation logic
Tests CSV parsing and database connection (without OpenAI)
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from scripts.seeds.seed_regional_recipes import read_ingredients_from_csv
from dotenv import load_dotenv

load_dotenv()


def test_csv_parsing():
    """Test that CSV files can be read and ingredients extracted"""
    print("=" * 60)
    print("Testing CSV Parsing")
    print("=" * 60 + "\n")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Test Dominican Republic
    dr_csv = os.path.join(base_dir, "excel docs", "Dominican Republic.csv")
    if os.path.exists(dr_csv):
        dr_ingredients = read_ingredients_from_csv(dr_csv)
        print(f"✓ Dominican Republic CSV: {len(dr_ingredients)} ingredients found")
        print(f"  Sample: {', '.join(dr_ingredients[:5])}")
    else:
        print(f"✗ Dominican Republic CSV not found at: {dr_csv}")
        return False
    
    # Test Kansas
    ks_csv = os.path.join(base_dir, "excel docs", "Kansas.csv")
    if os.path.exists(ks_csv):
        ks_ingredients = read_ingredients_from_csv(ks_csv)
        print(f"✓ Kansas CSV: {len(ks_ingredients)} ingredients found")
        print(f"  Sample: {', '.join(ks_ingredients[:5])}")
    else:
        print(f"✗ Kansas CSV not found at: {ks_csv}")
        return False
    
    print("\n✅ CSV parsing test passed!\n")
    return True


def test_database_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60 + "\n")
    
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database=os.getenv('DATABASE_NAME', 'gomums'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', '')
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM recipes")
            count = cur.fetchone()[0]
            print(f"✓ Database connection successful")
            print(f"  Current recipe count: {count}")
        
        conn.close()
        print("\n✅ Database connection test passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Please ensure PostgreSQL is running and credentials are correct in .env")
        return False


def test_openai_config():
    """Test OpenAI API configuration"""
    print("=" * 60)
    print("Testing OpenAI Configuration")
    print("=" * 60 + "\n")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("  Recipe generation will not work without an API key")
        print("  Add OPENAI_API_KEY to your .env file to enable AI generation")
        return False
    
    if api_key.startswith('sk-'):
        print("✓ OPENAI_API_KEY is configured")
        print(f"  Key format looks valid (starts with expected prefix)")
        print("\n✅ OpenAI configuration test passed!\n")
        return True
    elif api_key.startswith('your-'):
        print("⚠️  OPENAI_API_KEY appears to be a placeholder value")
        print("  Please replace 'your-openai-api-key-here' with your actual API key")
        return False
    else:
        print("⚠️  OPENAI_API_KEY format may be invalid")
        print("  OpenAI API keys typically start with 'sk-'")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Regional Recipe Generation - Validation Tests")
    print("=" * 60 + "\n")
    
    results = {
        "CSV Parsing": test_csv_parsing(),
        "Database Connection": test_database_connection(),
        "OpenAI Config": test_openai_config()
    }
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to generate recipes.")
        print("\nTo generate recipes, run:")
        print("  python scripts/seeds/seed_regional_recipes.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before generating recipes.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
