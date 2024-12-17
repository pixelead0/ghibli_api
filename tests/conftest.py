"""
Test configuration and fixtures.
This module contains all the shared fixtures for testing.
"""

from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_session
from app.main import app
from app.models.user import UserRole
from tests.utils import create_user_in_db

logger = get_logger(__name__)

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create a fresh database session for a test.

    Yields:
        Session: SQLModel session
    """
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> TestClient:
    """
    Create a new FastAPI TestClient with a fresh database session.

    Args:
        session: The database session fixture

    Returns:
        TestClient: FastAPI test client
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="superuser_token_headers")
def superuser_token_headers_fixture(
    client: TestClient, session: Session
) -> Dict[str, str]:
    """
    Create superuser and return token headers.

    Args:
        client: FastAPI test client
        session: Database session

    Returns:
        Dict containing Authorization header with token
    """
    user_data = create_user_in_db(
        session=session,
        username="admin",
        password="admin123",
        role=UserRole.ADMIN,
        is_superuser=True,
    )

    response = client.post(
        f"{settings.API_V1_STR}/login",
        data={
            "username": user_data["user"].username,
            "password": user_data["password"],
        },
    )
    tokens = response.json()
    logger.info(f"Superuser token generated for user: {user_data['user'].username}")
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(name="normal_user_token_headers")
def normal_user_token_headers_fixture(
    client: TestClient, session: Session
) -> Dict[str, str]:
    """
    Create normal user and return token headers.

    Args:
        client: FastAPI test client
        session: Database session

    Returns:
        Dict containing Authorization header with token
    """
    user_data = create_user_in_db(
        session=session,
        username="test_user",
        password="test123",
        role=UserRole.FILMS,
    )

    response = client.post(
        f"{settings.API_V1_STR}/login",
        data={
            "username": user_data["user"].username,
            "password": user_data["password"],
        },
    )
    tokens = response.json()
    logger.info(f"Normal user token generated for user: {user_data['user'].username}")
    return {"Authorization": f"Bearer {tokens['access_token']}"}
