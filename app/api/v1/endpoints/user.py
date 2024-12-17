import uuid
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import User, UserCreate, UserRead, UserRole, UserUpdate

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=UserRead)
def create_user(
    *,
    db: Session = Depends(deps.get_session),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_user_optional),
):
    """
    Create new user.
    Only superusers can create new users, except for the first user who will be a superuser.
    """
    logger.info(f"Attempting to create user: {user_in.username}")

    # Verificar si existe algún usuario en el sistema
    existing_users = crud.user.get_users(db, skip=0, limit=1)
    is_first_user = len(existing_users) == 0

    # Si no es el primer usuario, verificar que el usuario actual es superusuario
    if not is_first_user and (not current_user or not current_user.is_superuser):
        logger.warning(
            f"Unauthorized attempt to create user by: {getattr(current_user, 'username', 'anonymous')}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create new users",
        )

    # Si es el primer usuario, asegurarse de que sea superusuario
    if is_first_user:
        logger.info("Creating first superuser")
        user_in.is_superuser = True
        user_in.role = UserRole.ADMIN

    # Verificar si el usuario ya existe
    user = crud.user.get_user_by_username(db, username=user_in.username)
    if user:
        logger.warning(f"Username already exists: {user_in.username}")
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists.",
        )
    logger.info(user_in)
    user = crud.user.create_user(db, user=user_in)
    logger.info(f"User created successfully: {user.username}")
    return user


@router.get("/", response_model=List[UserRead])
def read_users(
    *,
    db: Session = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_superuser),
):
    """
    Retrieve users.
    Only accessible to admin users.
    """
    logger.info(
        f"Admin {current_user.username} retrieving users list. Skip: {skip}, Limit: {limit}"
    )
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=UserRead)
def read_user_me(current_user: User = Depends(deps.get_current_active_user)):
    """Get current user."""
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: uuid.UUID,
    db: Session = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_superuser),
):
    """
    Get user by ID.
    Only accessible to admin users.
    """
    logger.info(
        f"Admin {current_user.username} retrieving user details for ID: {user_id}"
    )
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    *,
    db: Session = Depends(deps.get_session),
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_superuser),
):
    """
    Update user.
    Only accessible to admin users.
    """
    logger.info(f"Admin {current_user.username} updating user: {user_id}")
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = crud.user.update_user(db, db_user=user, user_update=user_in)
    return user


@router.delete("/{user_id}", response_model=UserRead)
def delete_user(
    *,
    db: Session = Depends(deps.get_session),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_superuser),
):
    """
    Delete user.
    Only accessible to admin users.
    """
    logger.info(f"Admin {current_user.username} deleting user: {user_id}")
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = crud.user.delete_user(db, user_id=user_id)
    return user
