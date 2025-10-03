from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .models import Ingredient
from .schemas import IngredientCreate, IngredientUpdate
from src.core.exceptions import NotFoundError, AlreadyExistsError


class IngredientService:
    def __init__(self, db: Session):
        self.db = db

    def create_ingredient(self, ingredient_data: IngredientCreate) -> Ingredient:
        # Check if ingredient name already exists
        existing_ingredient = self.db.query(Ingredient).filter(
            Ingredient.name == ingredient_data.name
        ).first()
        
        if existing_ingredient:
            raise AlreadyExistsError("Ingredient", "name", ingredient_data.name)

        ingredient = Ingredient(**ingredient_data.model_dump())
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient

    def get_ingredient(self, ingredient_id: int) -> Ingredient:
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        if not ingredient:
            raise NotFoundError("Ingredient", str(ingredient_id))
        return ingredient

    def get_ingredients(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[Ingredient]:
        query = self.db.query(Ingredient)
        
        if search:
            query = query.filter(
                or_(
                    Ingredient.name.ilike(f"%{search}%"),
                    Ingredient.description.ilike(f"%{search}%"),
                    Ingredient.unit.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()

    def update_ingredient(self, ingredient_id: int, ingredient_data: IngredientUpdate) -> Ingredient:
        ingredient = self.get_ingredient(ingredient_id)
        
        update_data = ingredient_data.model_dump(exclude_unset=True)
        
        # Check for name conflict if name is being updated
        if 'name' in update_data:
            existing_ingredient = self.db.query(Ingredient).filter(
                Ingredient.name == update_data['name'],
                Ingredient.id != ingredient_id
            ).first()
            
            if existing_ingredient:
                raise AlreadyExistsError("Ingredient", "name", update_data['name'])

        for field, value in update_data.items():
            setattr(ingredient, field, value)

        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient

    def delete_ingredient(self, ingredient_id: int) -> bool:
        ingredient = self.get_ingredient(ingredient_id)
        
        # Check if ingredient is used in recipes
        if ingredient.recipes:
            from src.core.exceptions import ValidationError
            raise ValidationError(f"Cannot delete ingredient '{ingredient.name}' because it is used in {len(ingredient.recipes)} recipes")
        
        self.db.delete(ingredient)
        self.db.commit()
        return True

    def get_ingredient_count(self, search: Optional[str] = None) -> int:
        query = self.db.query(Ingredient)
        
        if search:
            query = query.filter(
                or_(
                    Ingredient.name.ilike(f"%{search}%"),
                    Ingredient.description.ilike(f"%{search}%"),
                    Ingredient.unit.ilike(f"%{search}%")
                )
            )
        
        return query.count()