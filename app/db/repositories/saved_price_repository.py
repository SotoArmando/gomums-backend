from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.core.database import db


class SavedPriceRepository:
    """Repository for saved ingredient price database operations"""

    @staticmethod
    def create(user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a single saved ingredient price record"""
        record_id = str(uuid.uuid4())

        query = """
            INSERT INTO saved_ingredient_prices (
                id, user_id, recipe_name, ingredient_name, original_price,
                modified_name, modified_price, status, is_homemade, is_added
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        values = (
            record_id, user_id,
            data["recipe_name"],
            data["ingredient_name"],
            data.get("original_price", 0),
            data.get("modified_name"),
            data.get("modified_price"),
            data.get("status", "original"),
            data.get("is_homemade", False),
            data.get("is_added", False),
        )

        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error creating saved ingredient price: {e}")
            return None

    @staticmethod
    def bulk_create(user_id: str, recipe_name: str, ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bulk-save ingredient prices for a recipe (replaces existing)"""
        try:
            with db.get_cursor(commit=True) as cursor:
                # Delete existing saved prices for this recipe
                cursor.execute(
                    "DELETE FROM saved_ingredient_prices WHERE user_id = %s AND recipe_name = %s",
                    (user_id, recipe_name)
                )

                created = []
                for ing in ingredients:
                    record_id = str(uuid.uuid4())
                    query = """
                        INSERT INTO saved_ingredient_prices (
                            id, user_id, recipe_name, ingredient_name, original_price,
                            modified_name, modified_price, status, is_homemade, is_added
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """
                    values = (
                        record_id, user_id, recipe_name,
                        ing["ingredient_name"],
                        ing.get("original_price", 0),
                        ing.get("modified_name"),
                        ing.get("modified_price"),
                        ing.get("status", "original"),
                        ing.get("is_homemade", False),
                        ing.get("is_added", False),
                    )
                    cursor.execute(query, values)
                    result = cursor.fetchone()
                    if result:
                        created.append(dict(result))

                return created
        except Exception as e:
            print(f"Error bulk creating saved ingredient prices: {e}")
            return []

    @staticmethod
    def get_by_recipe(user_id: str, recipe_name: str) -> List[Dict[str, Any]]:
        """Get all saved ingredient prices for a specific recipe"""
        query = """
            SELECT * FROM saved_ingredient_prices
            WHERE user_id = %s AND recipe_name = %s
            ORDER BY created_at ASC
        """
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, recipe_name))
                results = cursor.fetchall()
                return [dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching saved prices by recipe: {e}")
            return []

    @staticmethod
    def get_all_recipes(user_id: str) -> List[str]:
        """Get all distinct recipe names that have saved prices"""
        query = """
            SELECT DISTINCT recipe_name FROM saved_ingredient_prices
            WHERE user_id = %s
            ORDER BY recipe_name ASC
        """
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                return [r["recipe_name"] for r in results]
        except Exception as e:
            print(f"Error fetching recipe names: {e}")
            return []

    @staticmethod
    def get_by_id(record_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a single saved ingredient price by ID"""
        query = "SELECT * FROM saved_ingredient_prices WHERE id = %s AND user_id = %s"
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (record_id, user_id))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching saved price by id: {e}")
            return None

    @staticmethod
    def update(record_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a saved ingredient price"""
        fields = []
        values = []

        updatable = [
            "original_price", "modified_name", "modified_price",
            "status", "is_homemade", "is_added"
        ]

        for field in updatable:
            if field in data and data[field] is not None:
                fields.append(f"{field} = %s")
                values.append(data[field])

        if not fields:
            return SavedPriceRepository.get_by_id(record_id, user_id)

        fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        values.extend([record_id, user_id])

        query = f"""
            UPDATE saved_ingredient_prices
            SET {', '.join(fields)}
            WHERE id = %s AND user_id = %s
            RETURNING *
        """

        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error updating saved price: {e}")
            return None

    @staticmethod
    def delete(record_id: str, user_id: str) -> bool:
        """Delete a single saved ingredient price"""
        query = "DELETE FROM saved_ingredient_prices WHERE id = %s AND user_id = %s"
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (record_id, user_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting saved price: {e}")
            return False

    @staticmethod
    def delete_by_recipe(user_id: str, recipe_name: str) -> bool:
        """Delete all saved ingredient prices for a recipe"""
        query = "DELETE FROM saved_ingredient_prices WHERE user_id = %s AND recipe_name = %s"
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id, recipe_name))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting saved prices for recipe: {e}")
            return False

    @staticmethod
    def get_recipe_summary(user_id: str, recipe_name: str) -> Optional[Dict[str, Any]]:
        """Get a price summary for a saved recipe"""
        query = """
            SELECT
                recipe_name,
                COUNT(*) AS ingredient_count,
                COALESCE(SUM(original_price), 0) AS total_original,
                COALESCE(SUM(
                    CASE
                        WHEN status = 'removed' THEN 0
                        WHEN modified_price IS NOT NULL THEN modified_price
                        ELSE original_price
                    END
                ), 0) AS total_modified,
                COUNT(*) FILTER (WHERE status = 'swapped') AS swapped_count,
                COUNT(*) FILTER (WHERE status = 'removed') AS removed_count,
                COUNT(*) FILTER (WHERE is_homemade = TRUE) AS homemade_count
            FROM saved_ingredient_prices
            WHERE user_id = %s AND recipe_name = %s
            GROUP BY recipe_name
        """
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, recipe_name))
                result = cursor.fetchone()
                if result:
                    row = dict(result)
                    row["total_savings"] = float(row["total_original"]) - float(row["total_modified"])
                    return row
                return None
        except Exception as e:
            print(f"Error fetching recipe summary: {e}")
            return None
