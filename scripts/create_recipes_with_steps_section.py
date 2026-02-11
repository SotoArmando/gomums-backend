#!/usr/bin/env python3
"""
Create a home section for recipes with structured steps
"""
import sys
import os
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.core.database import db
from app.db.repositories.home_section_repository import HomeSectionRepository
import uuid

print("="*70)
print("Creating Home Section: Recipes with Steps")
print("="*70)

# Initialize database
db.initialize()

def create_recipes_with_steps_section(user_id: str = None):
    """
    Create a global home section for recipes with steps
    
    If user_id is provided, creates a user-specific section.
    If None, creates a global section visible to all users.
    """
    
    section_data = {
        "type": "recipes",
        "title": "Step-by-Step Recipes",
        "subtitle": "Learn with detailed cooking instructions",
        "visible": True,
        "order_index": 1,
        "data": {
            "filter": "with_steps",
            "show_phases": True,
            "show_prep_time": True,
            "show_difficulty": True,
            "limit": 10,
            "layout": "grid"
        }
    }
    
    # If no user_id provided, create as global section (admin-only in production)
    if user_id is None:
        query = """
            INSERT INTO home_sections (
                id, user_id, type, title, subtitle, visible, order_index, data
            )
            VALUES (%s, NULL, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id, user_id, type, title, subtitle, visible, order_index, data, created_at, updated_at
        """
        
        section_id = str(uuid.uuid4())
        values = (
            section_id,
            section_data["type"],
            section_data["title"],
            section_data["subtitle"],
            section_data["visible"],
            section_data["order_index"],
            json.dumps(section_data["data"])
        )
    else:
        query = """
            INSERT INTO home_sections (
                id, user_id, type, title, subtitle, visible, order_index, data
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id, user_id, type, title, subtitle, visible, order_index, data, created_at, updated_at
        """
        
        section_id = str(uuid.uuid4())
        values = (
            section_id,
            user_id,
            section_data["type"],
            section_data["title"],
            section_data["subtitle"],
            section_data["visible"],
            section_data["order_index"],
            json.dumps(section_data["data"])
        )
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            if result:
                print("\n✅ Section created successfully!")
                print(f"   ID: {result['id']}")
                print(f"   Type: {result['type']}")
                print(f"   Title: {result['title']}")
                print(f"   Subtitle: {result['subtitle']}")
                print(f"   Global: {'Yes' if result['user_id'] is None else 'No'}")
                print(f"   Order: {result['order_index']}")
                print(f"   Data: {result['data']}")
                return result
            else:
                print("\n❌ Failed to create section")
                return None
    except Exception as e:
        print(f"\n❌ Error creating section: {e}")
        return None

def get_test_user():
    """Get a test user to create the section for"""
    query = "SELECT id, email FROM users WHERE email = 'test@gomums.com' LIMIT 1"
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query)
            user = cursor.fetchone()
            return user
    except Exception as e:
        print(f"Error getting test user: {e}")
        return None


if __name__ == "__main__":
    print("\n1️⃣  Creating Global Section")
    print("   This section will be visible to all users\n")
    
    global_section = create_recipes_with_steps_section(user_id=None)
    
    if global_section:
        print("\n" + "="*70)
        print("Section Created Successfully!")
        print("="*70)
        print("\nTo use this section:")
        print("  • GET /api/home-sections/ - Will include this global section")
        print("  • GET /api/recipes/with-steps - Fetches the recipes for this section")
        print("\nSection displays:")
        print("  • 10 recipes with detailed step-by-step instructions")
        print("  • Phases: Prepare, Cook, Serve")
        print("  • Prep time and difficulty level")
        print("="*70)
    
    # Optionally create for a test user
    print("\n\n2️⃣  Optional: Create for Test User")
    response = input("Would you like to also create this section for test@gomums.com? (y/n): ")
    
    if response.lower() == 'y':
        test_user = get_test_user()
        if test_user:
            print(f"\nCreating section for user: {test_user['email']}")
            user_section = create_recipes_with_steps_section(user_id=test_user['id'])
            
            if user_section:
                print("\n✅ User-specific section created!")
        else:
            print("\n⚠️  Test user not found. Run registration first.")
    
    db.close()
    print("\n✨ Done!\n")
