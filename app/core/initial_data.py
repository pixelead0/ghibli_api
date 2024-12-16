from sqlmodel import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.crud.user import create_user
from app.models.user import UserCreate, UserRole

logger = get_logger(__name__)

FIRST_SUPERUSER = {
    "username": "admin",
    "password": "admin123",
    "role": UserRole.ADMIN,
    "is_superuser": True,
}

INITIAL_USERS = [
    {
        "username": "films",
        "password": "test123",
        "role": UserRole.FILMS,
    },
    {
        "username": "people",
        "password": "test123",
        "role": UserRole.PEOPLE,
    },
    {
        "username": "locations",
        "password": "test123",
        "role": UserRole.LOCATIONS,
    },
    {
        "username": "species",
        "password": "test123",
        "role": UserRole.SPECIES,
    },
    {
        "username": "vehicles",
        "password": "test123",
        "role": UserRole.VEHICLES,
    },
]


def init_db(db: Session) -> None:
    """
    Inicializa la base de datos con datos por defecto
    """
    try:
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
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


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
