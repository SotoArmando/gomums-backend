from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List, Dict, Any
from datetime import date

from app.models.budget import (
    BudgetEntryCreate, BudgetEntryUpdate, BudgetEntryResponse,
    BudgetStats, CategoryBreakdown, BudgetSettingsCreate, BudgetSettingsResponse
)
from app.db.repositories.budget_repository import BudgetRepository
from app.core.security import get_current_user


router = APIRouter()


@router.get("/stats", response_model=BudgetStats)
def get_budget_stats(
    period: str = Query("week", pattern="^(week|month|year)$"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive budget statistics
    
    Query Parameters:
    - period: week/month/year (default: week)
    
    Returns:
    - Budget statistics including score, averages, and savings
    """
    stats = BudgetRepository.get_stats(current_user["id"], period)
    return stats


@router.get("/entries", response_model=List[BudgetEntryResponse])
def get_budget_entries(
    from_date: Optional[date] = Query(None, description="Filter entries from this date (inclusive)"),
    to_date: Optional[date] = Query(None, description="Filter entries until this date (inclusive)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entries to return"),
    offset: int = Query(0, ge=0, description="Number of entries to skip for pagination"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all budget entries with optional filters
    
    Query Parameters:
    - from_date: Start date filter (YYYY-MM-DD)
    - to_date: End date filter (YYYY-MM-DD)
    - category: Filter by category name
    - limit: Max results (1-100, default 50)
    - offset: Pagination offset (default 0)
    
    Returns:
    - List of budget entries
    """
    entries = BudgetRepository.get_entries(
        user_id=current_user["id"],
        from_date=from_date,
        to_date=to_date,
        category=category,
        limit=limit,
        offset=offset
    )
    return entries


@router.get("/entries/{entry_id}", response_model=BudgetEntryResponse)
def get_budget_entry(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a single budget entry by ID
    
    Path Parameters:
    - entry_id: Budget entry UUID
    
    Returns:
    - Budget entry details
    """
    entry = BudgetRepository.get_entry_by_id(entry_id, current_user["id"])
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget entry not found"
        )
    
    return entry


@router.post("/entries", response_model=BudgetEntryResponse, status_code=status.HTTP_201_CREATED)
def create_budget_entry(
    entry: BudgetEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new budget entry
    
    Request Body:
    - date: Entry date (YYYY-MM-DD)
    - meal_name: Name of the meal
    - cost: Total cost in dollars
    - servings: Number of servings
    - category: Optional category (e.g., "Breakfast", "Lunch", "Dinner", "Snack")
    - notes: Optional notes
    - journal_entry_id: Optional link to journal entry
    
    Returns:
    - Created budget entry with calculated cost_per_serving
    """
    entry_data = entry.model_dump()
    created_entry = BudgetRepository.create_entry(current_user["id"], entry_data)
    
    if not created_entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create budget entry"
        )
    
    return created_entry


@router.patch("/entries/{entry_id}", response_model=BudgetEntryResponse)
def update_budget_entry(
    entry_id: str,
    entry: BudgetEntryUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an existing budget entry
    
    Path Parameters:
    - entry_id: Budget entry UUID
    
    Request Body (all fields optional):
    - date: Entry date
    - meal_name: Name of the meal
    - cost: Total cost
    - servings: Number of servings
    - category: Category
    - notes: Notes
    
    Returns:
    - Updated budget entry
    """
    # Filter out None values
    update_data = entry.model_dump(exclude_unset=True)
    
    updated_entry = BudgetRepository.update_entry(entry_id, current_user["id"], update_data)
    
    if not updated_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget entry not found"
        )
    
    return updated_entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget_entry(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a budget entry
    
    Path Parameters:
    - entry_id: Budget entry UUID
    
    Returns:
    - 204 No Content on success
    """
    deleted = BudgetRepository.delete_entry(entry_id, current_user["id"])
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget entry not found"
        )
    
    return None


@router.get("/category-breakdown", response_model=CategoryBreakdown)
def get_category_breakdown(
    period: str = Query("week", pattern="^(week|month|year)$"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get spending breakdown by category
    
    Query Parameters:
    - period: week/month/year (default: week)
    
    Returns:
    - Dictionary with category names as keys and total spending as values
    - Total field with sum of all categories
    """
    breakdown = BudgetRepository.get_category_breakdown(current_user["id"], period)
    
    total = sum(breakdown.values())
    
    return {
        "breakdown": breakdown,
        "total": round(total, 2)
    }
    
    return {
        "categories": breakdown,
        "total": round(total, 2)
    }


@router.get("/settings", response_model=BudgetSettingsResponse)
def get_budget_settings(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's budget settings
    
    Returns:
    - Budget settings including weekly/monthly budgets
    """
    settings = BudgetRepository.get_budget_settings(current_user["id"])
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget settings not found. Create settings first."
        )
    
    return settings


@router.post("/settings", response_model=BudgetSettingsResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget_settings(
    settings: BudgetSettingsCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create or update budget settings
    
    Request Body:
    - weekly_budget: Optional weekly budget limit
    - monthly_budget: Optional monthly budget limit
    
    Returns:
    - Created or updated budget settings
    """
    settings_data = settings.model_dump()
    upserted_settings = BudgetRepository.upsert_budget_settings(current_user["id"], settings_data)
    
    if not upserted_settings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save budget settings"
        )
    
    return upserted_settings
