from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text
from typing import List, Optional
from .models import Recipe
from .schemas import RecipeCreate, RecipeUpdate, RecipeIngredientCreate, RecipeIngredientUpdate, DifficultyLevel
from src.users.models import User
from src.categories.models import Category
from src.ingredients.models import Ingredient, recipe_ingredient_association
from src.core.exceptions import NotFoundError, ValidationError


class RecipeService:
    def __init__(self, db: Session):
        self.db = db

    def create_recipe(self, recipe_data: RecipeCreate) -> Recipe:
        # Validate author exists
        author = self.db.query(User).filter(User.id == recipe_data.author_id).first()
        if not author:
            raise NotFoundError("User", str(recipe_data.author_id))
        
        # Validate category exists
        category = self.db.query(Category).filter(Category.id == recipe_data.category_id).first()
        if not category:
            raise NotFoundError("Category", str(recipe_data.category_id))
        
        # Create recipe
        recipe_dict = recipe_data.model_dump(exclude={'ingredient_ids'})
        recipe = Recipe(**recipe_dict)
        
        # Add ingredients if provided
        if recipe_data.ingredient_ids:
            ingredients = self.db.query(Ingredient).filter(
                Ingredient.id.in_(recipe_data.ingredient_ids)
            ).all()
            
            if len(ingredients) != len(recipe_data.ingredient_ids):
                found_ids = [ing.id for ing in ingredients]
                missing_ids = set(recipe_data.ingredient_ids) - set(found_ids)
                raise NotFoundError("Ingredients", f"IDs: {list(missing_ids)}")
            
            recipe.ingredients = ingredients

        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def get_recipe(self, recipe_id: int) -> Recipe:
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise NotFoundError("Recipe", str(recipe_id))
        return recipe

    def get_recipes(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        difficulty: Optional[DifficultyLevel] = None,
        max_prep_time: Optional[int] = None,
        max_cook_time: Optional[int] = None
    ) -> List[Recipe]:
        query = self.db.query(Recipe)
        
        if search:
            query = query.filter(
                or_(
                    Recipe.title.ilike(f"%{search}%"),
                    Recipe.description.ilike(f"%{search}%"),
                    Recipe.instructions.ilike(f"%{search}%")
                )
            )
        
        if category_id:
            query = query.filter(Recipe.category_id == category_id)
            
        if author_id:
            query = query.filter(Recipe.author_id == author_id)
            
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty.value)
            
        if max_prep_time:
            query = query.filter(Recipe.prep_time <= max_prep_time)
            
        if max_cook_time:
            query = query.filter(Recipe.cook_time <= max_cook_time)
        
        return query.offset(skip).limit(limit).all()

    def update_recipe(self, recipe_id: int, recipe_data: RecipeUpdate) -> Recipe:
        recipe = self.get_recipe(recipe_id)
        
        update_data = recipe_data.model_dump(exclude_unset=True, exclude={'ingredient_ids'})
        
        # Validate category if being updated
        if 'category_id' in update_data:
            category = self.db.query(Category).filter(Category.id == update_data['category_id']).first()
            if not category:
                raise NotFoundError("Category", str(update_data['category_id']))

        # Update basic fields
        for field, value in update_data.items():
            setattr(recipe, field, value)

        # Update ingredients if provided
        if recipe_data.ingredient_ids is not None:
            if recipe_data.ingredient_ids:
                ingredients = self.db.query(Ingredient).filter(
                    Ingredient.id.in_(recipe_data.ingredient_ids)
                ).all()
                
                if len(ingredients) != len(recipe_data.ingredient_ids):
                    found_ids = [ing.id for ing in ingredients]
                    missing_ids = set(recipe_data.ingredient_ids) - set(found_ids)
                    raise NotFoundError("Ingredients", f"IDs: {list(missing_ids)}")
                
                recipe.ingredients = ingredients
            else:
                recipe.ingredients = []

        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe_id: int) -> bool:
        recipe = self.get_recipe(recipe_id)
        self.db.delete(recipe)
        self.db.commit()
        return True

    def add_ingredient_to_recipe(self, recipe_id: int, ingredient_data: RecipeIngredientCreate) -> Recipe:
        recipe = self.get_recipe(recipe_id)
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_data.ingredient_id).first()
        
        if not ingredient:
            raise NotFoundError("Ingredient", str(ingredient_data.ingredient_id))
        
        # Check if ingredient is already in recipe
        if ingredient in recipe.ingredients:
            raise ValidationError(f"Ingredient '{ingredient.name}' is already in this recipe")
        
        # Add ingredient with quantity and notes
        recipe.ingredients.append(ingredient)
        
        # Update the association table with quantity and notes if provided
        if ingredient_data.quantity or ingredient_data.notes:
            stmt = recipe_ingredient_association.update().where(
                and_(
                    recipe_ingredient_association.c.recipe_id == recipe_id,
                    recipe_ingredient_association.c.ingredient_id == ingredient_data.ingredient_id
                )
            ).values(
                quantity=ingredient_data.quantity,
                notes=ingredient_data.notes
            )
            self.db.execute(stmt)
        
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def remove_ingredient_from_recipe(self, recipe_id: int, ingredient_id: int) -> Recipe:
        recipe = self.get_recipe(recipe_id)
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        
        if not ingredient:
            raise NotFoundError("Ingredient", str(ingredient_id))
        
        if ingredient not in recipe.ingredients:
            raise ValidationError(f"Ingredient '{ingredient.name}' is not in this recipe")
        
        recipe.ingredients.remove(ingredient)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def update_recipe_ingredient(self, recipe_id: int, ingredient_id: int, ingredient_data: RecipeIngredientUpdate) -> Recipe:
        recipe = self.get_recipe(recipe_id)
        ingredient = self.db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        
        if not ingredient:
            raise NotFoundError("Ingredient", str(ingredient_id))
        
        if ingredient not in recipe.ingredients:
            raise ValidationError(f"Ingredient '{ingredient.name}' is not in this recipe")
        
        # Update the association table
        update_data = ingredient_data.model_dump(exclude_unset=True)
        if update_data:
            stmt = recipe_ingredient_association.update().where(
                and_(
                    recipe_ingredient_association.c.recipe_id == recipe_id,
                    recipe_ingredient_association.c.ingredient_id == ingredient_id
                )
            ).values(**update_data)
            self.db.execute(stmt)
            self.db.commit()
        
        self.db.refresh(recipe)
        return recipe

    def get_recipe_count(
        self, 
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        difficulty: Optional[DifficultyLevel] = None,
        max_prep_time: Optional[int] = None,
        max_cook_time: Optional[int] = None
    ) -> int:
        query = self.db.query(Recipe)
        
        if search:
            query = query.filter(
                or_(
                    Recipe.title.ilike(f"%{search}%"),
                    Recipe.description.ilike(f"%{search}%"),
                    Recipe.instructions.ilike(f"%{search}%")
                )
            )
        
        if category_id:
            query = query.filter(Recipe.category_id == category_id)
            
        if author_id:
            query = query.filter(Recipe.author_id == author_id)
            
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty.value)
            
        if max_prep_time:
            query = query.filter(Recipe.prep_time <= max_prep_time)
            
        if max_cook_time:
            query = query.filter(Recipe.cook_time <= max_cook_time)
        
        return query.count()