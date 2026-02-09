"""
Mission API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from app.models.mission import (
    UserMissionResponse, MissionResponse, UpdateProgressRequest, MissionStatsResponse
)
from app.db.repositories.mission_repository import MissionRepository
from app.core.security import get_current_user

router = APIRouter()
mission_repo = MissionRepository()


@router.get("/available", response_model=List[MissionResponse])
async def get_available_missions(
    mission_type: Optional[str] = None,
    kind: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all available missions that can be assigned
    
    - **mission_type**: Optional filter by type (daily/weekly/monthly)
    - **kind**: Optional filter by kind (mission/challenge/event)
    
    Returns list of mission templates from the missions table.
    Use kind='challenge' to get only challenges.
    """
    missions = await mission_repo.get_all_missions(mission_type, kind)
    return missions


@router.get("/check-availability/{mission_id}", response_model=Dict[str, Any])
async def check_mission_availability(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Check if a specific mission is available for assignment
    
    - **mission_id**: UUID of the mission to check
    
    Returns availability status and cooldown information:
    - If available: ready to assign
    - If in cooldown: shows hours remaining and when it becomes available again
    """
    user_id = current_user["id"]
    availability = await mission_repo.check_mission_availability(user_id, mission_id)
    return availability


@router.get("/active", response_model=List[UserMissionResponse])
async def get_active_missions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all active missions for the current user
    
    Returns list of missions with progress tracking.
    """
    user_id = current_user["id"]
    missions = await mission_repo.get_active_missions(user_id)
    
    return missions


@router.patch("/{user_mission_id}/progress", response_model=UserMissionResponse)
async def update_mission_progress(
    user_mission_id: str,
    progress_data: UpdateProgressRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update progress on a specific mission
    
    - **user_mission_id**: UUID of the user_mission record
    - **progress**: New progress value (must be >= 0)
    
    Automatically completes mission and awards points when target is reached.
    """
    user_id = current_user["id"]
    
    updated_mission = await mission_repo.update_mission_progress(
        user_mission_id=user_mission_id,
        user_id=user_id,
        progress=progress_data.progress
    )
    
    if not updated_mission:
        raise HTTPException(
            status_code=404,
            detail="Mission not found or you don't have permission to update it"
        )
    
    return updated_mission


@router.get("/stats", response_model=MissionStatsResponse)
async def get_mission_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get mission statistics for the current user
    
    Returns counts and points earned across different time periods.
    """
    user_id = current_user["id"]
    stats = await mission_repo.get_mission_stats(user_id)
    
    return stats


@router.post("/assign-daily", response_model=Dict[str, Any])
async def assign_daily_missions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Manually trigger assignment of daily missions
    
    Typically called automatically on user login, but can be triggered manually.
    Assigns up to 3 daily missions that have passed their 24-hour cooldown period.
    """
    user_id = current_user["id"]
    assigned_ids = await mission_repo.assign_daily_missions(user_id)
    
    return {
        "message": f"Assigned {len(assigned_ids)} daily missions",
        "assigned_count": len(assigned_ids),
        "mission_ids": assigned_ids
    }


@router.post("/assign/{mission_id}", response_model=Dict[str, Any])
async def assign_specific_mission(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Manually assign a specific mission to the current user
    
    - **mission_id**: UUID of the mission to assign
    
    Missions have cooldown periods before they can be reassigned:
    - Daily missions: 24 hours
    - Weekly missions: 7 days
    - Monthly missions: 30 days
    
    Returns 409 (Conflict) if mission is still in cooldown period.
    """
    user_id = current_user["id"]
    
    # Check availability first to provide better error messages
    availability = await mission_repo.check_mission_availability(user_id, mission_id)
    
    if not availability.get('available'):
        if 'hours_remaining' in availability:
            raise HTTPException(
                status_code=409,
                detail=f"Mission is in cooldown. Available in {availability['hours_remaining']} hours"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=availability.get('reason', 'Mission not found')
            )
    
    result = await mission_repo.assign_specific_mission(user_id, mission_id)
    
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to assign mission"
        )
    
    return {
        "message": "Mission assigned successfully",
        "user_mission_id": result.get('id'),
        "mission_id": mission_id
    }
