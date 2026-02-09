"""
Home Sections Models
Models for dynamic, customizable home screen sections
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SectionType(str, Enum):
    """Types of home sections"""
    STATS = "stats"
    ACHIEVEMENTS = "achievements"
    SUGGESTIONS = "suggestions"
    CHALLENGES = "challenges"
    MISSIONS = "missions"
    MEAL_PLANS = "meal_plans"
    RECIPES = "recipes"
    JOURNAL = "journal"
    LEADERBOARD = "leaderboard"
    TIPS = "tips"
    ARTICLES = "articles"
    VIDEOS = "videos"
    STREAK = "streak"
    BUDGET = "budget"
    SHOPPING = "shopping"
    CUSTOM = "custom"


class HomeSectionBase(BaseModel):
    """Base model for home sections"""
    type: SectionType
    title: str = Field(..., max_length=255, description="Section title")
    subtitle: Optional[str] = Field(None, max_length=255, description="Section subtitle")
    visible: bool = Field(True, description="Whether section is visible")
    order_index: int = Field(0, description="Display order (lower = higher)")
    data: Optional[Dict[str, Any]] = Field(None, description="Flexible data storage")


class HomeSectionCreate(HomeSectionBase):
    """Model for creating a home section"""
    pass


class HomeSectionUpdate(BaseModel):
    """Model for updating a home section"""
    type: Optional[SectionType] = None
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    visible: Optional[bool] = None
    order_index: Optional[int] = None
    data: Optional[Dict[str, Any]] = None


class HomeSectionResponse(HomeSectionBase):
    """Model for home section responses"""
    id: str
    user_id: Optional[str] = Field(None, description="NULL for global sections")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HomeSectionReorder(BaseModel):
    """Model for reordering sections"""
    section_id: str
    new_order_index: int


class BulkReorderSections(BaseModel):
    """Model for bulk reordering sections"""
    sections: List[HomeSectionReorder]


# ==================== Section Data Templates ====================

SECTION_TEMPLATES = {
    # Stats Section
    "stats": {
        "type": "stats",
        "title": "Your Cooking Stats",
        "subtitle": "Track your progress",
        "order_index": 0,
        "data": {
            "show_meals": True,
            "show_streak": True,
            "show_savings": True,
            "show_points": True,
            "show_level": True
        }
    },
    
    # Streak Section
    "streak": {
        "type": "streak",
        "title": "Cooking Streak",
        "subtitle": "Keep it going!",
        "order_index": 1,
        "data": {
            "show_days": True,
            "show_calendar": True,
            "show_motivation": True
        }
    },
    
    # Suggestions Section
    "suggestions": {
        "type": "suggestions",
        "title": "Suggested For You",
        "subtitle": "Personalized recommendations",
        "order_index": 2,
        "data": {
            "max_suggestions": 3,
            "show_dismissed": False,
            "auto_refresh": True
        }
    },
    
    # Achievements Section
    "achievements": {
        "type": "achievements",
        "title": "Recent Achievements",
        "subtitle": "Your latest unlocks",
        "order_index": 3,
        "data": {
            "show_count": 5,
            "show_progress": True,
            "show_locked": True,
            "filter_category": None
        }
    },
    
    # Active Challenges Section
    "challenges": {
        "type": "challenges",
        "title": "Active Challenges",
        "subtitle": "Your current challenges",
        "order_index": 4,
        "data": {
            "max_challenges": 3,
            "show_progress": True,
            "show_rewards": True,
            "status_filter": "active"
        }
    },
    
    # Daily Missions Section
    "missions": {
        "type": "missions",
        "title": "Today's Missions",
        "subtitle": "Complete to earn rewards",
        "order_index": 5,
        "data": {
            "max_missions": 3,
            "show_completed": False,
            "show_rewards": True
        }
    },
    
    # Meal Plans Section
    "meal_plans": {
        "type": "meal_plans",
        "title": "This Week's Meal Plan",
        "subtitle": "Plan your meals ahead",
        "order_index": 6,
        "data": {
            "show_calendar": True,
            "show_shopping_list": True,
            "days_ahead": 7
        }
    },
    
    # Budget Section
    "budget": {
        "type": "budget",
        "title": "Budget Overview",
        "subtitle": "Track your spending",
        "order_index": 7,
        "data": {
            "show_total": True,
            "show_remaining": True,
            "show_chart": True,
            "period": "monthly"
        }
    },
    
    # Recent Journal Entries
    "journal": {
        "type": "journal",
        "title": "Recent Meals",
        "subtitle": "Your cooking history",
        "order_index": 8,
        "data": {
            "max_entries": 5,
            "show_images": True,
            "show_cost": True,
            "show_portions": True
        }
    },
    
    # Recipe Recommendations
    "recipes": {
        "type": "recipes",
        "title": "Try These Recipes",
        "subtitle": "Based on your preferences",
        "order_index": 9,
        "data": {
            "max_recipes": 6,
            "filter_by": "recommended",
            "show_difficulty": True,
            "show_time": True,
            "show_cost": True
        }
    },
    
    # Leaderboard Section
    "leaderboard": {
        "type": "leaderboard",
        "title": "Leaderboard",
        "subtitle": "See how you rank",
        "order_index": 10,
        "data": {
            "show_top": 10,
            "show_user_rank": True,
            "period": "all_time"
        }
    },
    
    # Tips Section
    "tips": {
        "type": "tips",
        "title": "Cooking Tips",
        "subtitle": "Learn something new",
        "order_index": 11,
        "data": {
            "rotation": "daily",
            "categories": ["cooking", "savings", "meal_prep", "nutrition"]
        }
    },
    
    # Articles Section
    "articles": {
        "type": "articles",
        "title": "Featured Articles",
        "subtitle": "Read and learn",
        "order_index": 12,
        "data": {
            "max_articles": 3,
            "show_images": True,
            "filter_category": None
        }
    },
    
    # Videos Section
    "videos": {
        "type": "videos",
        "title": "How-To Videos",
        "subtitle": "Watch and learn",
        "order_index": 13,
        "data": {
            "max_videos": 3,
            "show_thumbnails": True,
            "filter_category": None
        }
    }
}


# Helper function to get default sections for a new user
def get_default_user_sections() -> List[Dict[str, Any]]:
    """Get default home sections for a new user"""
    return [
        SECTION_TEMPLATES["streak"],
        SECTION_TEMPLATES["suggestions"],
        SECTION_TEMPLATES["missions"],
        SECTION_TEMPLATES["challenges"],
        SECTION_TEMPLATES["achievements"],
        SECTION_TEMPLATES["meal_plans"],
        SECTION_TEMPLATES["journal"],
        SECTION_TEMPLATES["recipes"]
    ]
