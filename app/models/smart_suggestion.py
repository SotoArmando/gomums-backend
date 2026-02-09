"""
Smart Suggestions Models
Pydantic models for personalized user suggestions
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Suggestion Types ====================

class SuggestionType:
    """Standard suggestion types"""
    RECIPE = "recipe"
    CHALLENGE = "challenge"
    MISSION = "mission"
    TIP = "tip"
    ACHIEVEMENT = "achievement"
    MEAL_PLAN = "meal_plan"
    SHOPPING = "shopping"
    BUDGET = "budget"
    LEFTOVER = "leftover"
    BATCH_COOKING = "batch_cooking"


# ==================== Color Themes ====================

class DotColor:
    """Suggestion dot colors for visual indicators"""
    GREEN = "green"      # Positive actions, savings
    BLUE = "blue"        # Information, tips
    PURPLE = "purple"    # Achievements, milestones
    ORANGE = "orange"    # Warnings, reminders
    RED = "red"          # Urgent actions
    YELLOW = "yellow"    # Opportunities
    GRAY = "gray"        # Neutral, general


# ==================== Suggestion Base Models ====================

class SmartSuggestionBase(BaseModel):
    """Base suggestion fields"""
    title: str = Field(..., max_length=255, description="Suggestion title")
    subtitle: Optional[str] = Field(None, max_length=255, description="Suggestion subtitle")
    description: Optional[str] = Field(None, description="Detailed description")
    type: str = Field(..., max_length=100, description="Suggestion type")
    dot_color: Optional[str] = Field(None, max_length=50, description="Visual indicator color")
    action_text: Optional[str] = Field(None, max_length=100, description="Call-to-action text")
    priority: int = Field(default=0, ge=0, le=100, description="Priority (0-100, higher = more important)")


class SmartSuggestionCreate(SmartSuggestionBase):
    """Create new suggestion"""
    pass


class SmartSuggestionUpdate(BaseModel):
    """Update existing suggestion"""
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    type: Optional[str] = Field(None, max_length=100)
    dot_color: Optional[str] = Field(None, max_length=50)
    action_text: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=0, le=100)
    dismissed: Optional[bool] = None


class SmartSuggestionResponse(SmartSuggestionBase):
    """Suggestion response"""
    id: str
    user_id: str
    dismissed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Suggestion Actions ====================

class DismissSuggestionRequest(BaseModel):
    """Request to dismiss a suggestion"""
    dismissed: bool = Field(default=True)


class GenerateSuggestionsRequest(BaseModel):
    """Request to generate suggestions based on user data"""
    force_regenerate: bool = Field(default=False, description="Force regeneration even if recent suggestions exist")
    max_suggestions: int = Field(default=5, ge=1, le=20, description="Maximum suggestions to generate")


class SuggestionStats(BaseModel):
    """Statistics about user's suggestions"""
    total_suggestions: int
    active_suggestions: int
    dismissed_suggestions: int
    suggestions_by_type: dict
    most_recent_update: Optional[datetime] = None


# ==================== Predefined Suggestion Templates ====================

