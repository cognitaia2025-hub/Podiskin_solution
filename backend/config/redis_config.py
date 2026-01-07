"""
Configuración de Redis
======================
Para rate limiting, sesiones y blacklist de tokens en producción
"""

import os
from typing import Optional
import redis.asyncio as redis

class RedisConfig:
    """Configuración de Redis"""
    
    def __init__(self):
        self.enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.decode_responses = True
        
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> Optional[redis.Redis]:
        """
        Obtiene cliente de Redis.
        
        Returns:
            Cliente de Redis o None si está deshabilitado
        """
        if not self.enabled:
            return None
        
        if self._client is None:
            self._client = await redis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                decode_responses=self.decode_responses
            )
        
        return self._client
    
    async def close(self):
        """Cierra la conexión a Redis"""
        if self._client:
            await self._client.close()
            self._client = None

# Instancia global
redis_config = RedisConfig()

async def get_redis_client() -> Optional[redis.Redis]:
    """
    Helper function para obtener cliente de Redis.
    
    Returns:
        Cliente de Redis o None si está deshabilitado
    """
    return await redis_config.get_client()
