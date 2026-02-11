#!/usr/bin/env python3
"""
Clear all data for a specific user by email address.

Usage:
    python scripts/clear_user_data.py user@example.com
    python scripts/clear_user_data.py user@example.com --dry-run
    python scripts/clear_user_data.py user@example.com --keep-account

Options:
    --dry-run      Show what would be deleted without actually deleting
    --keep-account Delete user data but keep the account (user can log in again)
"""

import sys
import os
import argparse

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db


# Tables with user_id foreign key (order matters for foreign key constraints)
USER_DATA_TABLES = [
    # Junction/link tables first
    ("meal_purchase_links", "meal_id IN (SELECT id FROM journal_entries WHERE user_id = %s)"),
    ("user_challenge_goals", "user_challenge_id IN (SELECT id FROM user_challenges WHERE user_id = %s)"),
    
    # Child tables
    ("planned_meals", "meal_plan_id IN (SELECT id FROM meal_plans WHERE user_id = %s)"),
    ("shopping_list_items", "meal_plan_id IN (SELECT id FROM meal_plans WHERE user_id = %s)"),
    
    # Direct user_id tables
    ("journal_entries", "user_id = %s"),
    ("meal_plans", "user_id = %s"),
    ("budget_entries", "user_id = %s"),
    ("budget_settings", "user_id = %s"),
    ("user_missions", "user_id = %s"),
    ("user_challenges", "user_id = %s"),
    ("user_achievements", "user_id = %s"),
    ("user_preferences", "user_id = %s"),
    ("user_stats", "user_id = %s"),
    ("home_sections", "user_id = %s"),
    ("smart_suggestions", "user_id = %s"),
    ("saved_ingredient_prices", "user_id = %s"),
]


def get_user_by_email(email: str) -> dict | None:
    """Find user by email address."""
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT id, name, email, created_at FROM users WHERE email = %s",
            (email,)
        )
        return cursor.fetchone()


def count_user_data(user_id: str) -> dict:
    """Count records in each table for a user."""
    counts = {}
    
    with db.get_cursor() as cursor:
        for table, condition in USER_DATA_TABLES:
            try:
                cursor.execute("SAVEPOINT sp_count")
                query = f"SELECT COUNT(*) as count FROM {table} WHERE {condition}"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                counts[table] = result['count'] if result else 0
                cursor.execute("RELEASE SAVEPOINT sp_count")
            except Exception as e:
                cursor.execute("ROLLBACK TO SAVEPOINT sp_count")
                # Table might not exist - skip it
                counts[table] = None
    
    return counts


def clear_user_data(user_id: str, dry_run: bool = False) -> dict:
    """
    Delete all data for a user from all tables.
    
    Returns dict with deleted row counts per table.
    """
    deleted = {}
    
    with db.get_cursor(commit=not dry_run) as cursor:
        for table, condition in USER_DATA_TABLES:
            try:
                cursor.execute("SAVEPOINT sp_delete")
                if dry_run:
                    # Just count what would be deleted
                    query = f"SELECT COUNT(*) as count FROM {table} WHERE {condition}"
                    cursor.execute(query, (user_id,))
                    result = cursor.fetchone()
                    deleted[table] = result['count'] if result else 0
                else:
                    # Actually delete
                    query = f"DELETE FROM {table} WHERE {condition}"
                    cursor.execute(query, (user_id,))
                    deleted[table] = cursor.rowcount
                cursor.execute("RELEASE SAVEPOINT sp_delete")
            except Exception as e:
                cursor.execute("ROLLBACK TO SAVEPOINT sp_delete")
                # Table might not exist - skip it
                deleted[table] = None
    
    return deleted


def delete_user_account(user_id: str, dry_run: bool = False) -> bool:
    """Delete the user account itself."""
    if dry_run:
        return True
    
    with db.get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        return cursor.rowcount > 0


def main():
    parser = argparse.ArgumentParser(
        description="Clear all data for a user by email address"
    )
    parser.add_argument("email", help="Email address of the user")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--keep-account",
        action="store_true",
        help="Keep the user account, only delete their data"
    )
    
    args = parser.parse_args()
    
    # Initialize database
    print("Connecting to database...")
    db.initialize()
    
    try:
        # Find user
        user = get_user_by_email(args.email)
        
        if not user:
            print(f"❌ User not found: {args.email}")
            sys.exit(1)
        
        user_id = str(user['id'])
        print(f"\n👤 Found user:")
        print(f"   ID: {user_id}")
        print(f"   Name: {user['name']}")
        print(f"   Email: {user['email']}")
        print(f"   Created: {user['created_at']}")
        
        # Count data
        print(f"\n📊 Data to be {'deleted' if not args.dry_run else 'deleted (DRY RUN)'}:")
        counts = count_user_data(user_id)
        
        total = 0
        for table, count in counts.items():
            if isinstance(count, int) and count > 0:
                print(f"   {table}: {count} rows")
                total += count
            elif count is None:
                print(f"   {table}: (table not found, skipping)")
        
        if total == 0:
            print("   (no data found)")
        
        # Confirm deletion
        if not args.dry_run:
            print(f"\n⚠️  This will delete {total} rows from the database.")
            if not args.keep_account:
                print("   The user account will also be deleted.")
            
            confirm = input("\nType 'yes' to confirm: ")
            if confirm.lower() != 'yes':
                print("❌ Aborted.")
                sys.exit(0)
        
        # Delete data
        print(f"\n{'🔍 DRY RUN - ' if args.dry_run else ''}Deleting user data...")
        deleted = clear_user_data(user_id, dry_run=args.dry_run)
        
        for table, count in deleted.items():
            if isinstance(count, int) and count > 0:
                print(f"   ✓ {table}: {count} rows deleted")
            elif count is None:
                print(f"   ⏭ {table}: (table not found, skipped)")
        
        # Delete user account
        if not args.keep_account:
            print(f"\n{'🔍 DRY RUN - ' if args.dry_run else ''}Deleting user account...")
            if delete_user_account(user_id, dry_run=args.dry_run):
                print(f"   ✓ User account deleted")
            else:
                print(f"   ⚠ Failed to delete user account")
        
        if args.dry_run:
            print("\n✅ DRY RUN complete. No data was actually deleted.")
        else:
            print("\n✅ User data cleared successfully.")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
