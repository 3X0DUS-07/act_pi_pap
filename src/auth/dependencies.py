from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.auth import service, models
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = service.decode_access_token(token)
        if payload is None:
            raise credentials_exception
        user = db.query(models.User).filter(models.User.id == payload.get("sub")).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
    return user
