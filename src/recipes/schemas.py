from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Recipe title")
    description: Optional[str] = Field(None, max_length=1000, description="Recipe description")
    instructions: str = Field(..., min_length=10, description="Recipe instructions")
    prep_time: Optional[int] = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: Optional[int] = Field(None, ge=0, description="Cooking time in minutes")
    servings: Optional[int] = Field(None, ge=1, description="Number of servings")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Difficulty level")


class RecipeCreate(RecipeBase):
    author_id: int
    category_id: int
    ingredient_ids: Optional[List[int]] = Field(default=[], description="List of ingredient IDs")


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, min_length=10)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    difficulty: Optional[DifficultyLevel] = None
    category_id: Optional[int] = None
    ingredient_ids: Optional[List[int]] = Field(None, description="List of ingredient IDs")


class RecipeResponse(RecipeBase):
    id: int
    author_id: int
    category_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    total_time: Optional[int] = Field(None, description="Total time (prep + cook)")

    class Config:
        from_attributes = True

    @validator('total_time', always=True)
    def calculate_total_time(cls, v, values):
        prep_time = values.get('prep_time', 0) or 0
        cook_time = values.get('cook_time', 0) or 0
        return prep_time + cook_time if prep_time or cook_time else None


class RecipeWithDetails(RecipeResponse):
    author: "UserResponse"
    category: "CategoryResponse"
    ingredients: List["RecipeIngredient"] = []

    class Config:
        from_attributes = True


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: Optional[str] = Field(None, max_length=50, description="Quantity (e.g., '2 cups', '500g')")
    notes: Optional[str] = Field(None, max_length=200, description="Additional notes")


class RecipeIngredientUpdate(BaseModel):
    quantity: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=200)


# Forward references
from src.users.schemas import UserResponse
from src.categories.schemas import CategoryResponse
from src.ingredients.schemas import RecipeIngredient

RecipeWithDetails.model_rebuild()