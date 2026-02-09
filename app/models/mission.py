"""
Mission Pydantic models (schemas) for API validation
Multi-goal mission support
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==========================================
# MISSION GOAL SCHEMAS
# ==========================================

class MissionGoalBase(BaseModel):
    """Base schema for mission goal"""
    description: str
    target: int
    order_index: int = 0


class MissionGoalCreate(MissionGoalBase):
    """Schema for creating a mission goal"""
    mission_id: UUID


class MissionGoalResponse(MissionGoalBase):
    """Schema for mission goal response"""
    id: UUID
    mission_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# USER MISSION GOAL SCHEMAS
# ==========================================

class UserMissionGoalResponse(BaseModel):
    """Schema for user mission goal response"""
    id: UUID
    user_mission_id: UUID
    goal_id: UUID
    goal: MissionGoalResponse
    completed: bool = False
    progress: int = 0
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# MISSION SCHEMAS
# ==========================================

class MissionResponse(BaseModel):
    """Mission details"""
    id: str
    title: str
    description: Optional[str] = None
    type: str  # 'daily', 'weekly', 'monthly'
    category: Optional[str] = None
    difficulty: Optional[str] = None  # 'easy', 'medium', 'hard'
    target: int  # Kept for backward compatibility with single-goal missions
    reward_points: int = 0
    reward_achievement_id: Optional[str] = None
    kind: Optional[str] = 'mission'  # 'mission', 'challenge', 'event'
    goals: List[MissionGoalResponse] = []  # Multi-goal support
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserMissionResponse(BaseModel):
    """User's progress on a mission"""
    id: str
    user_id: str
    mission_id: str
    mission: MissionResponse  # Embedded mission details
    status: str  # 'active', 'completed', 'expired'
    progress: int = 0
    goal_progress: List[UserMissionGoalResponse] = []  # Individual goal tracking
    started_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UpdateProgressRequest(BaseModel):
    """Request to update mission progress"""
    progress: int = Field(..., ge=0, description="Current progress value (must be >= 0)")


class MissionCreate(BaseModel):
    """Schema for creating a mission with goals"""
    title: str
    description: Optional[str] = None
    type: str  # 'daily', 'weekly', 'monthly'
    category: Optional[str] = None
    difficulty: Optional[str] = None
    target: int = 1  # Default target for single-goal missions
    reward_points: int = 0
    reward_achievement_id: Optional[str] = None
    kind: Optional[str] = 'mission'
    goals: List[MissionGoalBase] = []  # Optional multi-goal support


class MissionGoalProgressUpdate(BaseModel):
    """Schema for updating specific goal progress"""
    goal_id: UUID
    progress_increment: int = 1


class MissionStatsResponse(BaseModel):
    """Mission statistics for the user"""
    total_active: int
    total_completed: int
    total_expired: int
    points_earned_today: int
    points_earned_week: int
    points_earned_total: int
