from pydantic import BaseModel

class IngredientBase(BaseModel):
    name: str
    unit: str | None = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    pass

class IngredientOut(IngredientBase):
    id: int
    class Config:
        orm_mode = True
