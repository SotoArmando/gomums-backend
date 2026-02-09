"""
Achievement Routes
Endpoints for achievements and user achievement tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.models.achievement import (
    AchievementResponse,
    AchievementCreate,
    AchievementUpdate,
    UserAchievementResponse,
    UserAchievementSummary,
    UpdateProgressRequest,
    PREDEFINED_ACHIEVEMENTS
)
from app.db.repositories.achievement_repository import AchievementRepository
from app.db.repositories.user_stats_repository import UserStatsRepository
from app.core.security import get_current_user_id


router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/", response_model=List[AchievementResponse])
def get_all_achievements(category: Optional[str] = Query(None)):
    """
    Get all available achievements
    
    Query params:
    - category: Optional filter by category (cooking, savings, streak, challenges, missions, special)
    
    Returns:
    - List of all achievements with details
    - Ordered by category and target value
    
    Use for:
    - Displaying all possible achievements
    - Showing achievement catalog
    - Discovery of what's available
    """
    achievements = AchievementRepository.get_all_achievements(category=category)
    return achievements


@router.get("/mine", response_model=List[UserAchievementResponse])
def get_my_achievements(
    category: Optional[str] = Query(None),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get current user's achievements with progress
    
    Query params:
    - category: Optional filter by category
    
    Returns:
    - All achievements with user's progress
    - Includes unlocked and locked achievements
    - Shows progress percentage for each
    - Ordered by unlocked status (unlocked first), then category
    
    Progress fields:
    - is_unlocked: Boolean indicating if achievement is unlocked
    - progress: Current progress value
    - progress_percentage: 0-100 percentage toward target
    - unlocked_date: When achievement was unlocked (null if locked)
    """
    achievements = AchievementRepository.get_user_achievements(
        user_id=current_user_id,
        category=category
    )
    return achievements


@router.get("/summary", response_model=UserAchievementSummary)
def get_achievement_summary(current_user_id: str = Depends(get_current_user_id)):
    """
    Get summary of user's achievement progress
    
    Returns:
    - total_achievements: Total number of achievements
    - unlocked_achievements: Number unlocked
    - locked_achievements: Number still locked
    - total_points_earned: Points from unlocked achievements
    - achievements_by_category: Breakdown by category
    - recent_unlocks: Last 5 achievements unlocked
    
    Use for:
    - Achievement overview screen
    - Progress dashboard
    - Gamification stats
    """
    summary = AchievementRepository.get_user_achievement_summary(current_user_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve achievement summary"
        )
    
    return summary


@router.post("/check", response_model=dict)
def check_achievements(current_user_id: str = Depends(get_current_user_id)):
    """
    Check user's stats and unlock eligible achievements
    
    This endpoint:
    - Fetches current user stats
    - Checks all achievements against stats
    - Unlocks any achievements where target is reached
    - Awards points for newly unlocked achievements
    - Updates user stats with new points
    - Increments achievements_unlocked counter
    
    Returns:
    - newly_unlocked: List of achievements just unlocked
    - points_awarded: Total points from new unlocks
    - updated_stats: Current user stats after points added
    
    Achievement criteria:
    - Cooking: Based on total_meals_cooked
    - Savings: Based on total_money_saved
    - Streak: Based on current_streak
    - Challenges: Based on challenges_completed
    - Missions: Based on missions_completed
    - Special: Custom logic per achievement
    """
    # Get current user stats
    stats = UserStatsRepository.get_or_create_stats(current_user_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user stats"
        )
    
    # Check and unlock achievements
    newly_unlocked = AchievementRepository.check_and_unlock_achievements(
        user_id=current_user_id,
        stats=stats
    )
    
    # Award points for newly unlocked achievements
    total_points = sum(a['points'] for a in newly_unlocked)
    
    if total_points > 0:
        # Add points to user stats
        UserStatsRepository.increment_stats(
            user_id=current_user_id,
            meals_cooked=0,
            money_saved=0,
            points=total_points
        )
        
        # Increment achievements counter
        for _ in newly_unlocked:
            UserStatsRepository.increment_achievements_count(current_user_id)
    
    # Get updated stats
    updated_stats = UserStatsRepository.get_stats_summary(current_user_id)
    
    return {
        "newly_unlocked": newly_unlocked,
        "count": len(newly_unlocked),
        "points_awarded": total_points,
        "updated_stats": updated_stats
    }


