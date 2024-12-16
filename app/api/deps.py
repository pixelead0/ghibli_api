import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_session
from app.models.user import User

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login", auto_error=False
)


def get_current_user_optional(
    db: Session = Depends(get_session),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Verifica el token de autenticación y retorna el usuario actual si existe
    Si no hay token o es inválido, retorna None en lugar de lanzar una excepción
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user = crud.user.get_user(db, user_id=uuid.UUID(user_id))
        if user is None:
            return None

        return user
    except JWTError:
        return None


def get_current_user(
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """
    Verifica el token de autenticación y retorna el usuario actual
    Lanza una excepción si no hay token o es inválido
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifica que el usuario actual esté activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verifica que el usuario actual sea un superusuario
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
