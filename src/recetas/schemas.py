from pydantic import BaseModel
from ..ingredientes.schemas import IngredientOut
from ..categorias.schemas import CategoryOut

class RecipeBase(BaseModel):
    title: str
    description: str | None = None
    instructions: str | None = None

class RecipeCreate(RecipeBase):
    category_id: int
    ingredients_ids: list[int] = []

class RecipeUpdate(RecipeBase):
    category_id: int
    ingredients_ids: list[int] = []

class RecipeOut(RecipeBase):
    id: int
    category: CategoryOut | None
    ingredients: list[IngredientOut] = []

    class Config:
        orm_mode = True
