import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import UserRole
from tests.utils import create_user_in_db

logger = get_logger(__name__)


class TestUser:
    """User management related tests"""

    def test_create_user(self, client: TestClient, superuser_token_headers):
        """Test user creation by superuser"""
        user_data = {
            "username": "new_user",
            "password": "newpass123",
            "role": UserRole.FILMS,
        }
        logger.info(f"Testing user creation: {user_data['username']}")
        response = client.post(
            f"{settings.API_V1_STR}/users",
            headers=superuser_token_headers,
            json=user_data,
        )
        data = response.json()
        assert response.status_code == 200
        assert data["username"] == user_data["username"]
        assert data["role"] == user_data["role"]

    def test_create_user_existing_username(
        self, client: TestClient, superuser_token_headers, normal_user_token_headers
    ):
        """Test creating user with existing username"""
        user_data = {
            "username": "test_user",  # This username is created in fixtures
            "password": "newpass123",
            "role": UserRole.FILMS,
        }
        logger.info(f"Testing duplicate user creation: {user_data['username']}")
        response = client.post(
            f"{settings.API_V1_STR}/users",
            headers=superuser_token_headers,
            json=user_data,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_get_users_superuser(self, client: TestClient, superuser_token_headers):
        """Test getting all users as superuser"""
        logger.info("Testing get all users as superuser")
        response = client.get(
            f"{settings.API_V1_STR}/users",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0

    def test_get_users_normal_user(self, client: TestClient, normal_user_token_headers):
        """Test getting all users as normal user (should fail)"""
        logger.info("Testing get all users as normal user")
        response = client.get(
            f"{settings.API_V1_STR}/users",
            headers=normal_user_token_headers,
        )
        assert response.status_code == 403
        assert "doesn't have enough privileges" in response.json()["detail"].lower()

    def test_get_user_me(self, client: TestClient, normal_user_token_headers):
        """Test getting current user info"""
        logger.info("Testing get current user info")
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers=normal_user_token_headers,
        )
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "test_user"
        assert user_data["role"] == UserRole.FILMS

    def test_update_user(
        self, client: TestClient, superuser_token_headers, session: Session
    ):
        """Test updating user"""
        user_data = create_user_in_db(
            session=session,
            username="update_test",
            password="password123",
            role=UserRole.FILMS,
        )
        user = user_data["user"]
        logger.info(f"Testing user update: {user.username}")

        user_id = user.id
        assert isinstance(user_id, uuid.UUID), "User ID must be a UUID instance"

        update_data = {
            "username": "updated_name",
            "role": UserRole.PEOPLE,
        }
        response = client.put(
            f"{settings.API_V1_STR}/users/{(user_id)}",
            headers=superuser_token_headers,
            json=update_data,
        )
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["username"] == update_data["username"]
        assert updated_user["role"] == update_data["role"]

    def test_delete_user(
        self, client: TestClient, superuser_token_headers, session: Session
    ):
        """Test deleting user"""
        user_data = create_user_in_db(
            session=session,
            username="delete_test",
            password="password123",
            role=UserRole.FILMS,
        )
        user = user_data["user"]
        logger.info(f"Testing user deletion: {user.username}")

        user_id = user.id
        assert isinstance(user_id, uuid.UUID), "User ID must be a UUID instance"

        response = client.delete(
            f"{settings.API_V1_STR}/users/{user_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        deleted_user = response.json()
        assert deleted_user["username"] == user.username

        # Verify user is deleted
        get_response = client.get(
            f"{settings.API_V1_STR}/users/{user_id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404
