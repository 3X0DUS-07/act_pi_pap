from sqlalchemy import Column, Integer, String
from src.core.database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    unit = Column(String(50), nullable=True)  # Ej: "gramos", "ml", "cucharadas"
