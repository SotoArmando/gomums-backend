"""
Meal Planning Routes
Endpoints for meal plans, planned meals, and shopping lists
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date

from app.models.meal_plan import (
    MealPlanResponse,
    MealPlanSummary,
    MealPlanCreate,
    MealPlanUpdate,
    PlannedMealResponse,
    PlannedMealCreate,
    PlannedMealUpdate,
    ShoppingListItemResponse,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    BulkUpdateShoppingList,
    WeeklyCalendar,
    QuickMealPlanCreate
)
from app.db.repositories.meal_plan_repository import MealPlanRepository
from app.core.security import get_current_user_id


router = APIRouter(prefix="/meal-plans", tags=["Meal Planning"])


# ==================== Meal Plan Endpoints ====================

@router.post("/", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
def create_meal_plan(
    meal_plan_data: MealPlanCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new meal plan
    
    Request body:
    - name: Meal plan name (e.g., "Week of Feb 8")
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - status: Optional status (draft, active, completed) - defaults to 'draft'
    
    Returns:
    - Created meal plan with ID
    
    Use for:
    - Weekly meal planning
    - Monthly meal planning
    - Event-specific planning
    """
    data = meal_plan_data.model_dump()
    meal_plan = MealPlanRepository.create_meal_plan(current_user_id, data)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create meal plan"
        )
    
    return meal_plan


@router.post("/quick", response_model=MealPlanSummary, status_code=status.HTTP_201_CREATED)
def quick_create_meal_plan(
    quick_data: QuickMealPlanCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Quick create meal plan with optional pre-populated meals
    
    Request body:
    - name: Meal plan name
    - start_date: Start date
    - end_date: End date
    - planned_meals: Optional list of meals to pre-populate
    
    Returns:
    - Created meal plan with all planned meals
    
    Use for:
    - Creating a week plan with meals in one request
    - Bulk meal planning
    """
    # Create meal plan
    meal_plan_data = {
        'name': quick_data.name,
        'start_date': quick_data.start_date,
        'end_date': quick_data.end_date,
        'status': 'draft'
    }
    
    meal_plan = MealPlanRepository.create_meal_plan(current_user_id, meal_plan_data)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create meal plan"
        )
    
    # Add planned meals if provided
    planned_meals = []
    for meal_data in quick_data.planned_meals:
        meal = MealPlanRepository.create_planned_meal(
            meal_plan_id=meal_plan['id'],
            user_id=current_user_id,
            meal_data=meal_data.model_dump()
        )
        if meal:
            planned_meals.append(meal)
    
    meal_plan['planned_meals'] = planned_meals
    meal_plan['shopping_list_items'] = []
    
    return meal_plan


@router.post("/add-to-date", response_model=PlannedMealResponse, status_code=status.HTTP_201_CREATED)
def add_meal_to_date(
    meal_data: PlannedMealCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add a planned meal to a specific date (auto-creates weekly meal plan if needed)
    
    This is a convenience endpoint for the Calendar Strip + Today's Plan workflow.
    Just provide the date and meal details - the system will automatically:
    1. Find or create the meal plan for that week
    2. Add the recipe to the specified date
    
    Request body:
    - date: Date from the calendar strip (YYYY-MM-DD)
    - meal_type: Type (breakfast, lunch, dinner, snack)
    - recipe_name: Name of the recipe/meal
    - recipe_id: Optional recipe ID if using existing recipe
    - servings: Number of servings (default: 1)
    - is_batch: Is this batch cooking? (default: false)
    - is_leftovers: Is this using leftovers? (default: false)
    
    Returns:
    - Created planned meal bound to the selected date
    
    Example:
    ```json
    {
        "date": "2026-02-10",
        "meal_type": "dinner",
        "recipe_name": "Apple Chicken",
        "recipe_id": "abc-123"
    }
    ```
    """
    # Get or create meal plan for the week containing this date
    meal_plan = MealPlanRepository.get_meal_plan_for_week(current_user_id, meal_data.date)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create meal plan for the specified week"
        )
    
    # Add the planned meal to this date
    meal = MealPlanRepository.create_planned_meal(
        meal_plan_id=meal_plan['id'],
        user_id=current_user_id,
        meal_data=meal_data.model_dump()
    )
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add meal to the date"
        )
    
    return meal


