import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.session import get_session
from app.main import app
from app.models.user import UserRole


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
            "role": UserRole.FILMS,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == UserRole.FILMS
    assert "password" not in data


def test_create_user_invalid_role(client):
    response = client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": "invalid_role",
        },
    )
    assert response.status_code == 422  # Validation error


def test_login(client):
    # First create a user
    client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "testpass123",
            "role": UserRole.FILMS,
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
            "role": UserRole.FILMS,
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
            "role": UserRole.FILMS,
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
