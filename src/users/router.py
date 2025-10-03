from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .schemas import UserResponse, UserCreate, UserUpdate, UserWithRecipes
from .service import UserService
from src.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    service = UserService(db)
    return service.create_user(user_data)


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in username, full_name, or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get list of users with pagination and filtering"""
    service = UserService(db)
    users = service.get_users(skip=skip, limit=limit, search=search, is_active=is_active)
    return users


@router.get("/count")
def get_users_count(
    search: Optional[str] = Query(None, description="Search in username, full_name, or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get total count of users matching filters"""
    service = UserService(db)
    count = service.get_user_count(search=search, is_active=is_active)
    return {"total": count}


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    service = UserService(db)
    return service.get_user(user_id)


@router.get("/{user_id}/with-recipes", response_model=UserWithRecipes)
def get_user_with_recipes(user_id: int, db: Session = Depends(get_db)):
    """Get a user with their recipes"""
    service = UserService(db)
    return service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    service = UserService(db)
    return service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    service = UserService(db)
    service.delete_user(user_id)
    return None