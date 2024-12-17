from sqlmodel import Session, select

from app.core.config import settings
from app.core.logging import get_logger
from app.crud.user import create_user
from app.models.user import User, UserCreate, UserRole

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


def check_if_users_exist(db: Session) -> bool:
    """
    Verifica si ya existen usuarios en la base de datos
    """
    statement = select(User)
    result = db.exec(statement).first()
    return result is not None


def check_if_user_exists(db: Session, username: str) -> bool:
    """
    Verifica si un usuario específico existe
    """
    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()
    return result is not None


def init_db(db: Session) -> None:
    """
    Inicializa la base de datos con datos por defecto solo si está vacía
    """
    try:
        # Primero verificamos si ya existen usuarios
        if check_if_users_exist(db):
            logger.info("Database already initialized with users")
            return

        logger.info("Creating initial data...")

        # Crear superusuario
        if superuser := create_superuser(db):
            logger.info(f"Superuser created: {superuser.username}")
        else:
            logger.info("Superuser already exists")

        # Crear usuarios iniciales
        users_created = 0
        for user_data in INITIAL_USERS:
            if not check_if_user_exists(db, user_data["username"]):
                if user := create_initial_user(db, user_data):
                    users_created += 1
                    logger.info(f"User created: {user.username}")

        logger.info(f"Initial data creation completed. {users_created} users created.")

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def create_superuser(db: Session):
    """
    Crea el superusuario si no existe
    """
    try:
        if not check_if_user_exists(db, FIRST_SUPERUSER["username"]):
            user_in = UserCreate(**FIRST_SUPERUSER)
            user = create_user(db=db, user=user_in)
            return user
        return None
    except Exception as e:
        logger.error(f"Error creating superuser: {str(e)}")
        return None


def create_initial_user(db: Session, user_data: dict):
    """
    Crea un usuario inicial si no existe
    """
    try:
        if not check_if_user_exists(db, user_data["username"]):
            user_in = UserCreate(**user_data)
            user = create_user(db=db, user=user_in)
            return user
        return None
    except Exception as e:
        logger.error(f"Error creating user {user_data['username']}: {str(e)}")
        return None
