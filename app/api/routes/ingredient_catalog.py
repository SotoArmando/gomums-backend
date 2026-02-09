from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from app.models.ingredient_catalog import (
    IngredientCatalogCreate,
    IngredientCatalogUpdate,
    IngredientCatalogResponse,
    IngredientCatalogBulkCreate,
    IngredientCatalogListResponse,
    RegionSummary,
)
from app.db.repositories.ingredient_catalog_repository import IngredientCatalogRepository

router = APIRouter()


# ==================== List regions ====================

@router.get("/regions", response_model=List[RegionSummary])
def list_regions():
    """Get all regions that have ingredient data, with counts and categories"""
    return IngredientCatalogRepository.get_all_regions()


# ==================== List categories ====================

@router.get("/categories", response_model=List[str])
def list_categories(
    region: Optional[str] = Query(None, description="Filter categories by region"),
):
    """Get all ingredient categories, optionally filtered by region"""
    return IngredientCatalogRepository.get_categories(region)


# ==================== Search ingredients ====================

@router.get("/search", response_model=List[IngredientCatalogResponse])
def search_ingredients(
    q: str = Query(..., min_length=1, description="Search query"),
    region: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(50, ge=1, le=200),
):
    """Search ingredients by name (English or local) across all regions"""
    return IngredientCatalogRepository.search(q, region=region, limit=limit)


# ==================== Get ingredients by region ====================

@router.get("/{region}", response_model=IngredientCatalogListResponse)
def get_ingredients_by_region(
    region: str,
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search within region"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get all ingredients for a specific region with optional filtering"""
    items = IngredientCatalogRepository.get_by_region(
        region=region, category=category, search=search, limit=limit, offset=offset
    )
    total = IngredientCatalogRepository.count_by_region(
        region=region, category=category, search=search
    )
    return IngredientCatalogListResponse(
        items=items, total=total, region=region, category=category
    )


# ==================== Get single ingredient ====================

@router.get("/item/{ingredient_id}", response_model=IngredientCatalogResponse)
def get_ingredient(ingredient_id: str):
    """Get a single ingredient by ID"""
    result = IngredientCatalogRepository.get_by_id(ingredient_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return result


# ==================== Create single ingredient ====================

@router.post(
    "/",
    response_model=IngredientCatalogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ingredient(data: IngredientCatalogCreate):
    """Create a single ingredient catalog entry (upserts on name+region)"""
    result = IngredientCatalogRepository.create(data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create ingredient")
    return result


# ==================== Bulk create ====================

@router.post(
    "/bulk",
    response_model=List[IngredientCatalogResponse],
    status_code=status.HTTP_201_CREATED,
)
def bulk_create_ingredients(payload: IngredientCatalogBulkCreate):
    """
    Bulk-create ingredient catalog entries for a region.
    Upserts on name+region (updates if already exists).
    """
    ingredients_data = [ing.model_dump() for ing in payload.ingredients]
    # Ensure every ingredient carries the region and currency
    for ing in ingredients_data:
        ing["region"] = payload.region
        ing["currency"] = payload.currency
        ing["language"] = payload.language

    results = IngredientCatalogRepository.bulk_create(ingredients_data)
    if not results:
        raise HTTPException(status_code=500, detail="Failed to create ingredients")
    return results


# ==================== Update ingredient ====================

@router.patch("/item/{ingredient_id}", response_model=IngredientCatalogResponse)
def update_ingredient(ingredient_id: str, data: IngredientCatalogUpdate):
    """Update an ingredient catalog entry"""
    existing = IngredientCatalogRepository.get_by_id(ingredient_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    result = IngredientCatalogRepository.update(
        ingredient_id, data.model_dump(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update ingredient")
    return result


# ==================== Delete single ingredient ====================

@router.delete("/item/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: str):
    """Delete a single ingredient catalog entry"""
    deleted = IngredientCatalogRepository.delete(ingredient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ingredient not found")


# ==================== Delete all ingredients for a region ====================

@router.delete("/{region}")
def delete_region_ingredients(region: str):
    """Delete all ingredients for a region"""
    count = IngredientCatalogRepository.delete_by_region(region)
    return {"deleted": count, "region": region}
