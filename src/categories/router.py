from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .schemas import CategoryResponse, CategoryCreate, CategoryUpdate, CategoryWithRecipes
from .service import CategoryService
from src.core.database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    service = CategoryService(db)
    return service.create_category(category_data)


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in name or description"),
    db: Session = Depends(get_db)
):
    """Get list of categories with pagination and filtering"""
    service = CategoryService(db)
    categories = service.get_categories(skip=skip, limit=limit, search=search)
    return categories


@router.get("/count")
def get_categories_count(
    search: Optional[str] = Query(None, description="Search in name or description"),
    db: Session = Depends(get_db)
):
    """Get total count of categories matching filters"""
    service = CategoryService(db)
    count = service.get_category_count(search=search)
    return {"total": count}


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID"""
    service = CategoryService(db)
    return service.get_category(category_id)


@router.get("/{category_id}/with-recipes", response_model=CategoryWithRecipes)
def get_category_with_recipes(category_id: int, db: Session = Depends(get_db)):
    """Get a category with its recipes"""
    service = CategoryService(db)
    return service.get_category(category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category"""
    service = CategoryService(db)
    return service.update_category(category_id, category_data)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    service = CategoryService(db)
    service.delete_category(category_id)
    return None