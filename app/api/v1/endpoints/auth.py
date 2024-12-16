import uuid
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_session
from app.models.user import User, UserCreate, UserRead, UserUpdate

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login")
def login(
    db: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    logger.info(f"Login attempt for user: {form_data.username}")

    user = crud.user.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )

    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    logger.info(f"Successful login for user: {form_data.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/users", response_model=UserRead)
def create_user(
    *,
    db: Session = Depends(get_session),
    user_in: UserCreate,
):
    """Create new user"""
    logger.info(f"Attempting to create user: {user_in.username}")

    user = crud.user.get_user_by_username(db, username=user_in.username)
    if user:
        logger.warning(f"Username already exists: {user_in.username}")
        raise HTTPException(
            status_code=400,
            detail="A user with this username already exists.",
        )

    user = crud.user.create_user(db, user=user_in)
    logger.info(f"User created successfully: {user.username}")
    return user


@router.get("/users", response_model=List[UserRead])
def read_users(
    *,
    db: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
):
    """Retrieve users"""
    logger.info(f"Retrieving users list. Skip: {skip}, Limit: {limit}")
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserRead)
def read_user(
    user_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_session),
):
    """Get a specific user by id"""
    logger.info(f"Retrieving user details for ID: {user_id}")
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    *,
    db: Session = Depends(get_session),
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    """Update a user"""
    logger.info(f"Attempting to update user: {user_id}")
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        logger.warning(f"User not found for update: {user_id}")
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = crud.user.update_user(db, db_user=user, user_update=user_in)
    logger.info(f"User updated successfully: {user_id}")
    return user


@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user(
    *,
    db: Session = Depends(get_session),
    user_id: uuid.UUID,
    current_user: User = Depends(deps.get_current_user),
):
    """Delete a user"""
    logger.info(f"Attempting to delete user: {user_id}")
    user = crud.user.get_user(db, user_id=user_id)
    if not user:
        logger.warning(f"User not found for deletion: {user_id}")
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = crud.user.delete_user(db, user_id=user_id)
    logger.info(f"User deleted successfully: {user_id}")
    return user
