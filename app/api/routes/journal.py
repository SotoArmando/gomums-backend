from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List, Union
from datetime import datetime

from app.models.journal import (
    JournalEntryCreate,
    MealResponse,
    PurchaseResponse,
    MealUpdate,
    PurchaseUpdate,
    LinkPurchaseRequest
)
from app.db.repositories.journal_repository import JournalRepository
from app.db.repositories.user_stats_repository import UserStatsRepository
from app.db.repositories.achievement_repository import AchievementRepository
from app.services.challenge_service import ChallengeService
from app.core.security import get_current_user_id


router = APIRouter()


# ==================== Get All Entries ====================

@router.get("/entries", response_model=List[Union[MealResponse, PurchaseResponse]])
def get_journal_entries(
    type: Optional[str] = Query(None, pattern="^(meal|purchase)$"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all journal entries (meals + purchases) for current user
    
    Query Parameters:
    - type: Filter by 'meal' or 'purchase'
    - from: ISO date - start date filter
    - to: ISO date - end date filter
    - limit: Maximum number of results (1-100, default: 50)
    - offset: Offset for pagination
    
    Returns:
    - List of journal entries (meals and purchases)
    """
    entries = JournalRepository.get_entries(
        user_id=user_id,
        entry_type=type,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset
    )
    
    return entries


# ==================== Get Single Entry ====================

@router.get("/entries/{entry_id}", response_model=Union[MealResponse, PurchaseResponse])
def get_journal_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a single journal entry by ID
    
    Returns:
    - Journal entry (meal or purchase)
    
    Raises:
    - 404: Entry not found
    """
    entry = JournalRepository.get_entry_by_id(entry_id, user_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return entry


# ==================== Create Entry ====================

@router.post("/entries", response_model=Union[MealResponse, PurchaseResponse], status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    entry_data: JournalEntryCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new journal entry (meal or purchase)
    
    Request Body (Meal):
    - type: "meal"
    - title: Meal name
    - meal_type: "breakfast", "lunch", "dinner", or "snack"
    - portions: Number of portions
    - portions_left: (optional) Portions remaining
    - status: (optional) "fresh", "leftovers", "frozen", or "completed"
    - ingredients_used: (optional) List of ingredient names
    - is_batch: (optional) Batch cooking indicator
    - used_leftovers: (optional) Made from leftovers
    - needs_restock: (optional) Ingredients need restocking
    - purchase_id: (optional) Linked purchase ID
    - timestamp: (optional) Custom timestamp
    
    Request Body (Purchase):
    - type: "purchase"
    - title: Purchase description
    - store: Store name
    - items: List of purchased items [{name, quantity, cost, category}]
    - timestamp: (optional) Custom timestamp
    
    Returns:
    - Created journal entry
    
    Raises:
    - 400: Invalid entry data
    - 422: Validation error
    """
    # Validate type-specific required fields
    if entry_data.type == "meal":
        if not entry_data.meal_type or not entry_data.portions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="meal_type and portions are required for meal entries"
            )
    elif entry_data.type == "purchase":
        if not entry_data.store or not entry_data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="store and items are required for purchase entries"
            )
    
    # Convert Pydantic model to dict
    entry_dict = entry_data.model_dump(exclude_unset=True)
    
    # Create entry
    entry = JournalRepository.create_entry(user_id, entry_dict)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create journal entry"
        )
    
    # Update challenge goals based on journal entry
    try:
        if entry_data.type == "meal":
            challenge_result = ChallengeService.update_challenges_on_journal_entry(
                user_id=user_id,
                entry_type=entry_data.type,
                meal_type=entry_data.meal_type,
                portions=entry_data.portions,
                status=entry_data.status,
                used_leftovers=entry_data.used_leftovers or False,
                is_batch=entry_data.is_batch or False,
                recipe_name=entry_data.title,
                ingredient_swaps=entry_data.ingredient_swaps,
                timestamp=entry_data.timestamp.isoformat() if entry_data.timestamp else None
            )
        elif entry_data.type == "purchase":
            challenge_result = ChallengeService.update_challenges_on_journal_entry(
                user_id=user_id,
                entry_type=entry_data.type,
                ingredient_swaps=entry_data.ingredient_swaps,
                timestamp=entry_data.timestamp.isoformat() if entry_data.timestamp else None
            )
        
        # Log completed challenges
        if challenge_result.get('completed_challenges'):
            for completed in challenge_result['completed_challenges']:
                print(f"🏆 Challenge completed! User: {user_id}, Challenge: {completed['user_challenge_id']}, Points: {completed['points_awarded']}")
        
        # Log updated goals
        if challenge_result.get('updated_goals'):
            for goal in challenge_result['updated_goals']:
                print(f"🎯 Goal updated! Progress: {goal.get('progress')}/{goal.get('target')}")
                
    except Exception as e:
        # Don't fail the journal entry creation if challenge update fails
        print(f"Error updating challenges: {e}")
    
    # Update user stats based on journal entry
    try:
        if entry_data.type == "meal":
            # Calculate money saved vs eating out
            # Estimate: $12 per meal portion at a restaurant
            avg_restaurant_cost_per_portion = 12.0
            estimated_savings = avg_restaurant_cost_per_portion * (entry_data.portions or 1)
            
            # Award points for cooking
            # 10 points per meal
            points_awarded = 10
            
            # Bonus points for batch cooking (20 instead of 10)
            if entry_data.is_batch:
                points_awarded = 20
            
            # Bonus points for using leftovers (15 instead of 10)
            if entry_data.used_leftovers:
                points_awarded = 15
            
            # Update stats - this also handles streak calculation
            UserStatsRepository.increment_stats(
                user_id=user_id,
                meals_cooked=1,
                money_saved=estimated_savings,
                points=points_awarded
            )
            
            print(f"📊 Stats updated! User: {user_id}, Meals: +1, Savings: ${estimated_savings:.2f}, Points: +{points_awarded}")
            
    except Exception as e:
        # Don't fail the journal entry creation if stats update fails
        print(f"Error updating user stats: {e}")
    
    # Check and unlock eligible achievements
    try:
        if entry_data.type == "meal":
            # Get updated stats after increment
            updated_stats = UserStatsRepository.get_or_create_stats(user_id)
            
            # Check for any newly unlocked achievements
            newly_unlocked = AchievementRepository.check_and_unlock_achievements(
                user_id=user_id,
                stats=updated_stats
            )
            
            # Award points for newly unlocked achievements
            if newly_unlocked:
                total_points = sum(a['points'] for a in newly_unlocked)
                UserStatsRepository.increment_stats(
                    user_id=user_id,
                    meals_cooked=0,
                    money_saved=0,
                    points=total_points
                )
                
                # Increment achievements counter
                for _ in newly_unlocked:
                    UserStatsRepository.increment_achievements_count(user_id)
                
                for unlock in newly_unlocked:
                    print(f"🏆 Achievement unlocked! User: {user_id}, Achievement: {unlock['title']}, Points: +{unlock['points']}")
    except Exception as e:
        # Don't fail the journal entry creation if achievement check fails
        print(f"Error checking achievements: {e}")
    
    return entry


# ==================== Update Entry ====================

@router.patch("/entries/{entry_id}", response_model=Union[MealResponse, PurchaseResponse])
def update_journal_entry(
    entry_id: str,
    entry_data: Union[MealUpdate, PurchaseUpdate],
    user_id: str = Depends(get_current_user_id)
):
    """
    Update an existing journal entry
    
    Request Body (Meal):
    - title: (optional) Update meal name
    - portions_left: (optional) Update portions remaining
    - status: (optional) Update status
    - needs_restock: (optional) Update restock flag
    
    Request Body (Purchase):
    - title: (optional) Update purchase description
    - store: (optional) Update store name
    - items: (optional) Update items list
    
    Returns:
    - Updated journal entry
    
    Raises:
    - 404: Entry not found
    """
    update_dict = entry_data.model_dump(exclude_unset=True)
    
    entry = JournalRepository.update_entry(entry_id, user_id, update_dict)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return entry


# ==================== Delete Entry ====================

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a journal entry
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Entry not found
    """
    success = JournalRepository.delete_entry(entry_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    
    return None


# ==================== Get Meals Only ====================

@router.get("/meals", response_model=List[MealResponse])
def get_meals(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get only meal entries (shortcut for /entries?type=meal)
    
    Returns:
    - List of meal entries
    """
    entries = JournalRepository.get_entries(
        user_id=user_id,
        entry_type="meal",
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset
    )
    
    return entries


# ==================== Get Purchases Only ====================

@router.get("/purchases", response_model=List[PurchaseResponse])
def get_purchases(
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get only purchase entries (shortcut for /entries?type=purchase)
    
    Returns:
    - List of purchase entries
    """
    entries = JournalRepository.get_entries(
        user_id=user_id,
        entry_type="purchase",
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset
    )
    
    return entries


# ==================== Link Meal to Purchase ====================

@router.post("/meals/{meal_id}/link-purchase", response_model=MealResponse)
def link_meal_to_purchase(
    meal_id: str,
    link_data: LinkPurchaseRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Link a meal to a purchase with matched ingredients
    
    Request Body:
    - purchase_id: UUID of the purchase to link
    - ingredients_used: List of ingredient names that match
    
    Returns:
    - Updated meal entry with linked purchase
    
    Raises:
    - 404: Meal not found
    """
    # Verify meal exists and is owned by user
    meal = JournalRepository.get_entry_by_id(meal_id, user_id)
    if not meal or meal.get("type") != "meal":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Verify purchase exists and is owned by user
    purchase = JournalRepository.get_entry_by_id(link_data.purchase_id, user_id)
    if not purchase or purchase.get("type") != "purchase":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found"
        )
    
    # Link meal to purchase
    updated_meal = JournalRepository.link_meal_to_purchase(
        meal_id=meal_id,
        purchase_id=link_data.purchase_id,
        user_id=user_id,
        ingredients_matched=link_data.ingredients_used
    )
    
    if not updated_meal:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link meal to purchase"
        )
    
    return updated_meal
