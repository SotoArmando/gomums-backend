from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
import re

from app.core.database import db
from app.services.mission_service import MissionService
from app.services.challenge_service import ChallengeService


def normalize_ingredient_name(name: str) -> str:
    """
    Extract core ingredient name by stripping quantities and units.
    
    Examples:
        "2 lb Chicken breast" → "chicken breast"
        "1/2 cup flour" → "flour"
        "3 medium onions" → "onions"
        "Chicken breast (2 lb)" → "chicken breast"
    """
    if not name:
        return ""
    
    text = name.lower().strip()
    
    # Remove parenthetical content: "(2 lb)" → ""
    text = re.sub(r'\([^)]*\)', '', text)
    
    # Remove leading numbers with fractions: "1/2", "2.5", "3"
    text = re.sub(r'^[\d\s./]+', '', text)
    
    # Common quantity words to remove
    quantity_words = [
        'lb', 'lbs', 'pound', 'pounds',
        'oz', 'ounce', 'ounces',
        'cup', 'cups', 'tbsp', 'tsp', 'tablespoon', 'teaspoon',
        'gallon', 'quart', 'pint', 'liter', 'ml',
        'kg', 'g', 'gram', 'grams',
        'bunch', 'bunches', 'head', 'heads', 'clove', 'cloves',
        'slice', 'slices', 'piece', 'pieces',
        'can', 'cans', 'jar', 'jars', 'bottle', 'bottles', 'bag', 'bags', 'box', 'boxes',
        'small', 'medium', 'large', 'extra-large',
        'fresh', 'frozen', 'dried', 'canned', 'chopped', 'diced', 'minced', 'sliced'
    ]
    
    # Remove quantity words
    words = text.split()
    filtered = [w for w in words if w not in quantity_words]
    text = ' '.join(filtered)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def get_ingredient_keywords(name: str) -> List[str]:
    """
    Get searchable keywords from an ingredient name.
    Returns both the full normalized name and individual significant words.
    
    Example: "boneless skinless chicken breast" → ["chicken", "breast", "chicken breast"]
    """
    normalized = normalize_ingredient_name(name)
    if not normalized:
        return []
    
    words = normalized.split()
    keywords = []
    
    # Add individual words (if they're significant - more than 2 chars)
    for word in words:
        if len(word) > 2:
            keywords.append(word)
    
    # Add the full normalized name
    if len(words) > 1:
        keywords.append(normalized)
    
    return keywords


def extract_ingredient_names_from_list(ingredients: Optional[List[Any]]) -> List[str]:
    """
    Extract ingredient names from either format:
    - ["Chicken", "Rice"] -> ["Chicken", "Rice"]
    - [{"name": "Chicken"}, {"name": "Rice"}] -> ["Chicken", "Rice"]
    - Mixed formats also supported
    """
    if not ingredients:
        return []
    
    names = []
    for ing in ingredients:
        if isinstance(ing, str):
            names.append(ing)
        elif isinstance(ing, dict):
            name = ing.get('name', '')
            if name:
                names.append(name)
    return names


def serialize_ingredients_for_db(ingredients: Optional[List[Any]]) -> Optional[List[str]]:
    """
    Serialize ingredients for database storage in TEXT[] column.
    Converts structured objects to JSON strings, keeps simple strings as-is.
    
    Returns a list that psycopg2 can convert to PostgreSQL TEXT[].
    """
    if not ingredients:
        return None
    
    result = []
    for ing in ingredients:
        if isinstance(ing, str):
            result.append(ing)
        elif isinstance(ing, dict):
            # Store structured ingredient as JSON string
            result.append(json.dumps(ing))
        else:
            # Pydantic model or other - convert to dict then JSON
            result.append(json.dumps(ing.model_dump() if hasattr(ing, 'model_dump') else str(ing)))
    
    return result if result else None


