"""
User Recipe Routes
API endpoints for user-created private recipes
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.models.user_recipe import (
    UserRecipeCreate,
    UserRecipeUpdate,
    UserRecipeResponse,
    UserRecipeListResponse,
    UserRecipeSummary
)
from app.db.repositories.user_recipe_repository import UserRecipeRepository
from app.core.security import get_current_user


router = APIRouter(prefix="/api/user-recipes", tags=["User Recipes"])


@router.get("/", response_model=UserRecipeListResponse)
async def get_my_recipes(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's private recipes with optional filtering
    
    - **category**: Filter by category
    - **difficulty**: Filter by difficulty (easy, medium, hard)
    - **is_favorite**: Filter by favorite status
    - **search**: Search in name and description
    - **tags**: Comma-separated tags to filter by
    - **limit**: Maximum results (1-100)
    - **offset**: Number of results to skip
    """
    user_id = current_user["sub"]
    
    # Parse tags if provided
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    
    result = UserRecipeRepository.get_user_recipes(
        user_id=user_id,
        category=category,
        difficulty=difficulty,
        is_favorite=is_favorite,
        search=search,
        tags=tag_list,
        limit=limit,
        offset=offset
    )
    
    return result


@router.get("/favorites", response_model=List[UserRecipeSummary])
async def get_favorite_recipes(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get user's favorite recipes"""
    user_id = current_user["sub"]
    return UserRecipeRepository.get_favorites(user_id, limit)


@router.get("/categories", response_model=List[str])
async def get_my_categories(
    current_user: dict = Depends(get_current_user)
):
    """Get list of categories used in user's recipes"""
    user_id = current_user["sub"]
    return UserRecipeRepository.get_categories(user_id)


@router.get("/stats")
async def get_recipe_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get statistics about user's recipes"""
    user_id = current_user["sub"]
    
    total = UserRecipeRepository.get_recipe_count(user_id)
    favorites = UserRecipeRepository.get_favorites(user_id, limit=1000)
    categories = UserRecipeRepository.get_categories(user_id)
    
    return {
        "total_recipes": total,
        "favorite_count": len(favorites),
        "category_count": len(categories),
        "categories": categories
    }


@router.get("/{recipe_id}", response_model=UserRecipeResponse)
async def get_recipe(
    recipe_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific user recipe by ID"""
    user_id = current_user["sub"]
    
    recipe = UserRecipeRepository.get_user_recipe_by_id(user_id, str(recipe_id))
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe


@router.post("/", response_model=UserRecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_data: UserRecipeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new private recipe"""
    user_id = current_user["sub"]
    
    # Convert Pydantic model to dict
    data = recipe_data.model_dump()
    
    # Convert nested models to dicts
    if data.get("ingredients"):
        data["ingredients"] = [ing if isinstance(ing, dict) else ing.model_dump() for ing in recipe_data.ingredients]
    if data.get("instructions"):
        data["instructions"] = [inst if isinstance(inst, dict) else inst.model_dump() for inst in recipe_data.instructions]
    
    recipe = UserRecipeRepository.create_user_recipe(user_id, data)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recipe"
        )
    
    return recipe


@router.patch("/{recipe_id}", response_model=UserRecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    update_data: UserRecipeUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing user recipe"""
    user_id = current_user["sub"]
    
    # Check if recipe exists
    existing = UserRecipeRepository.get_user_recipe_by_id(user_id, str(recipe_id))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Convert Pydantic model to dict, excluding None values
    data = update_data.model_dump(exclude_unset=True)
    
    # Convert nested models to dicts if present
    if "ingredients" in data and data["ingredients"] is not None:
        data["ingredients"] = [
            ing if isinstance(ing, dict) else ing.model_dump() 
            for ing in update_data.ingredients
        ]
    if "instructions" in data and data["instructions"] is not None:
        data["instructions"] = [
            inst if isinstance(inst, dict) else inst.model_dump() 
            for inst in update_data.instructions
        ]
    
    recipe = UserRecipeRepository.update_user_recipe(user_id, str(recipe_id), data)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recipe"
        )
    
    return recipe


@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete a user recipe"""
    user_id = current_user["sub"]
    
    success = UserRecipeRepository.delete_user_recipe(user_id, str(recipe_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return {"message": "Recipe deleted successfully"}


@router.patch("/{recipe_id}/toggle-favorite")
async def toggle_favorite(
    recipe_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Toggle favorite status of a recipe"""
    user_id = current_user["sub"]
    
    result = UserRecipeRepository.toggle_favorite(user_id, str(recipe_id))
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return {
        "message": "Favorite toggled",
        "recipe_id": result["id"],
        "is_favorite": result["is_favorite"]
    }


@router.post("/copy-from-public/{recipe_id}", response_model=UserRecipeResponse)
async def copy_public_recipe(
    recipe_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Copy a public recipe to user's private recipes
    
    This allows users to save public recipes and customize them.
    The original recipe ID is stored for reference.
    """
    user_id = current_user["sub"]
    
    recipe = UserRecipeRepository.copy_from_public_recipe(user_id, str(recipe_id))
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public recipe not found"
        )
    
    return recipe
