#!/usr/bin/env python3
"""
Debug script to test user registration directly
"""

import sys
sys.path.insert(0, '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend')

from app.core.database import db
from app.db.repositories.user_repository import UserRepository

print("="*60)
print("Debug: Testing User Registration")
print("="*60)

# Initialize database
print("\n1. Initializing database connection...")
db.initialize()

if not db.test_connection():
    print("❌ Database connection failed!")
    sys.exit(1)

print("✓ Database connected")

# Test user creation
print("\n2. Testing user creation...")
TEST_USER = {
    "name": "Test User",
    "email": "test@gomums.com",
    "password": "Test123!@#"
}

# First, check if user exists
print(f"\n3. Checking if user exists: {TEST_USER['email']}")
existing_user = UserRepository.get_user_by_email(TEST_USER['email'])

if existing_user:
    print(f"✓ User already exists: {existing_user['name']}")
    print(f"  ID: {existing_user['id']}")
    print(f"  OAuth Provider: {existing_user.get('oauth_provider')}")
    print(f"  Is Active: {existing_user.get('is_active')}")
else:
    print("ℹ User does not exist, creating...")
    
    try:
        new_user = UserRepository.create_user(
            name=TEST_USER['name'],
            email=TEST_USER['email'],
            password=TEST_USER['password'],
            oauth_provider='email'
        )
        
        if new_user:
            print(f"✓ User created successfully!")
            print(f"  ID: {new_user['id']}")
            print(f"  Name: {new_user['name']}")
            print(f"  Email: {new_user['email']}")
            print(f"  OAuth Provider: {new_user.get('oauth_provider')}")
        else:
            print("❌ User creation returned None")
    except Exception as e:
        print(f"❌ Exception during user creation: {e}")
        import traceback
        traceback.print_exc()

# Close database
db.close()
print("\n" + "="*60)
print("Debug test complete")
print("="*60)
