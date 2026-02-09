"""
Smart Suggestions API Routes
Endpoints for personalized user suggestions
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from app.models.smart_suggestion import (
    SmartSuggestionCreate,
    SmartSuggestionUpdate,
    SmartSuggestionResponse,
    DismissSuggestionRequest,
    GenerateSuggestionsRequest,
    SuggestionStats
)
from app.db.repositories.smart_suggestion_repository import SmartSuggestionRepository
from app.core.security import get_current_user

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("/", response_model=List[SmartSuggestionResponse])
def get_suggestions(
    include_dismissed: bool = False,
    type_filter: Optional[str] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized suggestions for the current user
    
    - **include_dismissed**: Include dismissed suggestions
    - **type_filter**: Filter by suggestion type (RECIPE, CHALLENGE, etc.)
    - **limit**: Maximum number of suggestions to return (default: 10)
    
    Returns active suggestions sorted by priority
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    suggestions = SmartSuggestionRepository.get_user_suggestions(
        user_id=user_id,
        include_dismissed=include_dismissed,
        type_filter=type_filter,
        limit=limit
    )
    
    return suggestions


@router.post("/generate", response_model=List[SmartSuggestionResponse])
def generate_suggestions(
    request: Optional[GenerateSuggestionsRequest] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate new personalized suggestions
    
    - **refresh**: If true, clear existing suggestions and generate new ones
    - **max_suggestions**: Maximum number of suggestions to generate (default: 5)
    
    Analyzes user data to create actionable suggestions:
    - Streak maintenance reminders
    - Leftover usage prompts
    - Challenge completion encouragement
    - Meal planning suggestions
    - Achievement progress alerts
    - General tips and best practices
    
    Suggestions are prioritized based on urgency and user patterns
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    if request is None:
        request = GenerateSuggestionsRequest()
    
    max_suggestions = request.max_suggestions
    
    # Determine whether to refresh or just get existing
    if request.force_regenerate:
        # Clear old and generate new
        suggestions = SmartSuggestionRepository.refresh_suggestions(
            user_id=user_id,
            max_suggestions=max_suggestions
        )
    else:
        # Check if there are existing suggestions
        existing = SmartSuggestionRepository.get_user_suggestions(
            user_id=user_id,
            include_dismissed=False,
            limit=max_suggestions
        )
        
        if existing:
            # Return existing suggestions
            suggestions = existing
        else:
            # No existing suggestions, generate fresh
            suggestions = SmartSuggestionRepository.refresh_suggestions(
                user_id=user_id,
                max_suggestions=max_suggestions
            )
    
    return suggestions


@router.patch("/{suggestion_id}/dismiss")
def dismiss_suggestion(
    suggestion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Dismiss a suggestion
    
    Dismissed suggestions won't appear in the active list but can be retrieved
    with include_dismissed=true
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    success = SmartSuggestionRepository.dismiss_suggestion(
        suggestion_id=suggestion_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return {"message": "Suggestion dismissed successfully"}


@router.patch("/{suggestion_id}", response_model=SmartSuggestionResponse)
def update_suggestion(
    suggestion_id: str,
    updates: SmartSuggestionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a suggestion
    
    Allows updating suggestion fields like title, description, priority, etc.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    suggestion = SmartSuggestionRepository.update_suggestion(
        suggestion_id=suggestion_id,
        user_id=user_id,
        updates=updates.model_dump(exclude_unset=True)
    )
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return suggestion


@router.delete("/{suggestion_id}")
def delete_suggestion(
    suggestion_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a suggestion permanently
    
    Use dismiss instead if you want to keep the suggestion for reference
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    success = SmartSuggestionRepository.delete_suggestion(
        suggestion_id=suggestion_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return {"message": "Suggestion deleted successfully"}


@router.delete("/")
def clear_old_suggestions(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Clear old dismissed suggestions
    
    - **days**: Remove dismissed suggestions older than this many days (default: 7)
    
    Only removes dismissed suggestions to maintain a clean history
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    count = SmartSuggestionRepository.clear_old_suggestions(
        user_id=user_id,
        days=days
    )
    
    return {
        "message": f"Cleared {count} old suggestions",
        "count": count
    }


@router.get("/stats", response_model=SuggestionStats)
def get_suggestion_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics about user's suggestions
    
    Returns counts of total, active, and dismissed suggestions,
    plus breakdown by suggestion type
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    stats = SmartSuggestionRepository.get_suggestion_stats(user_id=user_id)
    
    if not stats:
        # Return empty stats if none exist
        return {
            "total_suggestions": 0,
            "active_suggestions": 0,
            "dismissed_suggestions": 0,
            "suggestions_by_type": {},
            "most_recent_update": None
        }
    
    return stats


@router.post("/", response_model=SmartSuggestionResponse)
def create_custom_suggestion(
    suggestion: SmartSuggestionCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a custom suggestion manually
    
    Allows creating custom suggestions outside of the automatic generation logic.
    Useful for admin-created announcements or special promotions.
    """
    user_id = current_user.get("id") or current_user.get("user_id")
    
    created_suggestion = SmartSuggestionRepository.create_suggestion(
        user_id=user_id,
        suggestion_data=suggestion.model_dump(exclude_unset=True)
    )
    
    if not created_suggestion:
        raise HTTPException(status_code=500, detail="Failed to create suggestion")
    
    return created_suggestion
