from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .schemas import IngredientResponse, IngredientCreate, IngredientUpdate, IngredientWithRecipes
from .service import IngredientService
from src.core.database import get_db

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("/", response_model=IngredientResponse, status_code=201)
def create_ingredient(ingredient_data: IngredientCreate, db: Session = Depends(get_db)):
    """Create a new ingredient"""
    service = IngredientService(db)
    return service.create_ingredient(ingredient_data)


@router.get("/", response_model=List[IngredientResponse])
def get_ingredients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name, description, or unit"),
    db: Session = Depends(get_db)
):
    """Get list of ingredients with pagination and filtering"""
    service = IngredientService(db)
    ingredients = service.get_ingredients(skip=skip, limit=limit, search=search)
    return ingredients


@router.get("/count")
def get_ingredients_count(
    search: Optional[str] = Query(None, description="Search in name, description, or unit"),
    db: Session = Depends(get_db)
):
    """Get total count of ingredients matching filters"""
    service = IngredientService(db)
    count = service.get_ingredient_count(search=search)
    return {"total": count}


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Get a specific ingredient by ID"""
    service = IngredientService(db)
    return service.get_ingredient(ingredient_id)


@router.get("/{ingredient_id}/with-recipes", response_model=IngredientWithRecipes)
def get_ingredient_with_recipes(ingredient_id: int, db: Session = Depends(get_db)):
    """Get an ingredient with its recipes"""
    service = IngredientService(db)
    return service.get_ingredient(ingredient_id)


@router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(ingredient_id: int, ingredient_data: IngredientUpdate, db: Session = Depends(get_db)):
    """Update an ingredient"""
    service = IngredientService(db)
    return service.update_ingredient(ingredient_id, ingredient_data)


@router.delete("/{ingredient_id}", status_code=204)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    """Delete an ingredient"""
    service = IngredientService(db)
    service.delete_ingredient(ingredient_id)
    return None