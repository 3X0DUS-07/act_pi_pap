from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


# Association table for many-to-many relationship between recipes and ingredients
recipe_ingredient_association = Table(
    'recipe_ingredients',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True),
    Column('quantity', String(255), nullable=True),  # e.g., "2 cups", "1 kg", "3 units"
    Column('notes', Text, nullable=True)  # Additional notes about the ingredient in this recipe
)


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(255), nullable=True)  # Default unit (e.g., "cups", "grams", "units")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    recipes = relationship("Recipe", secondary=recipe_ingredient_association, back_populates="ingredients")