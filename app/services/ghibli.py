import requests
from fastapi import HTTPException

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
        Obtiene datos de la API de Studio Ghibli según el rol del usuario
        """
        if role == UserRole.ADMIN:
            return cls.get_all_data()

        endpoint = cls.ROLE_ENDPOINTS.get(role)
        if not endpoint:
            raise HTTPException(
                status_code=403, detail="Role not authorized to access Ghibli API"
            )

        try:
            response = requests.get(f"{cls.BASE_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error accessing Ghibli API: {str(e)}")
            raise HTTPException(status_code=500, detail="Error accessing Ghibli API")

    @classmethod
    def get_all_data(cls):
        """
        Obtiene todos los datos de la API (solo para admin)
        """
        all_data = {}
        for endpoint in cls.ROLE_ENDPOINTS.values():
            try:
                response = requests.get(f"{cls.BASE_URL}{endpoint}")
                response.raise_for_status()
                all_data[endpoint.strip("/")] = response.json()
            except requests.RequestException as e:
                logger.error(f"Error accessing {endpoint}: {str(e)}")

        return all_data
