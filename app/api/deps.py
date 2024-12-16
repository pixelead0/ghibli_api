import uuid
from typing import Generator, Optional

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_current_user(
    db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> User:
    logger.debug("Verifying authentication token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("Token payload does not contain user ID")
            raise credentials_exception

        logger.debug(f"Token contains user ID: {user_id}")

    except JWTError as e:
        logger.error(f"Error decoding JWT token: {str(e)}")
        raise credentials_exception

    user = crud.user.get_user(db, user_id=uuid.UUID(user_id))

    if user is None:
        logger.error(f"User not found for ID: {user_id}")
        raise credentials_exception

    logger.debug(f"Successfully authenticated user: {user.username}")
    return user


def verify_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica si el usuario actual es un administrador
    """
    logger.debug(f"Verifying admin privileges for user: {current_user.username}")

    if not current_user.is_superuser:
        logger.warning(
            f"Unauthorized admin access attempt by user: {current_user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    logger.debug(f"Admin privileges verified for user: {current_user.username}")
    return current_user


def verify_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica si el usuario actual está activo
    """
    logger.debug(f"Verifying active status for user: {current_user.username}")

    if not current_user.is_active:
        logger.warning(f"Inactive user attempt to access: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    logger.debug(f"Active status verified for user: {current_user.username}")
    return current_user
