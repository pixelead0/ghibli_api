import json
from typing import Any, Optional

import redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
        )
        self.default_ttl = settings.REDIS_TTL

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché
        """
        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(data)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Establece un valor en el caché
        """
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache set for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """
        Elimina un valor del caché
        """
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache deleted for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False

    def clear(self) -> bool:
        """
        Limpia todo el caché
        """
        try:
            self.redis_client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False


# Instancia global del caché
cache = RedisCache()
