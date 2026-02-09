from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json

from app.core.database import db
from app.services.mission_service import MissionService
from app.services.challenge_service import ChallengeService


class JournalRepository:
    """Repository for journal entry database operations"""
    
    @staticmethod
    def create_entry(user_id: str, entry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new journal entry (meal or purchase)
        
        Args:
            user_id: User's UUID
            entry_data: Dictionary containing entry data
        
        Returns:
            Dictionary with created entry data or None if failed
        """
        entry_id = str(uuid.uuid4())
        entry_type = entry_data.get("type")
        timestamp = entry_data.get("timestamp", datetime.now())
        
        # Build query based on type
        if entry_type == "meal":
            query = """
                INSERT INTO journal_entries (
                    id, user_id, type, timestamp, title,
                    meal_type, portions, portions_left, status, ingredients_used, ingredient_swaps,
                    is_batch, used_leftovers, has_leftovers, needs_restock, purchase_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, type, timestamp, title,
                          meal_type, portions, portions_left, status, ingredients_used, ingredient_swaps,
                          is_batch, used_leftovers, has_leftovers, needs_restock, purchase_id,
                          created_at, updated_at
            """
            
            values = (
                entry_id, user_id, entry_type, timestamp, entry_data["title"],
                entry_data.get("meal_type"), entry_data.get("portions"),
                entry_data.get("portions_left"), entry_data.get("status", "fresh"),
                entry_data.get("ingredients_used"),
                json.dumps(entry_data.get("ingredient_swaps")) if entry_data.get("ingredient_swaps") else None,
                entry_data.get("is_batch", False), entry_data.get("used_leftovers", False),
                entry_data.get("has_leftovers", False), entry_data.get("needs_restock", False),
                entry_data.get("purchase_id")
            )
        
        elif entry_type == "purchase":
            # Calculate total cost from items
            items = entry_data.get("items", [])
            total_cost = sum(item.get("cost", 0) for item in items)
            
            query = """
                INSERT INTO journal_entries (
                    id, user_id, type, timestamp, title, store, items
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, type, timestamp, title, store, items,
                          created_at, updated_at
            """
            
            values = (
                entry_id, user_id, entry_type, timestamp, entry_data["title"],
                entry_data["store"], json.dumps(items)
            )
        else:
            return None
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    # Prepare result dictionary
                    result_dict = dict(result)
                    
                    if entry_type == "purchase":
                        # Add total_cost to purchase response
                        items = result_dict.get("items", [])
                        if isinstance(items, str):
                            items = json.loads(items)
                        result_dict["items"] = items
                        result_dict["total_cost"] = sum(item.get("cost", 0) for item in items)
                    
                    # Trigger mission updates (non-blocking)
                    try:
                        MissionService.update_missions_on_journal_entry(user_id, entry_data)
                    except Exception as mission_error:
                        # Log error but don't fail the journal entry creation
                        print(f"Error updating missions on journal entry: {mission_error}")
                    
                    # Trigger challenge updates (non-blocking)
                    try:
                        ChallengeService.update_challenges_on_journal_entry(
                            user_id=uuid.UUID(user_id),
                            entry_type=entry_type,
                            meal_type=entry_data.get("meal_type"),
                            portions=entry_data.get("portions"),
                            status=entry_data.get("status"),
                            used_leftovers=entry_data.get("used_leftovers", False),
                            is_batch=entry_data.get("is_batch", False),
                            recipe_name=entry_data.get("title"),
                            ingredient_swaps=entry_data.get("ingredient_swaps"),
                            timestamp=entry_data.get("timestamp")
                        )
                    except Exception as challenge_error:
                        # Log error but don't fail the journal entry creation
                        print(f"Error updating challenges on journal entry: {challenge_error}")
                    
                    return result_dict
                
                return None
        except Exception as e:
            print(f"Error creating journal entry: {e}")
            return None
    
    @staticmethod
    def get_entries(
        user_id: str,
        entry_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get journal entries for a user with filters
        
        Args:
            user_id: User's UUID
            entry_type: Filter by 'meal' or 'purchase'
            from_date: Start date filter
            to_date: End date filter
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of journal entry dictionaries
        """
        conditions = ["user_id = %s"]
        values = [user_id]
        
        if entry_type:
            conditions.append("type = %s")
            values.append(entry_type)
        
        if from_date:
            conditions.append("timestamp >= %s")
            values.append(from_date)
        
        if to_date:
            conditions.append("timestamp <= %s")
            values.append(to_date)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, user_id, type, timestamp, title,
                   meal_type, portions, portions_left, status, ingredients_used, ingredient_swaps,
                   is_batch, used_leftovers, has_leftovers, needs_restock, purchase_id,
                   store, items,
                   created_at, updated_at
            FROM journal_entries
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """
        
        values.extend([limit, offset])
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, values)
                results = cursor.fetchall()
                
                entries = []
                for result in results:
                    entry = dict(result)
                    
                    # Parse items JSON for purchases and calculate total_cost
                    if entry.get("type") == "purchase" and entry.get("items"):
                        if isinstance(entry["items"], str):
                            entry["items"] = json.loads(entry["items"])
                        entry["total_cost"] = sum(item.get("cost", 0) for item in entry["items"])
                    
                    entries.append(entry)
                
                return entries
        except Exception as e:
            print(f"Error fetching journal entries: {e}")
            return []
    
    @staticmethod
    def get_entry_by_id(entry_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single journal entry by ID
        
        Args:
            entry_id: Entry UUID
            user_id: User's UUID (for authorization)
        
        Returns:
            Entry dictionary or None if not found
        """
        query = """
            SELECT id, user_id, type, timestamp, title,
                   meal_type, portions, portions_left, status, ingredients_used, ingredient_swaps,
                   is_batch, used_leftovers, has_leftovers, needs_restock, purchase_id,
                   store, items,
                   created_at, updated_at
            FROM journal_entries
            WHERE id = %s AND user_id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (entry_id, user_id))
                result = cursor.fetchone()
                
                if result:
                    entry = dict(result)
                    
                    # Parse items JSON for purchases
                    if entry.get("type") == "purchase" and entry.get("items"):
                        if isinstance(entry["items"], str):
                            entry["items"] = json.loads(entry["items"])
                        entry["total_cost"] = sum(item.get("cost", 0) for item in entry["items"])
                    
                    return entry
                return None
        except Exception as e:
            print(f"Error fetching journal entry: {e}")
            return None
    
    @staticmethod
    def update_entry(entry_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a journal entry
        
        Args:
            entry_id: Entry UUID
            user_id: User's UUID (for authorization)
            update_data: Dictionary with fields to update
        
        Returns:
            Updated entry dictionary or None if not found
        """
        if not update_data:
            return JournalRepository.get_entry_by_id(entry_id, user_id)
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        allowed_fields = [
            "title", "portions_left", "status", "needs_restock",
            "store", "items"
        ]
        
        for key, value in update_data.items():
            if key in allowed_fields:
                if key == "items":
                    set_clauses.append(f"{key} = %s")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
        
        if not set_clauses:
            return JournalRepository.get_entry_by_id(entry_id, user_id)
        
        values.extend([entry_id, user_id])
        
        query = f"""
            UPDATE journal_entries
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, type, timestamp, title,
                      meal_type, portions, portions_left, status, ingredients_used,
                      is_batch, used_leftovers, needs_restock, purchase_id,
                      store, items,
                      created_at, updated_at
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    entry = dict(result)
                    
                    if entry.get("type") == "purchase" and entry.get("items"):
                        if isinstance(entry["items"], str):
                            entry["items"] = json.loads(entry["items"])
                        entry["total_cost"] = sum(item.get("cost", 0) for item in entry["items"])
                    
                    return entry
                return None
        except Exception as e:
            print(f"Error updating journal entry: {e}")
            return None
    
    @staticmethod
    def delete_entry(entry_id: str, user_id: str) -> bool:
        """
        Delete a journal entry
        
        Args:
            entry_id: Entry UUID
            user_id: User's UUID (for authorization)
        
        Returns:
            True if deleted, False otherwise
        """
        query = """
            DELETE FROM journal_entries
            WHERE id = %s AND user_id = %s
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (entry_id, user_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting journal entry: {e}")
            return False
    
    @staticmethod
    def link_meal_to_purchase(
        meal_id: str,
        purchase_id: str,
        user_id: str,
        ingredients_matched: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Link a meal to a purchase with matched ingredients
        
        Args:
            meal_id: Meal entry UUID
            purchase_id: Purchase entry UUID
            user_id: User's UUID (for authorization)
            ingredients_matched: List of ingredients that match
        
        Returns:
            Updated meal entry or None if failed
        """
        link_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO meal_purchase_links (id, meal_id, purchase_id, ingredients_matched)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (meal_id, purchase_id) 
            DO UPDATE SET ingredients_matched = EXCLUDED.ingredients_matched
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (link_id, meal_id, purchase_id, ingredients_matched))
                
                # Also update the meal's purchase_id field
                update_query = """
                    UPDATE journal_entries
                    SET purchase_id = %s, updated_at = NOW()
                    WHERE id = %s AND user_id = %s AND type = 'meal'
                """
                cursor.execute(update_query, (purchase_id, meal_id, user_id))
            
            return JournalRepository.get_entry_by_id(meal_id, user_id)
        except Exception as e:
            print(f"Error linking meal to purchase: {e}")
            return None
    
    @staticmethod
    def get_active_leftovers(user_id: str) -> List[str]:
        """
        Get user's active leftover meals (meals with portions_left > 0)
        
        Args:
            user_id: User's UUID
        
        Returns:
            List of leftover meal titles
        """
        query = """
            SELECT title, portions_left
            FROM journal_entries
            WHERE user_id = %s 
            AND type = 'meal'
            AND portions_left > 0
            ORDER BY timestamp DESC
            LIMIT 20
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                
                leftovers = []
                for row in results:
                    title = row['title']
                    portions = row['portions_left']
                    leftovers.append(f"{title} ({portions} portion{'s' if portions != 1 else ''})")
                
                return leftovers
        except Exception as e:
            print(f"Error fetching active leftovers: {e}")
            return []
    
    @staticmethod
    def get_recent_purchased_ingredients(user_id: str, days: int = 7) -> List[str]:
        """
        Get ingredients from user's recent purchases (last N days)
        
        Args:
            user_id: User's UUID
            days: Number of days to look back (default: 7)
        
        Returns:
            List of ingredient names from recent purchases
        """
        query = """
            SELECT items
            FROM journal_entries
            WHERE user_id = %s 
            AND type = 'purchase'
            AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, days))
                results = cursor.fetchall()
                
                ingredients = []
                seen = set()  # To avoid duplicates
                
                for row in results:
                    items = row['items']
                    if isinstance(items, str):
                        items = json.loads(items)
                    
                    for item in items:
                        ingredient_name = item.get('name', '').strip().lower()
                        if ingredient_name and ingredient_name not in seen:
                            ingredients.append(item.get('name'))  # Keep original case
                            seen.add(ingredient_name)
                
                return ingredients
        except Exception as e:
            print(f"Error fetching recent purchased ingredients: {e}")
            return []
