from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException

from app.models.user import UserRole
from app.services.ghibli import GhibliService


class TestGhibliService:
    """Tests for GhibliService"""

    @pytest.fixture
    def mock_ghibli_films_response(self):
        """Mock response for films endpoint"""
        return [
            {
                "id": "2baf70d1-42bb-4437-b551-e5fed5a87abe",
                "title": "Castle in the Sky",
                "director": "Hayao Miyazaki",
            }
        ]

    def test_get_data_by_role_with_cache(
        self,
        mock_ghibli_films_response,
    ):
        """Test getting data from cache when cache is available and has data"""
        with patch("app.services.ghibli.cache") as mock_cache:
            # Setup mock cache
            mock_cache.is_available.return_value = True
            mock_cache.get.return_value = mock_ghibli_films_response

            # Get data for films role
            data = GhibliService.get_data_by_role(UserRole.FILMS)

            # Verify cache was checked and API was not called
            mock_cache.is_available.assert_called_once()
            mock_cache.get.assert_called_once_with("ghibli:/films")
            assert data == mock_ghibli_films_response

    def test_get_data_by_role_without_cache(
        self,
        mock_ghibli_films_response,
    ):
        """Test getting data from API when cache misses"""
        with patch("app.services.ghibli.cache") as mock_cache, patch(
            "app.services.ghibli.requests.get"
        ) as mock_get:
            # Setup mocks
            mock_cache.is_available.return_value = True
            mock_cache.get.return_value = None
            mock_get.return_value = MagicMock(
                json=lambda: mock_ghibli_films_response,
                raise_for_status=MagicMock(),
            )

            # Get data for films role
            data = GhibliService.get_data_by_role(UserRole.FILMS)

            # Verify cache was checked and API was called
            mock_cache.is_available.assert_called()
            mock_cache.get.assert_called_once_with("ghibli:/films")
            mock_get.assert_called_once_with(f"{GhibliService.BASE_URL}/films")
            mock_cache.set.assert_called_once_with(
                "ghibli:/films", mock_ghibli_films_response
            )
            assert data == mock_ghibli_films_response

    def test_get_data_by_role_cache_unavailable(
        self,
        mock_ghibli_films_response,
    ):
        """Test getting data when cache is unavailable"""
        with patch("app.services.ghibli.cache") as mock_cache, patch(
            "app.services.ghibli.requests.get"
        ) as mock_get:
            # Setup mocks
            mock_cache.is_available.return_value = False
            mock_get.return_value = MagicMock(
                json=lambda: mock_ghibli_films_response,
                raise_for_status=MagicMock(),
            )

            # Get data for films role
            data = GhibliService.get_data_by_role(UserRole.FILMS)

            # Verify cache was checked but not used
            mock_cache.is_available.assert_called()
            mock_cache.get.assert_not_called()
            mock_get.assert_called_once_with(f"{GhibliService.BASE_URL}/films")
            assert data == mock_ghibli_films_response

    def test_get_data_by_role_api_error(self):
        """Test handling of API errors"""
        with patch("app.services.ghibli.cache") as mock_cache, patch(
            "app.services.ghibli.requests.get"
        ) as mock_get:
            # Setup mocks
            mock_cache.is_available.return_value = False
            mock_get.side_effect = requests.RequestException("API Error")

            # Verify error handling
            with pytest.raises(HTTPException) as exc_info:
                GhibliService.get_data_by_role(UserRole.FILMS)

            assert exc_info.value.status_code == 500
            assert "error accessing ghibli api" in str(exc_info.value.detail).lower()

    def test_get_data_by_role_invalid_role(self):
        """Test handling of invalid role"""
        with pytest.raises(HTTPException) as exc_info:
            GhibliService.get_data_by_role("invalid_role")

        assert exc_info.value.status_code == 403
        assert "not authorized" in str(exc_info.value.detail).lower()
