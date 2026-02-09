"""
User Recipe Pydantic models (schemas) for API validation
Private recipes created by users - not visible to other users
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class IngredientItem(BaseModel):
    """Single ingredient in a recipe.
    
    Can be a plain text ingredient (just name/amount/unit) or optionally
    reference the ingredient_catalog for pricing and standardization.
    """
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None  # e.g., "diced", "room temperature"
    
    # Optional catalog reference & cost fields
    ingredient_catalog_id: Optional[str] = None  # UUID reference to ingredient_catalog
    author_cost: Optional[float] = None           # Cost set by the recipe author


class InstructionStep(BaseModel):
    """Single instruction step in a recipe"""
    step_number: int
    instruction: str
    phase: Optional[str] = None         # "prep", "cooking", or "serve"
    items: List[str] = Field(default_factory=list)  # Ingredients/tools used in this step
    time_minutes: Optional[int] = None  # Time for this step
    tip: Optional[str] = None  # Optional tip for this step


class NutritionInfo(BaseModel):
    """Nutrition information for a recipe"""
    calories: Optional[int] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None
    fiber: Optional[str] = None


# ==================== Request Models ====================

class UserRecipeCreate(BaseModel):
    """Create a new user recipe"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    servings: Optional[int] = Field(default=1, ge=1)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    
    # Recipe content
    ingredients: List[IngredientItem] = Field(default_factory=list)
    instructions: List[InstructionStep] = Field(default_factory=list)
    
    # Nutrition
    calories: Optional[int] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None
    fiber: Optional[str] = None
    
    # Organization
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Source info
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    original_recipe_id: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    is_favorite: bool = False


class UserRecipeUpdate(BaseModel):
    """Update an existing user recipe"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    servings: Optional[int] = Field(default=None, ge=1)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    
    # Recipe content
    ingredients: Optional[List[IngredientItem]] = None
    instructions: Optional[List[InstructionStep]] = None
    
    # Nutrition
    calories: Optional[int] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None
    fiber: Optional[str] = None
    
    # Organization
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Source info
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


# ==================== Response Models ====================

class UserRecipeResponse(BaseModel):
    """User recipe response model"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    
    # Recipe content
    ingredients: List[IngredientItem] = Field(default_factory=list)
    instructions: List[InstructionStep] = Field(default_factory=list)
    
    # Nutrition
    nutrition: NutritionInfo
    
    # Organization
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Source info
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    original_recipe_id: Optional[str] = None
    
    # Notes & status
    notes: Optional[str] = None
    is_favorite: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserRecipeSummary(BaseModel):
    """Summary view of user recipe (for lists)"""
    id: str
    name: str
    image: Optional[str] = None
    prep_time: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    is_favorite: bool = False
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserRecipeListResponse(BaseModel):
    """Response for listing user recipes"""
    recipes: List[UserRecipeSummary]
    total: int
    limit: int
    offset: int
