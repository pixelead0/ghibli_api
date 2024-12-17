from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import UserRole
from app.services.ghibli import GhibliService
from tests.utils import create_user_in_db

logger = get_logger(__name__)


# Fixtures a nivel de módulo
@pytest.fixture
def mock_ghibli_films_response():
    """Mock response for films endpoint"""
    return [
        {
            "id": "2baf70d1-42bb-4437-b551-e5fed5a87abe",
            "title": "Castle in the Sky",
            "original_title": "天空の城ラピュタ",
            "original_title_romanised": "Tenkū no shiro Rapyuta",
            "description": "The orphan Sheeta inherited a mysterious crystal...",
            "director": "Hayao Miyazaki",
            "producer": "Isao Takahata",
            "release_date": "1986",
            "running_time": "124",
            "rt_score": "95",
        },
    ]


@pytest.fixture
def mock_ghibli_people_response():
    """Mock response for people endpoint"""
    return [
        {
            "id": "fe93adf2-2f3a-4ec4-9f68-5422f1b87c01",
            "name": "Pazu",
            "gender": "Male",
            "age": "13",
            "eye_color": "Black",
            "hair_color": "Brown",
        },
    ]


class TestGhibliEndpoint:
    """Tests for Ghibli API endpoints"""

    def test_get_ghibli_data_films_role(
        self,
        client: TestClient,
        session: Session,
        mock_ghibli_films_response,
    ):
        """Test getting Ghibli data with films role"""
        # Create user with films role
        user_data = create_user_in_db(
            session=session,
            username="films_user",
            password="test123",
            role=UserRole.FILMS,
        )

        # Login to get access token
        response = client.post(
            f"{settings.API_V1_STR}/login",
            data={
                "username": user_data["user"].username,
                "password": user_data["password"],
            },
        )
        tokens = response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Mock the Ghibli API response
        with patch("app.services.ghibli.requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_ghibli_films_response
            mock_get.return_value.raise_for_status = MagicMock()

            response = client.get(
                f"{settings.API_V1_STR}/ghibli/",
                headers=headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["title"] == "Castle in the Sky"

    def test_get_ghibli_data_admin_role(
        self,
        client: TestClient,
        superuser_token_headers,
        mock_ghibli_films_response,
        mock_ghibli_people_response,
    ):
        """Test getting all Ghibli data with admin role"""
        # Mock the Ghibli API responses for all endpoints
        with patch("app.services.ghibli.requests.get") as mock_get:

            def mock_get_response(*args, **kwargs):
                url = args[0]
                mock_response = MagicMock()
                mock_response.raise_for_status = MagicMock()

                if "/films" in url:
                    mock_response.json.return_value = mock_ghibli_films_response
                elif "/people" in url:
                    mock_response.json.return_value = mock_ghibli_people_response
                else:
                    mock_response.json.return_value = []

                return mock_response

            mock_get.side_effect = mock_get_response

            response = client.get(
                f"{settings.API_V1_STR}/ghibli/",
                headers=superuser_token_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "films" in data
            assert "people" in data
            assert len(data["films"]) == 1
            assert len(data["people"]) == 1

    def test_get_ghibli_data_unauthorized(self, client: TestClient):
        """Test getting Ghibli data without authentication"""
        response = client.get(f"{settings.API_V1_STR}/ghibli/")
        assert response.status_code == 401
        assert "could not validate credentials" in response.json()["detail"].lower()
