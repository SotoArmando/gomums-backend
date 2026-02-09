from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import uuid

from app.core.database import db
from app.services.mission_service import MissionService


class BudgetRepository:
    """Repository for budget entry database operations"""
    
    @staticmethod
    def create_entry(user_id: str, entry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new budget entry
        
        Args:
            user_id: User's UUID
            entry_data: Dictionary containing entry data
        
        Returns:
            Dictionary with created entry data or None if failed
        """
        entry_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO budget_entries (
                id, user_id, date, meal_name, cost, servings, category, notes, journal_entry_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, date, meal_name, cost, servings, cost_per_serving,
                      category, notes, journal_entry_id, created_at, updated_at
        """
        
        values = (
            entry_id, user_id,
            entry_data["date"],
            entry_data["meal_name"],
            entry_data["cost"],
            entry_data["servings"],
            entry_data.get("category"),
            entry_data.get("notes"),
            entry_data.get("journal_entry_id")
        )
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    result_dict = dict(result)
                    
                    # Trigger mission updates (non-blocking)
                    try:
                        MissionService.update_missions_on_budget_entry(user_id, entry_data)
                    except Exception as mission_error:
                        # Log error but don't fail the budget entry creation
                        print(f"Error updating missions on budget entry: {mission_error}")
                    
                    return result_dict
                
                return None
        except Exception as e:
            print(f"Error creating budget entry: {e}")
            return None
    
    @staticmethod
    def get_entries(
        user_id: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get budget entries for a user with filters
        
        Args:
            user_id: User's UUID
            from_date: Start date filter
            to_date: End date filter
            category: Filter by category
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of budget entry dictionaries
        """
        conditions = ["user_id = %s"]
        values = [user_id]
        
        if from_date:
            conditions.append("date >= %s")
            values.append(from_date)
        
        if to_date:
            conditions.append("date <= %s")
            values.append(to_date)
        
        if category:
            conditions.append("category = %s")
            values.append(category)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, user_id, date, meal_name, cost, servings, cost_per_serving,
                   category, notes, journal_entry_id, created_at, updated_at
            FROM budget_entries
            WHERE {where_clause}
            ORDER BY date DESC
            LIMIT %s OFFSET %s
        """
        
        values.extend([limit, offset])
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, values)
                results = cursor.fetchall()
                return [dict(result) for result in results]
        except Exception as e:
            print(f"Error fetching budget entries: {e}")
            return []
    
    @staticmethod
    def get_entry_by_id(entry_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single budget entry by ID
        
        Args:
            entry_id: Entry UUID
            user_id: User's UUID (for authorization)
        
        Returns:
            Entry dictionary or None if not found
        """
        query = """
            SELECT id, user_id, date, meal_name, cost, servings, cost_per_serving,
                   category, notes, journal_entry_id, created_at, updated_at
            FROM budget_entries
            WHERE id = %s AND user_id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (entry_id, user_id))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching budget entry: {e}")
            return None
    
    @staticmethod
    def update_entry(entry_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a budget entry
        
        Args:
            entry_id: Entry UUID
            user_id: User's UUID (for authorization)
            update_data: Dictionary with fields to update
        
        Returns:
            Updated entry dictionary or None if not found
        """
        if not update_data:
            return BudgetRepository.get_entry_by_id(entry_id, user_id)
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        allowed_fields = ["date", "meal_name", "cost", "servings", "category", "notes"]
        
        for key, value in update_data.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = %s")
                values.append(value)
        
        if not set_clauses:
            return BudgetRepository.get_entry_by_id(entry_id, user_id)
        
        values.extend([entry_id, user_id])
        
        query = f"""
            UPDATE budget_entries
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, date, meal_name, cost, servings, cost_per_serving,
                      category, notes, journal_entry_id, created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error updating budget entry: {e}")
            return None
    
    @staticmethod
    def delete_entry(entry_id: str, user_id: str) -> bool:
        """
        Delete a budget entry
        
        Args:
            entry_id: Entry UUID
            user_id: User's UUID (for authorization)
        
        Returns:
            True if deleted, False otherwise
        """
        query = """
            DELETE FROM budget_entries
            WHERE id = %s AND user_id = %s
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (entry_id, user_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting budget entry: {e}")
            return False
    
    @staticmethod
    def get_stats(user_id: str, period: str = "week") -> Dict[str, Any]:
        """
        Get budget statistics for a user
        
        Args:
            user_id: User's UUID
            period: 'week', 'month', or 'year'
        
        Returns:
            Dictionary with budget statistics
        """
        # Calculate date range based on period
        today = date.today()
        if period == "week":
            from_date = today - timedelta(days=7)
        elif period == "month":
            from_date = today - timedelta(days=30)
        elif period == "year":
            from_date = today - timedelta(days=365)
        else:
            from_date = today - timedelta(days=7)
        
        query = """
            SELECT 
                COUNT(*) as meals_count,
                SUM(cost) as total_spent,
                AVG(cost_per_serving) as avg_cost_per_meal
            FROM budget_entries
            WHERE user_id = %s AND date >= %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, from_date))
                result = cursor.fetchone()
                
                if not result:
                    return _get_empty_stats()
                
                meals_count = result["meals_count"] or 0
                total_spent = float(result["total_spent"] or 0)
                avg_cost_per_meal = float(result["avg_cost_per_meal"] or 0)
                
                # Calculate savings vs restaurant (assuming $15 per meal average)
                restaurant_cost_per_meal = 15.0
                savings_vs_restaurant = (restaurant_cost_per_meal - avg_cost_per_meal) * float(meals_count)
                
                # Calculate budget score (0-100)
                # Lower cost per meal = higher score
                if avg_cost_per_meal <= 3:
                    score = 100
                elif avg_cost_per_meal <= 5:
                    score = 85
                elif avg_cost_per_meal <= 8:
                    score = 70
                elif avg_cost_per_meal <= 12:
                    score = 50
                else:
                    score = 30
                
                # Get budget settings
                settings = BudgetRepository.get_budget_settings(user_id)
                weekly_budget = float(settings.get("weekly_budget")) if settings and settings.get("weekly_budget") else None
                remaining_budget = None
                
                if weekly_budget and period == "week":
                    remaining_budget = weekly_budget - total_spent
                
                return {
                    "score": score,
                    "avg_cost_per_meal": round(avg_cost_per_meal, 2),
                    "savings_vs_restaurant": round(savings_vs_restaurant, 2),
                    "meals_this_week": meals_count,
                    "total_spent": round(total_spent, 2),
                    "weekly_budget": weekly_budget,
                    "remaining_budget": round(remaining_budget, 2) if remaining_budget is not None else None
                }
        except Exception as e:
            print(f"Error getting budget stats: {e}")
            return _get_empty_stats()
    
    @staticmethod
    def get_category_breakdown(user_id: str, period: str = "week") -> Dict[str, float]:
        """
        Get spending breakdown by category
        
        Args:
            user_id: User's UUID
            period: 'week', 'month', or 'year'
        
        Returns:
            Dictionary with category breakdown
        """
        # Calculate date range
        today = date.today()
        if period == "week":
            from_date = today - timedelta(days=7)
        elif period == "month":
            from_date = today - timedelta(days=30)
        elif period == "year":
            from_date = today - timedelta(days=365)
        else:
            from_date = today - timedelta(days=7)
        
        query = """
            SELECT category, SUM(cost) as total
            FROM budget_entries
            WHERE user_id = %s AND date >= %s AND category IS NOT NULL
            GROUP BY category
            ORDER BY total DESC
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, from_date))
                results = cursor.fetchall()
                
                breakdown = {}
                for result in results:
                    category = result["category"]
                    total = float(result["total"])
                    breakdown[category] = round(total, 2)
                
                return breakdown
        except Exception as e:
            print(f"Error getting category breakdown: {e}")
            return {}
    
    @staticmethod
    def get_budget_settings(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get budget settings for a user
        
        Args:
            user_id: User's UUID
        
        Returns:
            Settings dictionary or None if not found
        """
        query = """
            SELECT id, user_id, weekly_budget, monthly_budget, created_at, updated_at
            FROM budget_settings
            WHERE user_id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching budget settings: {e}")
            return None
    
    @staticmethod
    def upsert_budget_settings(user_id: str, settings_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create or update budget settings for a user
        
        Args:
            user_id: User's UUID
            settings_data: Dictionary with settings data
        
        Returns:
            Settings dictionary or None if failed
        """
        settings_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO budget_settings (id, user_id, weekly_budget, monthly_budget)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                weekly_budget = COALESCE(EXCLUDED.weekly_budget, budget_settings.weekly_budget),
                monthly_budget = COALESCE(EXCLUDED.monthly_budget, budget_settings.monthly_budget),
                updated_at = NOW()
            RETURNING id, user_id, weekly_budget, monthly_budget, created_at, updated_at
        """
        
        values = (
            settings_id,
            user_id,
            settings_data.get("weekly_budget"),
            settings_data.get("monthly_budget")
        )
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error upserting budget settings: {e}")
            return None


def _get_empty_stats() -> Dict[str, Any]:
    """Return empty stats structure"""
    return {
        "score": 0,
        "avg_cost_per_meal": 0.0,
        "savings_vs_restaurant": 0.0,
        "meals_this_week": 0,
        "total_spent": 0.0,
        "weekly_budget": None,
        "remaining_budget": None
    }
