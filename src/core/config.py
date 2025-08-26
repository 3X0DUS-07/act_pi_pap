from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recipe API"
    DATABASE_URL: str = "sqlite:///./app.db"  # Cambia a tu motor preferido
    SECRET_KEY: str = "supersecretkey"  # Reemplázala por una clave más segura
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
