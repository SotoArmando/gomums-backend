"""
Meal Planning Models
Pydantic models for meal plans, planned meals, and shopping lists
"""
from __future__ import annotations

from pydantic import BaseModel, Field, validator
from typing import Optional, List
import datetime as dt
from decimal import Decimal


# ==================== Meal Plan Models ====================

class MealPlanBase(BaseModel):
    """Base meal plan fields"""
    name: str = Field(..., max_length=255, description="Name of the meal plan (e.g., 'Week of Feb 8')")
    start_date: dt.date = Field(..., description="Start date of the meal plan")
    end_date: dt.date = Field(..., description="End date of the meal plan")
    
    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after or equal to start_date')
        return v


class MealPlanCreate(MealPlanBase):
    """Create new meal plan"""
    status: Optional[str] = Field(default='draft', pattern='^(draft|active|completed)$')


class MealPlanUpdate(BaseModel):
    """Update existing meal plan"""
    name: Optional[str] = Field(None, max_length=255)
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None
    total_cost: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern='^(draft|active|completed)$')


class MealPlanResponse(MealPlanBase):
    """Meal plan response with details"""
    id: str
    user_id: str
    total_cost: Optional[Decimal] = None
    status: str
    created_at: dt.datetime
    updated_at: dt.datetime
    
    # Computed fields (from related tables)
    total_meals: Optional[int] = 0
    total_shopping_items: Optional[int] = 0
    shopping_items_purchased: Optional[int] = 0

    class Config:
        from_attributes = True


class MealPlanSummary(MealPlanResponse):
    """Meal plan with embedded planned meals and shopping list"""
    planned_meals: List['PlannedMealResponse'] = []
    shopping_list_items: List['ShoppingListItemResponse'] = []


# ==================== Planned Meal Models ====================

class PlannedMealBase(BaseModel):
    """Base planned meal fields"""
    date: dt.date = Field(..., description="Date of the meal")
    meal_type: str = Field(..., pattern='^(breakfast|lunch|dinner|snack)$')
    recipe_name: str = Field(..., max_length=255, description="Name of the recipe/meal")
    servings: int = Field(default=1, ge=1, description="Number of servings")
    is_batch: bool = Field(default=False, description="Is this a batch cooking meal")
    is_leftovers: bool = Field(default=False, description="Is this using leftovers")


class PlannedMealCreate(PlannedMealBase):
    """Create new planned meal"""
    recipe_id: Optional[str] = Field(None, description="Optional recipe ID if using existing recipe")


class PlannedMealUpdate(BaseModel):
    """Update existing planned meal"""
    date: Optional[dt.date] = None
    meal_type: Optional[str] = Field(None, pattern='^(breakfast|lunch|dinner|snack)$')
    recipe_id: Optional[str] = None
    recipe_name: Optional[str] = Field(None, max_length=255)
    servings: Optional[int] = Field(None, ge=1)
    is_batch: Optional[bool] = None
    is_leftovers: Optional[bool] = None


class PlannedMealResponse(PlannedMealBase):
    """Planned meal response"""
    id: str
    meal_plan_id: str
    recipe_id: Optional[str] = None
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True


# ==================== Shopping List Models ====================

class ShoppingListItemBase(BaseModel):
    """Base shopping list item fields"""
    name: str = Field(..., max_length=255, description="Item name")
    quantity: Optional[str] = Field(None, max_length=100, description="Quantity (e.g., '2 lbs', '3 cups')")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    estimated_cost: Optional[Decimal] = Field(None, ge=0, description="Estimated cost")


class ShoppingListItemCreate(ShoppingListItemBase):
    """Create new shopping list item"""
    related_recipes: Optional[List[str]] = Field(default=[], description="Recipe IDs that need this item")


class ShoppingListItemUpdate(BaseModel):
    """Update existing shopping list item"""
    name: Optional[str] = Field(None, max_length=255)
    quantity: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = None
    purchased: Optional[bool] = None
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    related_recipes: Optional[List[str]] = None


class ShoppingListItemResponse(ShoppingListItemBase):
    """Shopping list item response"""
    id: str
    meal_plan_id: str
    purchased: bool
    related_recipes: List[str]
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True


class BulkUpdateShoppingList(BaseModel):
    """Bulk update shopping list items (mark multiple as purchased)"""
    item_ids: List[str] = Field(..., description="List of shopping list item IDs")
    purchased: bool = Field(..., description="Mark as purchased or not")


# ==================== Calendar View Models ====================

class CalendarDayMeals(BaseModel):
    """Meals for a specific day"""
    date: dt.date
    breakfast: Optional[PlannedMealResponse] = None
    lunch: Optional[PlannedMealResponse] = None
    dinner: Optional[PlannedMealResponse] = None
    snacks: List[PlannedMealResponse] = []


class WeeklyCalendar(BaseModel):
    """Weekly calendar view"""
    meal_plan_id: str
    meal_plan_name: str
    start_date: dt.date
    end_date: dt.date
    days: List[CalendarDayMeals]


# ==================== Quick Create Models ====================

class QuickMealPlanCreate(BaseModel):
    """Quick create a meal plan with meals"""
    name: str = Field(..., max_length=255)
    start_date: dt.date
    end_date: dt.date
    planned_meals: List[PlannedMealCreate] = Field(default=[], description="Optional pre-populated meals")


class GenerateShoppingListRequest(BaseModel):
    """Request to generate shopping list from planned meals"""
    consolidate_duplicates: bool = Field(default=True, description="Combine duplicate items")
    use_recipe_ingredients: bool = Field(default=True, description="Pull ingredients from recipes if available")


# ==================== Statistics Models ====================

class MealPlanStats(BaseModel):
    """Statistics for meal planning"""
    total_meal_plans: int
    active_meal_plans: int
    completed_meal_plans: int
    total_meals_planned_this_week: int
    total_meals_planned_this_month: int
    average_meals_per_week: float
    shopping_completion_rate: float  # Percentage of items marked purchased


# Update forward references
MealPlanSummary.model_rebuild()
