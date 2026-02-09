"""
Mission Time Simulator
Simulates time passage for testing mission expiration and validates mission completion
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "database": os.getenv("DATABASE_NAME", "gomums"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "7646")
}

TEST_EMAIL = "mission_auto@test.com"


def simulate_time_passage(hours: int = 25):
    """
    Simulate time passing by moving mission expiration times
    
    Args:
        hours: Number of hours to simulate (default 25 = past daily deadline)
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get test user
        cursor.execute("SELECT id FROM users WHERE email = %s", (TEST_EMAIL,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Test user not found: {TEST_EMAIL}")
            return
        
        user_id = user['id']
        print(f"✅ Found test user: {user_id}")
        
        # Get active missions before simulation
        cursor.execute("""
            SELECT 
                um.id, m.title, m.type, um.status, um.progress, m.target,
                um.expires_at, 
                (um.expires_at - NOW()) as time_remaining
            FROM user_missions um
            JOIN missions m ON um.mission_id = m.id
            WHERE um.user_id = %s
            AND um.status = 'active'
            ORDER BY um.expires_at
        """, (user_id,))
        
        missions_before = cursor.fetchall()
        
        if not missions_before:
            print("⚠️  No active missions found for this user")
            print("   Run: python3 seed_missions.py")
            print("   Then call the assign-daily endpoint")
            return
        
        print(f"\n📋 Active missions BEFORE time simulation:")
        for m in missions_before:
            time_left = m['time_remaining']
            print(f"   - {m['title']} ({m['type']})")
            print(f"     Progress: {m['progress']}/{m['target']}, Status: {m['status']}")
            print(f"     Expires: {m['expires_at']} (in {time_left})")
        
        # Simulate time passage by subtracting hours from expires_at
        print(f"\n⏰ Simulating {hours} hours passing...")
        cursor.execute("""
            UPDATE user_missions
            SET expires_at = expires_at - INTERVAL '%s hours'
            WHERE user_id = %s
            AND status = 'active'
            AND expires_at IS NOT NULL
            RETURNING id
        """, (hours, user_id))
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Updated {updated_count} missions")
        
        # Now check which missions should be expired
        cursor.execute("""
            SELECT 
                um.id, m.title, m.type, um.status, um.progress, m.target,
                um.expires_at,
                CASE 
                    WHEN um.expires_at < NOW() THEN 'SHOULD_EXPIRE'
                    ELSE 'STILL_ACTIVE'
                END as validation_status
            FROM user_missions um
            JOIN missions m ON um.mission_id = m.id
            WHERE um.user_id = %s
            AND um.status = 'active'
            ORDER BY um.expires_at
        """, (user_id,))
        
        missions_after = cursor.fetchall()
        
        print(f"\n📋 Mission status AFTER time simulation:")
        expired_count = 0
        active_count = 0
        
        for m in missions_after:
            status_emoji = "❌" if m['validation_status'] == 'SHOULD_EXPIRE' else "✅"
            print(f"   {status_emoji} {m['title']} ({m['type']})")
            print(f"     Progress: {m['progress']}/{m['target']}")
            print(f"     Expires: {m['expires_at']}")
            print(f"     Status: {m['validation_status']}")
            
            if m['validation_status'] == 'SHOULD_EXPIRE':
                expired_count += 1
            else:
                active_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   - Still active: {active_count}")
        print(f"   - Should expire: {expired_count}")
        print(f"\n💡 Next: Call GET /missions/active to see expiration happen automatically")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def validate_mission_completion():
    """
    Check if user's actions (journal entries, budget entries) would complete missions
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get test user
        cursor.execute("SELECT id FROM users WHERE email = %s", (TEST_EMAIL,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Test user not found: {TEST_EMAIL}")
            return
        
        user_id = user['id']
        
        print(f"\n🔍 Validating mission completion for user: {user_id}")
        
        # Count today's meal entries
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM journal_entries
            WHERE user_id = %s
            AND type = 'meal'
            AND DATE(created_at) = CURRENT_DATE
        """, (user_id,))
        
        meal_count = cursor.fetchone()['count']
        print(f"\n📊 User Activity Today:")
        print(f"   - Meal entries logged: {meal_count}")
        
        # Check all journal entries
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM journal_entries
            WHERE user_id = %s
            AND DATE(created_at) = CURRENT_DATE
        """, (user_id,))
        
        journal_count = cursor.fetchone()['count']
        print(f"   - Total journal entries: {journal_count}")
        
        # Check budget entries
        cursor.execute("""
            SELECT 
                COALESCE(SUM(cost), 0) as total_spent,
                COUNT(*) as entry_count
            FROM budget_entries
            WHERE user_id = %s
            AND DATE(created_at) = CURRENT_DATE
        """, (user_id,))
        
        budget_data = cursor.fetchone()
        print(f"   - Budget entries: {budget_data['entry_count']}")
        print(f"   - Money spent today: ${budget_data['total_spent']}")
        
        # Get budget goal
        cursor.execute("""
            SELECT weekly_budget
            FROM budget_settings
            WHERE user_id = %s
        """, (user_id,))
        
        budget_settings = cursor.fetchone()
        if budget_settings:
            weekly_budget = budget_settings['weekly_budget']
            daily_budget = float(weekly_budget) / 7 if weekly_budget else 0
            print(f"   - Daily budget target: ${daily_budget:.2f}/day")
            
            if budget_data['total_spent'] <= daily_budget:
                print(f"   ✅ Under budget!")
            else:
                print(f"   ❌ Over budget")
        
        # Check active missions and if they would be completed
        cursor.execute("""
            SELECT 
                um.id, m.title, m.type, m.category, m.target, um.progress, um.status
            FROM user_missions um
            JOIN missions m ON um.mission_id = m.id
            WHERE um.user_id = %s
            AND um.status IN ('active', 'completed')
            ORDER BY um.status, m.type, m.title
        """, (user_id,))
        
        missions = cursor.fetchall()
        
        print(f"\n🎯 Mission Validation:")
        for m in missions:
            status_emoji = "✅" if m['status'] == 'completed' else "🔄"
            print(f"   {status_emoji} {m['title']} ({m['category']})")
            print(f"      Progress: {m['progress']}/{m['target']} - Status: {m['status']}")
            
            # Validate if it should be complete based on activity
            expected_progress = 0
            if m['category'] == 'cooking':
                expected_progress = meal_count
            elif m['category'] == 'tracking':
                expected_progress = journal_count
            elif m['category'] == 'budget':
                if budget_settings and budget_data['total_spent'] <= daily_budget:
                    expected_progress = 1
            
            if expected_progress != m['progress']:
                print(f"      ⚠️  Expected progress: {expected_progress} (current: {m['progress']})")
            
            if expected_progress >= m['target'] and m['status'] != 'completed':
                print(f"      💡 Should be completed! (has {expected_progress}/{m['target']})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*60)
    print("Mission Time Simulator & Validator")
    print("="*60)
    
    print("\n[Option 1] Simulate time passage (expire old missions)")
    print("[Option 2] Validate mission completion without time change")
    print("[Option 3] Both - simulate time AND validate")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        hours = input("How many hours to simulate? (default 25): ").strip()
        hours = int(hours) if hours else 25
        simulate_time_passage(hours)
    elif choice == "2":
        validate_mission_completion()
    elif choice == "3":
        hours = input("How many hours to simulate? (default 25): ").strip()
        hours = int(hours) if hours else 25
        simulate_time_passage(hours)
        validate_mission_completion()
    else:
        print("Invalid choice")
