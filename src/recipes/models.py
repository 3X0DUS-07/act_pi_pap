from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base
from src.ingredients.models import recipe_ingredient_association


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=False)
    prep_time = Column(Integer, nullable=True, comment="Preparation time in minutes")
    cook_time = Column(Integer, nullable=True, comment="Cooking time in minutes")
    servings = Column(Integer, nullable=True, comment="Number of servings")
    difficulty = Column(String(255), nullable=True, comment="easy, medium, hard")
    
    # Foreign keys
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="recipes")
    category = relationship("Category", back_populates="recipes")
    ingredients = relationship("Ingredient", secondary=recipe_ingredient_association, back_populates="recipes")