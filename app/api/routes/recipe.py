"""
Recipe API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.models.recipe import RecipeResponse, RecipeListParams, NutritionInfo, RecipeStep, StructuredIngredient
from app.db.repositories.recipe_repository import RecipeRepository
from app.core.security import get_current_user

router = APIRouter()
recipe_repo = RecipeRepository()


@router.get("/", response_model=List[RecipeResponse])
async def get_recipes(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(
        None,
        pattern="^(easy|medium|hard)$",
        description="Filter by difficulty (easy, medium, hard)"
    ),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    search: Optional[str] = Query(None, description="Search in name or category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get recipes with optional filtering
    
    - **category**: Filter by category (e.g., "Breakfast", "Dinner")
    - **difficulty**: Filter by difficulty (easy, medium, hard)
    - **featured**: Filter by featured status (true/false)
    - **search**: Search in recipe name or category
    - **tags**: Comma-separated tags (recipe must have ALL specified tags)
    - **limit**: Maximum number of results (default: 20, max: 100)
    - **offset**: Number of results to skip for pagination
    """
    # Parse tags if provided
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    recipes = await recipe_repo.get_recipes(
        category=category,
        difficulty=difficulty,
        featured=featured,
        search=search,
        tags=tags_list,
        limit=limit,
        offset=offset
    )
    
    # Transform to response model
    response = []
    for recipe in recipes:
        structured = [StructuredIngredient(**s) for s in recipe.get("structured_ingredients", [])]
        response.append(RecipeResponse(
            id=recipe["id"],
            name=recipe["name"],
            description=recipe.get("description"),
            image=recipe["image"],
            prep_time=recipe["prep_time"],
            servings=recipe["servings"],
            difficulty=recipe["difficulty"],
            ingredients=recipe["ingredients"],
            structured_ingredients=structured,
            instructions=recipe["instructions"],
            steps=[RecipeStep(**s) for s in recipe.get("steps", [])],
            nutrition=NutritionInfo(
                calories=recipe["calories"],
                protein=recipe["protein"],
                carbs=recipe["carbs"],
                fat=recipe["fat"],
                fiber=recipe["fiber"]
            ),
            featured=recipe["featured"],
            category=recipe["category"],
            tags=recipe["tags"],
            created_at=recipe["created_at"],
            updated_at=recipe["updated_at"]
        ))
    
    return response


@router.get("/with-steps", response_model=List[RecipeResponse])
async def get_recipes_with_steps(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get recipes that have structured steps with phases (Prepare, Cook, Serve)
    
    Returns recipes that have the 'steps' field populated with detailed cooking instructions.
    """
    recipes = await recipe_repo.get_recipes_with_steps(limit=limit, offset=offset)
    
    # Transform to response model
    response = []
    for recipe in recipes:
        structured = [StructuredIngredient(**s) for s in recipe.get("structured_ingredients", [])]
        response.append(RecipeResponse(
            id=recipe["id"],
            name=recipe["name"],
            description=recipe.get("description"),
            image=recipe["image"],
            prep_time=recipe["prep_time"],
            servings=recipe["servings"],
            difficulty=recipe["difficulty"],
            ingredients=recipe["ingredients"],
            structured_ingredients=structured,
            instructions=recipe["instructions"],
            steps=[RecipeStep(**s) for s in recipe.get("steps", [])],
            nutrition=NutritionInfo(
                calories=recipe["calories"],
                protein=recipe["protein"],
                carbs=recipe["carbs"],
                fat=recipe["fat"],
                fiber=recipe["fiber"]
            ),
            featured=recipe["featured"],
            category=recipe["category"],
            tags=recipe["tags"],
            created_at=recipe["created_at"],
            updated_at=recipe["updated_at"]
        ))
    
    return response


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_by_id(
    recipe_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific recipe by ID
    
    - **recipe_id**: UUID of the recipe
    """
    recipe = await recipe_repo.get_recipe_by_id(recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return RecipeResponse(
        id=recipe["id"],
        name=recipe["name"],
        description=recipe.get("description"),
        image=recipe["image"],
        prep_time=recipe["prep_time"],
        servings=recipe["servings"],
        difficulty=recipe["difficulty"],
        ingredients=recipe["ingredients"],
        structured_ingredients=[StructuredIngredient(**s) for s in recipe.get("structured_ingredients", [])],
        instructions=recipe["instructions"],
        steps=[RecipeStep(**s) for s in recipe.get("steps", [])],
        nutrition=NutritionInfo(
            calories=recipe["calories"],
            protein=recipe["protein"],
            carbs=recipe["carbs"],
            fat=recipe["fat"],
            fiber=recipe["fiber"]
        ),
        featured=recipe["featured"],
        category=recipe["category"],
        tags=recipe["tags"],
        created_at=recipe["created_at"],
        updated_at=recipe["updated_at"]
    )


@router.get("/count/total")
async def get_recipes_count(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    featured: Optional[bool] = Query(None, description="Filter by featured status"),
    search: Optional[str] = Query(None, description="Search in name or category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get total count of recipes matching filters (useful for pagination)
    """
    # Parse tags if provided
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    count = await recipe_repo.count_recipes(
        category=category,
        difficulty=difficulty,
        featured=featured,
        search=search,
        tags=tags_list
    )
    
    return {"count": count}


