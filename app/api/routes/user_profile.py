"""
User Profile API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.models.user_profile import (
    UserProfileResponse, UserProfileUpdate,
    UserPreferencesResponse, UserPreferencesUpdate,
    UserStatsResponse, CompleteProfileResponse
)
from app.db.repositories.user_profile_repository import UserProfileRepository
from app.core.security import get_current_user

router = APIRouter()
profile_repo = UserProfileRepository()


@router.get("/me", response_model=CompleteProfileResponse)
async def get_complete_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get complete user profile including preferences and stats
    
    Returns the user's profile information, preferences, and statistics.
    """
    user_id = current_user["id"]
    
    profile = await profile_repo.get_profile(user_id)
    preferences = await profile_repo.get_preferences(user_id)
    stats = await profile_repo.get_stats(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "profile": profile,
        "preferences": preferences,
        "stats": stats
    }


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user profile information
    
    Returns basic profile details like name, email, avatar, etc.
    """
    user_id = current_user["id"]
    profile = await profile_repo.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@router.patch("/me/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user profile information
    
    - **name**: Update display name
    - **avatar_url**: Update profile picture URL
    """
    user_id = current_user["id"]
    
    updated_profile = await profile_repo.update_profile(
        user_id=user_id,
        name=profile_data.name,
        avatar_url=profile_data.avatar_url
    )
    
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return updated_profile


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user preferences
    
    Returns dietary restrictions, allergies, budget goals, household size, and skill level.
    """
    user_id = current_user["id"]
    preferences = await profile_repo.get_preferences(user_id)
    
    if not preferences:
        # Return empty preferences if none exist yet
        raise HTTPException(
            status_code=404,
            detail="Preferences not set. Use PATCH to create them."
        )
    
    return preferences


@router.patch("/me/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user preferences (creates if doesn't exist)
    
    - **dietary_restrictions**: List of dietary restrictions (e.g., ["vegetarian", "gluten-free"])
    - **allergies**: List of allergies (e.g., ["peanuts", "shellfish"])
    - **budget_goal**: Weekly or monthly budget goal
    - **household_size**: Number of people in household
    - **skill_level**: Cooking skill level ("beginner", "intermediate", "advanced")
    """
    user_id = current_user["id"]
    
    updated_prefs = await profile_repo.upsert_preferences(
        user_id=user_id,
        dietary_restrictions=preferences_data.dietary_restrictions,
        allergies=preferences_data.allergies,
        budget_goal=preferences_data.budget_goal,
        household_size=preferences_data.household_size,
        skill_level=preferences_data.skill_level
    )
    
    if not updated_prefs:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    
    return updated_prefs


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user statistics
    
    Returns total meals cooked, money saved, current streak, level, points, etc.
    """
    user_id = current_user["id"]
    stats = await profile_repo.get_stats(user_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    return stats
