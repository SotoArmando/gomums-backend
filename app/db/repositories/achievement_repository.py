"""
Achievement Repository
Database operations for achievements and user achievements
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.database import db


class AchievementRepository:
    """Repository for achievement operations"""
    
    db = db
    
    @staticmethod
    def create_achievement(achievement_data: dict) -> Optional[dict]:
        """
        Create a new achievement
        
        Args:
            achievement_data: Dict with title, description, icon, category, target, points
            
        Returns:
            Created achievement dict or None
        """
        try:
            with AchievementRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO achievements (title, description, icon, category, target, points)
                    VALUES (%(title)s, %(description)s, %(icon)s, %(category)s, %(target)s, %(points)s)
                    RETURNING id, title, description, icon, category, target, points, 
                              created_at, updated_at
                """, achievement_data)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error creating achievement: {e}")
            return None
    
    @staticmethod
    def get_achievement(achievement_id: str) -> Optional[dict]:
        """Get achievement by ID"""
        try:
            with AchievementRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, description, icon, category, target, points,
                           created_at, updated_at
                    FROM achievements
                    WHERE id = %s
                """, (achievement_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error fetching achievement: {e}")
            return None
    
    @staticmethod
    def get_all_achievements(category: Optional[str] = None) -> List[dict]:
        """
        Get all achievements, optionally filtered by category
        
        Args:
            category: Optional category filter
            
        Returns:
            List of achievement dicts
        """
        try:
            with AchievementRepository.db.get_cursor() as cursor:
                if category:
                    cursor.execute("""
                        SELECT id, title, description, icon, category, target, points,
                               created_at, updated_at
                        FROM achievements
                        WHERE category = %s
                        ORDER BY target ASC, points ASC
                    """, (category,))
                else:
                    cursor.execute("""
                        SELECT id, title, description, icon, category, target, points,
                               created_at, updated_at
                        FROM achievements
                        ORDER BY category ASC, target ASC
                    """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching achievements: {e}")
            return []
    
    @staticmethod
    def seed_achievements(achievements: List[dict]) -> int:
        """
        Seed predefined achievements (idempotent - skips existing)
        
        Args:
            achievements: List of achievement dicts
            
        Returns:
            Number of achievements created
        """
        created = 0
        try:
            with AchievementRepository.db.get_cursor(commit=True) as cursor:
                for achievement in achievements:
                    # Check if achievement already exists
                    cursor.execute("""
                        SELECT id FROM achievements WHERE title = %s
                    """, (achievement['title'],))
                    
                    if cursor.fetchone():
                        continue  # Skip existing
                    
                    # Create new achievement
                    cursor.execute("""
                        INSERT INTO achievements (title, description, icon, category, target, points)
                        VALUES (%(title)s, %(description)s, %(icon)s, %(category)s, %(target)s, %(points)s)
                    """, achievement)
                    created += 1
            
            return created
        except Exception as e:
            print(f"Error seeding achievements: {e}")
            return created
    
    # ==================== User Achievements ====================
    
    @staticmethod
    def get_user_achievements(user_id: str, category: Optional[str] = None) -> List[dict]:
        """
        Get all achievements for a user with progress
        
        Args:
            user_id: User ID
            category: Optional category filter
            
        Returns:
            List of achievements with user progress
        """
        try:
            with AchievementRepository.db.get_cursor() as cursor:
                category_filter = "AND a.category = %(category)s" if category else ""
                
                query = f"""
                    SELECT 
                        COALESCE(ua.id::text, gen_random_uuid()::text) as id,
                        a.id as achievement_id,
                        a.title as achievement_title,
                        a.description as achievement_description,
                        a.icon as achievement_icon,
                        a.category as achievement_category,
                        a.target as achievement_target,
                        a.points as achievement_points,
                        COALESCE(ua.progress, 0) as progress,
                        ua.unlocked_date,
                        (ua.unlocked_date IS NOT NULL) as is_unlocked,
                        CASE 
                            WHEN a.target > 0 THEN (COALESCE(ua.progress, 0)::float / a.target * 100)
                            ELSE 0
                        END as progress_percentage,
                        COALESCE(ua.created_at, NOW()) as created_at,
                        COALESCE(ua.updated_at, NOW()) as updated_at,
                        %(user_id)s as user_id
                    FROM achievements a
                    LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = %(user_id2)s
                    WHERE 1=1 {category_filter}
                    ORDER BY is_unlocked DESC, a.category ASC, a.target ASC
                """
                
                params = {'user_id': user_id, 'user_id2': user_id}
                if category:
                    params['category'] = category
                
                cursor.execute(query, params)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching user achievements: {e}")
            return []
    
    @staticmethod
    def get_user_achievement_summary(user_id: str) -> Optional[dict]:
        """
        Get summary of user's achievements
        
        Returns:
            Summary dict with counts and recent unlocks
        """
        try:
            with AchievementRepository.db.get_cursor() as cursor:
                # Get counts and totals
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT a.id) as total_achievements,
                        COUNT(DISTINCT ua.id) FILTER (WHERE ua.unlocked_date IS NOT NULL) as unlocked_achievements,
                        COUNT(DISTINCT a.id) FILTER (WHERE ua.unlocked_date IS NULL) as locked_achievements,
                        COALESCE(SUM(a.points) FILTER (WHERE ua.unlocked_date IS NOT NULL), 0) as total_points_earned
                    FROM achievements a
                    LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = %s
                """, (user_id,))
                
                summary = dict(cursor.fetchone())
                
                # Get achievements by category
                cursor.execute("""
                    SELECT 
                        a.category,
                        COUNT(DISTINCT a.id) as total,
                        COUNT(DISTINCT ua.id) FILTER (WHERE ua.unlocked_date IS NOT NULL) as unlocked
                    FROM achievements a
                    LEFT JOIN user_achievements ua ON ua.achievement_id = a.id AND ua.user_id = %s
                    GROUP BY a.category
                    ORDER BY a.category
                """, (user_id,))
                
                categories = {}
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    categories[row_dict['category']] = {
                        'total': row_dict['total'],
                        'unlocked': row_dict['unlocked']
                    }
                
                summary['achievements_by_category'] = categories
                
                # Get recent unlocks (last 5)
                cursor.execute("""
                    SELECT 
                        ua.id,
                        ua.user_id,
                        ua.achievement_id,
                        ua.progress,
                        ua.unlocked_date,
                        a.title as achievement_title,
                        a.description as achievement_description,
                        a.icon as achievement_icon,
                        a.category as achievement_category,
                        a.target as achievement_target,
                        a.points as achievement_points,
                        true as is_unlocked,
                        100.0 as progress_percentage,
                        ua.created_at,
                        ua.updated_at
                    FROM user_achievements ua
                    JOIN achievements a ON a.id = ua.achievement_id
                    WHERE ua.user_id = %s AND ua.unlocked_date IS NOT NULL
                    ORDER BY ua.unlocked_date DESC
                    LIMIT 5
                """, (user_id,))
                
                summary['recent_unlocks'] = [dict(row) for row in cursor.fetchall()]
                
                return summary
        except Exception as e:
            print(f"Error fetching achievement summary: {e}")
            return None
    
    @staticmethod
    def update_progress(user_id: str, achievement_id: str, progress: int) -> Optional[dict]:
        """
        Update progress on an achievement and unlock if target reached
        
        Args:
            user_id: User ID
            achievement_id: Achievement ID
            progress: New progress value
            
        Returns:
            Updated user_achievement dict or None
        """
        try:
            with AchievementRepository.db.get_cursor(commit=True) as cursor:
                # Get achievement target
                cursor.execute("""
                    SELECT target, points FROM achievements WHERE id = %s
                """, (achievement_id,))
                
                achievement = cursor.fetchone()
                if not achievement:
                    return None
                
                target = achievement['target']
                points = achievement['points']
                
                # Determine if unlocked
                unlocked = progress >= target
                unlocked_date = "NOW()" if unlocked else "NULL"
                
                # Upsert user_achievement
                cursor.execute(f"""
                    INSERT INTO user_achievements (user_id, achievement_id, progress, unlocked_date)
                    VALUES (%s, %s, %s, {unlocked_date})
                    ON CONFLICT (user_id, achievement_id) 
                    DO UPDATE SET 
                        progress = EXCLUDED.progress,
                        unlocked_date = CASE 
                            WHEN user_achievements.unlocked_date IS NULL AND EXCLUDED.progress >= %s 
                            THEN NOW() 
                            ELSE user_achievements.unlocked_date 
                        END,
                        updated_at = NOW()
                    RETURNING id, user_id, achievement_id, progress, unlocked_date, created_at, updated_at
                """, (user_id, achievement_id, progress, target))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    result['was_just_unlocked'] = unlocked and result['unlocked_date'] is not None
                    result['points_awarded'] = points if result['was_just_unlocked'] else 0
                    return result
                return None
        except Exception as e:
            print(f"Error updating achievement progress: {e}")
            return None
    
    @staticmethod
    def check_and_unlock_achievements(user_id: str, stats: dict) -> List[dict]:
        """
        Check user stats and unlock eligible achievements
        
        Args:
            user_id: User ID
            stats: User stats dict with meals, savings, streak, etc.
            
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        try:
            with AchievementRepository.db.get_cursor(commit=True) as cursor:
                # Get all achievements
                cursor.execute("""
                    SELECT id, title, category, target, points FROM achievements
                """)
                
                achievements = [dict(row) for row in cursor.fetchall()]
                
                for achievement in achievements:
                    # Determine progress based on category
                    progress = 0
                    category = achievement['category']
                    
                    if category == 'cooking':
                        progress = stats.get('total_meals_cooked', 0)
                    elif category == 'savings':
                        progress = int(stats.get('total_money_saved', 0))
                    elif category == 'streak':
                        progress = stats.get('current_streak', 0)
                    elif category == 'challenges':
                        progress = stats.get('challenges_completed', 0)
                    elif category == 'missions':
                        progress = stats.get('missions_completed', 0)
                    elif category == 'special':
                        # Special handling for specific achievements
                        if 'Batch' in achievement['title']:
                            progress = stats.get('batch_meals_cooked', 0)
                        elif 'Leftover' in achievement['title'] or 'Zero Waste' in achievement['title']:
                            progress = stats.get('leftover_meals_cooked', 0)
                        elif 'Early Adopter' in achievement['title']:
                            progress = 1  # Auto-grant to all users
                    
                    # Check if should unlock
                    if progress >= achievement['target']:
                        # Check if already unlocked
                        cursor.execute("""
                            SELECT unlocked_date FROM user_achievements
                            WHERE user_id = %s AND achievement_id = %s
                        """, (user_id, achievement['id']))
                        
                        existing = cursor.fetchone()
                        
                        if not existing or existing['unlocked_date'] is None:
                            # Unlock achievement
                            result = AchievementRepository.update_progress(
                                user_id, achievement['id'], progress
                            )
                            
                            if result and result.get('was_just_unlocked'):
                                newly_unlocked.append({
                                    'achievement_id': achievement['id'],
                                    'title': achievement['title'],
                                    'points': achievement['points']
                                })
            
            return newly_unlocked
        except Exception as e:
            print(f"Error checking achievements: {e}")
            return newly_unlocked
