from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class IngredientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Ingredient name")
    description: Optional[str] = Field(None, max_length=500, description="Ingredient description")
    unit: Optional[str] = Field(None, max_length=50, description="Default unit (e.g., grams, cups, units)")


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    unit: Optional[str] = Field(None, max_length=50)


class IngredientResponse(IngredientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RecipeIngredient(BaseModel):
    """Schema for ingredients within a recipe context"""
    id: int
    name: str
    description: Optional[str]
    unit: Optional[str]
    quantity: Optional[str] = Field(None, description="Quantity for this recipe")
    notes: Optional[str] = Field(None, description="Notes for this ingredient in this recipe")

    class Config:
        from_attributes = True


class IngredientWithRecipes(IngredientResponse):
    recipes: List["RecipeResponse"] = []

    class Config:
        from_attributes = True


# Forward reference
from src.recipes.schemas import RecipeResponse
IngredientWithRecipes.model_rebuild()