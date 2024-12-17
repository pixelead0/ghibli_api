import requests
from fastapi import HTTPException

from app.core.cache import cache
from app.core.logging import get_logger
from app.models.user import UserRole

logger = get_logger(__name__)


class GhibliService:
    BASE_URL = "https://ghibli.rest"

    ROLE_ENDPOINTS = {
        UserRole.FILMS: "/films",
        UserRole.PEOPLE: "/people",
        UserRole.LOCATIONS: "/locations",
        UserRole.SPECIES: "/species",
        UserRole.VEHICLES: "/vehicles",
    }

    @classmethod
    def _fetch_from_api(cls, endpoint: str) -> dict:
        """
        Obtiene datos directamente de la API
        """
        try:
            response = requests.get(f"{cls.BASE_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, Exception) as e:
            logger.error(f"Error accessing Ghibli API at {endpoint}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error accessing Ghibli API: {str(e)}"
            ) from e

    @classmethod
    def get_data_by_role(cls, role: UserRole):
        """
        Obtiene datos de Studio Ghibli API según el rol del usuario
        """
        if role == UserRole.ADMIN:
            return cls.get_all_data()

        endpoint = cls.ROLE_ENDPOINTS.get(role)
        if not endpoint:
            raise HTTPException(
                status_code=403, detail="Role not authorized to access Ghibli API"
            )

        # Intentar obtener datos del caché solo si está disponible
        if cache.is_available():
            cache_key = f"ghibli:{endpoint}"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached data for {endpoint}")
                return cached_data

        # Si no hay caché o no hay datos en caché, obtener de la API
        data = cls._fetch_from_api(endpoint)

        # Intentar guardar en caché si está disponible
        if cache.is_available():
            cache_key = f"ghibli:{endpoint}"
            cache.set(cache_key, data)
            logger.info(f"Data fetched and cached for {endpoint}")
        else:
            logger.warning("Cache not available, serving data directly from API")

        return data

    @classmethod
    def get_all_data(cls):
        """
        Obtiene todos los datos de la API (solo para admin)
        """
        if cache.is_available():
            cache_key = "ghibli:all_data"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("Returning cached all data")
                return cached_data

        all_data = {}
        try:
            for endpoint in cls.ROLE_ENDPOINTS.values():
                data = cls._fetch_from_api(endpoint)
                all_data[endpoint.strip("/")] = data

            # Intentar guardar en caché si está disponible
            if cache.is_available() and all_data:
                cache_key = "ghibli:all_data"
                cache.set(cache_key, all_data)
                logger.info("All data fetched and cached")

            return all_data
        except HTTPException as e:
            logger.error(f"Error fetching all data: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error fetching data from Ghibli API"
            ) from e
