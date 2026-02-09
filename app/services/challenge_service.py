"""
Challenge Service
Business logic for multi-goal challenge tracking
Auto-updates challenge goal progress based on user actions
"""

from typing import Optional, Dict, Any, List, Union
from uuid import UUID
from app.db.repositories.challenge_repository import ChallengeRepository
from app.models.journal import IngredientSwap
from app.core.database import db


class ChallengeService:
    """Service for challenge business logic"""

    @staticmethod
    def update_challenges_on_journal_entry(
        user_id: UUID,
        entry_type: str,
        meal_type: Optional[str] = None,
        portions: Optional[int] = None,
        status: Optional[str] = None,
        used_leftovers: bool = False,
        is_batch: bool = False,
        recipe_name: Optional[str] = None,
        ingredient_swaps: Optional[Union[List[IngredientSwap], List[Dict[str, Any]]]] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update challenge goal progress when user creates a journal entry
        Returns dict with updated goals and completed challenges
        """
        from datetime import datetime
        
        # Write debug info to file
        with open("challenge_debug.log", "a") as f:
            f.write(f"========================================\n")
            f.write(f"ChallengeService called: entry_type={entry_type}, timestamp={timestamp}\n")
        
        try:
            with db.get_cursor() as cursor:
                # Get active challenges with their goals
                cursor.execute("""
                    SELECT 
                        uc.id as user_challenge_id,
                        uc.challenge_id,
                        c.type as challenge_type,
                        ucg.id as user_goal_id,
                        ucg.goal_id,
                        cg.description as goal_description,
                        cg.target as goal_target,
                        ucg.progress as current_progress,
                        ucg.completed
                    FROM user_challenges uc
                    JOIN challenges c ON uc.challenge_id = c.id
                    JOIN user_challenge_goals ucg ON ucg.user_challenge_id = uc.id
                    JOIN challenge_goals cg ON ucg.goal_id = cg.id
                    WHERE uc.user_id = %s AND uc.status = 'active' AND ucg.completed = FALSE
                """, (str(user_id),))
                
                active_goals = cursor.fetchall()
            
            updated_goals = []
            completed_challenges = []
            
            # Process each active goal
            for goal in active_goals:
                should_increment = False
                user_challenge_id = goal['user_challenge_id']
                goal_id = goal['goal_id']
                goal_description = goal['goal_description'].lower()
                
                # Batch cooking goals - "Cook X meals with 3+ servings"
                if portions and portions >= 3:
                    if ("batch" in goal_description or "servings" in goal_description) and "cook" in goal_description:
                        should_increment = True
                
                # Leftover goals - "Use leftovers X times"
                if (status == 'leftovers' or used_leftovers):
                    if "leftover" in goal_description or "use" in goal_description and "leftover" in goal_description:
                        should_increment = True
                
                # Freeze meal goals - "Freeze X meals"
                if status == 'frozen':
                    if "freeze" in goal_description:
                        should_increment = True
                
                # New recipe goals - "Try X new recipes"
                if recipe_name and ("new" in goal_description and "recipe" in goal_description):
                    try:
                        with db.get_cursor() as cursor:
                            cursor.execute("""
                                SELECT COUNT(*) as count
                                FROM journal_entries
                                WHERE user_id = %s 
                                AND type = 'meal' 
                                AND LOWER(title) = LOWER(%s)
                                AND created_at < NOW() - INTERVAL '1 second'
                            """, (str(user_id), recipe_name))
                            
                            history_count = cursor.fetchone()['count']
                            
                            if history_count == 0:
                                should_increment = True
                    except Exception:
                        pass
                
                # Meal count goals - "Cook X meals at home"
                if entry_type == 'meal':
                    if ("cook" in goal_description and "meal" in goal_description) or \
                       ("meal" in goal_description and "home" in goal_description):
                        should_increment = True
                
                # One-pot meal goals - "Cook X one-pot meals"
                if "one-pot" in goal_description or "one pot" in goal_description:
                    # This would need a flag in journal entry
                    if "one-pot" in (recipe_name or "").lower():
                        should_increment = True
                
                # Pantry/fridge cooking - "Cook from pantry/fridge"
                if "pantry" in goal_description or "fridge" in goal_description:
                    # This would need a flag indicating no new groceries
                    if status == 'no_spend':
                        should_increment = True
                
                # Ingredient swap goals - any swap with ingredient_swaps data counts
                # Simple: if meal has ingredient_swaps, it means user swapped something
                if ingredient_swaps and len(ingredient_swaps) > 0:
                    # Check if goal is about swaps, ingredients, substitutes, etc.
                    swap_keywords = ["swap", "substitute", "ingredient", "replace", "alternative"]
                    if any(keyword in goal_description for keyword in swap_keywords):
                        # If goal mentions savings, verify that swaps actually saved money
                        if "save" in goal_description or "savings" in goal_description:
                            # Check if any swap has positive savings
                            has_savings = False
                            for swap in ingredient_swaps:
                                # Handle both Pydantic objects and dicts
                                if isinstance(swap, IngredientSwap):
                                    if swap.savings and swap.savings > 0:
                                        has_savings = True
                                        break
                                elif isinstance(swap, dict):
                                    savings = swap.get('savings')
                                    if savings and savings > 0:
                                        has_savings = True
                                        break
                            should_increment = has_savings
                        else:
                            # For non-savings goals, just having swaps is enough
                            should_increment = True
                
                # Budget/savings goals (for purchase entries)
                if entry_type == 'purchase':
                    # "Save $X total on groceries" - track cumulative savings from swaps
                    if "save" in goal_description and ("$" in goal_description or "grocery" in goal_description or "groceries" in goal_description):
                        # Accumulate savings from ingredient_swaps in this purchase
                        if ingredient_swaps and len(ingredient_swaps) > 0:
                            total_savings = 0
                            for swap in ingredient_swaps:
                                if isinstance(swap, IngredientSwap):
                                    if swap.savings and swap.savings > 0:
                                        total_savings += swap.savings
                                elif isinstance(swap, dict):
                                    savings = swap.get('savings', 0)
                                    if savings and savings > 0:
                                        total_savings += savings
                            
                            if total_savings > 0:
                                # Increment by the dollar amount saved (not just count)
                                result = ChallengeRepository.update_goal_progress(
                                    user_challenge_id=user_challenge_id,
                                    goal_id=goal_id,
                                    progress_increment=int(total_savings)  # Track dollars saved
                                )
                                if result:
                                    print(f"   💰 Savings goal updated: +${total_savings:.2f}")
                                    updated_goals.append(result)
                    
                    # "Stay under daily budget X days" - check if today's purchases are under budget
                    if "budget" in goal_description and "day" in goal_description and "under" in goal_description:
                        try:
                            # Determine which date to check (from timestamp or most recent)
                            check_date = "CURRENT_DATE"
                            date_params = [str(user_id)]
                            
                            if timestamp:
                                # Parse timestamp and use its date
                                try:
                                    parsed_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    check_date = "%s"
                                    date_params = [str(user_id), parsed_date.date()]
                                except:
                                    pass  # Fall back to CURRENT_DATE
                            
                            # Get user's budget settings
                            with db.get_cursor() as budget_cursor:
                                budget_cursor.execute("""
                                    SELECT weekly_budget
                                    FROM budget_settings
                                    WHERE user_id = %s
                                """, (str(user_id),))
                                
                                budget_settings = budget_cursor.fetchone()
                                
                                if budget_settings and budget_settings['weekly_budget']:
                                    weekly_budget = float(budget_settings['weekly_budget'])
                                    daily_budget = weekly_budget / 7
                                    
                                    # Get total purchases for the date being checked
                                    if len(date_params) == 2:
                                        query = f"""
                                            SELECT COALESCE(SUM((item->>'cost')::numeric), 0) as total_cost
                                            FROM journal_entries je,
                                            LATERAL jsonb_array_elements(je.items) as item
                                            WHERE je.user_id = %s 
                                            AND je.type = 'purchase'
                                            AND DATE(je.timestamp) = %s
                                        """
                                    else:
                                        query = f"""
                                            SELECT COALESCE(SUM((item->>'cost')::numeric), 0) as total_cost
                                            FROM journal_entries je,
                                            LATERAL jsonb_array_elements(je.items) as item
                                            WHERE je.user_id = %s 
                                            AND je.type = 'purchase'
                                            AND DATE(je.timestamp) = CURRENT_DATE
                                        """
                                    
                                    budget_cursor.execute(query, tuple(date_params))
                                    daily_total = budget_cursor.fetchone()['total_cost']
                                    daily_total = float(daily_total) if daily_total else 0
                                    
                                    # Check if stayed under budget for this day
                                    if daily_total <= daily_budget:
                                        # Check if we've already counted this date for this goal
                                        if len(date_params) == 2:
                                            count_query = """
                                                SELECT DATE(je.timestamp) as purchase_date
                                                FROM journal_entries je
                                                WHERE je.user_id = %s 
                                                AND je.type = 'purchase'
                                                AND DATE(je.timestamp) = %s
                                                ORDER BY je.created_at ASC
                                                LIMIT 1
                                            """
                                        else:
                                            count_query = """
                                                SELECT DATE(je.timestamp) as purchase_date
                                                FROM journal_entries je
                                                WHERE je.user_id = %s 
                                                AND je.type = 'purchase'
                                                AND DATE(je.timestamp) = CURRENT_DATE
                                                ORDER BY je.created_at ASC
                                                LIMIT 1
                                            """
                                        
                                        budget_cursor.execute(count_query, tuple(date_params))
                                        first_purchase = budget_cursor.fetchone()
                                        
                                        # Check if this date has been counted for this goal
                                        budget_cursor.execute("""
                                            SELECT progress FROM user_challenge_goals
                                            WHERE user_challenge_id = %s AND goal_id = %s
                                        """, (user_challenge_id, goal_id))
                                        
                                        current_progress = budget_cursor.fetchone()['progress']
                                        
                                        # Count unique days under budget
                                        budget_cursor.execute("""
                                            WITH daily_totals AS (
                                                SELECT 
                                                    DATE(je.timestamp) as purchase_date,
                                                    COALESCE(SUM((item->>'cost')::numeric), 0) as daily_total
                                                FROM journal_entries je,
                                                LATERAL jsonb_array_elements(je.items) as item
                                                WHERE je.user_id = %s 
                                                AND je.type = 'purchase'
                                                GROUP BY DATE(je.timestamp)
                                            )
                                            SELECT COUNT(*) as days_under_budget
                                            FROM daily_totals
                                            WHERE daily_total <= %s
                                        """, (str(user_id), daily_budget))
                                        
                                        result = budget_cursor.fetchone()
                                        actual_days_under = result['days_under_budget'] if result else 0
                                        
                                        # Write debug info to file
                                        with open("challenge_debug.log", "a") as f:
                                            f.write(f"💰 Budget tracking: {actual_days_under} days under ${daily_budget:.2f}/day (current: {current_progress})\n")
                                        print(f"💰 Budget tracking: {actual_days_under} days under ${daily_budget:.2f}/day (current: {current_progress})")
                                        
                                        # Update to the correct count if different
                                        if actual_days_under != current_progress:
                                            print(f"   📊 Updating from {current_progress} to {actual_days_under} days")
                                            update_result = ChallengeRepository.update_goal_progress_absolute(
                                                user_challenge_id=user_challenge_id,
                                                goal_id=goal_id,
                                                progress_value=actual_days_under
                                            )
                                            if update_result:
                                                print(f"   ✅ Updated successfully!")
                                                updated_goals.append(update_result)
                                    else:
                                        print(f"   📊 Budget check: ${daily_total:.2f} > ${daily_budget:.2f}/day ❌")
                                else:
                                    print(f"   ⚠️  No budget settings found - can't track budget goals")
                        except Exception as e:
                            print(f"   ❌ Error checking budget: {e}")
                            import traceback
                            traceback.print_exc()
                
                # Breakfast goals - "Cook breakfast X times"
                if meal_type == 'breakfast':
                    if "breakfast" in goal_description:
                        should_increment = True
                
                # Consecutive days cooking - "Cook for X consecutive days"
                if entry_type == 'meal' and ("consecutive" in goal_description or "streak" in goal_description):
                    # Check how many consecutive days user has cooked
                    try:
                        # Need a new cursor since the original one is closed
                        with db.get_cursor() as check_cursor:
                            check_cursor.execute("""
                                SELECT DISTINCT DATE(timestamp) as cook_date
                                FROM journal_entries
                                WHERE user_id = %s 
                                AND type = 'meal'
                                ORDER BY cook_date DESC
                            """, (str(user_id),))
                            
                            cook_dates = [row['cook_date'] for row in check_cursor.fetchall()]
                        
                        print(f"🔍 Consecutive days check - Found {len(cook_dates)} cooking dates")
                        if cook_dates:
                            print(f"   Dates: {cook_dates}")
                        
                        if len(cook_dates) > 0:
                            # Count consecutive days from the most recent cooking date backwards
                            from datetime import timedelta
                            consecutive_days = 1  # Start with 1 for the first date
                            current_date = cook_dates[0]
                            
                            for i in range(1, len(cook_dates)):
                                expected_date = current_date - timedelta(days=i)
                                if cook_dates[i] == expected_date:
                                    consecutive_days += 1
                                else:
                                    print(f"   Streak broken at day {i+1}: expected {expected_date}, got {cook_dates[i]}")
                                    break  # Streak is broken
                            
                            print(f"   🔥 Consecutive days calculated: {consecutive_days}")
                            
                            # For consecutive days, we need to update with actual count, not increment
                            consecutive_result = ChallengeRepository.update_goal_progress_absolute(
                                user_challenge_id=user_challenge_id,
                                goal_id=goal_id,
                                progress_value=consecutive_days
                            )
                            
                            if consecutive_result:
                                print(f"   ✅ Updated consecutive days goal: {consecutive_days}/{goal['goal_target']}")
                                updated_goals.append(consecutive_result)
                            else:
                                print(f"   ⚠️ Failed to update consecutive days goal")
                        
                        should_increment = False  # Already handled, don't use regular increment
                    except Exception as e:
                        print(f"❌ Error checking consecutive days: {e}")
                        import traceback
                        traceback.print_exc()
                        pass
                
                # Update goal if criteria met
                if should_increment:
                    result = ChallengeRepository.update_goal_progress(
                        user_challenge_id=user_challenge_id,
                        goal_id=goal_id,
                        progress_increment=1
                    )
                    
                    if result:
                        updated_goals.append(result)
                        
                        if result.get('challenge_completed'):
                            completed_challenges.append({
                                'user_challenge_id': user_challenge_id,
                                'points_awarded': result.get('points_awarded', 0)
                            })
            
            return {
                "updated_goals": updated_goals,
                "completed_challenges": completed_challenges
            }
            
        except Exception as e:
            print(f"Error updating challenges on journal entry: {e}")
            return {"updated_goals": [], "completed_challenges": []}

    @staticmethod
    def update_challenges_on_budget_entry(
        user_id: UUID,
        cost: float,
        daily_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update challenge goal progress when user creates a budget entry
        Returns dict with updated goals and completed challenges
        """
        try:
            with db.get_cursor() as cursor:
                # Get active budget-related challenge goals
                cursor.execute("""
                    SELECT 
                        uc.id as user_challenge_id,
                        uc.challenge_id,
                        c.type as challenge_type,
                        ucg.id as user_goal_id,
                        ucg.goal_id,
                        cg.description as goal_description,
                        cg.target as goal_target,
                        ucg.progress as current_progress
                    FROM user_challenges uc
                    JOIN challenges c ON uc.challenge_id = c.id
                    JOIN user_challenge_goals ucg ON ucg.user_challenge_id = uc.id
                    JOIN challenge_goals cg ON ucg.goal_id = cg.id
                    WHERE uc.user_id = %s 
                    AND uc.status = 'active' 
                    AND ucg.completed = FALSE
                    AND (LOWER(cg.description) LIKE '%budget%' 
                         OR LOWER(cg.description) LIKE '%save%' 
                         OR LOWER(cg.description) LIKE '%spend%')
                """, (str(user_id),))
                
                active_goals = cursor.fetchall()
            
            updated_goals = []
            completed_challenges = []
            
            # Process budget-related goals
            for goal in active_goals:
                should_increment = False
                user_challenge_id = goal['user_challenge_id']
                goal_id = goal['goal_id']
                goal_description = goal['goal_description'].lower()
                
                # "Stay under budget" goals
                if "under budget" in goal_description and daily_budget:
                    if cost <= daily_budget:
                        should_increment = True
                
                # "Save X dollars" goals (track total savings)
                elif "save" in goal_description and "$" in goal_description:
                    # This would need to calculate actual savings vs. expected cost
                    # For now, we'll increment based on under-budget meals
                    if daily_budget and cost < daily_budget:
                        savings = daily_budget - cost
                        result = ChallengeRepository.update_goal_progress(
                            user_challenge_id=user_challenge_id,
                            goal_id=goal_id,
                            progress_increment=int(savings)
                        )
                        
                        if result:
                            updated_goals.append(result)
                            
                            if result.get('challenge_completed'):
                                completed_challenges.append({
                                    'user_challenge_id': user_challenge_id,
                                    'points_awarded': result.get('points_awarded', 0)
                                })
                    continue
                
                # Update goal if criteria met
                if should_increment:
                    result = ChallengeRepository.update_goal_progress(
                        user_challenge_id=user_challenge_id,
                        goal_id=goal_id,
                        progress_increment=1
                    )
                    
                    if result:
                        updated_goals.append(result)
                        
                        if result.get('challenge_completed'):
                            completed_challenges.append({
                                'user_challenge_id': user_challenge_id,
                                'points_awarded': result.get('points_awarded', 0)
                            })
            
            return {
                "updated_goals": updated_goals,
                "completed_challenges": completed_challenges
            }
            
        except Exception as e:
            print(f"Error updating challenges on budget entry: {e}")
            return {"updated_goals": [], "completed_challenges": []}

    @staticmethod
    def check_streak_goals(user_id: UUID) -> Dict[str, Any]:
        """
        Check and update streak-based goals daily
        Should be called by a scheduler or on user login
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get active streak goals
                cursor.execute("""
                    SELECT 
                        uc.id as user_challenge_id,
                        ucg.goal_id,
                        cg.description,
                        cg.target
                    FROM user_challenges uc
                    JOIN user_challenge_goals ucg ON ucg.user_challenge_id = uc.id
                    JOIN challenge_goals cg ON ucg.goal_id = cg.id
                    WHERE uc.user_id = %s 
                    AND uc.status = 'active' 
                    AND ucg.completed = FALSE
                    AND (LOWER(cg.description) LIKE '%streak%' 
                         OR LOWER(cg.description) LIKE '%consecutive%')
                """, (str(user_id),))
                
                streak_goals = cursor.fetchall()
                
                updated_goals = []
                completed_challenges = []
                
                for goal in streak_goals:
                    user_challenge_id = goal['user_challenge_id']
                    goal_id = goal['goal_id']
                    
                    # Calculate current streak
                    cursor.execute("""
                        WITH RECURSIVE date_series AS (
                            SELECT 
                                CURRENT_DATE as check_date,
                                0 as days_back
                            UNION ALL
                            SELECT 
                                check_date - INTERVAL '1 day',
                                days_back + 1
                            FROM date_series
                            WHERE days_back < 30
                        )
                        SELECT COUNT(*) as streak
                        FROM (
                            SELECT ds.check_date
                            FROM date_series ds
                            WHERE EXISTS (
                                SELECT 1 
                                FROM journal_entries je
                                WHERE je.user_id = %s
                                AND je.type = 'meal'
                                AND DATE(je.timestamp) = ds.check_date
                            )
                            ORDER BY ds.check_date DESC
                        ) consecutive_days
                    """, (str(user_id),))
                    
                    current_streak = cursor.fetchone()['streak']
                    
                    # Update goal progress to match streak
                    cursor.execute("""
                        UPDATE user_challenge_goals
                        SET progress = %s, updated_at = NOW()
                        WHERE user_challenge_id = %s AND goal_id = %s
                    """, (current_streak, str(user_challenge_id), str(goal_id)))
                
                return {
                    "updated_goals": updated_goals,
                    "completed_challenges": completed_challenges
                }
                
        except Exception as e:
            print(f"Error checking streak goals: {e}")
            return {"updated_goals": [], "completed_challenges": []}
