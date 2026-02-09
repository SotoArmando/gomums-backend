"""
User Profile Pydantic models (schemas) for API validation
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class UserProfileResponse(BaseModel):
    """User profile information"""
    id: str
    name: str
    email: EmailStr
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_premium: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserProfileUpdate(BaseModel):
    """Update user profile information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None


class UserPreferencesResponse(BaseModel):
    """User preferences"""
    id: str
    user_id: str
    dietary_restrictions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    budget_goal: Optional[Decimal] = None
    household_size: Optional[int] = None
    skill_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserPreferencesUpdate(BaseModel):
    """Update user preferences"""
    dietary_restrictions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    budget_goal: Optional[Decimal] = Field(None, ge=0)
    household_size: Optional[int] = Field(None, ge=1, le=20)
    skill_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")


class UserStatsResponse(BaseModel):
    """User statistics"""
    id: str
    user_id: str
    total_meals_cooked: int = 0
    total_money_saved: Decimal = Decimal("0")
    current_streak: int = 0
    achievements_unlocked: int = 0
    level: int = 1
    points: int = 0
    last_activity_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class CompleteProfileResponse(BaseModel):
    """Complete user profile with preferences and stats"""
    profile: UserProfileResponse
    preferences: Optional[UserPreferencesResponse] = None
    stats: Optional[UserStatsResponse] = None
