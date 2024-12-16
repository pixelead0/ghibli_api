import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.core.logging import get_logger
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserUpdate

logger = get_logger(__name__)


def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    logger.debug(f"Fetching user with ID: {user_id}")
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    logger.debug(f"Fetching user by username: {username}")
    statement = select(User).where(User.username == username)
    return db.exec(statement).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    logger.debug(f"Fetching users list with skip: {skip}, limit: {limit}")
    statement = select(User).offset(skip).limit(limit)
    return db.exec(statement).all()


def create_user(db: Session, user: UserCreate) -> User:
    logger.info(f"Creating new user with username: {user.username}")
    try:
        db_user = User(
            username=user.username,
            hashed_password=get_password_hash(user.password),
            role=user.role,
            is_active=True,
            is_superuser=user.is_superuser,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Successfully created user: {user.username}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user {user.username}: {str(e)}", exc_info=True)
        db.rollback()
        raise


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    logger.info(f"Updating user: {db_user.username}")
    try:
        update_data = user_update.dict(exclude_unset=True)

        if "password" in update_data:
            logger.debug("Updating user password")
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        update_data["updated_at"] = datetime.utcnow()

        for field, value in update_data.items():
            logger.debug(f"Updating field {field}")
            setattr(db_user, field, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Successfully updated user: {db_user.username}")
        return db_user
    except Exception as e:
        logger.error(f"Error updating user {db_user.username}: {str(e)}", exc_info=True)
        db.rollback()
        raise


def delete_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    logger.info(f"Deleting user with ID: {user_id}")
    try:
        user = get_user(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            logger.info(f"Successfully deleted user: {user.username}")
        else:
            logger.warning(f"User not found for deletion: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    logger.debug(f"Attempting to authenticate user: {username}")
    user = get_user_by_username(db, username)
    if not user:
        logger.warning(f"Authentication failed: user not found: {username}")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: invalid password for user: {username}")
        return None
    logger.info(f"Successfully authenticated user: {username}")
    return user
