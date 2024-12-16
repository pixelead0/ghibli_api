import asyncio

from sqlmodel import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.crud.user import create_user
from app.models.user import UserCreate

logger = get_logger(__name__)

FIRST_SUPERUSER = {
    "username": "admin",
    "password": "admin123",
    "role": "admin",
    "is_superuser": True,
}

INITIAL_USERS = [
    {
        "username": "films_user",
        "password": "films123",
        "role": "films",
    },
    {
        "username": "people_user",
        "password": "people123",
        "role": "people",
    },
    {
        "username": "locations_user",
        "password": "locations123",
        "role": "locations",
    },
    {
        "username": "species_user",
        "password": "species123",
        "role": "species",
    },
]


def init_db(db: Session) -> None:
    """
    Inicializa la base de datos con datos por defecto
    """
    # Crear superusuario
    if superuser := create_superuser(db):
        logger.info(f"Superuser created: {superuser.username}")
    else:
        logger.info("Superuser already exists")

    # Crear usuarios iniciales
    for user_data in INITIAL_USERS:
        if user := create_initial_user(db, user_data):
            logger.info(f"User created: {user.username}")
        else:
            logger.info(f"User already exists: {user_data['username']}")


def create_superuser(db: Session):
    """
    Crea el superusuario si no existe
    """
    try:
        user_in = UserCreate(**FIRST_SUPERUSER)
        user = create_user(db=db, user=user_in)
        return user
    except Exception as e:
        logger.warning(f"Error creating superuser: {str(e)}")
        return None


def create_initial_user(db: Session, user_data: dict):
    """
    Crea un usuario inicial si no existe
    """
    try:
        user_in = UserCreate(**user_data)
        user = create_user(db=db, user=user_in)
        return user
    except Exception as e:
        logger.warning(f"Error creating user {user_data['username']}: {str(e)}")
        return None
