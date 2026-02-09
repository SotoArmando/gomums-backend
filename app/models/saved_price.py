from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Saved Ingredient Price Models ====================

class SavedIngredientPriceBase(BaseModel):
    """Base schema for a saved ingredient price"""
    recipe_name: str = Field(..., min_length=1, max_length=255)
    ingredient_name: str = Field(..., min_length=1, max_length=255)
    original_price: float = Field(ge=0, default=0)
    modified_name: Optional[str] = Field(None, max_length=255)
    modified_price: Optional[float] = Field(None, ge=0)
    status: str = Field(default="original", pattern="^(original|swapped|removed)$")
    is_homemade: bool = False
    is_added: bool = False


class SavedIngredientPriceCreate(SavedIngredientPriceBase):
    """Schema for creating a saved ingredient price"""
    pass


class SavedIngredientPriceUpdate(BaseModel):
    """Schema for updating a saved ingredient price"""
    original_price: Optional[float] = Field(None, ge=0)
    modified_name: Optional[str] = Field(None, max_length=255)
    modified_price: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(original|swapped|removed)$")
    is_homemade: Optional[bool] = None
    is_added: Optional[bool] = None


class SavedIngredientPriceResponse(SavedIngredientPriceBase):
    """Schema for returning a saved ingredient price"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SavedIngredientPriceBulkCreate(BaseModel):
    """Schema for bulk-saving ingredient prices for a recipe"""
    recipe_name: str = Field(..., min_length=1, max_length=255)
    ingredients: List[SavedIngredientPriceCreate]


class RecipePriceSummary(BaseModel):
    """Summary of saved prices for a recipe"""
    recipe_name: str
    total_original: float
    total_modified: float
    total_savings: float
    ingredient_count: int
    swapped_count: int
    removed_count: int
    homemade_count: int
