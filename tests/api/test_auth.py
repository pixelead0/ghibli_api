import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import UserRole
from tests.utils import create_user_in_db

logger = get_logger(__name__)


class TestAuth:
    """Authentication related tests"""

    @pytest.fixture
    def create_test_user(self, session: Session):
        """Create test user for authentication tests"""
        return create_user_in_db(
            session=session,
            username="admin",
            password="admin123",
            role=UserRole.ADMIN,
            is_superuser=True,
        )

    def test_login_success(self, client: TestClient, create_test_user):
        """Test successful login"""
        logger.info(f"Testing login for user: {create_test_user['user'].username}")
        response = client.post(
            f"{settings.API_V1_STR}/login",
            data={
                "username": create_test_user["user"].username,
                "password": create_test_user["password"],
            },
        )
        tokens = response.json()
        assert response.status_code == 200
        assert "access_token" in tokens
        assert tokens["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, create_test_user):
        """Test login with wrong password"""
        logger.info(
            f"Testing login with wrong password for user: {create_test_user['user'].username}"
        )
        response = client.post(
            f"{settings.API_V1_STR}/login",
            data={
                "username": create_test_user["user"].username,
                "password": "wrong",
            },
        )
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_wrong_username(self, client: TestClient):
        """Test login with non-existent username"""
        logger.info("Testing login with non-existent username")
        response = client.post(
            f"{settings.API_V1_STR}/login",
            data={"username": "nonexistent", "password": "wrong"},
        )
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"].lower()

    def test_login_inactive_user(self, client: TestClient, session: Session):
        """Test login with inactive user"""
        user_data = create_user_in_db(
            session=session,
            username="inactive",
            password="password123",
            role=UserRole.FILMS,
            is_active=False,
        )
        logger.info(f"Testing login for inactive user: {user_data['user'].username}")
        response = client.post(
            f"{settings.API_V1_STR}/login",
            data={
                "username": user_data["user"].username,
                "password": user_data["password"],
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user"
