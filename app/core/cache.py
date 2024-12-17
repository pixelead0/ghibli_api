import json
from typing import Any, Optional

import redis
from redis.exceptions import ConnectionError, RedisError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    _instance = None
    _is_connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.redis_client = None
            self.default_ttl = settings.REDIS_TTL
            self.initialized = True
            self._connect()

    def _connect(self) -> None:
        """
        Intenta establecer conexión con Redis
        """
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            # Verificar conexión
            self.redis_client.ping()
            self._is_connected = True
            logger.info("Successfully connected to Redis")
        except (ConnectionError, RedisError) as e:
            self._is_connected = False
            logger.warning(f"Could not connect to Redis: {str(e)}")
            self.redis_client = None

    def is_available(self) -> bool:
        """
        Verifica si Redis está disponible
        """
        if not self._is_connected:
            self._connect()
        return self._is_connected

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché
        """
        if not self.is_available():
            return None

        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(data)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except (ConnectionError, RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            self._is_connected = False
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Establece un valor en el caché
        """
        if not self.is_available():
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache set for key: {key}")
            return True
        except (ConnectionError, RedisError, TypeError) as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            self._is_connected = False
            return False

    def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché
        """
        if not self.is_available():
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache deleted for key: {key}")
            return True
        except (ConnectionError, RedisError) as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            self._is_connected = False
            return False

    def clear(self) -> bool:
        """
        Limpia todo el caché
        """
        if not self.is_available():
            return False

        try:
            self.redis_client.flushdb()
            logger.info("Cache cleared")
            return True
        except (ConnectionError, RedisError) as e:
            logger.error(f"Error clearing cache: {str(e)}")
            self._is_connected = False
            return False


# Instancia global del caché
cache = RedisCache()
