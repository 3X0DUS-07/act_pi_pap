from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.recetas import models, schemas
from src.ingredientes.models import Ingredient


router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("/", response_model=schemas.RecipeOut)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.Recipe(
        title=recipe.title,
        description=recipe.description,
        instructions=recipe.instructions,
        category_id=recipe.category_id,
    )
    if recipe.ingredients_ids:
        db_recipe.ingredients = db.query(Ingredient).filter(Ingredient.id.in_(recipe.ingredients_ids)).all()

    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@router.get("/", response_model=list[schemas.RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    return db.query(models.Recipe).all()
