"""
User Stats Routes
Endpoints for user statistics, leaderboard, and achievements tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.models.stats import (
    UserStatsResponse,
    UserStatsSummary,
    IncrementStatsRequest,
    LeaderboardEntry
)
from app.db.repositories.user_stats_repository import UserStatsRepository
from app.core.security import get_current_user, get_current_user_id


router = APIRouter(prefix="/user/stats", tags=["User Stats"])


@router.get("/", response_model=UserStatsResponse)
def get_user_stats(current_user_id: str = Depends(get_current_user_id)):
    """
    Get current user's stats
    
    Returns:
    - total_meals_cooked: Total number of meals cooked
    - total_money_saved: Total money saved vs eating out
    - current_streak: Current consecutive days cooking streak
    - achievements_unlocked: Number of achievements unlocked
    - level: Current user level
    - points: Total points earned
    - last_activity_date: Last date user cooked a meal
    """
    stats = UserStatsRepository.get_or_create_stats(current_user_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user stats"
        )
    
    return UserStatsResponse(**stats)


@router.get("/summary", response_model=UserStatsSummary)
def get_stats_summary(current_user_id: str = Depends(get_current_user_id)):
    """
    Get comprehensive stats summary with additional context
    
    Returns:
    - All basic stats (meals, money, streak, achievements, level, points)
    - points_to_next_level: Points needed to level up
    - level_progress_percentage: Progress toward next level (0-100)
    - money_saved_this_week: Savings in the last 7 days
    - money_saved_this_month: Savings this calendar month
    - meals_this_week: Meals cooked in the last 7 days
    - meals_this_month: Meals cooked this calendar month
    """
    summary = UserStatsRepository.get_stats_summary(current_user_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stats summary"
        )
    
    return UserStatsSummary(**summary)


@router.post("/increment", response_model=dict)
def increment_stats(
    request: IncrementStatsRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Manually increment user stats
    
    Request body:
    - meals_cooked (optional): Number of meals to add (default: 0)
    - money_saved (optional): Amount of money saved to add (default: 0.0)
    - points (optional): Points to add (default: 0)
    
    This endpoint:
    - Increments the specified stats
    - Updates or maintains the cooking streak based on last_activity_date
    - Automatically calculates level based on total points
    - Returns updated stats summary
    
    Streak Logic:
    - First activity: Streak starts at 1
    - Activity on consecutive day: Streak increments by 1
    - Activity after 1+ day gap: Streak resets to 1
    - Activity on same day: Streak unchanged
    """
    success = UserStatsRepository.increment_stats(
        user_id=current_user_id,
        meals_cooked=request.meals_cooked,
        money_saved=request.money_saved,
        points=request.points
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to increment stats"
        )
    
    # Return updated stats
    summary = UserStatsRepository.get_stats_summary(current_user_id)
    
    return {
        "success": True,
        "message": "Stats updated successfully",
        "stats": summary
    }


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get user leaderboard ranked by points
    
    Query params:
    - limit: Number of entries to return (1-100, default: 10)
    - offset: Number of entries to skip for pagination (default: 0)
    
    Returns:
    - Leaderboard entries with user name, points, level, stats, and rank
    - Ordered by points (highest first)
    - Only includes active users
    
    Use for:
    - Global leaderboard display
    - Competitive features
    - User motivation
    """
    entries = UserStatsRepository.get_leaderboard(limit=limit, offset=offset)
    return entries


@router.post("/reset", response_model=dict)
def reset_streak(current_user_id: str = Depends(get_current_user_id)):
    """
    Reset user's cooking streak to 0
    
    Use this endpoint for:
    - Manual streak reset
    - Testing purposes
    - User-requested reset
    
    Note: This does NOT affect other stats (meals, money, points, level)
    """
    try:
        with UserStatsRepository.db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE user_stats
                SET current_streak = 0,
                    updated_at = NOW()
                WHERE user_id = %s
            """, (current_user_id,))
        
        return {
            "success": True,
            "message": "Streak reset to 0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset streak: {str(e)}"
        )
