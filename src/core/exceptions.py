from fastapi import HTTPException, status

def not_found_exception(entity: str = "Recurso"):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} no encontrado")

def unauthorized_exception():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")

def forbidden_exception():
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
