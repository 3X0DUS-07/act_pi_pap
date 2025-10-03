from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.exceptions import RecipeAPIException
from src.users.router import router as users_router
from src.categories.router import router as categories_router
from src.ingredients.router import router as ingredients_router
from src.recipes.router import router as recipes_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Recipe Management API built with FastAPI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS: necesario para que el frontend (HTML/JS) pueda consumir la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción pon solo el dominio de tu front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler
@app.exception_handler(RecipeAPIException)
async def recipe_api_exception_handler(request: Request, exc: RecipeAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": type(exc).__name__}
    )

# Health check básico
@app.get("/", tags=["Health"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "status": "healthy",
        "docs_url": "/docs",
        "api_base_url": "/api/v1"
    }

# Routers principales
app.include_router(users_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(ingredients_router, prefix="/api/v1")
app.include_router(recipes_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
