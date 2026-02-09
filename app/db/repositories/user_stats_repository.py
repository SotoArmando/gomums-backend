"""
User Stats Repository - Database operations for user statistics
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from app.core.database import db
from decimal import Decimal


class UserStatsRepository:
    """Repository for user stats database operations"""
    
    @staticmethod
    def get_or_create_stats(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user stats, create if doesn't exist
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User stats dictionary or None
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Try to get existing stats
                cursor.execute("""
                    SELECT id, user_id, total_meals_cooked, total_money_saved,
                           current_streak, achievements_unlocked, level, points,
                           last_activity_date, created_at, updated_at
                    FROM user_stats
                    WHERE user_id = %s
                """, (user_id,))
                
                stats = cursor.fetchone()
                
                if stats:
                    return dict(stats)
                
                # Create new stats record if doesn't exist
                cursor.execute("""
                    INSERT INTO user_stats (user_id, total_meals_cooked, total_money_saved,
                                          current_streak, achievements_unlocked, level, points)
                    VALUES (%s, 0, 0, 0, 0, 1, 0)
                    RETURNING id, user_id, total_meals_cooked, total_money_saved,
                             current_streak, achievements_unlocked, level, points,
                             last_activity_date, created_at, updated_at
                """, (user_id,))
                
                new_stats = cursor.fetchone()
                return dict(new_stats) if new_stats else None
                
        except Exception as e:
            print(f"Error getting/creating user stats: {e}")
            return None
    
    @staticmethod
    def increment_stats(user_id: str, meals_cooked: int = 0, 
                       money_saved: float = 0.0, points: int = 0) -> bool:
        """
        Increment user stats and update streak
        
        Args:
            user_id: UUID of the user
            meals_cooked: Number of meals to add
            money_saved: Amount of money to add
            points: Points to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                # Get current stats
                cursor.execute("""
                    SELECT current_streak, last_activity_date, level, points
                    FROM user_stats
                    WHERE user_id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    # Create stats if doesn't exist
                    UserStatsRepository.get_or_create_stats(user_id)
                    result = {'current_streak': 0, 'last_activity_date': None, 'level': 1, 'points': 0}
                else:
                    result = dict(result)
                
                # Calculate new streak
                today = date.today()
                last_activity = result['last_activity_date']
                current_streak = result['current_streak']
                
                if last_activity:
                    days_diff = (today - last_activity).days
                    
                    if days_diff == 0:
                        # Same day - no streak change
                        new_streak = current_streak
                    elif days_diff == 1:
                        # Consecutive day - increment streak
                        new_streak = current_streak + 1
                    else:
                        # Streak broken - reset to 1
                        new_streak = 1
                else:
                    # First activity - start streak
                    new_streak = 1
                
                # Calculate level up
                current_points = result['points']
                current_level = result['level']
                new_total_points = current_points + points
                new_level = UserStatsRepository._calculate_level(new_total_points)
                
                # Update stats
                cursor.execute("""
                    UPDATE user_stats
                    SET total_meals_cooked = total_meals_cooked + %s,
                        total_money_saved = total_money_saved + %s,
                        points = points + %s,
                        current_streak = %s,
                        level = %s,
                        last_activity_date = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """, (meals_cooked, money_saved, points, new_streak, new_level, today, user_id))
                
                return True
                
        except Exception as e:
            print(f"Error incrementing user stats: {e}")
            return False
    
    @staticmethod
    def _calculate_level(points: int) -> int:
        """
        Calculate user level based on points
        
        Level formula: Every 1000 points = 1 level
        Level 1: 0-999 points
        Level 2: 1000-1999 points
        etc.
        
        Args:
            points: Total points
            
        Returns:
            User level
        """
        return max(1, (points // 1000) + 1)
    
    @staticmethod
    def _points_to_next_level(current_points: int) -> int:
        """
        Calculate points needed for next level
        
        Args:
            current_points: Current total points
            
        Returns:
            Points needed for next level
        """
        current_level = UserStatsRepository._calculate_level(current_points)
        next_level_threshold = current_level * 1000
        return next_level_threshold - current_points
    
    @staticmethod
    def get_stats_summary(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive stats summary including weekly and monthly data
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Stats summary dictionary
        """
        try:
            with db.get_cursor() as cursor:
                # Get basic stats
                stats = UserStatsRepository.get_or_create_stats(user_id)
                if not stats:
                    return None
                
                # Get this week's data from budget entries
                cursor.execute("""
                    SELECT 
                        COUNT(*) as meals_count,
                        COALESCE(SUM(cost), 0) as total_spent,
                        COALESCE(SUM(cost_per_serving * servings * 3) - SUM(cost), 0) as savings
                    FROM budget_entries
                    WHERE user_id = %s 
                    AND date >= CURRENT_DATE - INTERVAL '7 days'
                """, (user_id,))
                
                week_data = cursor.fetchone()
                
                # Get this month's data
                cursor.execute("""
                    SELECT 
                        COUNT(*) as meals_count,
                        COALESCE(SUM(cost), 0) as total_spent,
                        COALESCE(SUM(cost_per_serving * servings * 3) - SUM(cost), 0) as savings
                    FROM budget_entries
                    WHERE user_id = %s 
                    AND date >= DATE_TRUNC('month', CURRENT_DATE)
                """, (user_id,))
                
                month_data = cursor.fetchone()
                
                # Calculate level progress
                points = stats['points']
                level = stats['level']
                points_to_next = UserStatsRepository._points_to_next_level(points)
                level_progress = ((points % 1000) / 1000) * 100
                
                return {
                    'total_meals_cooked': stats['total_meals_cooked'],
                    'total_money_saved': float(stats['total_money_saved']),
                    'current_streak': stats['current_streak'],
                    'achievements_unlocked': stats['achievements_unlocked'],
                    'level': level,
                    'points': points,
                    'points_to_next_level': points_to_next,
                    'level_progress_percentage': round(level_progress, 2),
                    'money_saved_this_week': float(week_data['savings']) if week_data else 0.0,
                    'money_saved_this_month': float(month_data['savings']) if month_data else 0.0,
                    'meals_this_week': week_data['meals_count'] if week_data else 0,
                    'meals_this_month': month_data['meals_count'] if month_data else 0
                }
                
        except Exception as e:
            print(f"Error getting stats summary: {e}")
            return None
    
    @staticmethod
    def get_leaderboard(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get leaderboard of top users by points
        
        Args:
            limit: Number of entries to return
            offset: Number of entries to skip
            
        Returns:
            List of leaderboard entries
        """
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        us.user_id,
                        u.name as user_name,
                        us.points,
                        us.level,
                        us.total_meals_cooked,
                        us.total_money_saved,
                        ROW_NUMBER() OVER (ORDER BY us.points DESC) as rank
                    FROM user_stats us
                    JOIN users u ON us.user_id = u.id
                    WHERE u.is_active = TRUE
                    ORDER BY us.points DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
                
                entries = []
                for row in cursor.fetchall():
                    entries.append({
                        'user_id': str(row['user_id']),
                        'user_name': row['user_name'],
                        'points': row['points'],
                        'level': row['level'],
                        'total_meals_cooked': row['total_meals_cooked'],
                        'total_money_saved': float(row['total_money_saved']),
                        'rank': row['rank']
                    })
                
                return entries
                
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    @staticmethod
    def increment_achievements_count(user_id: str) -> bool:
        """
        Increment achievements unlocked count
        
        Args:
            user_id: UUID of the user
            
        Returns:
            True if successful
        """
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE user_stats
                    SET achievements_unlocked = achievements_unlocked + 1,
                        updated_at = NOW()
                    WHERE user_id = %s
                """, (user_id,))
                return True
        except Exception as e:
            print(f"Error incrementing achievements count: {e}")
            return False
