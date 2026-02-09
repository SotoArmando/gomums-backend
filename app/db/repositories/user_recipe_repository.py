"""
User Recipe Repository - Database operations for user-created private recipes
"""
from typing import List, Optional, Dict, Any
import json
from app.core.database import db


class UserRecipeRepository:
    """Repository for user recipe-related database operations"""
    
    @staticmethod
    def _row_to_dict(row: tuple, columns: List[str]) -> Dict[str, Any]:
        """Convert a database row to a dictionary"""
        return dict(zip(columns, row))
    
    @staticmethod
    def _format_recipe(row: Dict[str, Any]) -> Dict[str, Any]:
        """Format a recipe row for API response"""
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "name": row["name"],
            "description": row.get("description"),
            "image": row.get("image"),
            "prep_time": row.get("prep_time"),
            "cook_time": row.get("cook_time"),
            "total_time": row.get("total_time"),
            "servings": row.get("servings"),
            "difficulty": row.get("difficulty"),
            "ingredients": row.get("ingredients") or [],
            "instructions": row.get("instructions") or [],
            "nutrition": {
                "calories": row.get("calories"),
                "protein": row.get("protein"),
                "carbs": row.get("carbs"),
                "fat": row.get("fat"),
                "fiber": row.get("fiber"),
            },
            "category": row.get("category"),
            "tags": row.get("tags") or [],
            "source_url": row.get("source_url"),
            "source_name": row.get("source_name"),
            "original_recipe_id": str(row["original_recipe_id"]) if row.get("original_recipe_id") else None,
            "notes": row.get("notes"),
            "is_favorite": row.get("is_favorite", False),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
    
    @staticmethod
    def _format_recipe_summary(row: Dict[str, Any]) -> Dict[str, Any]:
        """Format a recipe row for list/summary response"""
        return {
            "id": str(row["id"]),
            "name": row["name"],
            "image": row.get("image"),
            "prep_time": row.get("prep_time"),
            "difficulty": row.get("difficulty"),
            "category": row.get("category"),
            "is_favorite": row.get("is_favorite", False),
            "created_at": row["created_at"],
        }
    
    @staticmethod
    def get_user_recipes(
        user_id: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get user's private recipes with optional filtering
        
        Args:
            user_id: The user's ID
            category: Filter by category
            difficulty: Filter by difficulty (easy, medium, hard)
            is_favorite: Filter by favorite status
            search: Search in name, description
            tags: Filter by tags (recipe must have ALL specified tags)
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            Dict with recipes list, total count, limit, and offset
        """
        # Base query for counting
        count_query = "SELECT COUNT(*) FROM user_recipes WHERE user_id = %s"
        
        # Base query for fetching
        query = """
            SELECT 
                id, name, image, prep_time, difficulty, 
                category, is_favorite, created_at
            FROM user_recipes
            WHERE user_id = %s
        """
        params = [user_id]
        
        # Apply filters
        if category:
            query += " AND category = %s"
            count_query += " AND category = %s"
            params.append(category)
        
        if difficulty:
            query += " AND difficulty = %s"
            count_query += " AND difficulty = %s"
            params.append(difficulty)
        
        if is_favorite is not None:
            query += " AND is_favorite = %s"
            count_query += " AND is_favorite = %s"
            params.append(is_favorite)
        
        if search:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            count_query += " AND (name ILIKE %s OR description ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if tags:
            query += " AND tags @> %s"
            count_query += " AND tags @> %s"
            params.append(tags)
        
        # Get total count
        try:
            with db.get_cursor() as cursor:
                cursor.execute(count_query, params)
                total = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting user recipes: {e}")
            total = 0
        
        # Order and pagination
        query += " ORDER BY is_favorite DESC, updated_at DESC"
        query += " LIMIT %s OFFSET %s"
        params_with_pagination = params + [limit, offset]
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, params_with_pagination)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                recipes = [
                    UserRecipeRepository._format_recipe_summary(
                        UserRecipeRepository._row_to_dict(row, columns)
                    )
                    for row in rows
                ]
                
                return {
                    "recipes": recipes,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
        except Exception as e:
            print(f"Error fetching user recipes: {e}")
            return {
                "recipes": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
    
    @staticmethod
    def get_user_recipe_by_id(user_id: str, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get a single user recipe by ID (only if owned by user)"""
        query = """
            SELECT 
                id, user_id, name, description, image, 
                prep_time, cook_time, total_time, servings, difficulty,
                ingredients, instructions,
                calories, protein, carbs, fat, fiber,
                category, tags,
                source_url, source_name, original_recipe_id,
                notes, is_favorite,
                created_at, updated_at
            FROM user_recipes
            WHERE id = %s AND user_id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (recipe_id, user_id))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                columns = [desc[0] for desc in cursor.description]
                recipe_dict = UserRecipeRepository._row_to_dict(row, columns)
                return UserRecipeRepository._format_recipe(recipe_dict)
        except Exception as e:
            print(f"Error fetching user recipe: {e}")
            return None
    
    @staticmethod
    def create_user_recipe(user_id: str, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user recipe"""
        query = """
            INSERT INTO user_recipes (
                user_id, name, description, image,
                prep_time, cook_time, total_time, servings, difficulty,
                ingredients, instructions,
                calories, protein, carbs, fat, fiber,
                category, tags,
                source_url, source_name, original_recipe_id,
                notes, is_favorite
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s
            )
            RETURNING id, created_at, updated_at
        """
        
        # Convert lists to JSON
        ingredients = json.dumps(recipe_data.get("ingredients", []))
        instructions = json.dumps(recipe_data.get("instructions", []))
        
        params = (
            user_id,
            recipe_data["name"],
            recipe_data.get("description"),
            recipe_data.get("image"),
            recipe_data.get("prep_time"),
            recipe_data.get("cook_time"),
            recipe_data.get("total_time"),
            recipe_data.get("servings", 1),
            recipe_data.get("difficulty"),
            ingredients,
            instructions,
            recipe_data.get("calories"),
            recipe_data.get("protein"),
            recipe_data.get("carbs"),
            recipe_data.get("fat"),
            recipe_data.get("fiber"),
            recipe_data.get("category"),
            recipe_data.get("tags", []),
            recipe_data.get("source_url"),
            recipe_data.get("source_name"),
            recipe_data.get("original_recipe_id"),
            recipe_data.get("notes"),
            recipe_data.get("is_favorite", False)
        )
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if result:
                    # Return the full recipe
                    return UserRecipeRepository.get_user_recipe_by_id(user_id, str(result[0]))
                return None
        except Exception as e:
            print(f"Error creating user recipe: {e}")
            return None
    
    @staticmethod
    def update_user_recipe(
        user_id: str, 
        recipe_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing user recipe"""
        # Build dynamic update query based on provided fields
        update_fields = []
        params = []
        
        field_mapping = {
            "name": "name",
            "description": "description",
            "image": "image",
            "prep_time": "prep_time",
            "cook_time": "cook_time",
            "total_time": "total_time",
            "servings": "servings",
            "difficulty": "difficulty",
            "calories": "calories",
            "protein": "protein",
            "carbs": "carbs",
            "fat": "fat",
            "fiber": "fiber",
            "category": "category",
            "tags": "tags",
            "source_url": "source_url",
            "source_name": "source_name",
            "notes": "notes",
            "is_favorite": "is_favorite",
        }
        
        for field, column in field_mapping.items():
            if field in update_data and update_data[field] is not None:
                update_fields.append(f"{column} = %s")
                params.append(update_data[field])
        
        # Handle JSON fields specially
        if "ingredients" in update_data and update_data["ingredients"] is not None:
            update_fields.append("ingredients = %s")
            params.append(json.dumps(update_data["ingredients"]))
        
        if "instructions" in update_data and update_data["instructions"] is not None:
            update_fields.append("instructions = %s")
            params.append(json.dumps(update_data["instructions"]))
        
        if not update_fields:
            return UserRecipeRepository.get_user_recipe_by_id(user_id, recipe_id)
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = NOW()")
        
        query = f"""
            UPDATE user_recipes
            SET {", ".join(update_fields)}
            WHERE id = %s AND user_id = %s
            RETURNING id
        """
        params.extend([recipe_id, user_id])
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if result:
                    return UserRecipeRepository.get_user_recipe_by_id(user_id, recipe_id)
                return None
        except Exception as e:
            print(f"Error updating user recipe: {e}")
            return None
    
    @staticmethod
    def delete_user_recipe(user_id: str, recipe_id: str) -> bool:
        """Delete a user recipe"""
        query = """
            DELETE FROM user_recipes
            WHERE id = %s AND user_id = %s
            RETURNING id
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (recipe_id, user_id))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f"Error deleting user recipe: {e}")
            return False
    
    @staticmethod
    def toggle_favorite(user_id: str, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Toggle favorite status of a user recipe"""
        query = """
            UPDATE user_recipes
            SET is_favorite = NOT is_favorite, updated_at = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING id, is_favorite
        """
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, (recipe_id, user_id))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "id": str(result[0]),
                        "is_favorite": result[1]
                    }
                return None
        except Exception as e:
            print(f"Error toggling favorite: {e}")
            return None
    
    @staticmethod
    def get_favorites(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's favorite recipes"""
        query = """
            SELECT 
                id, name, image, prep_time, difficulty, 
                category, is_favorite, created_at
            FROM user_recipes
            WHERE user_id = %s AND is_favorite = TRUE
            ORDER BY updated_at DESC
            LIMIT %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id, limit))
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                return [
                    UserRecipeRepository._format_recipe_summary(
                        UserRecipeRepository._row_to_dict(row, columns)
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"Error fetching favorites: {e}")
            return []
    
    @staticmethod
    def get_recipe_count(user_id: str) -> int:
        """Get total count of user's recipes"""
        query = "SELECT COUNT(*) FROM user_recipes WHERE user_id = %s"
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting recipes: {e}")
            return 0
    
    @staticmethod
    def get_categories(user_id: str) -> List[str]:
        """Get list of categories used by user"""
        query = """
            SELECT DISTINCT category 
            FROM user_recipes 
            WHERE user_id = %s AND category IS NOT NULL
            ORDER BY category
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (user_id,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
    
    @staticmethod
    def copy_from_public_recipe(user_id: str, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Copy a public recipe to user's private recipes
        This allows users to save and modify public recipes
        """
        # First, get the public recipe
        query = """
            SELECT 
                name, image, prep_time, servings, difficulty,
                ingredients, instructions, steps,
                calories, protein, carbs, fat, fiber,
                category, tags
            FROM recipes
            WHERE id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (recipe_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                columns = [desc[0] for desc in cursor.description]
                public_recipe = dict(zip(columns, row))
            
            # Convert ingredients and instructions to expected format
            # Public recipes store these as text arrays
            ingredients_raw = public_recipe.get("ingredients") or []
            steps_raw = public_recipe.get("steps") or []
            instructions_raw = public_recipe.get("instructions") or []
            
            # Convert to structured format
            ingredients = [
                {"name": ing, "amount": None, "unit": None, "notes": None}
                for ing in ingredients_raw
            ]
            
            # If structured steps exist, use them; otherwise fall back to flat instructions
            if steps_raw:
                instructions = [
                    {
                        "step_number": s.get("order", i + 1),
                        "instruction": s.get("text", ""),
                        "phase": s.get("phase"),
                        "items": s.get("items", []),
                        "time_minutes": s.get("time_minutes"),
                        "tip": s.get("tip")
                    }
                    for i, s in enumerate(steps_raw)
                ]
            else:
                instructions = [
                    {"step_number": i + 1, "instruction": inst, "time_minutes": None, "tip": None}
                    for i, inst in enumerate(instructions_raw)
                ]
            
            # Create the user recipe
            recipe_data = {
                "name": f"{public_recipe['name']} (My Version)",
                "image": public_recipe.get("image"),
                "prep_time": public_recipe.get("prep_time"),
                "servings": public_recipe.get("servings"),
                "difficulty": public_recipe.get("difficulty"),
                "ingredients": ingredients,
                "instructions": instructions,
                "calories": public_recipe.get("calories"),
                "protein": public_recipe.get("protein"),
                "carbs": public_recipe.get("carbs"),
                "fat": public_recipe.get("fat"),
                "fiber": public_recipe.get("fiber"),
                "category": public_recipe.get("category"),
                "tags": public_recipe.get("tags") or [],
                "source_name": "GoMums Recipes",
                "original_recipe_id": recipe_id,
                "notes": "Copied from public recipes"
            }
            
            return UserRecipeRepository.create_user_recipe(user_id, recipe_data)
            
        except Exception as e:
            print(f"Error copying public recipe: {e}")
            return None
