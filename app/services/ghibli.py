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
    def get_data_by_role(cls, role: UserRole):
        """
        Obtiene datos de la API de Studio Ghibli según el rol del usuario,
        utilizando caché cuando esté disponible
        """
        if role == UserRole.ADMIN:
            return cls.get_all_data()

        endpoint = cls.ROLE_ENDPOINTS.get(role)
        if not endpoint:
            raise HTTPException(
                status_code=403, detail="Role not authorized to access Ghibli API"
            )

        # Intentar obtener datos del caché
        cache_key = f"ghibli:{endpoint}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for {endpoint}")
            return cached_data

        try:
            response = requests.get(f"{cls.BASE_URL}{endpoint}")
            response.raise_for_status()
            data = response.json()

            # Guardar en caché
            cache.set(cache_key, data)
            logger.info(f"Data fetched and cached for {endpoint}")
            return data
        except requests.RequestException as e:
            logger.error(f"Error accessing Ghibli API: {str(e)}")
            raise HTTPException(status_code=500, detail="Error accessing Ghibli API")

    @classmethod
    def get_all_data(cls):
        """
        Obtiene todos los datos de la API (solo para admin)
        """
        cache_key = "ghibli:all_data"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached data for all endpoints")
            return cached_data

        all_data = {}
        for endpoint in cls.ROLE_ENDPOINTS.values():
            try:
                response = requests.get(f"{cls.BASE_URL}{endpoint}")
                response.raise_for_status()
                all_data[endpoint.strip("/")] = response.json()
            except requests.RequestException as e:
                logger.error(f"Error accessing {endpoint}: {str(e)}")

        # Guardar en caché
        if all_data:
            cache.set(cache_key, all_data)
            logger.info("All data fetched and cached")

        return all_data
