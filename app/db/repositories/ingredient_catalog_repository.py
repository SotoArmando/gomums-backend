from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.core.database import db


class IngredientCatalogRepository:
    """Repository for ingredient catalog database operations"""

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a single ingredient catalog entry"""
        record_id = str(uuid.uuid4())

        query = """
            INSERT INTO ingredient_catalog (
                id, name, name_local, category, unit,
                price, price_low, price_high, currency, region, language, source
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (LOWER(name), LOWER(region)) DO UPDATE
            SET price = EXCLUDED.price,
                price_low = EXCLUDED.price_low,
                price_high = EXCLUDED.price_high,
                name_local = EXCLUDED.name_local,
                category = EXCLUDED.category,
                unit = EXCLUDED.unit,
                currency = EXCLUDED.currency,
                language = EXCLUDED.language,
                source = EXCLUDED.source,
                updated_at = NOW()
            RETURNING *
        """

        values = (
            record_id,
            data["name"],
            data.get("name_local"),
            data["category"],
            data["unit"],
            data["price"],
            data.get("price_low"),
            data.get("price_high"),
            data["currency"],
            data["region"],
            data.get("language", "en"),
            data.get("source", "manual"),
        )

        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error creating ingredient catalog entry: {e}")
            return None

    @staticmethod
    def bulk_create(ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Bulk-create ingredient catalog entries (upserts on name+region)"""
        try:
            with db.get_cursor(commit=True) as cursor:
                created = []
                for ing in ingredients:
                    record_id = str(uuid.uuid4())
                    query = """
                        INSERT INTO ingredient_catalog (
                            id, name, name_local, category, unit,
                            price, price_low, price_high, currency, region, language, source
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (LOWER(name), LOWER(region)) DO UPDATE
                        SET price = EXCLUDED.price,
                            price_low = EXCLUDED.price_low,
                            price_high = EXCLUDED.price_high,
                            name_local = EXCLUDED.name_local,
                            category = EXCLUDED.category,
                            unit = EXCLUDED.unit,
                            currency = EXCLUDED.currency,
                            language = EXCLUDED.language,
                            source = EXCLUDED.source,
                            updated_at = NOW()
                        RETURNING *
                    """
                    values = (
                        record_id,
                        ing["name"],
                        ing.get("name_local"),
                        ing["category"],
                        ing["unit"],
                        ing["price"],
                        ing.get("price_low"),
                        ing.get("price_high"),
                        ing["currency"],
                        ing["region"],
                        ing.get("language", "en"),
                        ing.get("source", "csv_import"),
                    )
                    cursor.execute(query, values)
                    result = cursor.fetchone()
                    if result:
                        created.append(dict(result))

                return created
        except Exception as e:
            print(f"Error bulk creating ingredient catalog entries: {e}")
            return []

    @staticmethod
    def get_by_region(
        region: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get all ingredients for a specific region, optionally filtered"""
        conditions = ["LOWER(region) = LOWER(%s)"]
        params: list = [region]

        if category:
            conditions.append("LOWER(category) = LOWER(%s)")
            params.append(category)

        if search:
            conditions.append("(LOWER(name) LIKE LOWER(%s) OR LOWER(name_local) LIKE LOWER(%s))")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT * FROM ingredient_catalog
            WHERE {where_clause}
            ORDER BY category, name
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching ingredients by region: {e}")
            return []

    @staticmethod
    def count_by_region(
        region: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count ingredients for a region"""
        conditions = ["LOWER(region) = LOWER(%s)"]
        params: list = [region]

        if category:
            conditions.append("LOWER(category) = LOWER(%s)")
            params.append(category)

        if search:
            conditions.append("(LOWER(name) LIKE LOWER(%s) OR LOWER(name_local) LIKE LOWER(%s))")
            params.extend([f"%{search}%", f"%{search}%"])

        where_clause = " AND ".join(conditions)

        query = f"SELECT COUNT(*) as cnt FROM ingredient_catalog WHERE {where_clause}"

        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result["cnt"] if result else 0
        except Exception as e:
            print(f"Error counting ingredients: {e}")
            return 0

    @staticmethod
    def get_by_id(record_id: str) -> Optional[Dict[str, Any]]:
        """Get a single ingredient by ID"""
        query = "SELECT * FROM ingredient_catalog WHERE id = %s"
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (record_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error fetching ingredient by id: {e}")
            return None

    @staticmethod
    def update(record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an ingredient catalog entry"""
        fields = []
        values = []

        updatable = [
            "name", "name_local", "category", "unit",
            "price", "price_low", "price_high",
            "currency", "region", "language", "source",
        ]

        for field in updatable:
            if field in data and data[field] is not None:
                fields.append(f"{field} = %s")
                values.append(data[field])

        if not fields:
            return IngredientCatalogRepository.get_by_id(record_id)

        fields.append("updated_at = %s")
        values.append(datetime.utcnow())
        values.append(record_id)

        query = f"""
            UPDATE ingredient_catalog
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING *
        """

        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"Error updating ingredient: {e}")
            return None

    @staticmethod
    def delete(record_id: str) -> bool:
        """Delete a single ingredient catalog entry"""
        query = "DELETE FROM ingredient_catalog WHERE id = %s"
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (record_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting ingredient: {e}")
            return False

    @staticmethod
    def delete_by_region(region: str) -> int:
        """Delete all ingredients for a region. Returns count deleted."""
        query = "DELETE FROM ingredient_catalog WHERE LOWER(region) = LOWER(%s)"
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (region,))
                return cursor.rowcount
        except Exception as e:
            print(f"Error deleting ingredients for region: {e}")
            return 0

    @staticmethod
    def get_all_regions() -> List[Dict[str, Any]]:
        """Get all regions with their ingredient counts and currencies"""
        query = """
            SELECT
                region,
                currency,
                MAX(language) AS language,
                COUNT(*) AS total_ingredients,
                array_agg(DISTINCT category ORDER BY category) AS categories
            FROM ingredient_catalog
            GROUP BY region, currency
            ORDER BY region
        """
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                return [dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching regions: {e}")
            return []

    @staticmethod
    def get_categories(region: Optional[str] = None) -> List[str]:
        """Get all distinct categories, optionally filtered by region"""
        if region:
            query = """
                SELECT DISTINCT category FROM ingredient_catalog
                WHERE LOWER(region) = LOWER(%s)
                ORDER BY category
            """
            params = (region,)
        else:
            query = "SELECT DISTINCT category FROM ingredient_catalog ORDER BY category"
            params = ()

        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [r["category"] for r in results]
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

    @staticmethod
    def search(query_text: str, region: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search ingredients by name across regions"""
        conditions = ["(LOWER(name) LIKE LOWER(%s) OR LOWER(name_local) LIKE LOWER(%s))"]
        params: list = [f"%{query_text}%", f"%{query_text}%"]

        if region:
            conditions.append("LOWER(region) = LOWER(%s)")
            params.append(region)

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT * FROM ingredient_catalog
            WHERE {where_clause}
            ORDER BY region, category, name
            LIMIT %s
        """
        params.append(limit)

        try:
            with db.get_cursor() as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                return [dict(r) for r in results]
        except Exception as e:
            print(f"Error searching ingredients: {e}")
            return []
