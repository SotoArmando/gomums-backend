"""
Recipe Pydantic models (schemas) for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime


class StructuredIngredient(BaseModel):
    """Structured ingredient for public recipes.
    
    Used when a recipe ingredient references the ingredient catalog
    with amount, unit, and author-provided cost.
    """
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    ingredient_catalog_id: Optional[str] = None  # UUID reference to ingredient_catalog
    author_cost: Optional[float] = None           # Cost set by the recipe author


class NutritionInfo(BaseModel):
    """Nutrition information for a recipe"""
    calories: Optional[int] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None
    fiber: Optional[str] = None


class RecipeStep(BaseModel):
    """Single step in a recipe, categorized by phase"""
    order: int                                          # Step number (1-based)
    phase: str = Field(..., pattern="^(prep|cooking|serve)$")  # Phase of the recipe
    text: str                                           # Instruction text
    items: List[str] = Field(default_factory=list)      # Ingredients/tools used in this step
    time_minutes: Optional[int] = None                  # Estimated time for this step
    tip: Optional[str] = None                           # Optional tip


class RecipeResponse(BaseModel):
    """Recipe response model"""
    id: str
    name: str
    image: Optional[str] = None
    prep_time: Optional[str] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None  # 'easy', 'medium', 'hard'
    ingredients: List[str] = Field(default_factory=list)  # Plain text ingredients (backward compat)
    structured_ingredients: List[StructuredIngredient] = Field(default_factory=list)  # Optional structured format
    instructions: List[str] = Field(default_factory=list)
    steps: List[RecipeStep] = Field(default_factory=list)  # Structured steps with phases
    nutrition: NutritionInfo
    featured: bool = False
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class RecipeListParams(BaseModel):
    """Query parameters for listing recipes"""
    category: Optional[str] = None
    difficulty: Optional[str] = None
    featured: Optional[bool] = None
    search: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated tags
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
