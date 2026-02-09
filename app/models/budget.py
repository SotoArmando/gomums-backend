from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import date, datetime


# ==================== Budget Entry Models ====================

class BudgetEntryBase(BaseModel):
    """Base budget entry schema"""
    date: date
    meal_name: str = Field(..., min_length=1, max_length=255)
    cost: float = Field(ge=0)
    servings: int = Field(ge=1)
    category: Optional[str] = None
    notes: Optional[str] = None


class BudgetEntryCreate(BudgetEntryBase):
    """Schema for creating a budget entry"""
    journal_entry_id: Optional[str] = None


class BudgetEntryUpdate(BaseModel):
    """Schema for updating a budget entry"""
    date: Optional[date] = None
    meal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    cost: Optional[float] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    category: Optional[str] = None
    notes: Optional[str] = None


class BudgetEntryResponse(BaseModel):
    """Schema for budget entry response"""
    id: str
    user_id: str
    date: date
    meal_name: str
    cost: float
    servings: int
    cost_per_serving: float
    category: Optional[str] = None
    notes: Optional[str] = None
    journal_entry_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Budget Stats Models ====================

class BudgetStats(BaseModel):
    """Schema for budget statistics"""
    score: int = Field(ge=0, le=100)
    avg_cost_per_meal: float
    savings_vs_restaurant: float
    meals_this_week: int
    total_spent: float
    weekly_budget: Optional[float] = None
    remaining_budget: Optional[float] = None


class CategoryBreakdown(BaseModel):
    """Schema for category spending breakdown"""
    breakdown: Dict[str, float]
    total: float


# ==================== Budget Settings Models ====================

class BudgetSettingsCreate(BaseModel):
    """Schema for creating/updating budget settings"""
    weekly_budget: Optional[float] = Field(None, ge=0)
    monthly_budget: Optional[float] = Field(None, ge=0)


class BudgetSettingsResponse(BaseModel):
    """Schema for budget settings response"""
    id: str
    user_id: str
    weekly_budget: Optional[float] = None
    monthly_budget: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
