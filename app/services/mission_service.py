"""
Mission Service - Business logic for mission progress tracking
Handles automatic mission updates based on user actions
"""
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from app.core.database import db


class MissionService:
    """Service for automatic mission progress tracking"""
    
    @staticmethod
    def update_missions_on_journal_entry(user_id: str, entry_data: Dict[str, Any]) -> List[str]:
        """
        Update missions when a journal entry is created
        
        Args:
            user_id: UUID of the user
            entry_data: Journal entry data
        
        Returns:
            List of updated mission IDs
        """
        updated_missions = []
        
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get today's active missions for this user
                cursor.execute("""
                    SELECT um.id, um.mission_id, um.progress, m.title, m.type, m.category, m.target
                    FROM user_missions um
                    JOIN missions m ON um.mission_id = m.id
                    WHERE um.user_id = %s 
                    AND um.status = 'active'
                    AND (um.expires_at IS NULL OR um.expires_at > NOW())
                """, (user_id,))
                
                active_missions = cursor.fetchall()
                
                for mission in active_missions:
                    should_update = False
                    new_progress = None
                    
                    # Check mission category and type
                    category = mission['category']
                    mission_type = mission['type']
                    mission_title = mission['title'].lower()
                    
                    # Special handling for "Try a new recipe" missions
                    if 'new recipe' in mission_title and entry_data.get('type') == 'meal':
                        meal_title = entry_data.get('title', '')
                        
                        # Check if this meal title has been logged before (excluding today)
                        cursor.execute("""
                            SELECT COUNT(*) as count
                            FROM journal_entries
                            WHERE user_id = %s 
                            AND type = 'meal'
                            AND LOWER(title) = LOWER(%s)
                            AND DATE(created_at) < CURRENT_DATE
                        """, (user_id, meal_title))
                        
                        previous_count = cursor.fetchone()
                        is_new_recipe = previous_count['count'] == 0
                        
                        if is_new_recipe:
                            # Get period filter
                            if mission_type == 'daily':
                                date_filter = "DATE(created_at) = CURRENT_DATE"
                            elif mission_type == 'weekly':
                                date_filter = "created_at >= CURRENT_DATE - INTERVAL '7 days'"
                            else:  # monthly
                                date_filter = "created_at >= CURRENT_DATE - INTERVAL '30 days'"
                            
                            # Count distinct NEW recipes in period (recipes never made before)
                            cursor.execute(f"""
                                SELECT COUNT(DISTINCT title) as count
                                FROM journal_entries je
                                WHERE je.user_id = %s 
                                AND {date_filter}
                                AND je.type = 'meal'
                                AND NOT EXISTS (
                                    SELECT 1 FROM journal_entries je2
                                    WHERE je2.user_id = je.user_id
                                    AND LOWER(je2.title) = LOWER(je.title)
                                    AND je2.type = 'meal'
                                    AND DATE(je2.created_at) < DATE(je.created_at)
                                )
                            """, (user_id,))
                            
                            count_result = cursor.fetchone()
                            new_progress = count_result['count'] if count_result else 0
                            # Add 1 for current entry (transaction isolation)
                            new_progress += 1
                            should_update = True
                    
                    # "Batch Cooking Challenge" - meals with 3+ portions
                    elif 'batch cooking' in mission_title and entry_data.get('type') == 'meal':
                        portions = entry_data.get('portions', 0)
                        if portions >= 3:
                            # Get period filter
                            if mission_type == 'daily':
                                date_filter = "DATE(created_at) = CURRENT_DATE"
                            elif mission_type == 'weekly':
                                date_filter = "created_at >= CURRENT_DATE - INTERVAL '7 days'"
                            else:  # monthly
                                date_filter = "created_at >= CURRENT_DATE - INTERVAL '30 days'"
                            
                            # Count batch cooking meals in period (3+ portions)
                            cursor.execute(f"""
                                SELECT COUNT(*) as count
                                FROM journal_entries
                                WHERE user_id = %s 
                                AND {date_filter}
                                AND type = 'meal'
                                AND portions >= 3
                            """, (user_id,))
                            
                            count_result = cursor.fetchone()
                            new_progress = count_result['count'] if count_result else 0
                            # Add 1 for current entry
                            new_progress += 1
                            should_update = True
                    
                    # "Leftover Makeover" - meals with leftover status
                    elif 'leftover' in mission_title and entry_data.get('type') == 'meal':
                        meal_status = entry_data.get('status', '').lower()
                        if meal_status == 'leftovers':
                            # Get period filter
                            if mission_type == 'daily':
                                date_filter = "DATE(created_at) = CURRENT_DATE"
                            elif mission_type == 'weekly':
                                date_filter = "created_at >= CURRENT_DATE - INTERVAL '7 days'"
                            else:  # monthly
                                date_filter = "created_at >= CURRENT_DATE - INTERVAL '30 days'"
                            
                            # Count leftover meals in period
                            cursor.execute(f"""
                                SELECT COUNT(*) as count
                                FROM journal_entries
                                WHERE user_id = %s 
                                AND {date_filter}
                                AND type = 'meal'
                                AND LOWER(status) = 'leftovers'
                            """, (user_id,))
                            
                            count_result = cursor.fetchone()
                            new_progress = count_result['count'] if count_result else 0
                            # Add 1 for current entry
                            new_progress += 1
                            should_update = True
                    
                    # "Cook Streak" - consecutive days of cooking
                    elif 'cook streak' in mission_title or 'streak' in mission_title:
                        if entry_data.get('type') == 'meal':
                            # Get the current cooking streak
                            cursor.execute("""
                                WITH RECURSIVE dates AS (
                                    SELECT CURRENT_DATE as check_date, 0 as days_back
                                    UNION ALL
                                    SELECT check_date - INTERVAL '1 day', days_back + 1
                                    FROM dates
                                    WHERE days_back < 30
                                ),
                                cooking_days AS (
                                    SELECT DISTINCT DATE(created_at) as cook_date
                                    FROM journal_entries
                                    WHERE user_id = %s
                                    AND type = 'meal'
                                    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                                )
                                SELECT COUNT(*) as streak
                                FROM dates d
                                WHERE EXISTS (
                                    SELECT 1 FROM cooking_days cd
                                    WHERE cd.cook_date = d.check_date
                                )
                                AND NOT EXISTS (
                                    SELECT 1 FROM dates d2
                                    WHERE d2.check_date < d.check_date
                                    AND NOT EXISTS (
                                        SELECT 1 FROM cooking_days cd2
                                        WHERE cd2.cook_date = d2.check_date
                                    )
                                )
                            """, (user_id,))
                            
                            streak_result = cursor.fetchone()
                            new_progress = streak_result['streak'] if streak_result else 1
                            should_update = True
                    
                    # "Log your meals" - tracking category
                    elif category == 'tracking':
                        should_update = True
                    
                    # "Cook X meals" - cooking category for meal entries (excluding "new recipe" missions)
                    elif category == 'cooking' and entry_data.get('type') == 'meal' and 'new recipe' not in mission_title:
                        should_update = True
                    
                    # Vegetarian/healthy missions - check tags or type
                    elif category == 'healthy' and entry_data.get('type') == 'meal':
                        # Could check recipe tags here in future
                        should_update = True
                    
                    if should_update and new_progress is None:
                        # Get current count for today (daily) or period (weekly/monthly)
                        if mission_type == 'daily':
                            date_filter = "DATE(je.created_at) = CURRENT_DATE"
                        elif mission_type == 'weekly':
                            date_filter = "je.created_at >= CURRENT_DATE - INTERVAL '7 days'"
                        else:  # monthly
                            date_filter = "je.created_at >= CURRENT_DATE - INTERVAL '30 days'"
                        
                        # Add type filter for meal-specific missions
                        type_filter = ""
                        if category in ('cooking', 'healthy', 'meal-prep'):
                            type_filter = "AND je.type = 'meal'"
                        
                        # Count entries in period
                        cursor.execute(f"""
                            SELECT COUNT(*) as count
                            FROM journal_entries je
                            WHERE je.user_id = %s AND {date_filter} {type_filter}
                        """, (user_id,))
                        
                        count_result = cursor.fetchone()
                        new_progress = count_result['count'] if count_result else 0
                        
                        # Add 1 to include the entry currently being created
                        # (It's not yet visible in the COUNT query since we're in the same transaction)
                        new_progress += 1
                    
                    # Update mission progress if should_update is True
                    if should_update and new_progress is not None:
                        # Update mission progress
                        cursor.execute("""
                            UPDATE user_missions
                            SET 
                                progress = %s,
                                status = CASE 
                                    WHEN %s >= %s THEN 'completed'
                                    ELSE status
                                END,
                                completed_at = CASE
                                    WHEN %s >= %s AND status != 'completed' THEN NOW()
                                    ELSE completed_at
                                END,
                                updated_at = NOW()
                            WHERE id = %s
                            RETURNING status
                        """, (new_progress, new_progress, mission['target'], 
                              new_progress, mission['target'], mission['id']))
                        
                        result = cursor.fetchone()
                        
                        # If just completed, award points
                        if result and result['status'] == 'completed' and new_progress >= mission['target']:
                            cursor.execute("""
                                SELECT reward_points FROM missions WHERE id = %s
                            """, (mission['mission_id'],))
                            
                            reward = cursor.fetchone()
                            if reward and reward['reward_points']:
                                # Ensure user_stats exists, then update points
                                cursor.execute("""
                                    INSERT INTO user_stats (user_id, points, level, total_meals_cooked, total_money_saved, current_streak)
                                    VALUES (%s, %s, 1, 0, 0, 0)
                                    ON CONFLICT (user_id) DO UPDATE
                                    SET points = user_stats.points + EXCLUDED.points,
                                        updated_at = NOW()
                                """, (user_id, reward['reward_points']))
                        
                        updated_missions.append(str(mission['id']))
                
                return updated_missions
                
        except Exception as e:
            print(f"[ERROR JOURNAL] Error updating missions on journal entry: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def update_missions_on_budget_entry(user_id: str, entry_data: Dict[str, Any]) -> List[str]:
        """
        Update missions when a budget entry is created
        
        Args:
            user_id: UUID of the user
            entry_data: Budget entry data
        
        Returns:
            List of updated mission IDs
        """
        updated_missions = []
        
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get active budget-related missions
                cursor.execute("""
                    SELECT um.id, um.mission_id, um.progress, m.title, m.type, m.category, m.target
                    FROM user_missions um
                    JOIN missions m ON um.mission_id = m.id
                    WHERE um.user_id = %s 
                    AND um.status = 'active'
                    AND m.category IN ('budget', 'meal-prep')
                    AND (um.expires_at IS NULL OR um.expires_at > NOW())
                """, (user_id,))
                
                active_missions = cursor.fetchall()
                
                for mission in active_missions:
                    category = mission['category']
                    mission_type = mission['type']
                    mission_title = mission['title'].lower()
                    
                    # "No Spend Weekend" or "Weekly Savings Challenge" - specific budget challenges
                    if 'no spend' in mission_title or 'savings challenge' in mission_title:
                        # Get period filter
                        if mission_type == 'daily':
                            date_filter = "DATE(be.created_at) = CURRENT_DATE"
                        elif mission_type == 'weekly':
                            date_filter = "be.created_at >= CURRENT_DATE - INTERVAL '7 days'"
                        else:  # monthly
                            date_filter = "be.created_at >= CURRENT_DATE - INTERVAL '30 days'"
                        
                        # Get budget setting
                        cursor.execute("""
                            SELECT weekly_budget FROM budget_settings WHERE user_id = %s
                        """, (user_id,))
                        
                        budget_result = cursor.fetchone()
                        if budget_result:
                            budget = float(budget_result['weekly_budget'] or 0)
                            daily_budget = budget / 7 if mission_type == 'daily' else budget
                            
                            # Count days under budget in period
                            cursor.execute(f"""
                                WITH daily_spending AS (
                                    SELECT 
                                        DATE(created_at) as spend_date,
                                        SUM(cost) as daily_cost
                                    FROM budget_entries
                                    WHERE user_id = %s 
                                    AND {date_filter}
                                    GROUP BY DATE(created_at)
                                )
                                SELECT COUNT(*) as days_under_budget
                                FROM daily_spending
                                WHERE daily_cost <= %s
                            """, (user_id, daily_budget))
                            
                            count_result = cursor.fetchone()
                            new_progress = count_result['days_under_budget'] if count_result else 0
                            
                            # Check current day spending (including this entry)
                            cursor.execute("""
                                SELECT COALESCE(SUM(cost), 0) as today_spent
                                FROM budget_entries
                                WHERE user_id = %s AND DATE(created_at) = CURRENT_DATE
                            """, (user_id,))
                            
                            today_result = cursor.fetchone()
                            today_spent = float(today_result['today_spent'] or 0) if today_result else 0
                            today_spent += float(entry_data.get('cost', 0))
                            
                            # If today is also under budget, add 1
                            if today_spent <= daily_budget:
                                new_progress += 1
                            
                            cursor.execute("""
                                UPDATE user_missions
                                SET 
                                    progress = %s,
                                    status = CASE 
                                        WHEN %s >= %s THEN 'completed'
                                        ELSE status
                                    END,
                                    completed_at = CASE
                                        WHEN %s >= %s AND status != 'completed' THEN NOW()
                                        ELSE completed_at
                                    END,
                                    updated_at = NOW()
                                WHERE id = %s
                                RETURNING status
                            """, (new_progress, new_progress, mission['target'],
                                  new_progress, mission['target'], mission['id']))
                            
                            result = cursor.fetchone()
                            
                            # Award points if completed
                            if result and result['status'] == 'completed':
                                cursor.execute("""
                                    SELECT reward_points FROM missions WHERE id = %s
                                """, (mission['mission_id'],))
                                
                                reward = cursor.fetchone()
                                if reward and reward['reward_points']:
                                    cursor.execute("""
                                        INSERT INTO user_stats (user_id, points, level, total_meals_cooked, total_money_saved, current_streak)
                                        VALUES (%s, %s, 1, 0, 0, 0)
                                        ON CONFLICT (user_id) DO UPDATE
                                        SET points = user_stats.points + EXCLUDED.points,
                                            updated_at = NOW()
                                    """, (user_id, reward['reward_points']))
                            
                            updated_missions.append(str(mission['id']))
                    
                    # Budget tracking missions
                    elif category == 'budget':
                        # Check if staying under budget
                        if mission_type == 'daily':
                            date_filter = "DATE(be.created_at) = CURRENT_DATE"
                        elif mission_type == 'weekly':
                            date_filter = "be.created_at >= CURRENT_DATE - INTERVAL '7 days'"
                        else:  # monthly
                            date_filter = "be.created_at >= CURRENT_DATE - INTERVAL '30 days'"
                        
                        # Calculate if under budget (simple check)
                        cursor.execute(f"""
                            SELECT 
                                COALESCE(SUM(be.cost), 0) as total_spent
                            FROM budget_entries be
                            WHERE be.user_id = %s 
                            AND {date_filter}
                        """, (user_id,))
                        
                        spent_result = cursor.fetchone()
                        total_spent = float(spent_result['total_spent'] or 0) if spent_result else 0
                        
                        # Add current entry cost (since it's not yet committed when this runs)
                        current_entry_cost = float(entry_data.get('cost', 0))
                        total_spent += current_entry_cost
                        
                        # Get budget setting separately
                        cursor.execute("""
                            SELECT weekly_budget FROM budget_settings WHERE user_id = %s
                        """, (user_id,))
                        
                        budget_result = cursor.fetchone()
                        if budget_result:
                            budget = float(budget_result['weekly_budget'] or 0)
                            daily_budget = budget / 7 if mission_type == 'daily' else budget
                            
                            # If under budget, mark as progress
                            if daily_budget > 0 and total_spent <= daily_budget:
                                new_progress = 1  # Simple binary: under budget = 1
                            else:
                                new_progress = 0
                            
                            cursor.execute("""
                                UPDATE user_missions
                                SET 
                                    progress = %s,
                                    status = CASE 
                                        WHEN %s >= %s THEN 'completed'
                                        ELSE status
                                    END,
                                    completed_at = CASE
                                        WHEN %s >= %s AND status != 'completed' THEN NOW()
                                        ELSE completed_at
                                    END,
                                    updated_at = NOW()
                                WHERE id = %s
                                RETURNING status
                            """, (new_progress, new_progress, mission['target'],
                                  new_progress, mission['target'], mission['id']))
                            
                            result = cursor.fetchone()
                            
                            # Award points if completed
                            if result and result['status'] == 'completed' and new_progress >= mission['target']:
                                cursor.execute("""
                                    SELECT reward_points FROM missions WHERE id = %s
                                """, (mission['mission_id'],))
                                
                                reward = cursor.fetchone()
                                if reward and reward['reward_points']:
                                    # Ensure user_stats exists, then update points
                                    cursor.execute("""
                                        INSERT INTO user_stats (user_id, points, level, total_meals_cooked, total_money_saved, current_streak)
                                        VALUES (%s, %s, 1, 0, 0, 0)
                                        ON CONFLICT (user_id) DO UPDATE
                                        SET points = user_stats.points + EXCLUDED.points,
                                            updated_at = NOW()
                                    """, (user_id, reward['reward_points']))
                            
                            updated_missions.append(str(mission['id']))
                    
                    # Meal prep missions - count meals cooked
                    elif category == 'meal-prep':
                        if mission_type == 'weekly':
                            cursor.execute("""
                                SELECT COUNT(*) as count
                                FROM budget_entries
                                WHERE user_id = %s 
                                AND created_at >= CURRENT_DATE - INTERVAL '7 days'
                            """, (user_id,))
                            
                            count_result = cursor.fetchone()
                            new_progress = count_result['count'] if count_result else 0
                            
                            cursor.execute("""
                                UPDATE user_missions
                                SET 
                                    progress = %s,
                                    status = CASE 
                                        WHEN %s >= %s THEN 'completed'
                                        ELSE status
                                    END,
                                    completed_at = CASE
                                        WHEN %s >= %s AND status != 'completed' THEN NOW()
                                        ELSE completed_at
                                    END,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (new_progress, new_progress, mission['target'],
                                  new_progress, mission['target'], mission['id']))
                            
                            updated_missions.append(str(mission['id']))
                
                return updated_missions
                
        except Exception as e:
            print(f"[ERROR BUDGET] Error updating missions on budget entry: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def recalculate_all_missions(user_id: str) -> Dict[str, Any]:
        """
        Recalculate all active missions for a user based on current data
        Useful for fixing inconsistencies or initial setup
        
        Args:
            user_id: UUID of the user
        
        Returns:
            Summary of updates
        """
        try:
            # Trigger updates by simulating entries
            # This will recalculate based on actual data
            updated_journal = MissionService.update_missions_on_journal_entry(user_id, {"type": "meal"})
            updated_budget = MissionService.update_missions_on_budget_entry(user_id, {})
            
            return {
                "journal_missions_updated": len(updated_journal),
                "budget_missions_updated": len(updated_budget),
                "total_updated": len(set(updated_journal + updated_budget))
            }
        except Exception as e:
            print(f"Error recalculating missions: {e}")
            return {"error": str(e)}
