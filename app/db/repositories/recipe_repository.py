"""
Recipe Repository - Database operations for recipes
"""
from typing import List, Optional, Dict, Any
from app.core.database import db


class RecipeRepository:
    """Repository for recipe-related database operations"""
    
    async def get_recipes(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        featured: Optional[bool] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get recipes with optional filtering
        
        Args:
            category: Filter by category
            difficulty: Filter by difficulty (easy, medium, hard)
            featured: Filter by featured status
            search: Search in name, category
            tags: Filter by tags (recipe must have ALL specified tags)
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of recipe dictionaries
        """
        query = """
            SELECT 
                id, name, description, image, prep_time, servings, difficulty,
                ingredients, instructions, steps,
                structured_ingredients,
                calories, protein, carbs, fat, fiber,
                featured, category, tags,
                created_at, updated_at
            FROM recipes
            WHERE 1=1
        """
        params = []
        
        # Apply filters
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if difficulty:
            query += " AND difficulty = %s"
            params.append(difficulty)
        
        if featured is not None:
            query += " AND featured = %s"
            params.append(featured)
        
        if search:
            query += " AND (name ILIKE %s OR category ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if tags:
            # Check if recipe contains ALL specified tags
            query += " AND tags @> %s"
            params.append(tags)
        
        # Order by featured first, then by name
        query += " ORDER BY featured DESC, name ASC"
        
        # Pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                recipes = []
                for row in rows:
                    recipes.append({
                        'id': str(row['id']),
                        'name': row['name'],
                        'description': row['description'],
                        'image': row['image'],
                        'prep_time': row['prep_time'],
                        'servings': row['servings'],
                        'difficulty': row['difficulty'],
                        'ingredients': row['ingredients'] if row['ingredients'] else [],
                        'instructions': row['instructions'] if row['instructions'] else [],
                        'steps': row['steps'] if row['steps'] else [],
                        'structured_ingredients': row.get('structured_ingredients') or [],
                        'calories': row['calories'],
                        'protein': row['protein'],
                        'carbs': row['carbs'],
                        'fat': row['fat'],
                        'fiber': row['fiber'],
                        'featured': row['featured'],
                        'category': row['category'],
                        'tags': row['tags'] if row['tags'] else [],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return recipes
        except Exception as e:
            print(f"Error getting recipes: {e}")
            return []
    
    async def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single recipe by ID
        
        Args:
            recipe_id: UUID of the recipe
        
        Returns:
            Recipe dictionary or None if not found
        """
        query = """
            SELECT 
                id, name, description, image, prep_time, servings, difficulty,
                ingredients, instructions, steps,
                structured_ingredients,
                calories, protein, carbs, fat, fiber,
                featured, category, tags,
                created_at, updated_at
            FROM recipes
            WHERE id = %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, (recipe_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'name': row['name'],
                    'description': row['description'],
                    'image': row['image'],
                    'prep_time': row['prep_time'],
                    'servings': row['servings'],
                    'difficulty': row['difficulty'],
                    'ingredients': row['ingredients'] if row['ingredients'] else [],
                    'instructions': row['instructions'] if row['instructions'] else [],
                    'steps': row['steps'] if row['steps'] else [],
                    'structured_ingredients': row.get('structured_ingredients') or [],
                    'calories': row['calories'],
                    'protein': row['protein'],
                    'carbs': row['carbs'],
                    'fat': row['fat'],
                    'fiber': row['fiber'],
                    'featured': row['featured'],
                    'category': row['category'],
                    'tags': row['tags'] if row['tags'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error getting recipe: {e}")
            return None
    
    async def count_recipes(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        featured: Optional[bool] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Count total recipes matching filters (for pagination)
        
        Returns:
            Total count of matching recipes
        """
        query = "SELECT COUNT(*) FROM recipes WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if difficulty:
            query += " AND difficulty = %s"
            params.append(difficulty)
        
        if featured is not None:
            query += " AND featured = %s"
            params.append(featured)
        
        if search:
            query += " AND (name ILIKE %s OR category ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if tags:
            query += " AND tags @> %s"
            params.append(tags)
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting recipes: {e}")
            return 0
    
    async def get_recipes_with_steps(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get recipes that have structured steps populated
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of recipe dictionaries with steps
        """
        query = """
            SELECT 
                id, name, description, image, prep_time, servings, difficulty,
                ingredients, instructions, steps,
                structured_ingredients,
                calories, protein, carbs, fat, fiber,
                featured, category, tags,
                created_at, updated_at
            FROM recipes
            WHERE steps IS NOT NULL 
                AND steps != '[]'::jsonb
                AND jsonb_array_length(steps) > 0
            ORDER BY featured DESC, created_at DESC
            LIMIT %s OFFSET %s
        """
        
        try:
            with db.get_cursor() as cursor:
                cursor.execute(query, [limit, offset])
                rows = cursor.fetchall()
                
                recipes = []
                for row in rows:
                    recipes.append({
                        'id': str(row['id']),
                        'name': row['name'],
                        'description': row['description'],
                        'image': row['image'],
                        'prep_time': row['prep_time'],
                        'servings': row['servings'],
                        'difficulty': row['difficulty'],
                        'ingredients': row['ingredients'] if row['ingredients'] else [],
                        'instructions': row['instructions'] if row['instructions'] else [],
                        'steps': row['steps'] if row['steps'] else [],
                        'structured_ingredients': row.get('structured_ingredients') or [],
                        'calories': row['calories'],
                        'protein': row['protein'],
                        'carbs': row['carbs'],
                        'fat': row['fat'],
                        'fiber': row['fiber'],
                        'featured': row['featured'],
                        'category': row['category'],
                        'tags': row['tags'] if row['tags'] else [],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return recipes
        except Exception as e:
            print(f"Error getting recipes with steps: {e}")
            return []
    
    @staticmethod
    def create_recipe(recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new recipe
        
        Args:
            recipe_data: Dictionary containing recipe information
        
        Returns:
            Created recipe dictionary or None if failed
        """
        import uuid
        import json
        
        query = """
            INSERT INTO recipes (
                id, name, image, prep_time, servings, difficulty,
                ingredients, instructions, steps,
                structured_ingredients,
                calories, protein, carbs, fat, fiber,
                featured, category, tags
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, image, prep_time, servings, difficulty,
                      ingredients, instructions, steps,
                      structured_ingredients,
                      calories, protein, carbs, fat, fiber,
                      featured, category, tags,
                      created_at, updated_at
        """
        
        recipe_id = str(uuid.uuid4())
        
        values = (
            recipe_id,
            recipe_data.get('name'),
            recipe_data.get('image'),
            recipe_data.get('prep_time'),
            recipe_data.get('servings'),
            recipe_data.get('difficulty', 'medium'),
            recipe_data.get('ingredients', []),
            recipe_data.get('instructions', []),
            json.dumps(recipe_data.get('steps', [])),
            json.dumps(recipe_data.get('structured_ingredients', [])),
            recipe_data.get('calories'),
            recipe_data.get('protein'),
            recipe_data.get('carbs'),
            recipe_data.get('fat'),
            recipe_data.get('fiber'),
            recipe_data.get('featured', False),
            recipe_data.get('category'),
            recipe_data.get('tags', [])
        )
        
        try:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, values)
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    'id': str(row['id']),
                    'name': row['name'],
                    'description': row.get('description'),
                    'image': row['image'],
                    'prep_time': row['prep_time'],
                    'servings': row['servings'],
                    'difficulty': row['difficulty'],
                    'ingredients': row['ingredients'] if row['ingredients'] else [],
                    'instructions': row['instructions'] if row['instructions'] else [],
                    'steps': row['steps'] if row['steps'] else [],
                    'structured_ingredients': row.get('structured_ingredients') or [],
                    'calories': row['calories'],
                    'protein': row['protein'],
                    'carbs': row['carbs'],
                    'fat': row['fat'],
                    'fiber': row['fiber'],
                    'featured': row['featured'],
                    'category': row['category'],
                    'tags': row['tags'] if row['tags'] else [],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
        except Exception as e:
            print(f"Error creating recipe: {e}")
            return None

