"""
Smart Suggestions Repository
Database operations and suggestion generation logic
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from app.core.database import db
from app.models.smart_suggestion import SUGGESTION_TEMPLATES, SuggestionType, DotColor


class SmartSuggestionRepository:
    """Repository for smart suggestions with generation logic"""
    
    db = db
    
    # ==================== CRUD Operations ====================
    
    @staticmethod
    def create_suggestion(user_id: str, suggestion_data: dict) -> Optional[dict]:
        """Create a new suggestion"""
        try:
            with SmartSuggestionRepository.db.get_cursor(commit=True) as cursor:
                params = {'user_id': user_id, **suggestion_data}
                cursor.execute("""
                    INSERT INTO smart_suggestions 
                        (user_id, title, subtitle, description, type, dot_color, action_text, priority)
                    VALUES 
                        (%(user_id)s, %(title)s, %(subtitle)s, %(description)s, %(type)s, 
                         %(dot_color)s, %(action_text)s, COALESCE(%(priority)s, 0))
                    RETURNING id, user_id, title, subtitle, description, type, dot_color,
                              action_text, priority, dismissed, created_at, updated_at
                """, params)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error creating suggestion: {e}")
            return None
    
    @staticmethod
    def get_user_suggestions(user_id: str, include_dismissed: bool = False,
                            type_filter: Optional[str] = None,
                            limit: int = 10) -> List[dict]:
        """Get suggestions for a user"""
        try:
            with SmartSuggestionRepository.db.get_cursor() as cursor:
                dismissed_filter = "" if include_dismissed else "AND NOT dismissed"
                type_filter_sql = "AND type = %(type)s" if type_filter else ""
                
                query = f"""
                    SELECT id, user_id, title, subtitle, description, type, dot_color,
                           action_text, priority, dismissed, created_at, updated_at
                    FROM smart_suggestions
                    WHERE user_id = %(user_id)s {dismissed_filter} {type_filter_sql}
                    ORDER BY priority DESC, created_at DESC
                    LIMIT %(limit)s
                """
                
                cursor.execute(query, {
                    'user_id': user_id,
                    'type': type_filter,
                    'limit': limit
                })
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching suggestions: {e}")
            return []
    
    @staticmethod
    def update_suggestion(suggestion_id: str, user_id: str, updates: dict) -> Optional[dict]:
        """Update a suggestion"""
        try:
            allowed_fields = ['title', 'subtitle', 'description', 'type', 'dot_color',
                            'action_text', 'priority', 'dismissed']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    values[field] = updates[field]
            
            if not set_parts:
                return None
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['suggestion_id'] = suggestion_id
            values['user_id'] = user_id
            
            with SmartSuggestionRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE smart_suggestions
                    SET {set_clause}
                    WHERE id = %(suggestion_id)s AND user_id = %(user_id)s
                    RETURNING id, user_id, title, subtitle, description, type, dot_color,
                              action_text, priority, dismissed, created_at, updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error updating suggestion: {e}")
            return None
    
    @staticmethod
    def dismiss_suggestion(suggestion_id: str, user_id: str) -> bool:
        """Dismiss a suggestion"""
        try:
            with SmartSuggestionRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE smart_suggestions
                    SET dismissed = true, updated_at = NOW()
                    WHERE id = %s AND user_id = %s
                """, (suggestion_id, user_id))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error dismissing suggestion: {e}")
            return False
    
    @staticmethod
    def delete_suggestion(suggestion_id: str, user_id: str) -> bool:
        """Delete a suggestion"""
        try:
            with SmartSuggestionRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM smart_suggestions
                    WHERE id = %s AND user_id = %s
                """, (suggestion_id, user_id))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting suggestion: {e}")
            return False
    
    @staticmethod
    def clear_old_suggestions(user_id: str, days: int = 7) -> int:
        """Clear old dismissed suggestions"""
        try:
            with SmartSuggestionRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM smart_suggestions
                    WHERE user_id = %s 
                      AND dismissed = true 
                      AND updated_at < NOW() - INTERVAL '%s days'
                """, (user_id, days))
                
                return cursor.rowcount
        except Exception as e:
            print(f"Error clearing old suggestions: {e}")
            return 0
    
    # ==================== Suggestion Generation Logic ====================
    
    @staticmethod
    def generate_suggestions(user_id: str, max_suggestions: int = 5) -> List[dict]:
        """
        Generate personalized suggestions based on user data
        
        Analyzes:
        - User stats (meals, streak, savings)
        - Journal entries (leftovers, recent activity)
        - Meal plans (active, incomplete)
        - Challenges (active, near completion)
        - Achievements (close to unlock)
        """
        suggestions = []
        
        try:
            with SmartSuggestionRepository.db.get_cursor() as cursor:
                # Get user stats
                cursor.execute("""
                    SELECT total_meals_cooked, current_streak, total_money_saved,
                           last_activity_date, achievements_unlocked
                    FROM user_stats
                    WHERE user_id = %s
                """, (user_id,))
                
                stats = cursor.fetchone()
                if stats:
                    stats = dict(stats)
                else:
                    stats = {
                        'total_meals_cooked': 0,
                        'current_streak': 0,
                        'total_money_saved': 0,
                        'last_activity_date': None,
                        'achievements_unlocked': 0
                    }
                
                # 1. Check for streak maintenance (HIGH PRIORITY)
                if stats['current_streak'] >= 3:
                    last_activity = stats.get('last_activity_date')
                    if last_activity:
                        days_since = (date.today() - last_activity).days
                        if days_since == 0:
                            # Already cooked today, encourage tomorrow
                            pass
                        elif days_since == 1:
                            # Haven't cooked today - HIGH PRIORITY
                            template = SUGGESTION_TEMPLATES['maintain_streak']
                            suggestions.append({
                                'title': template['title'],
                                'subtitle': f"{stats['current_streak']} day streak",
                                'description': f"You're on a roll! Cook today to maintain your {stats['current_streak']} day cooking streak",
                                'type': template['type'],
                                'dot_color': template['dot_color'],
                                'action_text': template['action_text'],
                                'priority': 90
                            })
                
                # 2. Check for active leftovers (HIGH PRIORITY)
                cursor.execute("""
                    SELECT COUNT(*) as leftover_count
                    FROM journal_entries
                    WHERE user_id = %s 
                      AND type = 'meal'
                      AND status IN ('leftovers', 'fresh')
                      AND portions_left > 0
                """, (user_id,))
                
                leftover_result = cursor.fetchone()
                if leftover_result and leftover_result['leftover_count'] > 0:
                    template = SUGGESTION_TEMPLATES['use_leftovers']
                    suggestions.append({
                        'title': template['title'],
                        'subtitle': f"You have {leftover_result['leftover_count']} leftover items",
                        'description': "Reduce waste and save money by using your leftovers today",
                        'type': template['type'],
                        'dot_color': template['dot_color'],
                        'action_text': template['action_text'],
                        'priority': 75
                    })
                
                # 3. Check for active challenges near completion
                cursor.execute("""
                    SELECT c.title, c.points, 
                           COALESCE(SUM(ucg.progress), 0) as total_progress,
                           COALESCE(SUM(cg.target), 1) as total_target
                    FROM user_challenges uc
                    JOIN challenges c ON c.id = uc.challenge_id
                    LEFT JOIN user_challenge_goals ucg ON ucg.user_challenge_id = uc.id
                    LEFT JOIN challenge_goals cg ON cg.id = ucg.goal_id
                    WHERE uc.user_id = %s 
                      AND uc.status = 'active'
                    GROUP BY c.id, c.title, c.points
                    HAVING COALESCE(SUM(ucg.progress), 0)::float / COALESCE(SUM(cg.target), 1) >= 0.5
                    ORDER BY COALESCE(SUM(ucg.progress), 0)::float / COALESCE(SUM(cg.target), 1) DESC
                    LIMIT 1
                """, (user_id,))
                
                challenge = cursor.fetchone()
                if challenge:
                    challenge = dict(challenge)
                    progress_pct = int((challenge['total_progress'] / challenge['total_target']) * 100)
                    remaining = challenge['total_target'] - challenge['total_progress']
                    
                    template = SUGGESTION_TEMPLATES['complete_challenge']
                    suggestions.append({
                        'title': template['title'],
                        'subtitle': f"You're {progress_pct}% done with {challenge['title']}",
                        'description': f"Keep going! Just {remaining} more to finish and earn {challenge['points']} points",
                        'type': template['type'],
                        'dot_color': template['dot_color'],
                        'action_text': template['action_text'],
                        'priority': 80
                    })
                
                # 4. Check for incomplete meal plans (MEDIUM PRIORITY)
                cursor.execute("""
                    SELECT mp.id, mp.name, mp.start_date, mp.end_date,
                           COUNT(pm.id) as meal_count
                    FROM meal_plans mp
                    LEFT JOIN planned_meals pm ON pm.meal_plan_id = mp.id
                    WHERE mp.user_id = %s 
                      AND mp.status = 'draft'
                      AND mp.start_date <= CURRENT_DATE + INTERVAL '7 days'
                      AND mp.end_date >= CURRENT_DATE
                    GROUP BY mp.id
                    HAVING COUNT(pm.id) < 14  -- Less than 2 meals per day for a week
                    ORDER BY mp.start_date ASC
                    LIMIT 1
                """, (user_id,))
                
                meal_plan = cursor.fetchone()
                if meal_plan:
                    meal_plan = dict(meal_plan)
                    days = (meal_plan['end_date'] - meal_plan['start_date']).days + 1
                    expected_meals = days * 2  # At least 2 meals per day
                    empty_slots = expected_meals - meal_plan['meal_count']
                    
                    if empty_slots > 0:
                        template = SUGGESTION_TEMPLATES['complete_meal_plan']
                        suggestions.append({
                            'title': template['title'],
                            'subtitle': f"You have {empty_slots} empty meal slots",
                            'description': "Fill in the remaining days to make the most of your weekly plan",
                            'type': template['type'],
                            'dot_color': template['dot_color'],
                            'action_text': template['action_text'],
                            'priority': 65
                        })
                
                # 5. Check for achievementsclose to unlock (MEDIUM PRIORITY)
                cursor.execute("""
                    SELECT a.title, a.target, a.category,
                           COALESCE(ua.progress, 0) as progress
                    FROM achievements a
                    LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = %s
                    WHERE (ua.unlocked_date IS NULL OR ua.id IS NULL)
                      AND COALESCE(ua.progress, 0)::float / a.target >= 0.7
                    ORDER BY COALESCE(ua.progress, 0)::float / a.target DESC
                    LIMIT 1
                """, (user_id,))
                
                achievement = cursor.fetchone()
                if achievement:
                    achievement = dict(achievement)
                    remaining = achievement['target'] - achievement['progress']
                    metric = "meals" if achievement['category'] == 'cooking' else "points"
                    
                    template = SUGGESTION_TEMPLATES['close_to_achievement']
                    suggestions.append({
                        'title': template['title'],
                        'subtitle': achievement['title'],
                        'description': f"You're almost there! Just {remaining} more {metric} to unlock this achievement",
                        'type': template['type'],
                        'dot_color': template['dot_color'],
                        'action_text': template['action_text'],
                        'priority': 70
                    })
                
                # 6. Check if no meal plan exists for current week (MEDIUM PRIORITY)
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM meal_plans
                    WHERE user_id = %s 
                      AND start_date <= CURRENT_DATE
                      AND end_date >= CURRENT_DATE
                """, (user_id,))
                
                plan_count = cursor.fetchone()
                if plan_count and plan_count['count'] == 0:
                    template = SUGGESTION_TEMPLATES['plan_week']
                    suggestions.append({
                        'title': template['title'],
                        'subtitle': template['subtitle'],
                        'description': template['description'],
                        'type': template['type'],
                        'dot_color': template['dot_color'],
                        'action_text': template['action_text'],
                        'priority': 60
                    })
                
                # 7. Check for available challenges (LOW-MEDIUM PRIORITY)
                if len(suggestions) < max_suggestions:
                    cursor.execute("""
                        SELECT c.title, c.description, c.points
                        FROM challenges c
                        WHERE c.id NOT IN (
                            SELECT challenge_id 
                            FROM user_challenges 
                            WHERE user_id = %s 
                              AND status IN ('active', 'completed')
                        )
                        ORDER BY c.points DESC
                        LIMIT 1
                    """, (user_id,))
                    
                    new_challenge = cursor.fetchone()
                    if new_challenge:
                        new_challenge = dict(new_challenge)
                        template = SUGGESTION_TEMPLATES['start_challenge']
                        suggestions.append({
                            'title': template['title'],
                            'subtitle': new_challenge['title'],
                            'description': f"Challenge yourself and earn {new_challenge['points']} points",
                            'type': template['type'],
                            'dot_color': template['dot_color'],
                            'action_text': template['action_text'],
                            'priority': 55
                        })
                
                # 8. Add general tips if we don't have enough suggestions (LOW PRIORITY)
                if len(suggestions) < max_suggestions:
                    tips = ['save_money_tip', 'meal_prep_tip', 'batch_cooking']
                    for tip_key in tips:
                        if len(suggestions) >= max_suggestions:
                            break
                        if tip_key in SUGGESTION_TEMPLATES:
                            template = SUGGESTION_TEMPLATES[tip_key]
                            suggestions.append({
                                'title': template['title'],
                                'subtitle': template.get('subtitle', ''),
                                'description': template.get('description', ''),
                                'type': template['type'],
                                'dot_color': template['dot_color'],
                                'action_text': template['action_text'],
                                'priority': template.get('priority', 40)
                            })
                
                # Limit to max_suggestions
                suggestions = sorted(suggestions, key=lambda x: x['priority'], reverse=True)[:max_suggestions]
                
                return suggestions
                
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return []
    
    @staticmethod
    def refresh_suggestions(user_id: str, max_suggestions: int = 5) -> List[dict]:
        """Clear old suggestions and generate new ones"""
        try:
            # Delete old non-dismissed suggestions (keep dismissed for user reference)
            with SmartSuggestionRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM smart_suggestions
                    WHERE user_id = %s AND NOT dismissed
                """, (user_id,))
            
            # Generate new suggestions
            new_suggestions_data = SmartSuggestionRepository.generate_suggestions(
                user_id=user_id,
                max_suggestions=max_suggestions
            )
            
            # Create new suggestion records
            created_suggestions = []
            for suggestion_data in new_suggestions_data:
                suggestion = SmartSuggestionRepository.create_suggestion(
                    user_id=user_id,
                    suggestion_data=suggestion_data
                )
                if suggestion:
                    created_suggestions.append(suggestion)
            
            return created_suggestions
            
        except Exception as e:
            print(f"Error refreshing suggestions: {e}")
            return []
    
    @staticmethod
    def get_suggestion_stats(user_id: str) -> Optional[dict]:
        """Get statistics about user's suggestions"""
        try:
            with SmartSuggestionRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_suggestions,
                        COUNT(*) FILTER (WHERE NOT dismissed) as active_suggestions,
                        COUNT(*) FILTER (WHERE dismissed) as dismissed_suggestions,
                        MAX(updated_at) as most_recent_update
                    FROM smart_suggestions
                    WHERE user_id = %s
                """, (user_id,))
                
                stats = dict(cursor.fetchone())
                
                # Get by type
                cursor.execute("""
                    SELECT type, COUNT(*) as count
                    FROM smart_suggestions
                    WHERE user_id = %s AND NOT dismissed
                    GROUP BY type
                """, (user_id,))
                
                by_type = {}
                for row in cursor.fetchall():
                    by_type[row['type']] = row['count']
                
                stats['suggestions_by_type'] = by_type
                
                return stats
        except Exception as e:
            print(f"Error getting suggestion stats: {e}")
            return None
