import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.session import get_session
from app.main import app
from app.models.user import User


@pytest.fixture
def client():
    """
    Create a test client using an in-memory database
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    return TestClient(app)


def test_create_user(client):
    response = client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "user",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data


def test_login(client):
    # First create a user
    client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "user",
        },
    )

    # Then try to login
    response = client.post(
        "/api/v1/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    # First create a user
    client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "user",
        },
    )

    # Then try to login with wrong password
    response = client.post(
        "/api/v1/login", data={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "incorrect username or password" in response.json()["detail"].lower()


def test_get_users(client):
    # First create a user and get token
    client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "user",
        },
    )

    login_response = client.post(
        "/api/v1/login", data={"username": "testuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]

    # Then try to get users list
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
