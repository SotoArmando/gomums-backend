from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from psycopg2.extras import RealDictRow

from app.core.database import db
from app.core.security import hash_password


class UserRepository:
    """Repository for user database operations"""
    
    @staticmethod
    def create_user(name: str, email: str, password: str, oauth_provider: str = "email") -> Optional[Dict[str, Any]]:
        """
        Create a new user in the database
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password (will be hashed)
            oauth_provider: Authentication provider ('email', 'google', 'facebook', 'apple')
        
        Returns:
            Dictionary with user data or None if email already exists
        """
        # Check if user already exists
        if UserRepository.get_user_by_email(email):
            return None
        
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        
        query = """
            INSERT INTO users (id, name, email, password_hash, oauth_provider, is_active, is_premium)
            VALUES (%s, %s, %s, %s, %s, TRUE, FALSE)
            RETURNING id, name, email, oauth_provider, oauth_id, avatar_url, is_active, is_premium, created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id, name, email, hashed_password, oauth_provider))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address
        
        Args:
            email: User's email address
        
        Returns:
            Dictionary with user data (including password_hash) or None if not found
        """
        query = """
            SELECT id, name, email, password_hash, oauth_provider, oauth_id, avatar_url, is_active, is_premium, created_at, updated_at
            FROM users
            WHERE email = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching user by email: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User's UUID
        
        Returns:
            Dictionary with user data (without password_hash) or None if not found
        """
        query = """
            SELECT id, name, email, oauth_provider, oauth_id, avatar_url, is_active, is_premium, created_at, updated_at
            FROM users
            WHERE id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update user fields
        
        Args:
            user_id: User's UUID
            **kwargs: Fields to update (name, email, etc.)
        
        Returns:
            Updated user dictionary or None if user not found
        """
        if not kwargs:
            return UserRepository.get_user_by_id(user_id)
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['name', 'email', 'is_active', 'is_premium']:
                set_clauses.append(f"{key} = %s")
                values.append(value)
        
        if not set_clauses:
            return UserRepository.get_user_by_id(user_id)
        
        values.append(user_id)
        query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s
            RETURNING id, name, email, oauth_provider, oauth_id, avatar_url, is_active, is_premium, created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Soft delete user (set is_active to False)
        
        Args:
            user_id: User's UUID
        
        Returns:
            True if successful, False otherwise
        """
        query = """
            UPDATE users
            SET is_active = FALSE, updated_at = NOW()
            WHERE id = %s
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    @staticmethod
    def update_last_login(user_id: str) -> None:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User's UUID
        """
        query = """
            UPDATE users
            SET updated_at = NOW()
            WHERE id = %s
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id,))
        except Exception as e:
            print(f"Error updating last login: {e}")
