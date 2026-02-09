"""
Challenge Routes
API endpoints for multi-goal challenges
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.challenge import (
    ChallengeResponse,
    ChallengeCreate,
    UserChallengeAssign,
    UserChallengeSimpleResponse,
    UserChallengeResponse,
    ChallengeProgressUpdate
)
from app.core.security import get_current_user
from app.db.repositories.challenge_repository import ChallengeRepository


router = APIRouter()


@router.get("/", response_model=List[ChallengeResponse])
async def get_all_challenges(
    challenge_type: Optional[str] = None,
    active_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all available challenges
    
    - **challenge_type**: Filter by type (e.g., 'batch_cooking', 'budget_savings')
    - **active_only**: Only show challenges within their date range
    """
    challenges = ChallengeRepository.get_all_challenges(
        challenge_type=challenge_type,
        active_only=active_only
    )
    
    return challenges


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(
    challenge_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific challenge by ID with all its goals"""
    challenge = ChallengeRepository.get_challenge_by_id(challenge_id)
    
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    return challenge


@router.post("/assign/{challenge_id}")
async def assign_challenge(
    challenge_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Assign a challenge to the current user
    Creates user_challenge entry and initializes all goal tracking
    """
    user_id = UUID(current_user["sub"])
    
    # Check if challenge exists
    challenge = ChallengeRepository.get_challenge_by_id(challenge_id)
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Assign challenge
    user_challenge = ChallengeRepository.assign_challenge(
        user_id=user_id,
        challenge_id=challenge_id
    )
    
    if not user_challenge:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Challenge already assigned or could not be assigned"
        )
    
    return {
        "message": "Challenge assigned successfully",
        "user_challenge_id": user_challenge["id"],
        "challenge_title": challenge["title"],
        "total_goals": len(challenge["goals"]),
        "reward_points": challenge["reward_points"]
    }


@router.get("/active/all", response_model=List[UserChallengeSimpleResponse])
async def get_active_challenges(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all active challenges for the current user
    Shows progress on each goal
    """
    user_id = UUID(current_user["sub"])
    
    active_challenges = ChallengeRepository.get_active_user_challenges(user_id)
    
    return active_challenges


@router.get("/completed/all", response_model=List[UserChallengeSimpleResponse])
async def get_completed_challenges(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all completed challenges for the current user
    Shows all goals that were completed
    """
    user_id = UUID(current_user["sub"])
    
    completed_challenges = ChallengeRepository.get_completed_user_challenges(user_id)
    
    return completed_challenges


@router.get("/active/{user_challenge_id}")
async def get_active_challenge_details(
    user_challenge_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific active challenge
    Shows all goals with individual progress
    """
    user_id = UUID(current_user["sub"])
    
    challenge_details = ChallengeRepository.get_user_challenge_details(user_challenge_id)
    
    if not challenge_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    # Verify ownership
    if str(challenge_details["user_id"]) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this challenge"
        )
    
    return challenge_details


@router.post("/progress/update")
async def update_challenge_goal_progress(
    progress_update: ChallengeProgressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update progress for a specific goal in a user's challenge
    
    Args:
        user_challenge_id: ID of the user's active challenge
        goal_id: ID of the specific goal to update
        progress_increment: Amount to increment progress by (default: 1)
    
    Returns:
        Updated goal information and challenge completion status
    """
    user_id = UUID(current_user["sub"])
    
    # Verify the user_challenge belongs to the current user
    challenge_details = ChallengeRepository.get_user_challenge_details(progress_update.user_challenge_id)
    
    if not challenge_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if str(challenge_details["user_id"]) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this challenge"
        )
    
    # Update goal progress
    result = ChallengeRepository.update_goal_progress(
        user_challenge_id=progress_update.user_challenge_id,
        goal_id=progress_update.goal_id,
        progress_increment=progress_update.progress_increment
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or could not be updated"
        )
    
    return {
        "message": "Goal progress updated successfully",
        "goal_completed": result.get("completed", False),
        "challenge_completed": result.get("challenge_completed", False),
        "points_awarded": result.get("points_awarded", 0) if result.get("challenge_completed") else 0,
        "current_progress": result.get("progress", 0)
    }


@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge: ChallengeCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new multi-goal challenge
    
    **Admin only** (TODO: Add admin check)
    
    Example:
    ```json
    {
      "title": "Zero Waste Week",
      "description": "Complete all 3 goals to reduce food waste",
      "type": "zero_waste",
      "duration": 7,
      "reward_points": 200,
      "goals": [
        {"description": "Use leftovers 5 times", "target": 5, "order_index": 0},
        {"description": "Freeze 3 meals", "target": 3, "order_index": 1},
        {"description": "Cook with scraps 2 times", "target": 2, "order_index": 2}
      ]
    }
    ```
    """
    # TODO: Add admin role check
    # if not current_user.get("is_admin"):
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    created_challenge = ChallengeRepository.create_challenge(
        title=challenge.title,
        description=challenge.description,
        type=challenge.type,
        duration=challenge.duration,
        reward_points=challenge.reward_points,
        goals=[goal.model_dump() for goal in challenge.goals],
        start_date=str(challenge.start_date) if challenge.start_date else None,
        end_date=str(challenge.end_date) if challenge.end_date else None,
        reward_achievement_ids=[str(aid) for aid in challenge.reward_achievement_ids] if challenge.reward_achievement_ids else None
    )
    
    if not created_challenge:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create challenge"
        )
    
    return created_challenge
