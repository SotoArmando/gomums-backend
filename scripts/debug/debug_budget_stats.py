#!/usr/bin/env python3
"""
Debug budget stats and category breakdown
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.core.database import db
from app.db.repositories.budget_repository import BudgetRepository
from app.db.repositories.user_repository import UserRepository
from datetime import date, timedelta

print("="*60)
print("Debug Budget Stats & Category Breakdown")
print("="*60)

db.initialize()

# Get test user
user = UserRepository.get_user_by_email("test@gomums.com")
if not user:
    print("❌ Test user not found")
    sys.exit(1)

user_id = user['id']
print(f"✓ Using user: {user['name']} ({user_id})")

# Check what entries exist
print("\n1. Checking existing budget entries...")
entries = BudgetRepository.get_entries(user_id, limit=100)
print(f"✓ Found {len(entries)} entries")
for entry in entries:
    print(f"  - {entry['date']}: {entry['meal_name']} (${entry['cost']}) - {entry['category']}")

# Calculate date range for "week"
today = date.today()
from_date = today - timedelta(days=7)
print(f"\n2. Stats date range:")
print(f"  Today: {today}")
print(f"  From date (week): {from_date}")
print(f"  Should include entries from {from_date} to {today}")

# Test stats query manually
print("\n3. Testing stats query manually...")
try:
    query = """
        SELECT 
            COUNT(*) as meals_count,
            SUM(cost) as total_spent,
            AVG(cost_per_serving) as avg_cost_per_meal,
            MIN(date) as earliest_date,
            MAX(date) as latest_date
        FROM budget_entries
        WHERE user_id = %s AND date >= %s
    """
    
    with db.get_cursor() as cursor:
        cursor.execute(query, (user_id, from_date))
        result = cursor.fetchone()
        print(f"✓ Query result: {dict(result)}")
        
        if result['meals_count'] == 0:
            print("\n❌ No entries found in date range!")
            print("   Checking without date filter...")
            
            cursor.execute("""
                SELECT COUNT(*) as meals_count,
                       MIN(date) as earliest_date,
                       MAX(date) as latest_date
                FROM budget_entries
                WHERE user_id = %s
            """, (user_id,))
            
            all_result = cursor.fetchone()
            print(f"   All entries: {dict(all_result)}")
except Exception as e:
    print(f"❌ Stats query error: {e}")
    import traceback
    traceback.print_exc()

# Test category breakdown
print("\n4. Testing category breakdown...")
try:
    breakdown = BudgetRepository.get_category_breakdown(user_id, "week")
    print(f"✓ Category breakdown: {breakdown}")
except Exception as e:
    print(f"❌ Category breakdown error: {e}")
    import traceback
    traceback.print_exc()

# Test manually
print("\n5. Testing category query manually...")
try:
    query = """
        SELECT category, SUM(cost) as total
        FROM budget_entries
        WHERE user_id = %s AND date >= %s AND category IS NOT NULL
        GROUP BY category
        ORDER BY total DESC
    """
    
    with db.get_cursor() as cursor:
        cursor.execute(query, (user_id, from_date))
        results = cursor.fetchall()
        print(f"✓ Found {len(results)} categories")
        for row in results:
            print(f"  - {row['category']}: ${row['total']}")
except Exception as e:
    print(f"❌ Category query error: {e}")
    import traceback
    traceback.print_exc()

db.close()
print("\n" + "="*60)
print("Debug complete")
print("="*60)
