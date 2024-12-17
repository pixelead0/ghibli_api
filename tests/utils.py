import uuid
from typing import Dict, Union

from sqlmodel import Session

from app.core.security import get_password_hash
from app.models.user import User, UserRole


def create_user_in_db(
    session: Session,
    username: str,
    password: str,
    role: UserRole = UserRole.FILMS,
    is_superuser: bool = False,
    is_active: bool = True,
    user_id: uuid.UUID = None,
) -> Dict[str, Union[User, str]]:
    """
    Helper function to create a user in the database and return user object and raw password.

    Args:
        session: Database session
        username: Username for the new user
        password: Raw password for the new user
        role: User role
        is_superuser: Whether the user is a superuser
        is_active: Whether the user is active
        user_id: Optional UUID for the user (generates new one if not provided)

    Returns:
        Dictionary containing user object and raw password
    """
    if user_id is None:
        user_id = uuid.uuid4()
    elif isinstance(user_id, str):
        user_id = uuid.UUID(user_id)

    user = User(
        id=user_id,
        username=username,
        hashed_password=get_password_hash(password),
        role=role,
        is_superuser=is_superuser,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "user": user,
        "password": password,
    }
