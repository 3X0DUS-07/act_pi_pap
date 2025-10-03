from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CategoryWithRecipes(CategoryResponse):
    recipes: List["RecipeResponse"] = []

    class Config:
        from_attributes = True


# Forward reference
from src.recipes.schemas import RecipeResponse
CategoryWithRecipes.model_rebuild()