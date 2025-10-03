from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .models import Category
from .schemas import CategoryCreate, CategoryUpdate
from src.core.exceptions import NotFoundError, AlreadyExistsError


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category_data: CategoryCreate) -> Category:
        # Check if category name already exists
        existing_category = self.db.query(Category).filter(
            Category.name == category_data.name
        ).first()
        
        if existing_category:
            raise AlreadyExistsError("Category", "name", category_data.name)

        category = Category(**category_data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: int) -> Category:
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundError("Category", str(category_id))
        return category

    def get_categories(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[Category]:
        query = self.db.query(Category)
        
        if search:
            query = query.filter(
                or_(
                    Category.name.ilike(f"%{search}%"),
                    Category.description.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()

    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        
        update_data = category_data.model_dump(exclude_unset=True)
        
        # Check for name conflict if name is being updated
        if 'name' in update_data:
            existing_category = self.db.query(Category).filter(
                Category.name == update_data['name'],
                Category.id != category_id
            ).first()
            
            if existing_category:
                raise AlreadyExistsError("Category", "name", update_data['name'])

        for field, value in update_data.items():
            setattr(category, field, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        category = self.get_category(category_id)
        
        # Check if category has recipes
        if category.recipes:
            from src.core.exceptions import ValidationError
            raise ValidationError(f"Cannot delete category '{category.name}' because it has {len(category.recipes)} associated recipes")
        
        self.db.delete(category)
        self.db.commit()
        return True

    def get_category_count(self, search: Optional[str] = None) -> int:
        query = self.db.query(Category)
        
        if search:
            query = query.filter(
                or_(
                    Category.name.ilike(f"%{search}%"),
                    Category.description.ilike(f"%{search}%")
                )
            )
        
        return query.count()