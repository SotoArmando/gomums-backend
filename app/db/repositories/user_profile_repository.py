"""
User Profile Repository - Database operations for user profiles
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from app.core.database import db


class UserProfileRepository:
    """Repository for user profile-related database operations"""
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information
        
        Args:
            user_id: UUID of the user
        
        Returns:
            User profile dictionary or None if not found
        """
        query = """
            SELECT id, name, email, oauth_provider, oauth_id, avatar_url,
                   is_active, is_premium, created_at, updated_at
            FROM users
            WHERE id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'name': row['name'],
                    'email': row['email'],
                    'oauth_provider': row['oauth_provider'],
                    'oauth_id': row['oauth_id'],
                    'avatar_url': row['avatar_url'],
                    'is_active': row['is_active'],
                    'is_premium': row['is_premium'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    async def update_profile(
        self, 
        user_id: str, 
        name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile information
        
        Args:
            user_id: UUID of the user
            name: New name (optional)
            avatar_url: New avatar URL (optional)
        
        Returns:
            Updated profile dictionary or None if failed
        """
        # Build dynamic update query
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        
        if avatar_url is not None:
            updates.append("avatar_url = %s")
            params.append(avatar_url)
        
        if not updates:
            # No updates requested, just return current profile
            return await self.get_profile(user_id)
        
        updates.append("updated_at = NOW()")
        params.append(user_id)
        
        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, name, email, oauth_provider, oauth_id, avatar_url,
                      is_active, is_premium, created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'name': row['name'],
                    'email': row['email'],
                    'oauth_provider': row['oauth_provider'],
                    'oauth_id': row['oauth_id'],
                    'avatar_url': row['avatar_url'],
                    'is_active': row['is_active'],
                    'is_premium': row['is_premium'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error updating profile: {e}")
            return None
    
    async def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences
        
        Args:
            user_id: UUID of the user
        
        Returns:
            User preferences dictionary or None if not found
        """
        query = """
            SELECT id, user_id, dietary_restrictions, allergies, budget_goal,
                   household_size, skill_level, created_at, updated_at
            FROM user_preferences
            WHERE user_id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'user_id': str(row['user_id']),
                    'dietary_restrictions': row['dietary_restrictions'] if row['dietary_restrictions'] else [],
                    'allergies': row['allergies'] if row['allergies'] else [],
                    'budget_goal': row['budget_goal'],
                    'household_size': row['household_size'],
                    'skill_level': row['skill_level'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error getting preferences: {e}")
            return None
    
    async def upsert_preferences(
        self,
        user_id: str,
        dietary_restrictions: Optional[list] = None,
        allergies: Optional[list] = None,
        budget_goal: Optional[Decimal] = None,
        household_size: Optional[int] = None,
        skill_level: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create or update user preferences
        
        Args:
            user_id: UUID of the user
            dietary_restrictions: List of dietary restrictions (optional)
            allergies: List of allergies (optional)
            budget_goal: Budget goal (optional)
            household_size: Number of people in household (optional)
            skill_level: Cooking skill level (optional)
        
        Returns:
            Updated preferences dictionary or None if failed
        """
        # Check if preferences exist
        existing = await self.get_preferences(user_id)
        
        if existing:
            # Update existing preferences
            updates = []
            params = []
            
            if dietary_restrictions is not None:
                updates.append("dietary_restrictions = %s")
                params.append(dietary_restrictions)
            
            if allergies is not None:
                updates.append("allergies = %s")
                params.append(allergies)
            
            if budget_goal is not None:
                updates.append("budget_goal = %s")
                params.append(budget_goal)
            
            if household_size is not None:
                updates.append("household_size = %s")
                params.append(household_size)
            
            if skill_level is not None:
                updates.append("skill_level = %s")
                params.append(skill_level)
            
            if not updates:
                return existing
            
            updates.append("updated_at = NOW()")
            params.append(user_id)
            
            query = f"""
                UPDATE user_preferences
                SET {', '.join(updates)}
                WHERE user_id = %s
                RETURNING id, user_id, dietary_restrictions, allergies, budget_goal,
                          household_size, skill_level, created_at, updated_at
            """
        else:
            # Create new preferences
            query = """
                INSERT INTO user_preferences (
                    user_id, dietary_restrictions, allergies, budget_goal,
                    household_size, skill_level
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, dietary_restrictions, allergies, budget_goal,
                          household_size, skill_level, created_at, updated_at
            """
            params = [
                user_id,
                dietary_restrictions or [],
                allergies or [],
                budget_goal,
                household_size,
                skill_level
            ]
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'user_id': str(row['user_id']),
                    'dietary_restrictions': row['dietary_restrictions'] if row['dietary_restrictions'] else [],
                    'allergies': row['allergies'] if row['allergies'] else [],
                    'budget_goal': row['budget_goal'],
                    'household_size': row['household_size'],
                    'skill_level': row['skill_level'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error upserting preferences: {e}")
            return None
    
    async def get_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user statistics
        
        Args:
            user_id: UUID of the user
        
        Returns:
            User stats dictionary or None if not found
        """
        query = """
            SELECT id, user_id, total_meals_cooked, total_money_saved,
                   current_streak, achievements_unlocked, level, points,
                   last_activity_date, created_at, updated_at
            FROM user_stats
            WHERE user_id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    # Create stats if not exist
                    return await self.create_stats(user_id)
                
                return {
                    'id': str(row['id']),
                    'user_id': str(row['user_id']),
                    'total_meals_cooked': row['total_meals_cooked'],
                    'total_money_saved': row['total_money_saved'],
                    'current_streak': row['current_streak'],
                    'achievements_unlocked': row['achievements_unlocked'],
                    'level': row['level'],
                    'points': row['points'],
                    'last_activity_date': row['last_activity_date'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    async def create_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Create initial stats for a user
        
        Args:
            user_id: UUID of the user
        
        Returns:
            Created stats dictionary
        """
        query = """
            INSERT INTO user_stats (user_id)
            VALUES (%s)
            RETURNING id, user_id, total_meals_cooked, total_money_saved,
                      current_streak, achievements_unlocked, level, points,
                      last_activity_date, created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'user_id': str(row['user_id']),
                    'total_meals_cooked': row['total_meals_cooked'],
                    'total_money_saved': row['total_money_saved'],
                    'current_streak': row['current_streak'],
                    'achievements_unlocked': row['achievements_unlocked'],
                    'level': row['level'],
                    'points': row['points'],
                    'last_activity_date': row['last_activity_date'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error creating stats: {e}")
            return None
