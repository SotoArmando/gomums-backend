"""
Challenge Models and Schemas
Multi-goal challenge support with individual goal tracking
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field
from uuid import UUID


# ==========================================
# CHALLENGE GOAL SCHEMAS
# ==========================================

class ChallengeGoalBase(BaseModel):
    """Base schema for challenge goal"""
    description: str
    target: int
    order_index: int = 0


class ChallengeGoalCreate(ChallengeGoalBase):
    """Schema for creating a challenge goal"""
    challenge_id: UUID


class ChallengeGoalResponse(ChallengeGoalBase):
    """Schema for challenge goal response"""
    id: UUID
    challenge_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# CHALLENGE SCHEMAS
# ==========================================

class ChallengeBase(BaseModel):
    """Base schema for challenge"""
    title: str
    description: Optional[str] = None
    type: str  # e.g., 'batch_cooking', 'budget_savings', 'zero_waste'
    duration: int  # days
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reward_points: int = 0
    reward_achievement_ids: Optional[List[UUID]] = None


class ChallengeCreate(ChallengeBase):
    """Schema for creating a challenge"""
    goals: List[ChallengeGoalBase] = Field(..., min_items=1)


class ChallengeUpdate(BaseModel):
    """Schema for updating a challenge"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reward_points: Optional[int] = None
    reward_achievement_ids: Optional[List[UUID]] = None


class ChallengeResponse(ChallengeBase):
    """Schema for challenge response"""
    id: UUID
    goals: List[ChallengeGoalResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# USER CHALLENGE GOAL SCHEMAS
# ==========================================

class UserChallengeGoalBase(BaseModel):
    """Base schema for user challenge goal"""
    completed: bool = False
    progress: int = 0


class UserChallengeGoalResponse(UserChallengeGoalBase):
    """Schema for user challenge goal response"""
    id: UUID
    user_challenge_id: UUID
    goal_id: UUID
    goal: ChallengeGoalResponse
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# USER CHALLENGE SCHEMAS
# ==========================================

class GoalProgressSimple(BaseModel):
    """Simplified goal progress info"""
    id: UUID
    user_challenge_id: UUID
    goal_id: UUID
    completed: bool
    progress: int
    completed_at: Optional[datetime] = None
    goal_description: str
    goal_target: int
    order_index: int

    class Config:
        from_attributes = True


class UserChallengeBase(BaseModel):
    """Base schema for user challenge"""
    status: str = "active"  # 'active', 'completed', 'failed'
    progress: int = 0


class UserChallengeAssign(BaseModel):
    """Schema for assigning a challenge to user"""
    challenge_id: UUID


class UserChallengeResponse(UserChallengeBase):
    """Schema for user challenge response"""
    id: UUID
    user_id: UUID
    challenge_id: UUID
    challenge: ChallengeResponse
    goal_progress: List[UserChallengeGoalResponse] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserChallengeSimpleResponse(BaseModel):
    """Simplified user challenge response (without nested challenge details)"""
    id: UUID
    user_id: UUID
    challenge_id: UUID
    challenge_title: str
    challenge_description: Optional[str] = None
    challenge_type: str
    status: str
    progress: int
    total_goals: int
    completed_goals: int
    reward_points: int
    goal_progress: List[GoalProgressSimple] = []
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# CHALLENGE PROGRESS UPDATE
# ==========================================

class ChallengeProgressUpdate(BaseModel):
    """Schema for updating challenge goal progress"""
    user_challenge_id: UUID
    goal_id: UUID
    progress_increment: int = 1  # How much to increment progress by