def deserialize_ingredients_from_db(ingredients: Optional[List[str]]) -> Optional[List[Any]]:
    """
    Deserialize ingredients from database TEXT[] column.
    Parses JSON strings back to dicts, keeps simple strings as-is.
    """
    if not ingredients:
        return None
    
    result = []
    for ing in ingredients:
        if not ing:
            continue
        # Try to parse as JSON (structured ingredient)
        if ing.startswith('{'):
            try:
                result.append(json.loads(ing))
            except json.JSONDecodeError:
                result.append(ing)  # Keep as string if parse fails
        else:
            result.append(ing)
    
    return result if result else None


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
                serialize_ingredients_for_db(entry_data.get("ingredients_used")),
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
        
        result_dict = None
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    # Prepare result dictionary
                    result_dict = dict(result)
                    
                    if entry_type == "meal":
                        # Parse ingredients_used from TEXT[] (may contain JSON strings)
                        if result_dict.get("ingredients_used"):
                            result_dict["ingredients_used"] = deserialize_ingredients_from_db(
                                result_dict["ingredients_used"]
                            )
                    
                    if entry_type == "purchase":
                        # Add total_cost to purchase response
                        items = result_dict.get("items", [])
                        if isinstance(items, str):
                            items = json.loads(items)
                        result_dict["items"] = items
                        result_dict["total_cost"] = sum(item.get("cost", 0) for item in items)
            
            # After commit: trigger side effects
            if result_dict:
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
                
                # Auto-link meals to recent purchases with matching ingredients
                if entry_type == "meal" and entry_data.get("ingredients_used") and not entry_data.get("purchase_id"):
                    try:
                        # Extract ingredient names from either format (strings or objects)
                        ingredient_names = extract_ingredient_names_from_list(entry_data.get("ingredients_used"))
                        if ingredient_names:
                            linked_result = JournalRepository.auto_link_meal_to_purchase(
                                meal_id=str(result_dict["id"]),
                                user_id=user_id,
                                ingredients_used=ingredient_names
                            )
                        if linked_result:
                            # Update result_dict with linked purchase_id
                            result_dict["purchase_id"] = linked_result.get("purchase_id")
                    except Exception as link_error:
                        # Log error but don't fail the journal entry creation
                        print(f"Error auto-linking meal to purchase: {link_error}")
                
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
                    
                    # Parse ingredients_used from TEXT[] for meals
                    if entry.get("type") == "meal" and entry.get("ingredients_used"):
                        entry["ingredients_used"] = deserialize_ingredients_from_db(
                            entry["ingredients_used"]
                        )
                    
                    # Parse items JSON for purchases and calculate total_cost
                    if entry.get("type") == "purchase" and entry.get("items"):
                        if isinstance(entry["items"], str):
                            entry["items"] = json.loads(entry["items"])
                        entry["total_cost"] = sum(item.get("cost", 0) for item in entry["items"])
                    
                    # For meals with purchase_id, add linked purchase info
                    if entry.get("type") == "meal" and entry.get("purchase_id"):
                        link_info = JournalRepository.get_meal_purchase_link(
                            str(entry["id"]), str(entry["purchase_id"])
                        )
                        if link_info:
                            entry["linked_purchase"] = link_info
                    
                    entries.append(entry)
                
                return entries
        except Exception as e:
            print(f"Error fetching journal entries: {e}")
            return []
    
    @staticmethod
    def get_meal_purchase_link(meal_id: str, purchase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get linked purchase details for a meal.
        
        Returns:
            Dict with purchase info and matched ingredients, or None
        """
        query = """
            SELECT 
                p.id, p.title, p.store, p.items, p.timestamp,
                mpl.ingredients_matched
            FROM journal_entries p
            LEFT JOIN meal_purchase_links mpl 
                ON mpl.purchase_id = p.id AND mpl.meal_id = %s
            WHERE p.id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (meal_id, purchase_id))
                result = cursor.fetchone()
                
                if result:
                    purchase_data = dict(result)
                    if purchase_data.get("items"):
                        if isinstance(purchase_data["items"], str):
                            purchase_data["items"] = json.loads(purchase_data["items"])
                    return purchase_data
                return None
        except Exception as e:
            print(f"Error getting meal-purchase link: {e}")
            return None
    
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
                    
                    # Parse ingredients_used from TEXT[] for meals
                    if entry.get("type") == "meal" and entry.get("ingredients_used"):
                        entry["ingredients_used"] = deserialize_ingredients_from_db(
                            entry["ingredients_used"]
                        )
                    
                    # Parse items JSON for purchases
                    if entry.get("type") == "purchase" and entry.get("items"):
                        if isinstance(entry["items"], str):
                            entry["items"] = json.loads(entry["items"])
                        entry["total_cost"] = sum(item.get("cost", 0) for item in entry["items"])
                    
                    # For meals with purchase_id, add linked purchase info
                    if entry.get("type") == "meal" and entry.get("purchase_id"):
                        link_info = JournalRepository.get_meal_purchase_link(
                            str(entry["id"]), str(entry["purchase_id"])
                        )
                        if link_info:
                            entry["linked_purchase"] = link_info
                    
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
    def find_matching_purchase(
        user_id: str,
        ingredients_used: List[str],
        days_back: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Find a recent purchase with items matching the meal's ingredients.
        Returns the purchase with the most matching ingredients.
        
        Args:
            user_id: User's UUID
            ingredients_used: List of ingredient names from the meal
            days_back: How far back to look for purchases (default: 7 days)
        
        Returns:
            Dict with purchase_id and matched_ingredients, or None if no match
        """
        if not ingredients_used:
            return None
        
        # Get recent purchases
        query = """
            SELECT id, items
            FROM journal_entries
            WHERE user_id = %s 
            AND type = 'purchase'
            AND timestamp >= NOW() - INTERVAL '1 day' * %s
            ORDER BY timestamp DESC
            LIMIT 20
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, days_back))
                purchases = cursor.fetchall()
                
                print(f"🔍 Auto-link: Found {len(purchases)} recent purchases for user")
                
                if not purchases:
                    return None
                
                best_match = None
                best_match_count = 0
                
                # Build keyword sets for meal ingredients
                meal_keywords = {}  # ingredient -> set of keywords
                for ing in ingredients_used:
                    meal_keywords[ing] = set(get_ingredient_keywords(ing))
                
                for purchase in purchases:
                    items = purchase['items']
                    if isinstance(items, str):
                        items = json.loads(items)
                    
                    if not items:
                        continue
                    
                    # Build keyword sets for purchase items
                    purchase_keywords = []  # list of (item_name, keyword_set)
                    for item in items:
                        item_name = item.get('name', '')
                        keywords = set(get_ingredient_keywords(item_name))
                        purchase_keywords.append((item_name, keywords))
                    
                    print(f"🔍 Purchase {str(purchase['id'])[:8]}... items: {[p[0] for p in purchase_keywords]}")
                    
                    # Find matching ingredients using keyword overlap
                    matched = []
                    for ingredient, ing_keywords in meal_keywords.items():
                        if not ing_keywords:
                            continue
                        
                        for item_name, item_keywords in purchase_keywords:
                            if not item_keywords:
                                continue
                            
                            # Check for keyword overlap
                            overlap = ing_keywords & item_keywords
                            if overlap:
                                matched.append(ingredient)
                                print(f"   ✓ '{ingredient}' matched '{item_name}' via: {overlap}")
                                break
                    
                    print(f"🔍 Total matched: {len(matched)} ingredients")
                    
                    if len(matched) > best_match_count:
                        best_match_count = len(matched)
                        best_match = {
                            'purchase_id': str(purchase['id']),
                            'matched_ingredients': matched
                        }
                
                # Only return if at least 1 ingredient matched
                return best_match if best_match_count > 0 else None
                
        except Exception as e:
            print(f"Error finding matching purchase: {e}")
            return None
    
    @staticmethod
    def auto_link_meal_to_purchase(
        meal_id: str,
        user_id: str,
        ingredients_used: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Automatically find and link a meal to a matching purchase.
        
        Args:
            meal_id: The meal entry UUID
            user_id: User's UUID
            ingredients_used: List of ingredients used in the meal
        
        Returns:
            Updated meal entry if linked, None otherwise
        """
        match = JournalRepository.find_matching_purchase(user_id, ingredients_used)
        
        if match:
            print(f"🔗 Auto-linking meal to purchase {match['purchase_id'][:8]}... ({len(match['matched_ingredients'])} ingredients matched)")
            return JournalRepository.link_meal_to_purchase(
                meal_id=meal_id,
                purchase_id=match['purchase_id'],
                user_id=user_id,
                ingredients_matched=match['matched_ingredients']
            )
        
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