SUGGESTION_TEMPLATES = {
    # Recipe suggestions
    "try_new_recipe": {
        "title": "Try something new!",
        "subtitle": "Explore recipes you haven't cooked before",
        "description": "Based on your preferences, we think you'd love {recipe_name}",
        "type": SuggestionType.RECIPE,
        "dot_color": DotColor.BLUE,
        "action_text": "View Recipe",
        "priority": 50
    },
    "use_leftovers": {
        "title": "Use your leftovers",
        "subtitle": "You have {leftover_count} leftover items",
        "description": "Reduce waste and save money by using your leftovers. Try: {recipe_suggestions}",
        "type": SuggestionType.LEFTOVER,
        "dot_color": DotColor.GREEN,
        "action_text": "See Recipes",
        "priority": 70
    },
    "batch_cooking": {
        "title": "Plan a batch cooking session",
        "subtitle": "Cook once, eat multiple times",
        "description": "Save time this week by preparing {recipe_name} in bulk",
        "type": SuggestionType.BATCH_COOKING,
        "dot_color": DotColor.PURPLE,
        "action_text": "Plan It",
        "priority": 60
    },
    
    # Challenge suggestions
    "start_challenge": {
        "title": "Start a new challenge",
        "subtitle": "{challenge_name}",
        "description": "Challenge yourself and earn {points} points by completing {challenge_description}",
        "type": SuggestionType.CHALLENGE,
        "dot_color": DotColor.PURPLE,
        "action_text": "Join Challenge",
        "priority": 65
    },
    "complete_challenge": {
        "title": "Complete your challenge",
        "subtitle": "You're {progress}% done with {challenge_name}",
        "description": "Keep going! Just {remaining} more to finish and earn {points} points",
        "type": SuggestionType.CHALLENGE,
        "dot_color": DotColor.ORANGE,
        "action_text": "Continue",
        "priority": 80
    },
    
    # Mission suggestions
    "daily_mission": {
        "title": "Today's mission",
        "subtitle": "{mission_name}",
        "description": "Complete today's mission and earn {points} points",
        "type": SuggestionType.MISSION,
        "dot_color": DotColor.BLUE,
        "action_text": "Start Mission",
        "priority": 75
    },
    
    # Achievement suggestions
    "close_to_achievement": {
        "title": "Achievement unlocked soon!",
        "subtitle": "{achievement_name}",
        "description": "You're almost there! Just {remaining} more {metric} to unlock this achievement",
        "type": SuggestionType.ACHIEVEMENT,
        "dot_color": DotColor.PURPLE,
        "action_text": "View Progress",
        "priority": 70
    },
    
    # Meal planning suggestions
    "plan_week": {
        "title": "Plan your week",
        "subtitle": "No meal plan for this week yet",
        "description": "Create a meal plan to stay organized and save money",
        "type": SuggestionType.MEAL_PLAN,
        "dot_color": DotColor.BLUE,
        "action_text": "Create Plan",
        "priority": 60
    },
    "complete_meal_plan": {
        "title": "Complete your meal plan",
        "subtitle": "You have {empty_slots} empty meal slots",
        "description": "Fill in the remaining days to make the most of your weekly plan",
        "type": SuggestionType.MEAL_PLAN,
        "dot_color": DotColor.ORANGE,
        "action_text": "Fill Slots",
        "priority": 65
    },
    
    # Shopping suggestions
    "create_shopping_list": {
        "title": "Create shopping list",
        "subtitle": "Generate list from your meal plan",
        "description": "Your meal plan is ready! Generate a shopping list to make grocery shopping easier",
        "type": SuggestionType.SHOPPING,
        "dot_color": DotColor.BLUE,
        "action_text": "Generate List",
        "priority": 70
    },
    
    # Budget suggestions
    "track_spending": {
        "title": "Track your spending",
        "subtitle": "No entries this week",
        "description": "Log your meals to see how much you're saving by cooking at home",
        "type": SuggestionType.BUDGET,
        "dot_color": DotColor.GREEN,
        "action_text": "Log Meal",
        "priority": 55
    },
    "exceeding_budget": {
        "title": "Budget alert",
        "subtitle": "You're {percentage}% of your weekly budget",
        "description": "Consider meal planning to stay within budget and save money",
        "type": SuggestionType.BUDGET,
        "dot_color": DotColor.ORANGE,
        "action_text": "View Budget",
        "priority": 85
    },
    
    # Streak suggestions
    "maintain_streak": {
        "title": "Keep your streak going!",
        "subtitle": "{streak_days} day streak",
        "description": "You're on a roll! Cook today to maintain your {streak_days} day cooking streak",
        "type": SuggestionType.TIP,
        "dot_color": DotColor.ORANGE,
        "action_text": "Cook Today",
        "priority": 90
    },
    
    # Tips
    "save_money_tip": {
        "title": "Money-saving tip",
        "subtitle": "Buy in bulk and freeze",
        "description": "Save up to 30% by buying proteins in bulk and freezing portions for later",
        "type": SuggestionType.TIP,
        "dot_color": DotColor.GREEN,
        "action_text": "Learn More",
        "priority": 40
    },
    "meal_prep_tip": {
        "title": "Meal prep tip",
        "subtitle": "Prep vegetables in advance",
        "description": "Wash and chop vegetables on Sunday to save time during the week",
        "type": SuggestionType.TIP,
        "dot_color": DotColor.BLUE,
        "action_text": "See Tips",
        "priority": 40
    }
}
