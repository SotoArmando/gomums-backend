#!/usr/bin/env python3
"""
Test budget API directly through the code (not HTTP)
This will show us the actual error
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.core.database import db
from app.db.repositories.budget_repository import BudgetRepository
from datetime import date

print("="*60)
print("Direct Budget Repository Test")
print("="*60)

# Initialize database
db.initialize()

# Get a user
print("\n1. Getting test user...")
from app.db.repositories.user_repository import UserRepository
user = UserRepository.get_user_by_email("test@gomums.com")

if not user:
    print("❌ Test user not found")
    sys.exit(1)

user_id = user['id']
print(f"✓ Using user: {user['name']} ({user_id})")

# Test creating budget settings
print("\n2. Testing create budget settings...")
try:
    settings_data = {
        "weekly_budget": 150.00,
        "monthly_budget": 600.00
    }
    
    settings = BudgetRepository.upsert_budget_settings(user_id, settings_data)
    
    if settings:
        print(f"✓ Budget settings created/updated:")
        print(f"  Weekly: ${settings['weekly_budget']}")
        print(f"  Monthly: ${settings['monthly_budget']}")
    else:
        print("❌ Failed to create settings")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

# Test creating budget entry
print("\n3. Testing create budget entry...")
try:
    entry_data = {
        "date": date.today(),
        "meal_name": "Test Spaghetti",
        "cost": 12.50,
        "servings": 4,
        "category": "Dinner",
        "notes": "Test entry"
    }
    
    entry = BudgetRepository.create_entry(user_id, entry_data)
    
    if entry:
        print(f"✓ Budget entry created:")
        print(f"  ID: {entry['id']}")
        print(f"  Meal: {entry['meal_name']}")
        print(f"  Cost: ${entry['cost']}")
        print(f"  Cost per serving: ${entry['cost_per_serving']}")
    else:
        print("❌ Failed to create entry")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

# Test getting stats
print("\n4. Testing get stats...")
try:
    stats = BudgetRepository.get_stats(user_id, "week")
    print(f"✓ Stats retrieved:")
    print(f"  Score: {stats['score']}")
    print(f"  Avg cost per meal: ${stats['avg_cost_per_meal']}")
    print(f"  Total spent: ${stats['total_spent']}")
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

db.close()

print("\n" + "="*60)
print("Direct test complete")
print("="*60)
