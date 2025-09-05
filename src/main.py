from fastapi import FastAPI
from src.recetas.router import router as recetas_router
from src.ingredientes.router import router as ingredientes_router
from src.categorias.router import router as categorias_router
# Si tienes un router de autenticación, impórtalo también:
# from src.auth.router import router as auth_router

app = FastAPI(
    title="API de Gestión de Recetas",
    description="API para gestionar recetas, ingredientes y categorías.",
    version="0.1.0"
)

# Incluir routers principales
app.include_router(recetas_router)
app.include_router(ingredientes_router)
app.include_router(categorias_router)
# Si tienes autenticación:
# app.include_router(auth_router)

# Ruta raíz opcional
@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Gestión de Recetas"}