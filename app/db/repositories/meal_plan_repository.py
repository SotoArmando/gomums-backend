"""
Meal Plan Repository
Database operations for meal plans, planned meals, and shopping lists
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.core.database import db


class MealPlanRepository:
    """Repository for meal plan operations"""
    
    db = db
    
    # ==================== Meal Plan CRUD ====================
    
    @staticmethod
    def create_meal_plan(user_id: str, meal_plan_data: dict) -> Optional[dict]:
        """
        Create a new meal plan
        
        Args:
            user_id: User ID
            meal_plan_data: Dict with name, start_date, end_date, status
            
        Returns:
            Created meal plan dict or None
        """
        try:
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                params = {'user_id': user_id, **meal_plan_data}
                cursor.execute("""
                    INSERT INTO meal_plans (user_id, name, start_date, end_date, status)
                    VALUES (%(user_id)s, %(name)s, %(start_date)s, %(end_date)s, COALESCE(%(status)s, 'draft'))
                    RETURNING id, user_id, name, start_date, end_date, total_cost, status,
                              created_at, updated_at
                """, params)
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    result['total_meals'] = 0
                    result['total_shopping_items'] = 0
                    result['shopping_items_purchased'] = 0
                    return result
                return None
        except Exception as e:
            print(f"Error creating meal plan: {e}")
            return None
    
    @staticmethod
    def get_meal_plan(meal_plan_id: str, user_id: str) -> Optional[dict]:
        """Get meal plan by ID (with counts)"""
        try:
            with MealPlanRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        mp.id, mp.user_id, mp.name, mp.start_date, mp.end_date,
                        mp.total_cost, mp.status, mp.created_at, mp.updated_at,
                        COUNT(DISTINCT pm.id) as total_meals,
                        COUNT(DISTINCT sli.id) as total_shopping_items,
                        COUNT(DISTINCT sli.id) FILTER (WHERE sli.purchased = true) as shopping_items_purchased
                    FROM meal_plans mp
                    LEFT JOIN planned_meals pm ON pm.meal_plan_id = mp.id
                    LEFT JOIN shopping_list_items sli ON sli.meal_plan_id = mp.id
                    WHERE mp.id = %s AND mp.user_id = %s
                    GROUP BY mp.id
                """, (meal_plan_id, user_id))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error fetching meal plan: {e}")
            return None
    
    @staticmethod
    def get_meal_plan_with_details(meal_plan_id: str, user_id: str) -> Optional[dict]:
        """Get meal plan with planned meals and shopping list"""
        try:
            meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            if not meal_plan:
                return None
            
            # Get planned meals
            planned_meals = MealPlanRepository.get_planned_meals(meal_plan_id, user_id)
            meal_plan['planned_meals'] = planned_meals
            
            # Get shopping list items
            shopping_items = MealPlanRepository.get_shopping_list_items(meal_plan_id, user_id)
            meal_plan['shopping_list_items'] = shopping_items
            
            return meal_plan
        except Exception as e:
            print(f"Error fetching meal plan with details: {e}")
            return None
    
    @staticmethod
    def get_user_meal_plans(user_id: str, status: Optional[str] = None,
                           limit: int = 20, offset: int = 0) -> List[dict]:
        """
        Get all meal plans for a user
        
        Args:
            user_id: User ID
            status: Optional filter by status (draft, active, completed)
            limit: Max results
            offset: Pagination offset
            
        Returns:
            List of meal plan dicts with counts
        """
        try:
            with MealPlanRepository.db.get_cursor() as cursor:
                status_filter = "AND mp.status = %(status)s" if status else ""
                
                query = f"""
                    SELECT 
                        mp.id, mp.user_id, mp.name, mp.start_date, mp.end_date,
                        mp.total_cost, mp.status, mp.created_at, mp.updated_at,
                        COUNT(DISTINCT pm.id) as total_meals,
                        COUNT(DISTINCT sli.id) as total_shopping_items,
                        COUNT(DISTINCT sli.id) FILTER (WHERE sli.purchased = true) as shopping_items_purchased
                    FROM meal_plans mp
                    LEFT JOIN planned_meals pm ON pm.meal_plan_id = mp.id
                    LEFT JOIN shopping_list_items sli ON sli.meal_plan_id = mp.id
                    WHERE mp.user_id = %(user_id)s {status_filter}
                    GROUP BY mp.id
                    ORDER BY mp.start_date DESC, mp.created_at DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                """
                
                cursor.execute(query, {
                    'user_id': user_id,
                    'status': status,
                    'limit': limit,
                    'offset': offset
                })
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching user meal plans: {e}")
            return []
    
    @staticmethod
    def update_meal_plan(meal_plan_id: str, user_id: str, updates: dict) -> Optional[dict]:
        """Update meal plan"""
        try:
            # Build SET clause dynamically
            allowed_fields = ['name', 'start_date', 'end_date', 'total_cost', 'status']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    values[field] = updates[field]
            
            if not set_parts:
                return MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['meal_plan_id'] = meal_plan_id
            values['user_id'] = user_id
            
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE meal_plans
                    SET {set_clause}
                    WHERE id = %(meal_plan_id)s AND user_id = %(user_id)s
                    RETURNING id, user_id, name, start_date, end_date, total_cost, status,
                              created_at, updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error updating meal plan: {e}")
            return None
    
    @staticmethod
    def delete_meal_plan(meal_plan_id: str, user_id: str) -> bool:
        """Delete meal plan (cascades to planned meals and shopping items)"""
        try:
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM meal_plans
                    WHERE id = %s AND user_id = %s
                """, (meal_plan_id, user_id))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting meal plan: {e}")
            return False
    
    # ==================== Planned Meal CRUD ====================
    
    @staticmethod
    def create_planned_meal(meal_plan_id: str, user_id: str, meal_data: dict) -> Optional[dict]:
        """Create a new planned meal"""
        try:
            # Verify meal plan belongs to user
            meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            if not meal_plan:
                return None
            
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                params = {'meal_plan_id': meal_plan_id, **meal_data}
                cursor.execute("""
                    INSERT INTO planned_meals 
                        (meal_plan_id, date, meal_type, recipe_id, recipe_name, servings, is_batch, is_leftovers)
                    VALUES 
                        (%(meal_plan_id)s, %(date)s, %(meal_type)s, %(recipe_id)s, %(recipe_name)s, 
                         COALESCE(%(servings)s, 1), COALESCE(%(is_batch)s, false), COALESCE(%(is_leftovers)s, false))
                    RETURNING id, meal_plan_id, date, meal_type, recipe_id, recipe_name,
                              servings, is_batch, is_leftovers, created_at, updated_at
                """, params)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error creating planned meal: {e}")
            return None
    
    @staticmethod
    def get_planned_meals(meal_plan_id: str, user_id: str,
                          date_filter: Optional[date] = None) -> List[dict]:
        """Get planned meals for a meal plan"""
        try:
            # Verify ownership
            meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            if not meal_plan:
                return []
            
            with MealPlanRepository.db.get_cursor() as cursor:
                date_filter_sql = "AND pm.date = %(date)s" if date_filter else ""
                
                query = f"""
                    SELECT id, meal_plan_id, date, meal_type, recipe_id, recipe_name,
                           servings, is_batch, is_leftovers, created_at, updated_at
                    FROM planned_meals pm
                    WHERE meal_plan_id = %(meal_plan_id)s {date_filter_sql}
                    ORDER BY date ASC, 
                             CASE meal_type
                                 WHEN 'breakfast' THEN 1
                                 WHEN 'lunch' THEN 2
                                 WHEN 'dinner' THEN 3
                                 WHEN 'snack' THEN 4
                             END
                """
                
                cursor.execute(query, {'meal_plan_id': meal_plan_id, 'date': date_filter})
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching planned meals: {e}")
            return []
    
    @staticmethod
    def update_planned_meal(planned_meal_id: str, user_id: str, updates: dict) -> Optional[dict]:
        """Update planned meal"""
        try:
            # Build SET clause
            allowed_fields = ['date', 'meal_type', 'recipe_id', 'recipe_name', 'servings', 'is_batch', 'is_leftovers']
            set_parts = []
            values = {}
            
            for field in allowed_fields:
                if field in updates and updates[field] is not None:
                    set_parts.append(f"{field} = %({field})s")
                    values[field] = updates[field]
            
            if not set_parts:
                # Return current  
                with MealPlanRepository.db.get_cursor() as cursor:
                    cursor.execute("""
                        SELECT pm.* FROM planned_meals pm
                        JOIN meal_plans mp ON mp.id = pm.meal_plan_id
                        WHERE pm.id = %s AND mp.user_id = %s
                    """, (planned_meal_id, user_id))
                    row = cursor.fetchone()
                    return dict(row) if row else None
            
            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)
            values['planned_meal_id'] = planned_meal_id
            values['user_id'] = user_id
            
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE planned_meals pm
                    SET {set_clause}
                    FROM meal_plans mp
                    WHERE pm.id = %(planned_meal_id)s 
                      AND pm.meal_plan_id = mp.id 
                      AND mp.user_id = %(user_id)s
                    RETURNING pm.id, pm.meal_plan_id, pm.date, pm.meal_type, pm.recipe_id,
                              pm.recipe_name, pm.servings, pm.is_batch, pm.is_leftovers,
                              pm.created_at, pm.updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error updating planned meal: {e}")
            return None
    
    @staticmethod
    def delete_planned_meal(planned_meal_id: str, user_id: str) -> bool:
        """Delete planned meal"""
        try:
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM planned_meals pm
                    USING meal_plans mp
                    WHERE pm.id = %s 
                      AND pm.meal_plan_id = mp.id 
                      AND mp.user_id = %s
                """, (planned_meal_id, user_id))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting planned meal: {e}")
            return False
    
    # ==================== Shopping List CRUD ====================
    
    @staticmethod
    def create_shopping_list_item(meal_plan_id: str, user_id: str, item_data: dict) -> Optional[dict]:
        """Create a shopping list item"""
        try:
            # Verify ownership
            meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            if not meal_plan:
                return None
            
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                params = {'meal_plan_id': meal_plan_id, **item_data}
                cursor.execute("""
                    INSERT INTO shopping_list_items 
                        (meal_plan_id, name, quantity, category, estimated_cost, related_recipes)
                    VALUES 
                        (%(meal_plan_id)s, %(name)s, %(quantity)s, %(category)s, %(estimated_cost)s, 
                         COALESCE(%(related_recipes)s, ARRAY[]::UUID[]))
                    RETURNING id, meal_plan_id, name, quantity, category, purchased,
                              estimated_cost, related_recipes, created_at, updated_at
                """, params)
                
                row = cursor.fetchone()
                if row:
                    item = dict(row)
                    # Convert related_recipes from PostgreSQL array to list
                    if item.get('related_recipes'):
                        if isinstance(item['related_recipes'], str):
                            if item['related_recipes'] in ('{}', ''):
                                item['related_recipes'] = []
                            else:
                                item['related_recipes'] = item['related_recipes'].strip('{}').split(',') if item['related_recipes'] != '{}' else []
                        elif not isinstance(item['related_recipes'], list):
                            item['related_recipes'] = []
                    else:
                        item['related_recipes'] = []
                    return item
                return None
        except Exception as e:
            print(f"Error creating shopping list item: {e}")
            return None
    
    @staticmethod
    def get_shopping_list_items(meal_plan_id: str, user_id: str,
                                purchased_filter: Optional[bool] = None) -> List[dict]:
        """Get shopping list items for a meal plan"""
        try:
            # Verify ownership
            meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            if not meal_plan:
                return []
            
            with MealPlanRepository.db.get_cursor() as cursor:
                purchased_sql = ""
                if purchased_filter is not None:
                    purchased_sql = "AND sli.purchased = %(purchased)s"
                
                query = f"""
                    SELECT id, meal_plan_id, name, quantity, category, purchased,
                           estimated_cost, related_recipes, created_at, updated_at
                    FROM shopping_list_items sli
                    WHERE meal_plan_id = %(meal_plan_id)s {purchased_sql}
                    ORDER BY purchased ASC, category ASC, name ASC
                """
                
                cursor.execute(query, {'meal_plan_id': meal_plan_id, 'purchased': purchased_filter})
                
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    item = dict(row)
                    # Convert related_recipes from PostgreSQL array or empty string to list
                    if item.get('related_recipes'):
                        if isinstance(item['related_recipes'], str):
                            # Handle '{...}' string format from PostgreSQL
                            if item['related_recipes'] in ('{}', ''):
                                item['related_recipes'] = []
                            else:
                                # Parse array string format
                                item['related_recipes'] = item['related_recipes'].strip('{}').split(',') if item['related_recipes'] != '{}' else []
                        elif not isinstance(item['related_recipes'], list):
                            item['related_recipes'] = []
                    else:
                        item['related_recipes'] = []
                    results.append(item)
                return results
        except Exception as e:
            print(f"Error fetching shopping list items: {e}")
            return []
    
    @staticmethod
    def update_shopping_list_item(item_id: str, user_id: str, updates: dict) -> Optional[dict]:
        """Update shopping list item"""
        try:
            allowed_fields = ['name', 'quantity', 'category', 'purchased', 'estimated_cost', 'related_recipes']
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
            values['item_id'] = item_id
            values['user_id'] = user_id
            
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                query = f"""
                    UPDATE shopping_list_items sli
                    SET {set_clause}
                    FROM meal_plans mp
                    WHERE sli.id = %(item_id)s 
                      AND sli.meal_plan_id = mp.id 
                      AND mp.user_id = %(user_id)s
                    RETURNING sli.id, sli.meal_plan_id, sli.name, sli.quantity, sli.category,
                              sli.purchased, sli.estimated_cost, sli.related_recipes,
                              sli.created_at, sli.updated_at
                """
                
                cursor.execute(query, values)
                
                row = cursor.fetchone()
                if row:
                    item = dict(row)
                    # Convert related_recipes from PostgreSQL array to list
                    if item.get('related_recipes'):
                        if isinstance(item['related_recipes'], str):
                            if item['related_recipes'] in ('{}', ''):
                                item['related_recipes'] = []
                            else:
                                item['related_recipes'] = item['related_recipes'].strip('{}').split(',') if item['related_recipes'] != '{}' else []
                        elif not isinstance(item['related_recipes'], list):
                            item['related_recipes'] = []
                    else:
                        item['related_recipes'] = []
                    return item
                return None
        except Exception as e:
            print(f"Error updating shopping list item: {e}")
            return None
    
    @staticmethod
    def bulk_update_shopping_items(item_ids: List[str], user_id: str, purchased: bool) -> int:
        """Bulk update shopping items (mark as purchased/not purchased)"""
        try:
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE shopping_list_items sli
                    SET purchased = %s, updated_at = NOW()
                    FROM meal_plans mp
                    WHERE sli.id = ANY(%s::uuid[])
                      AND sli.meal_plan_id = mp.id
                      AND mp.user_id = %s
                """, (purchased, item_ids, user_id))
                
                return cursor.rowcount
        except Exception as e:
            print(f"Error bulk updating shopping items: {e}")
            return 0
    
    @staticmethod
    def delete_shopping_list_item(item_id: str, user_id: str) -> bool:
        """Delete shopping list item"""
        try:
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    DELETE FROM shopping_list_items sli
                    USING meal_plans mp
                    WHERE sli.id = %s 
                      AND sli.meal_plan_id = mp.id 
                      AND mp.user_id = %s
                """, (item_id, user_id))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting shopping list item: {e}")
            return False
    
    # ==================== Week-Based Methods ====================
    
    @staticmethod
    def get_week_range(target_date: date) -> tuple[date, date]:
        """
        Get the start (Monday) and end (Sunday) of the week containing target_date
        
        Args:
            target_date: Any date within the week
            
        Returns:
            Tuple of (start_date, end_date) for the week
        """
        # Get the Monday of the week (weekday 0=Monday, 6=Sunday)
        days_since_monday = target_date.weekday()
        start_date = target_date - timedelta(days=days_since_monday)
        end_date = start_date + timedelta(days=6)
        return (start_date, end_date)
    
    @staticmethod
    def get_current_week_meal_plan(user_id: str) -> Optional[dict]:
        """
        Get or create meal plan for the current week
        
        Returns meal plan with planned_meals and shopping_list_items
        """
        return MealPlanRepository.get_meal_plan_for_week(user_id, date.today())
    
    @staticmethod
    def get_meal_plan_for_week(user_id: str, target_date: date) -> Optional[dict]:
        """
        Get or create meal plan for the week containing target_date
        
        Args:
            user_id: User ID
            target_date: Any date within the target week
            
        Returns:
            Meal plan dict with planned_meals and shopping_list_items, or None on error
        """
        try:
            # Calculate week range
            start_date, end_date = MealPlanRepository.get_week_range(target_date)
            
            # Try to find existing meal plan for this week
            with MealPlanRepository.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        mp.id, mp.user_id, mp.name, mp.start_date, mp.end_date,
                        mp.total_cost, mp.status, mp.created_at, mp.updated_at,
                        COUNT(DISTINCT pm.id) as total_meals,
                        COUNT(DISTINCT sli.id) as total_shopping_items,
                        COUNT(DISTINCT sli.id) FILTER (WHERE sli.purchased = true) as shopping_items_purchased
                    FROM meal_plans mp
                    LEFT JOIN planned_meals pm ON pm.meal_plan_id = mp.id
                    LEFT JOIN shopping_list_items sli ON sli.meal_plan_id = mp.id
                    WHERE mp.user_id = %s
                      AND mp.start_date = %s
                      AND mp.end_date = %s
                    GROUP BY mp.id
                    LIMIT 1
                """, (user_id, start_date, end_date))
                
                row = cursor.fetchone()
                
                if row:
                    # Found existing plan
                    meal_plan = dict(row)
                else:
                    # Create new plan for this week
                    month_name = start_date.strftime('%b')
                    day = start_date.day
                    plan_name = f"Week of {month_name} {day}"
                    
                    meal_plan_data = {
                        'name': plan_name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': 'draft'
                    }
                    
                    meal_plan = MealPlanRepository.create_meal_plan(user_id, meal_plan_data)
                    
                    if not meal_plan:
                        return None
            
            # Get planned meals
            planned_meals = MealPlanRepository.get_planned_meals(meal_plan['id'], user_id)
            meal_plan['planned_meals'] = planned_meals
            
            # Get shopping list items
            shopping_items = MealPlanRepository.get_shopping_list_items(meal_plan['id'], user_id)
            meal_plan['shopping_list_items'] = shopping_items
            
            return meal_plan
            
        except Exception as e:
            print(f"Error getting/creating meal plan for week: {e}")
            return None
    
    # ==================== Helper Methods ====================
    
    @staticmethod
    def get_calendar_view(meal_plan_id: str, user_id: str) -> Optional[dict]:
        """Get calendar view of meal plan (organized by day)"""
        try:
            meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, user_id)
            if not meal_plan:
                return None
            
            planned_meals = MealPlanRepository.get_planned_meals(meal_plan_id, user_id)
            
            # Organize meals by date
            days_dict = {}
            current_date = meal_plan['start_date']
            end_date = meal_plan['end_date']
            
            # Initialize all days
            while current_date <= end_date:
                days_dict[current_date] = {
                    'date': current_date,
                    'breakfast': None,
                    'lunch': None,
                    'dinner': None,
                    'snacks': []
                }
                current_date += timedelta(days=1)
            
            # Populate meals
            for meal in planned_meals:
                meal_date = meal['date']
                if meal_date in days_dict:
                    meal_type = meal['meal_type']
                    if meal_type == 'snack':
                        days_dict[meal_date]['snacks'].append(meal)
                    else:
                        days_dict[meal_date][meal_type] = meal
            
            # Convert to list
            days_list = list(days_dict.values())
            
            return {
                'meal_plan_id': meal_plan['id'],
                'meal_plan_name': meal_plan['name'],
                'start_date': meal_plan['start_date'],
                'end_date': meal_plan['end_date'],
                'days': days_list
            }
        except Exception as e:
            print(f"Error getting calendar view: {e}")
            return None
    
    @staticmethod
    def calculate_total_cost(meal_plan_id: str, user_id: str) -> Optional[Decimal]:
        """Calculate total cost from shopping list"""
        try:
            with MealPlanRepository.db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    WITH total AS (
                        SELECT COALESCE(SUM(estimated_cost), 0) as cost
                        FROM shopping_list_items sli
                        JOIN meal_plans mp ON mp.id = sli.meal_plan_id
                        WHERE sli.meal_plan_id = %s AND mp.user_id = %s
                    )
                    UPDATE meal_plans
                    SET total_cost = (SELECT cost FROM total),
                        updated_at = NOW()
                    WHERE id = %s AND user_id = %s
                    RETURNING total_cost
                """, (meal_plan_id, user_id, meal_plan_id, user_id))
                
                row = cursor.fetchone()
                if row:
                    return row['total_cost']
                return None
        except Exception as e:
            print(f"Error calculating total cost: {e}")
            return None
