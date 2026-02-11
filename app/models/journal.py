from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Dict, Any, Union
from datetime import datetime


# ==================== Ingredient Models ====================

class MealIngredient(BaseModel):
    """Structured ingredient for meal entries (matches recipe IngredientItem)"""
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    ingredient_catalog_id: Optional[str] = None
    author_cost: Optional[float] = None


# Type alias for flexible ingredient input
IngredientInput = Union[str, MealIngredient, Dict[str, Any]]


def normalize_ingredients_input(ingredients: Optional[List[IngredientInput]]) -> Optional[List[MealIngredient]]:
    """
    Normalize ingredients input to structured format.
    Accepts:
        - ["Chicken", "Rice"] -> [{name: "Chicken"}, {name: "Rice"}]
        - [{name: "Chicken", amount: "2 lbs"}] -> as-is
        - Mixed: ["Chicken", {name: "Rice", amount: "1 cup"}]
    """
    if not ingredients:
        return None
    
    result = []
    for ing in ingredients:
        if isinstance(ing, str):
            result.append(MealIngredient(name=ing))
        elif isinstance(ing, dict):
            result.append(MealIngredient(**ing))
        elif isinstance(ing, MealIngredient):
            result.append(ing)
    return result if result else None


def extract_ingredient_names(ingredients: Optional[List[IngredientInput]]) -> List[str]:
    """
    Extract just the ingredient names from either format.
    Used for auto-linking and other matching operations.
    """
    if not ingredients:
        return []
    
    names = []
    for ing in ingredients:
        if isinstance(ing, str):
            names.append(ing)
        elif isinstance(ing, dict):
            names.append(ing.get('name', ''))
        elif isinstance(ing, MealIngredient):
            names.append(ing.name)
    return [n for n in names if n]  # Filter out empty strings


# ==================== Base Models ====================

class JournalEntryBase(BaseModel):
    """Base journal entry schema"""
    type: Literal["meal", "purchase"]
    timestamp: datetime
    title: str = Field(..., min_length=1, max_length=255)


class IngredientSwap(BaseModel):
    """Schema for tracking ingredient substitutions with cost information"""
    recipe_id: Optional[str] = Field(None, description="Recipe reference ID (optional for purchase swaps)")
    original_ingredient: str = Field(..., description="Name of the original ingredient from the recipe")
    original_cost: Optional[float] = Field(None, ge=0, description="Cost of the original ingredient")
    swapped_ingredient: str = Field(..., description="Name of the substituted ingredient used")
    swapped_cost: Optional[float] = Field(None, ge=0, description="Cost of the swapped ingredient")
    savings: Optional[float] = Field(None, description="Calculated savings (original_cost - swapped_cost)")

    class Config:
        from_attributes = True


# ==================== Meal Models ====================

class MealCreate(BaseModel):
    """Schema for creating a meal entry"""
    title: str = Field(..., min_length=1, max_length=255)
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    portions: int = Field(ge=1)
    portions_left: Optional[int] = Field(None, ge=0)
    status: Literal["fresh", "leftovers", "frozen", "completed"] = "fresh"
    ingredients_used: Optional[List[IngredientInput]] = Field(
        None,
        description="Ingredients used. Accepts strings or objects: ['Chicken'] or [{name: 'Chicken', amount: '2 lbs'}]"
    )
    ingredient_swaps: Optional[List[IngredientSwap]] = Field(None, description="List of ingredient swaps with cost information")
    is_batch: bool = False
    used_leftovers: bool = False
    has_leftovers: bool = False
    needs_restock: bool = False
    purchase_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def get_ingredient_names(self) -> List[str]:
        """Get list of ingredient names for matching/linking"""
        return extract_ingredient_names(self.ingredients_used)
    
    def get_structured_ingredients(self) -> Optional[List[MealIngredient]]:
        """Get ingredients as structured objects"""
        return normalize_ingredients_input(self.ingredients_used)


class MealUpdate(BaseModel):
    """Schema for updating a meal entry"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    portions_left: Optional[int] = Field(None, ge=0)
    status: Optional[Literal["fresh", "leftovers", "frozen", "completed"]] = None
    needs_restock: Optional[bool] = None


class LinkedPurchase(BaseModel):
    """Schema for linked purchase info embedded in meal response"""
    id: str
    title: str
    store: str
    items: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime
    ingredients_matched: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    """Schema for meal entry response"""
    id: str
    user_id: str
    type: Literal["meal"]
    timestamp: datetime
    title: str
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    portions: int
    portions_left: Optional[int] = None
    status: Literal["fresh", "leftovers", "frozen", "completed"]
    ingredients_used: Optional[List[Union[str, MealIngredient, Dict[str, Any]]]] = None
    ingredient_swaps: Optional[List[IngredientSwap]] = None
    is_batch: bool
    used_leftovers: bool
    has_leftovers: bool
    needs_restock: bool
    purchase_id: Optional[str] = None
    linked_purchase: Optional[LinkedPurchase] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Purchase Models ====================

class PurchaseItem(BaseModel):
    """Schema for a single purchase item"""
    name: str
    quantity: str
    cost: float = Field(ge=0)
    category: Optional[str] = None


class PurchaseCreate(BaseModel):
    """Schema for creating a purchase entry"""
    title: str = Field(..., min_length=1, max_length=255)
    store: str = Field(..., min_length=1, max_length=255)
    items: List[PurchaseItem]
    timestamp: Optional[datetime] = None


class PurchaseUpdate(BaseModel):
    """Schema for updating a purchase entry"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    store: Optional[str] = Field(None, min_length=1, max_length=255)
    items: Optional[List[PurchaseItem]] = None


class PurchaseResponse(BaseModel):
    """Schema for purchase entry response"""
    id: str
    user_id: str
    type: Literal["purchase"]
    timestamp: datetime
    title: str
    store: str
    items: List[PurchaseItem]
    total_cost: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Combined Models ====================

class JournalEntryCreate(BaseModel):
    """Schema for creating any journal entry (discriminated union)"""
    type: Literal["meal", "purchase"]
    # Meal fields (required if type=meal)
    meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None
    portions: Optional[int] = Field(None, ge=1)
    portions_left: Optional[int] = Field(None, ge=0)
    status: Optional[Literal["fresh", "leftovers", "frozen", "completed"]] = "fresh"
    ingredients_used: Optional[List[IngredientInput]] = Field(
        None,
        description="Ingredients used. Accepts strings or objects: ['Chicken'] or [{name: 'Chicken', amount: '2 lbs'}]"
    )
    ingredient_swaps: Optional[List[IngredientSwap]] = None
    is_batch: Optional[bool] = False
    used_leftovers: Optional[bool] = False
    has_leftovers: Optional[bool] = False
    needs_restock: Optional[bool] = False
    purchase_id: Optional[str] = None
    # Purchase fields (required if type=purchase)
    store: Optional[str] = None
    items: Optional[List[PurchaseItem]] = None
    # Common fields
    title: str = Field(..., min_length=1, max_length=255)
    timestamp: Optional[datetime] = None
    
    def get_ingredient_names(self) -> List[str]:
        """Get list of ingredient names for matching/linking"""
        return extract_ingredient_names(self.ingredients_used)


# Union type for responses
JournalEntryResponse = MealResponse | PurchaseResponse


# ==================== Link Models ====================

class LinkPurchaseRequest(BaseModel):
    """Schema for linking a meal to a purchase"""
    purchase_id: str
    ingredients_used: List[str]
