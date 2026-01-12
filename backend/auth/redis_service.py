"""
Redis Service para Autenticación
=================================
Servicio unificado para rate limiting, token blacklist y refresh tokens
usando Redis cuando está disponible, fallback a memoria local.
"""

import os
import time
import logging
from typing import Optional, Set, Dict, List, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Intentar importar Redis
try:
    from config.redis_config import get_redis_client
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory storage")


class AuthRedisService:
    """
    Servicio para rate limiting, token blacklist y refresh tokens.
    Usa Redis si está disponible, fallback a memoria local.
    """
    
    def __init__(self):
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        
        # Almacenamiento en memoria (fallback)
        self._login_attempts: Dict[str, List[float]] = {}
        self._token_blacklist: Set[str] = set()
        self._refresh_tokens: Dict[str, dict] = {}
        
        logger.info(f"AuthRedisService initialized - Redis: {self.redis_enabled}")
    
    async def _get_redis(self):
        """Helper para obtener cliente Redis si está disponible"""
        if not self.redis_enabled or not REDIS_AVAILABLE:
            return None
        try:
            return await get_redis_client()
        except Exception as e:
            logger.error(f"Error getting Redis client: {e}")
            return None
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    async def check_rate_limit(
        self, 
        username: str, 
        max_attempts: int = 10, 
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Verifica rate limit para login attempts.
        
        Args:
            username: Identificador del usuario
            max_attempts: Máximo de intentos permitidos
            window_seconds: Ventana de tiempo en segundos
            
        Returns:
            Tupla (permitido: bool, segundos_para_reintentar: int)
        """
        redis = await self._get_redis()
        
        if redis:
            return await self._check_rate_limit_redis(redis, username, max_attempts, window_seconds)
        else:
            return self._check_rate_limit_memory(username, max_attempts, window_seconds)
    
    async def _check_rate_limit_redis(
        self, 
        redis, 
        username: str, 
        max_attempts: int, 
        window_seconds: int
    ) -> Tuple[bool, int]:
        """Rate limit usando Redis con sorted sets"""
        key = f"rate_limit:{username}"
        current_time = time.time()
        window_start = current_time - window_seconds
        
        try:
            # Limpiar intentos antiguos
            await redis.zremrangebyscore(key, 0, window_start)
            
            # Contar intentos en ventana
            count = await redis.zcard(key)
            
            if count >= max_attempts:
                # Obtener el intento más antiguo para calcular retry_after
                oldest = await redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = int(window_seconds - (current_time - oldest_time))
                    return False, max(retry_after, 1)
            
            # Agregar intento actual
            await redis.zadd(key, {str(current_time): current_time})
            await redis.expire(key, window_seconds)
            
            return True, 0
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}, falling back to memory")
            return self._check_rate_limit_memory(username, max_attempts, window_seconds)
    
    def _check_rate_limit_memory(
        self, 
        username: str, 
        max_attempts: int, 
        window_seconds: int
    ) -> Tuple[bool, int]:
        """Rate limit usando memoria local"""
        current_time = time.time()
        
        # Inicializar si no existe
        if username not in self._login_attempts:
            self._login_attempts[username] = []
        
        # Limpiar intentos antiguos
        self._login_attempts[username] = [
            attempt_time
            for attempt_time in self._login_attempts[username]
            if current_time - attempt_time < window_seconds
        ]
        
        # Verificar límite
        if len(self._login_attempts[username]) >= max_attempts:
            oldest_attempt = self._login_attempts[username][0]
            retry_after = int(window_seconds - (current_time - oldest_attempt))
            return False, max(retry_after, 1)
        
        # Agregar intento
        self._login_attempts[username].append(current_time)
        return True, 0
    
    # ========================================================================
    # TOKEN BLACKLIST
    # ========================================================================
    
    async def add_token_to_blacklist(self, jti: str, exp_timestamp: int):
        """
        Agrega token a blacklist con TTL automático.
        
        Args:
            jti: JWT ID (identificador único del token)
            exp_timestamp: Timestamp de expiración del token (Unix timestamp)
        """
        redis = await self._get_redis()
        
        if redis:
            await self._add_token_to_blacklist_redis(redis, jti, exp_timestamp)
        else:
            self._add_token_to_blacklist_memory(jti)
    
    async def _add_token_to_blacklist_redis(self, redis, jti: str, exp_timestamp: int):
        """Blacklist usando Redis con TTL automático"""
        try:
            key = f"token_blacklist:{jti}"
            current_time = int(time.time())
            ttl = max(exp_timestamp - current_time, 1)  # TTL hasta expiración
            
            await redis.setex(key, ttl, "revoked")
            logger.info(f"Token blacklisted in Redis: {jti[:8]}... (TTL: {ttl}s)")
            
        except Exception as e:
            logger.error(f"Redis blacklist error: {e}, falling back to memory")
            self._add_token_to_blacklist_memory(jti)
    
    def _add_token_to_blacklist_memory(self, jti: str):
        """Blacklist usando memoria local"""
        self._token_blacklist.add(jti)
        logger.info(f"Token blacklisted in memory: {jti[:8]}...")
        
        # Advertir si crece demasiado
        if len(self._token_blacklist) > 1000:
            logger.warning(
                f"Token blacklist size: {len(self._token_blacklist)} - "
                "Consider enabling Redis for production"
            )
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """
        Verifica si token está en blacklist.
        
        Args:
            jti: JWT ID del token
            
        Returns:
            True si está revocado, False si es válido
        """
        redis = await self._get_redis()
        
        if redis:
            return await self._is_token_blacklisted_redis(redis, jti)
        else:
            return self._is_token_blacklisted_memory(jti)
    
    async def _is_token_blacklisted_redis(self, redis, jti: str) -> bool:
        """Verificar blacklist en Redis"""
        try:
            key = f"token_blacklist:{jti}"
            exists = await redis.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Redis blacklist check error: {e}, checking memory")
            return self._is_token_blacklisted_memory(jti)
    
    def _is_token_blacklisted_memory(self, jti: str) -> bool:
        """Verificar blacklist en memoria"""
        return jti in self._token_blacklist
    
    # ========================================================================
    # REFRESH TOKENS
    # ========================================================================
    
    async def store_refresh_token(
        self, 
        token_id: str, 
        user_id: str, 
        expires_at: datetime,
        device_info: Optional[dict] = None
    ):
        """
        Almacena refresh token con metadata.
        
        Args:
            token_id: ID único del refresh token
            user_id: ID del usuario
            expires_at: Fecha de expiración
            device_info: Información del dispositivo (opcional)
        """
        redis = await self._get_redis()
        
        token_data = {
            "user_id": user_id,
            "expires_at": expires_at.isoformat(),
            "device_info": device_info or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        if redis:
            await self._store_refresh_token_redis(redis, token_id, token_data, expires_at)
        else:
            self._store_refresh_token_memory(token_id, token_data)
    
    async def _store_refresh_token_redis(
        self, 
        redis, 
        token_id: str, 
        token_data: dict,
        expires_at: datetime
    ):
        """Almacenar refresh token en Redis con TTL"""
        try:
            key = f"refresh_token:{token_id}"
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            ttl = max(ttl, 1)  # Asegurar TTL positivo
            
            await redis.setex(key, ttl, json.dumps(token_data))
            logger.info(f"Refresh token stored in Redis: {token_id[:8]}... (TTL: {ttl}s)")
            
        except Exception as e:
            logger.error(f"Redis refresh token store error: {e}, using memory")
            self._store_refresh_token_memory(token_id, token_data)
    
    def _store_refresh_token_memory(self, token_id: str, token_data: dict):
        """Almacenar refresh token en memoria"""
        self._refresh_tokens[token_id] = token_data
        logger.info(f"Refresh token stored in memory: {token_id[:8]}...")
    
    async def get_refresh_token(self, token_id: str) -> Optional[dict]:
        """
        Obtiene refresh token y su metadata.
        
        Args:
            token_id: ID del refresh token
            
        Returns:
            Diccionario con datos del token o None si no existe/expiró
        """
        redis = await self._get_redis()
        
        if redis:
            return await self._get_refresh_token_redis(redis, token_id)
        else:
            return self._get_refresh_token_memory(token_id)
    
    async def _get_refresh_token_redis(self, redis, token_id: str) -> Optional[dict]:
        """Obtener refresh token de Redis"""
        try:
            key = f"refresh_token:{token_id}"
            data = await redis.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Redis refresh token get error: {e}, checking memory")
            return self._get_refresh_token_memory(token_id)
    
    def _get_refresh_token_memory(self, token_id: str) -> Optional[dict]:
        """Obtener refresh token de memoria"""
        token_data = self._refresh_tokens.get(token_id)
        
        if token_data:
            # Verificar expiración
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.utcnow() > expires_at:
                del self._refresh_tokens[token_id]
                return None
        
        return token_data
    
    async def revoke_refresh_token(self, token_id: str):
        """
        Revoca refresh token eliminándolo del almacenamiento.
        
        Args:
            token_id: ID del refresh token a revocar
        """
        redis = await self._get_redis()
        
        if redis:
            await self._revoke_refresh_token_redis(redis, token_id)
        else:
            self._revoke_refresh_token_memory(token_id)
    
    async def _revoke_refresh_token_redis(self, redis, token_id: str):
        """Revocar refresh token en Redis"""
        try:
            key = f"refresh_token:{token_id}"
            await redis.delete(key)
            logger.info(f"Refresh token revoked in Redis: {token_id[:8]}...")
        except Exception as e:
            logger.error(f"Redis refresh token revoke error: {e}")
    
    def _revoke_refresh_token_memory(self, token_id: str):
        """Revocar refresh token en memoria"""
        if token_id in self._refresh_tokens:
            del self._refresh_tokens[token_id]
            logger.info(f"Refresh token revoked in memory: {token_id[:8]}...")


# Instancia singleton
_auth_redis_service: Optional[AuthRedisService] = None

def get_auth_redis_service() -> AuthRedisService:
    """Obtiene instancia singleton del servicio"""
    global _auth_redis_service
    if _auth_redis_service is None:
        _auth_redis_service = AuthRedisService()
    return _auth_redis_service
