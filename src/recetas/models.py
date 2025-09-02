from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.core.database import Base

# Relación Many-to-Many entre recetas e ingredientes
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", backref="recipes")

    ingredients = relationship("Ingredient", secondary=recipe_ingredient, backref="recipes")
