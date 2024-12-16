import os
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

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


def get_auth_token(client, role: UserRole = UserRole.FILMS):
    """Helper function to get authentication token"""
    # Create user
    client.post(
        "/api/v1/users",
        json={
            "username": f"test_{role}_user",
            "password": "testpass123",
            "role": role,
        },
    )

    # Login and get token
    response = client.post(
        "/api/v1/login",
        data={"username": f"test_{role}_user", "password": "testpass123"},
    )
    return response.json()["access_token"]


@patch("requests.get")
def test_get_films(mock_get, client):
    mock_get.return_value.json.return_value = [{"title": "My Neighbor Totoro"}]
    mock_get.return_value.status_code = 200

    token = get_auth_token(client, UserRole.FILMS)
    response = client.get(
        "/api/v1/ghibli", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == [{"title": "My Neighbor Totoro"}]
    mock_get.assert_called_once_with("https://ghibli.rest/films")


@patch("requests.get")
def test_get_people(mock_get, client):
    mock_get.return_value.json.return_value = [{"name": "Totoro"}]
    mock_get.return_value.status_code = 200

    token = get_auth_token(client, UserRole.PEOPLE)
    response = client.get(
        "/api/v1/ghibli", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == [{"name": "Totoro"}]
    mock_get.assert_called_once_with("https://ghibli.rest/people")


@patch("requests.get")
def test_admin_gets_all_data(mock_get, client):
    mock_responses = {
        "/films": [{"title": "Totoro"}],
        "/people": [{"name": "Mei"}],
        "/locations": [{"name": "Forest"}],
        "/species": [{"name": "Cat"}],
        "/vehicles": [{"name": "Catbus"}],
    }

    def mock_get_side_effect(url):
        for endpoint, response in mock_responses.items():
            if url.endswith(endpoint):
                mock_response = type(
                    "MockResponse",
                    (),
                    {
                        "json": lambda: response,
                        "status_code": 200,
                        "raise_for_status": lambda: None,
                    },
                )
                return mock_response
        return None

    mock_get.side_effect = mock_get_side_effect

    token = get_auth_token(client, UserRole.ADMIN)
    response = client.get(
        "/api/v1/ghibli", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "films" in data
    assert "people" in data
    assert "locations" in data
    assert "species" in data
    assert "vehicles" in data

    assert mock_get.call_count == 5


def test_unauthorized_access(client):
    response = client.get("/api/v1/ghibli")
    assert response.status_code == 401