@router.get("/", response_model=List[MealPlanResponse])
def get_meal_plans(
    status_filter: Optional[str] = Query(None, pattern="^(draft|active|completed)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all meal plans for current user
    
    Query params:
    - status: Optional filter (draft, active, completed)
    - limit: Max results (1-100, default: 20)
    - offset: Pagination offset (default: 0)
    
    Returns:
    - List of meal plans with counts (total_meals, shopping items, etc.)
    - Ordered by start date (newest first)
    
    Use for:
    - Viewing all meal plans
    - Filtering by status
    - Pagination
    """
    meal_plans = MealPlanRepository.get_user_meal_plans(
        user_id=current_user_id,
        status=status_filter,
        limit=limit,
        offset=offset
    )
    
    return meal_plans


@router.get("/current", response_model=MealPlanSummary)
def get_current_week_meal_plan(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get or create meal plan for the current week
    
    Returns:
    - Meal plan for current week (Monday-Sunday)
    - If no plan exists for this week, creates one automatically
    - Includes planned_meals and shopping_list_items
    
    Use for:
    - Home screen "This Week's Meal Plan" section
    - Quick access to current week without knowing meal_plan_id
    - Auto-creating new weeks as needed
    """
    meal_plan = MealPlanRepository.get_current_week_meal_plan(current_user_id)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create current week meal plan"
        )
    
    return meal_plan


@router.get("/week", response_model=MealPlanSummary)
def get_meal_plan_for_week(
    date_param: date = Query(..., alias="date", description="Any date within the target week (YYYY-MM-DD)"),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get or create meal plan for a specific week
    
    Query params:
    - date: Any date within the target week (e.g., "2026-02-10")
    
    Returns:
    - Meal plan for the week containing the given date (Monday-Sunday)
    - If no plan exists for that week, creates one automatically
    - Includes planned_meals and shopping_list_items
    
    Use for:
    - Planning view week navigation
    - Getting next/previous week's meal plan
    - Creating meal plans for future weeks
    """
    meal_plan = MealPlanRepository.get_meal_plan_for_week(current_user_id, date_param)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create meal plan for the specified week"
        )
    
    return meal_plan


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
def get_meal_plan(
    meal_plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get specific meal plan by ID
    
    Returns:
    - Meal plan with counts
    
    Use for:
    - Viewing meal plan summary
    - Checking meal plan status
    """
    meal_plan = MealPlanRepository.get_meal_plan(meal_plan_id, current_user_id)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal_plan


@router.get("/{meal_plan_id}/details", response_model=MealPlanSummary)
def get_meal_plan_details(
    meal_plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get meal plan with all planned meals and shopping list
    
    Returns:
    - Complete meal plan with:
      - All planned meals
      - All shopping list items
      - Meal plan metadata
    
    Use for:
    - Full meal plan view
    - Editing meal plan
    - Viewing complete week
    """
    meal_plan = MealPlanRepository.get_meal_plan_with_details(meal_plan_id, current_user_id)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal_plan


@router.get("/{meal_plan_id}/calendar", response_model=WeeklyCalendar)
def get_calendar_view(
    meal_plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get calendar view of meal plan (organized by day)
    
    Returns:
    - Calendar structure with days array
    - Each day has: date, breakfast, lunch, dinner, snacks[]
    - All days in date range included (even if no meals)
    
    Use for:
    - Visual calendar display
    - Week-at-a-glance view
    - Drag-and-drop meal planning UI
    """
    calendar = MealPlanRepository.get_calendar_view(meal_plan_id, current_user_id)
    
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return calendar


@router.patch("/{meal_plan_id}", response_model=MealPlanResponse)
def update_meal_plan(
    meal_plan_id: str,
    updates: MealPlanUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update meal plan
    
    Request body (all optional):
    - name: Update name
    - start_date: Update start date
    - end_date: Update end date
    - total_cost: Update total cost
    - status: Update status (draft, active, completed)
    
    Returns:
    - Updated meal plan
    """
    data = updates.model_dump(exclude_unset=True)
    
    meal_plan = MealPlanRepository.update_meal_plan(
        meal_plan_id=meal_plan_id,
        user_id=current_user_id,
        updates=data
    )
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal_plan


@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_plan(
    meal_plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete meal plan
    
    This will also delete:
    - All planned meals in the meal plan
    - All shopping list items for the meal plan
    
    Use with caution - this action cannot be undone!
    """
    success = MealPlanRepository.delete_meal_plan(meal_plan_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return None


# ==================== Planned Meal Endpoints ====================

@router.post("/{meal_plan_id}/meals", response_model=PlannedMealResponse, status_code=status.HTTP_201_CREATED)
def add_planned_meal(
    meal_plan_id: str,
    meal_data: PlannedMealCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add a planned meal to a meal plan
    
    Request body:
    - date: Date of the meal (YYYY-MM-DD)
    - meal_type: Type (breakfast, lunch, dinner, snack)
    - recipe_name: Name of the recipe/meal
    - recipe_id: Optional recipe ID if using existing recipe
    - servings: Number of servings (default: 1)
    - is_batch: Is this batch cooking? (default: false)
    - is_leftovers: Is this using leftovers? (default: false)
    
    Returns:
    - Created planned meal
    """
    data = meal_data.model_dump()
    
    meal = MealPlanRepository.create_planned_meal(
        meal_plan_id=meal_plan_id,
        user_id=current_user_id,
        meal_data=data
    )
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal


@router.get("/{meal_plan_id}/meals", response_model=List[PlannedMealResponse])
def get_planned_meals(
    meal_plan_id: str,
    date_filter: Optional[date] = Query(None),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get planned meals for a meal plan
    
    Query params:
    - date: Optional filter by specific date (YYYY-MM-DD)
    
    Returns:
    - List of planned meals
    - Ordered by date, then meal type (breakfast, lunch, dinner, snack)
    
    Use for:
    - Viewing all meals in plan
    - Filtering meals by date
    """
    meals = MealPlanRepository.get_planned_meals(
        meal_plan_id=meal_plan_id,
        user_id=current_user_id,
        date_filter=date_filter
    )
    
    return meals


@router.patch("/meals/{planned_meal_id}", response_model=PlannedMealResponse)
def update_planned_meal(
    planned_meal_id: str,
    updates: PlannedMealUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a planned meal
    
    Request body (all optional):
    - date: Update date
    - meal_type: Update meal type
    - recipe_id: Update recipe ID
    - recipe_name: Update recipe name
    - servings: Update servings
    - is_batch: Update batch flag
    - is_leftovers: Update leftovers flag
    
    Returns:
    - Updated planned meal
    """
    data = updates.model_dump(exclude_unset=True)
    
    meal = MealPlanRepository.update_planned_meal(
        planned_meal_id=planned_meal_id,
        user_id=current_user_id,
        updates=data
    )
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned meal not found"
        )
    
    return meal


@router.delete("/meals/{planned_meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planned_meal(
    planned_meal_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a planned meal
    
    Removes the meal from the meal plan.
    This does not delete the recipe, only the plan to make it.
    """
    success = MealPlanRepository.delete_planned_meal(planned_meal_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned meal not found"
        )
    
    return None


# ==================== Shopping List Endpoints ====================

@router.post("/{meal_plan_id}/shopping", response_model=ShoppingListItemResponse, status_code=status.HTTP_201_CREATED)
def add_shopping_item(
    meal_plan_id: str,
    item_data: ShoppingListItemCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add an item to shopping list
    
    Request body:
    - name: Item name (e.g., "Chicken breast")
    - quantity: Optional quantity (e.g., "2 lbs", "3 cups")
    - category: Optional category (e.g., "Protein", "Produce")
    - estimated_cost: Optional estimated cost
    - related_recipes: Optional list of recipe IDs that need this item
    
    Returns:
    - Created shopping list item
    """
    data = item_data.model_dump()
    
    item = MealPlanRepository.create_shopping_list_item(
        meal_plan_id=meal_plan_id,
        user_id=current_user_id,
        item_data=data
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return item


@router.get("/{meal_plan_id}/shopping", response_model=List[ShoppingListItemResponse])
def get_shopping_list(
    meal_plan_id: str,
    purchased: Optional[bool] = Query(None),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get shopping list for a meal plan
    
    Query params:
    - purchased: Optional filter by purchased status (true/false)
    
    Returns:
    - List of shopping list items
    - Ordered by purchased status, then category, then name
    
    Use for:
    - Displaying shopping list
    - Filtering purchased/unpurchased items
    - Grocery shopping
    """
    items = MealPlanRepository.get_shopping_list_items(
        meal_plan_id=meal_plan_id,
        user_id=current_user_id,
        purchased_filter=purchased
    )
    
    return items


@router.patch("/shopping/{item_id}", response_model=ShoppingListItemResponse)
def update_shopping_item(
    item_id: str,
    updates: ShoppingListItemUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a shopping list item
    
    Request body (all optional):
    - name: Update name
    - quantity: Update quantity
    - category: Update category
    - purchased: Mark as purchased/not purchased
    - estimated_cost: Update cost
    - related_recipes: Update related recipes
    
    Returns:
    - Updated shopping list item
    
    Common use:
    - Mark items as purchased while shopping
    - Update quantities or costs
    """
    data = updates.model_dump(exclude_unset=True)
    
    item = MealPlanRepository.update_shopping_list_item(
        item_id=item_id,
        user_id=current_user_id,
        updates=data
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found"
        )
    
    return item


@router.post("/shopping/bulk-update", response_model=dict)
def bulk_update_shopping_items(
    bulk_data: BulkUpdateShoppingList,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Bulk update shopping list items (mark multiple as purchased)
    
    Request body:
    - item_ids: Array of shopping list item IDs
    - purchased: Mark as purchased (true) or not purchased (false)
    
    Returns:
    - Number of items updated
    
    Use for:
    - Marking all items as purchased after shopping
    - Bulk operations
    - "Mark all as purchased" feature
    """
    count = MealPlanRepository.bulk_update_shopping_items(
        item_ids=bulk_data.item_ids,
        user_id=current_user_id,
        purchased=bulk_data.purchased
    )
    
    return {
        "success": True,
        "updated_count": count,
        "message": f"Updated {count} shopping list items"
    }


@router.delete("/shopping/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a shopping list item
    
    Removes the item from the shopping list.
    """
    success = MealPlanRepository.delete_shopping_list_item(item_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found"
        )
    
    return None


# ==================== Helper Endpoints ====================

@router.post("/{meal_plan_id}/calculate-cost", response_model=dict)
def calculate_total_cost(
    meal_plan_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Calculate total cost from shopping list
    
    Sums all estimated_cost values from shopping list items
    and updates the meal plan's total_cost field.
    
    Returns:
    - Updated total cost
    
    Use for:
    - Budget tracking
    - Cost estimation
    - After adding/updating shopping items
    """
    total_cost = MealPlanRepository.calculate_total_cost(meal_plan_id, current_user_id)
    
    if total_cost is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return {
        "success": True,
        "meal_plan_id": meal_plan_id,
        "total_cost": float(total_cost),
        "message": f"Total cost calculated: ${total_cost}"
    }
