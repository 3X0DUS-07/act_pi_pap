from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recipe API"
    DATABASE_URL: str = "sqlite:///./app.db" 
    SECRET_KEY: str = "1234"  
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
