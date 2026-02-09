"""
Ingredient Catalog Pydantic models (schemas) for API validation
Master reference ingredient prices by region
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ==================== Ingredient Catalog Models ====================

class IngredientCatalogBase(BaseModel):
    """Base schema for an ingredient catalog entry"""
    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name in English")
    name_local: Optional[str] = Field(None, max_length=255, description="Local language name")
    category: str = Field(..., min_length=1, max_length=100, description="Category (e.g., vegetables, proteins)")
    unit: str = Field(..., min_length=1, max_length=100, description="Unit of measure (e.g., 1 kg, 500 g)")
    price: Decimal = Field(..., ge=0, description="Average/typical price")
    price_low: Optional[Decimal] = Field(None, ge=0, description="Low end of price range")
    price_high: Optional[Decimal] = Field(None, ge=0, description="High end of price range")
    currency: str = Field(..., min_length=1, max_length=10, description="Currency code (e.g., RD$, USD)")
    region: str = Field(..., min_length=1, max_length=100, description="Region name (e.g., Dominican Republic, Kansas)")
    language: str = Field(default="en", min_length=2, max_length=10, description="Language code (e.g., en, es)")


class IngredientCatalogCreate(IngredientCatalogBase):
    """Schema for creating an ingredient catalog entry"""
    source: str = Field(default="manual", max_length=100)


class IngredientCatalogUpdate(BaseModel):
    """Schema for updating an ingredient catalog entry"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_local: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    unit: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    price_low: Optional[Decimal] = Field(None, ge=0)
    price_high: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=1, max_length=10)
    region: Optional[str] = Field(None, min_length=1, max_length=100)
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    source: Optional[str] = Field(None, max_length=100)


class IngredientCatalogResponse(IngredientCatalogBase):
    """Schema for returning an ingredient catalog entry"""
    id: str
    source: str = "manual"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IngredientCatalogBulkCreate(BaseModel):
    """Schema for bulk-creating ingredient catalog entries"""
    region: str = Field(..., min_length=1, max_length=100)
    currency: str = Field(..., min_length=1, max_length=10)
    language: str = Field(default="en", min_length=2, max_length=10, description="Language code")
    ingredients: List[IngredientCatalogCreate]


class IngredientCatalogListResponse(BaseModel):
    """Response for listing ingredient catalog entries"""
    items: List[IngredientCatalogResponse]
    total: int
    region: Optional[str] = None
    category: Optional[str] = None


class RegionSummary(BaseModel):
    """Summary of ingredients available for a region"""
    region: str
    currency: str
    language: str
    total_ingredients: int
    categories: List[str]
