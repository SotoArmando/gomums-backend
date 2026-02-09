from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Dict, Any

from app.models.saved_price import (
    SavedIngredientPriceCreate,
    SavedIngredientPriceUpdate,
    SavedIngredientPriceResponse,
    SavedIngredientPriceBulkCreate,
    RecipePriceSummary,
)
from app.db.repositories.saved_price_repository import SavedPriceRepository
from app.core.security import get_current_user

router = APIRouter()


# ==================== Bulk save (primary flow) ====================

@router.post(
    "/recipes",
    response_model=List[SavedIngredientPriceResponse],
    status_code=status.HTTP_201_CREATED,
)
def bulk_save_ingredient_prices(
    payload: SavedIngredientPriceBulkCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Bulk-save ingredient prices for a recipe from Price Compare.
    Replaces any previously saved prices for the same recipe.

    Request Body:
    - recipe_name: Name of the recipe
    - ingredients: List of ingredient price objects
    """
    ingredients_data = [ing.model_dump() for ing in payload.ingredients]
    # Ensure every ingredient carries the recipe_name
    for ing in ingredients_data:
        ing["recipe_name"] = payload.recipe_name

    results = SavedPriceRepository.bulk_create(
        user_id=current_user["id"],
        recipe_name=payload.recipe_name,
        ingredients=ingredients_data,
    )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save ingredient prices",
        )

    return results


# ==================== Single create ====================

@router.post(
    "/",
    response_model=SavedIngredientPriceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_saved_price(
    data: SavedIngredientPriceCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Create a single saved ingredient price entry"""
    result = SavedPriceRepository.create(current_user["id"], data.model_dump())

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save ingredient price",
        )

    return result


# ==================== List recipes with saved prices ====================

@router.get("/recipes", response_model=List[str])
def list_saved_recipes(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get all recipe names that have saved ingredient prices"""
    return SavedPriceRepository.get_all_recipes(current_user["id"])


# ==================== Get prices for a recipe ====================

@router.get("/recipes/{recipe_name}", response_model=List[SavedIngredientPriceResponse])
def get_saved_prices_for_recipe(
    recipe_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get all saved ingredient prices for a specific recipe"""
    return SavedPriceRepository.get_by_recipe(current_user["id"], recipe_name)


# ==================== Recipe price summary ====================

@router.get("/recipes/{recipe_name}/summary", response_model=RecipePriceSummary)
def get_recipe_price_summary(
    recipe_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get a price summary for a saved recipe (totals, savings, counts)"""
    summary = SavedPriceRepository.get_recipe_summary(current_user["id"], recipe_name)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No saved prices found for this recipe",
        )

    return summary


# ==================== Get single price ====================

@router.get("/{price_id}", response_model=SavedIngredientPriceResponse)
def get_saved_price(
    price_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get a single saved ingredient price by ID"""
    result = SavedPriceRepository.get_by_id(price_id, current_user["id"])

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved ingredient price not found",
        )

    return result


# ==================== Update price ====================

@router.patch("/{price_id}", response_model=SavedIngredientPriceResponse)
def update_saved_price(
    price_id: str,
    data: SavedIngredientPriceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update a saved ingredient price"""
    existing = SavedPriceRepository.get_by_id(price_id, current_user["id"])
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved ingredient price not found",
        )

    result = SavedPriceRepository.update(
        price_id, current_user["id"], data.model_dump(exclude_unset=True)
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ingredient price",
        )

    return result


# ==================== Delete single price ====================

@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_price(
    price_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete a single saved ingredient price"""
    deleted = SavedPriceRepository.delete(price_id, current_user["id"])

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved ingredient price not found",
        )


# ==================== Delete all prices for a recipe ====================

@router.delete("/recipes/{recipe_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_prices_for_recipe(
    recipe_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete all saved ingredient prices for a specific recipe"""
    deleted = SavedPriceRepository.delete_by_recipe(current_user["id"], recipe_name)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No saved prices found for this recipe",
        )
