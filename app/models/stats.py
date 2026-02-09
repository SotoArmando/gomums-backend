"""
User Stats Models and Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class UserStatsResponse(BaseModel):
    """Schema for user stats response"""
    id: UUID
    user_id: UUID
    total_meals_cooked: int
    total_money_saved: float
    current_streak: int
    achievements_unlocked: int
    level: int
    points: int
    last_activity_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStatsUpdate(BaseModel):
    """Schema for updating user stats"""
    total_meals_cooked: Optional[int] = None
    total_money_saved: Optional[float] = None
    current_streak: Optional[int] = None
    achievements_unlocked: Optional[int] = None
    level: Optional[int] = None
    points: Optional[int] = None


class UserStatsSummary(BaseModel):
    """Schema for user stats summary"""
    total_meals_cooked: int
    total_money_saved: float
    current_streak: int
    achievements_unlocked: int
    level: int
    points: int
    points_to_next_level: int
    level_progress_percentage: float
    money_saved_this_week: float
    money_saved_this_month: float
    meals_this_week: int
    meals_this_month: int


class IncrementStatsRequest(BaseModel):
    """Schema for incrementing stats"""
    meals_cooked: Optional[int] = 0
    money_saved: Optional[float] = 0.0
    points: Optional[int] = 0


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry"""
    user_id: UUID
    user_name: str
    points: int
    level: int
    total_meals_cooked: int
    total_money_saved: float
    rank: Optional[int] = None
