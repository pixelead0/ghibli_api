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

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login")
def login(
    db: Session = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
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
