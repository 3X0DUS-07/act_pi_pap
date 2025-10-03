from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .models import User
from .schemas import UserCreate, UserUpdate
from src.core.exceptions import NotFoundError, AlreadyExistsError


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        # Check if username or email already exists
        existing_user = self.db.query(User).filter(
            or_(User.username == user_data.username, User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise AlreadyExistsError("User", "username", user_data.username)
            else:
                raise AlreadyExistsError("User", "email", user_data.email)

        user = User(**user_data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        query = self.db.query(User)
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.get_user(user_id)
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Check for conflicts with username/email if they're being updated
        if 'username' in update_data or 'email' in update_data:
            filters = []
            if 'username' in update_data:
                filters.append(User.username == update_data['username'])
            if 'email' in update_data:
                filters.append(User.email == update_data['email'])
            
            existing_user = self.db.query(User).filter(
                or_(*filters),
                User.id != user_id
            ).first()
            
            if existing_user:
                if 'username' in update_data and existing_user.username == update_data['username']:
                    raise AlreadyExistsError("User", "username", update_data['username'])
                if 'email' in update_data and existing_user.email == update_data['email']:
                    raise AlreadyExistsError("User", "email", update_data['email'])

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        self.db.delete(user)
        self.db.commit()
        return True

    def get_user_count(self, search: Optional[str] = None, is_active: Optional[bool] = None) -> int:
        query = self.db.query(User)
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.count()