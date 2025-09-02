from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    class Config:
        orm_mode = True
