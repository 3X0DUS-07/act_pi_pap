from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .schemas import (
    RecipeResponse, 
    RecipeCreate, 
    RecipeUpdate, 
    RecipeWithDetails,
    DifficultyLevel,
    RecipeIngredientCreate,
    RecipeIngredientUpdate
)
from .service import RecipeService
from src.core.database import get_db

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe_data: RecipeCreate, db: Session = Depends(get_db)):
    """Create a new recipe"""
    service = RecipeService(db)
    return service.create_recipe(recipe_data)


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in title, description, or instructions"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    max_prep_time: Optional[int] = Query(None, ge=0, description="Maximum preparation time in minutes"),
    max_cook_time: Optional[int] = Query(None, ge=0, description="Maximum cooking time in minutes"),
    db: Session = Depends(get_db)
):
    """Get list of recipes with pagination and filtering"""
    service = RecipeService(db)
    recipes = service.get_recipes(
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id,
        author_id=author_id,
        difficulty=difficulty,
        max_prep_time=max_prep_time,
        max_cook_time=max_cook_time
    )
    return recipes


@router.get("/count")
def get_recipes_count(
    search: Optional[str] = Query(None, description="Search in title, description, or instructions"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    max_prep_time: Optional[int] = Query(None, ge=0, description="Maximum preparation time in minutes"),
    max_cook_time: Optional[int] = Query(None, ge=0, description="Maximum cooking time in minutes"),
    db: Session = Depends(get_db)
):
    """Get total count of recipes matching filters"""
    service = RecipeService(db)
    count = service.get_recipe_count(
        search=search,
        category_id=category_id,
        author_id=author_id,
        difficulty=difficulty,
        max_prep_time=max_prep_time,
        max_cook_time=max_cook_time
    )
    return {"total": count}


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Get a specific recipe by ID"""
    service = RecipeService(db)
    return service.get_recipe(recipe_id)


@router.get("/{recipe_id}/details", response_model=RecipeWithDetails)
def get_recipe_with_details(recipe_id: int, db: Session = Depends(get_db)):
    """Get a recipe with full details (author, category, ingredients)"""
    service = RecipeService(db)
    return service.get_recipe(recipe_id)


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, recipe_data: RecipeUpdate, db: Session = Depends(get_db)):
    """Update a recipe"""
    service = RecipeService(db)
    return service.update_recipe(recipe_id, recipe_data)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe"""
    service = RecipeService(db)
    service.delete_recipe(recipe_id)
    return None


@router.post("/{recipe_id}/ingredients", response_model=RecipeResponse)
def add_ingredient_to_recipe(
    recipe_id: int, 
    ingredient_data: RecipeIngredientCreate, 
    db: Session = Depends(get_db)
):
    """Add an ingredient to a recipe"""
    service = RecipeService(db)
    return service.add_ingredient_to_recipe(recipe_id, ingredient_data)


@router.delete("/{recipe_id}/ingredients/{ingredient_id}", status_code=204)
def remove_ingredient_from_recipe(
    recipe_id: int, 
    ingredient_id: int, 
    db: Session = Depends(get_db)
):
    """Remove an ingredient from a recipe"""
    service = RecipeService(db)
    service.remove_ingredient_from_recipe(recipe_id, ingredient_id)
    return None


@router.put("/{recipe_id}/ingredients/{ingredient_id}", response_model=RecipeResponse)
def update_recipe_ingredient(
    recipe_id: int,
    ingredient_id: int,
    ingredient_data: RecipeIngredientUpdate,
    db: Session = Depends(get_db)
):
    """Update ingredient quantity/notes in a recipe"""
    service = RecipeService(db)
    return service.update_recipe_ingredient(recipe_id, ingredient_id, ingredient_data)