@router.post("/seed", response_model=dict)
def seed_achievements():
    """
    Seed predefined achievements into the database
    
    This endpoint:
    - Creates all predefined achievements
    - Skips achievements that already exist (idempotent)
    - Returns count of new achievements created
    
    Predefined achievements include:
    - Cooking milestones (1, 5, 25, 50, 100 meals)
    - Savings milestones ($50, $100, $500, $1000)
    - Streak milestones (3, 7, 30, 100 days)
    - Challenge milestones (1, 5, 10 completed)
    - Mission milestones (1, 10, 50 completed)
    - Special achievements (batch cooking, zero waste, etc.)
    
    Use for:
    - Initial database setup
    - Adding new achievements
    - Development/testing
    """
    created = AchievementRepository.seed_achievements(PREDEFINED_ACHIEVEMENTS)
    
    return {
        "success": True,
        "message": f"Seeded {created} new achievements",
        "total_predefined": len(PREDEFINED_ACHIEVEMENTS),
        "created": created,
        "skipped": len(PREDEFINED_ACHIEVEMENTS) - created
    }


# ==================== Admin Endpoints ====================

@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
def create_achievement(
    achievement_data: AchievementCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new custom achievement (admin only)
    
    Request body:
    - title: Achievement title
    - description: Achievement description
    - icon: Icon/emoji for achievement
    - category: Category (cooking, savings, streak, etc.)
    - target: Target value to unlock
    - points: Points awarded when unlocked
    
    Returns:
    - Created achievement with ID
    
    Note: This endpoint should be restricted to admin users
    TODO: Add admin role check
    """
    data = achievement_data.model_dump()
    achievement = AchievementRepository.create_achievement(data)
    
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create achievement"
        )
    
    return achievement


@router.get("/{achievement_id}", response_model=AchievementResponse)
def get_achievement(achievement_id: str):
    """
    Get specific achievement by ID
    
    Returns:
    - Achievement details
    
    Use for:
    - Achievement detail view
    - Displaying single achievement
    """
    achievement = AchievementRepository.get_achievement(achievement_id)
    
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )
    
    return achievement


@router.post("/{achievement_id}/progress", response_model=dict)
def update_achievement_progress(
    achievement_id: str,
    progress_data: UpdateProgressRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Manually update progress on an achievement
    
    Request body:
    - progress: New progress value
    
    This endpoint:
    - Updates user's progress toward achievement
    - Automatically unlocks if target reached
    - Awards points if unlocked
    - Updates user stats
    
    Returns:
    - Updated achievement progress
    - Whether achievement was just unlocked
    - Points awarded if unlocked
    
    Use for:
    - Manual progress updates
    - Testing
    - Custom achievement logic
    """
    result = AchievementRepository.update_progress(
        user_id=current_user_id,
        achievement_id=achievement_id,
        progress=progress_data.progress
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )
    
    # If just unlocked, award points and increment counter
    if result.get('was_just_unlocked'):
        UserStatsRepository.increment_stats(
            user_id=current_user_id,
            meals_cooked=0,
            money_saved=0,
            points=result['points_awarded']
        )
        UserStatsRepository.increment_achievements_count(current_user_id)
    
    return {
        "success": True,
        "achievement_id": achievement_id,
        "progress": result['progress'],
        "unlocked": result['unlocked_date'] is not None,
        "was_just_unlocked": result.get('was_just_unlocked', False),
        "points_awarded": result.get('points_awarded', 0)
    }
