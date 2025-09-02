from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from . import models, schemas

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.post("/", response_model=schemas.IngredientOut)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = models.Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.get("/", response_model=list[schemas.IngredientOut])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(models.Ingredient).all()
