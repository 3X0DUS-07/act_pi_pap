from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3 and 50 characters")
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserWithRecipes(UserResponse):
    recipes: List["RecipeResponse"] = []

    class Config:
        from_attributes = True


# Forward reference
from src.recipes.schemas import RecipeResponse
UserWithRecipes.model_rebuild()