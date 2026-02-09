"""
Achievement Models
Pydantic models for achievements and user achievements
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Achievement Base Models ====================

class AchievementBase(BaseModel):
    """Base achievement fields"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    target: int = Field(..., gt=0, description="Target value to unlock achievement")
    points: int = Field(default=0, ge=0, description="Points awarded when unlocked")


class AchievementCreate(AchievementBase):
    """Create new achievement (admin only)"""
    pass


class AchievementUpdate(BaseModel):
    """Update existing achievement (admin only)"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    target: Optional[int] = Field(None, gt=0)
    points: Optional[int] = Field(None, ge=0)


class AchievementResponse(AchievementBase):
    """Achievement response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== User Achievement Models ====================

class UserAchievementBase(BaseModel):
    """Base user achievement fields"""
    progress: int = Field(default=0, ge=0, description="Current progress toward target")


class UserAchievementResponse(BaseModel):
    """User achievement with details"""
    id: str
    user_id: str
    achievement_id: str
    progress: int
    unlocked_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Achievement details (joined)
    achievement_title: str
    achievement_description: Optional[str] = None
    achievement_icon: Optional[str] = None
    achievement_category: Optional[str] = None
    achievement_target: int
    achievement_points: int
    
    # Computed fields
    is_unlocked: bool
    progress_percentage: float

    class Config:
        from_attributes = True


class UserAchievementSummary(BaseModel):
    """Summary of user's achievements"""
    total_achievements: int
    unlocked_achievements: int
    locked_achievements: int
    total_points_earned: int
    achievements_by_category: dict
    recent_unlocks: List[UserAchievementResponse]


class UpdateProgressRequest(BaseModel):
    """Request to update achievement progress"""
    progress: int = Field(..., ge=0)


class CheckAchievementsRequest(BaseModel):
    """Request to check and unlock achievements based on stats"""
    pass  # Uses current user stats automatically


# ==================== Achievement Categories ====================

class AchievementCategory:
    """Standard achievement categories"""
    COOKING = "cooking"
    SAVINGS = "savings"
    STREAK = "streak"
    SOCIAL = "social"
    CHALLENGES = "challenges"
    MISSIONS = "missions"
    SPECIAL = "special"


# ==================== Predefined Achievements ====================

PREDEFINED_ACHIEVEMENTS = [
    # Cooking Milestones
    {
        "title": "First Steps",
        "description": "Cook your first meal at home",
        "icon": "🍳",
        "category": AchievementCategory.COOKING,
        "target": 1,
        "points": 10
    },
    {
        "title": "Getting Started",
        "description": "Cook 5 meals at home",
        "icon": "👨‍🍳",
        "category": AchievementCategory.COOKING,
        "target": 5,
        "points": 25
    },
    {
        "title": "Home Chef",
        "description": "Cook 25 meals at home",
        "icon": "👩‍🍳",
        "category": AchievementCategory.COOKING,
        "target": 25,
        "points": 50
    },
    {
        "title": "Master Chef",
        "description": "Cook 50 meals at home",
        "icon": "🏆",
        "category": AchievementCategory.COOKING,
        "target": 50,
        "points": 100
    },
    {
        "title": "Century Club",
        "description": "Cook 100 meals at home",
        "icon": "💯",
        "category": AchievementCategory.COOKING,
        "target": 100,
        "points": 250
    },
    
    # Savings Milestones
    {
        "title": "Penny Pincher",
        "description": "Save $50 by cooking at home",
        "icon": "💰",
        "category": AchievementCategory.SAVINGS,
        "target": 50,
        "points": 25
    },
    {
        "title": "Money Saver",
        "description": "Save $100 by cooking at home",
        "icon": "💵",
        "category": AchievementCategory.SAVINGS,
        "target": 100,
        "points": 50
    },
    {
        "title": "Budget Boss",
        "description": "Save $500 by cooking at home",
        "icon": "💸",
        "category": AchievementCategory.SAVINGS,
        "target": 500,
        "points": 100
    },
    {
        "title": "Savings Star",
        "description": "Save $1000 by cooking at home",
        "icon": "⭐",
        "category": AchievementCategory.SAVINGS,
        "target": 1000,
        "points": 200
    },
    
    # Streak Achievements
    {
        "title": "Consistency",
        "description": "Maintain a 3-day cooking streak",
        "icon": "🔥",
        "category": AchievementCategory.STREAK,
        "target": 3,
        "points": 15
    },
    {
        "title": "Week Warrior",
        "description": "Maintain a 7-day cooking streak",
        "icon": "📅",
        "category": AchievementCategory.STREAK,
        "target": 7,
        "points": 50
    },
    {
        "title": "Streak Master",
        "description": "Maintain a 30-day cooking streak",
        "icon": "🎯",
        "category": AchievementCategory.STREAK,
        "target": 30,
        "points": 150
    },
    {
        "title": "Unstoppable",
        "description": "Maintain a 100-day cooking streak",
        "icon": "🚀",
        "category": AchievementCategory.STREAK,
        "target": 100,
        "points": 500
    },
    
    # Challenge Achievements
    {
        "title": "Challenge Accepted",
        "description": "Complete your first challenge",
        "icon": "🎪",
        "category": AchievementCategory.CHALLENGES,
        "target": 1,
        "points": 20
    },
    {
        "title": "Challenge Champion",
        "description": "Complete 5 challenges",
        "icon": "🏅",
        "category": AchievementCategory.CHALLENGES,
        "target": 5,
        "points": 75
    },
    {
        "title": "Challenge Master",
        "description": "Complete 10 challenges",
        "icon": "👑",
        "category": AchievementCategory.CHALLENGES,
        "target": 10,
        "points": 200
    },
    
    # Mission Achievements
    {
        "title": "Mission Starter",
        "description": "Complete your first mission",
        "icon": "📋",
        "category": AchievementCategory.MISSIONS,
        "target": 1,
        "points": 10
    },
    {
        "title": "Mission Runner",
        "description": "Complete 10 missions",
        "icon": "🎖️",
        "category": AchievementCategory.MISSIONS,
        "target": 10,
        "points": 50
    },
    {
        "title": "Mission Expert",
        "description": "Complete 50 missions",
        "icon": "⚡",
        "category": AchievementCategory.MISSIONS,
        "target": 50,
        "points": 150
    },
    
    # Special Achievements
    {
        "title": "Early Adopter",
        "description": "Join GoMums in the early days",
        "icon": "🌟",
        "category": AchievementCategory.SPECIAL,
        "target": 1,
        "points": 50
    },
    {
        "title": "Batch Cooking Pro",
        "description": "Cook 10 batch meals",
        "icon": "🍲",
        "category": AchievementCategory.SPECIAL,
        "target": 10,
        "points": 75
    },
    {
        "title": "Zero Waste Hero",
        "description": "Use leftovers in 20 meals",
        "icon": "♻️",
        "category": AchievementCategory.SPECIAL,
        "target": 20,
        "points": 100
    }
]
