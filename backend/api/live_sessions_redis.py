"""
Redis Service para Live Sessions
=================================
Servicio para gestión de sesiones de voz con Gemini Live
usando Redis para horizontal scaling y persistencia.
"""

import os
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

# Intentar importar Redis
try:
    from config.redis_config import get_redis_client
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available for live sessions, using in-memory storage")


class LiveSessionsRedisService:
    """
    Servicio para sesiones de voz usando Redis con fallback a memoria.
    """
    
    def __init__(self):
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self._memory_sessions: Dict[str, Dict[str, Any]] = {}
        logger.info(f"LiveSessionsRedisService initialized - Redis: {self.redis_enabled}")
    
    async def _get_redis(self):
        """Helper para obtener cliente Redis si está disponible"""
        if not self.redis_enabled or not REDIS_AVAILABLE:
            return None
        try:
            return await get_redis_client()
        except Exception as e:
            logger.error(f"Error getting Redis client: {e}")
            return None
    
    async def create_session(
        self,
        session_id: str,
        patient_id: str,
        appointment_id: str,
        user_id: str,
        ttl_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Crea una nueva sesión con token efímero.
        
        Args:
            session_id: ID único de la sesión
            patient_id: ID del paciente
            appointment_id: ID de la cita
            user_id: ID del usuario (médico)
            ttl_minutes: Tiempo de vida en minutos
            
        Returns:
            Diccionario con token, sessionId y expiresAt
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        
        session_data = {
            "session_id": session_id,
            "token": token,
            "patient_id": patient_id,
            "appointment_id": appointment_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        redis = await self._get_redis()
        
        if redis:
            await self._store_session_redis(redis, session_id, session_data, ttl_minutes)
        else:
            self._store_session_memory(session_id, session_data)
        
        return {
            "token": token,
            "sessionId": session_id,
            "expiresAt": expires_at
        }
    
    async def _store_session_redis(
        self,
        redis,
        session_id: str,
        session_data: dict,
        ttl_minutes: int
    ):
        """Almacenar sesión en Redis con TTL"""
        try:
            key = f"live_session:{session_id}"
            ttl_seconds = ttl_minutes * 60
            await redis.setex(key, ttl_seconds, json.dumps(session_data))
            logger.info(f"Session stored in Redis: {session_id} (TTL: {ttl_minutes}m)")
        except Exception as e:
            logger.error(f"Redis session store error: {e}, falling back to memory")
            self._store_session_memory(session_id, session_data)
    
    def _store_session_memory(self, session_id: str, session_data: dict):
        """Almacenar sesión en memoria"""
        # Convertir expires_at a datetime para memoria
        session_data_mem = session_data.copy()
        session_data_mem['expires_at'] = datetime.fromisoformat(session_data['expires_at'])
        self._memory_sessions[session_id] = session_data_mem
        logger.info(f"Session stored in memory: {session_id}")
    
    async def validate_session(self, session_id: str, token: str) -> bool:
        """
        Valida un token de sesión.
        
        Args:
            session_id: ID de la sesión
            token: Token a validar
            
        Returns:
            True si es válido, False si no existe o expiró
        """
        redis = await self._get_redis()
        
        if redis:
            return await self._validate_session_redis(redis, session_id, token)
        else:
            return self._validate_session_memory(session_id, token)
    
    async def _validate_session_redis(self, redis, session_id: str, token: str) -> bool:
        """Validar sesión en Redis"""
        try:
            key = f"live_session:{session_id}"
            data = await redis.get(key)
            
            if not data:
                logger.warning(f"Session not found in Redis: {session_id}")
                return False
            
            session = json.loads(data)
            
            if session['token'] != token:
                logger.warning(f"Token mismatch for session: {session_id}")
                return False
            
            # Redis TTL maneja la expiración automáticamente
            return True
            
        except Exception as e:
            logger.error(f"Redis session validate error: {e}, checking memory")
            return self._validate_session_memory(session_id, token)
    
    def _validate_session_memory(self, session_id: str, token: str) -> bool:
        """Validar sesión en memoria"""
        if session_id not in self._memory_sessions:
            logger.warning(f"Session not found in memory: {session_id}")
            return False
        
        session = self._memory_sessions[session_id]
        
        if session['token'] != token:
            logger.warning(f"Token mismatch for session: {session_id}")
            return False
        
        # Verificar expiración
        if datetime.utcnow() > session['expires_at']:
            logger.info(f"Session expired in memory: {session_id}")
            del self._memory_sessions[session_id]
            return False
        
        return True
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Diccionario con datos de la sesión o None si no existe
        """
        redis = await self._get_redis()
        
        if redis:
            return await self._get_session_redis(redis, session_id)
        else:
            return self._get_session_memory(session_id)
    
    async def _get_session_redis(self, redis, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtener sesión de Redis"""
        try:
            key = f"live_session:{session_id}"
            data = await redis.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Redis session get error: {e}, checking memory")
            return self._get_session_memory(session_id)
    
    def _get_session_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtener sesión de memoria"""
        session = self._memory_sessions.get(session_id)
        
        if session:
            # Verificar expiración
            if datetime.utcnow() > session['expires_at']:
                del self._memory_sessions[session_id]
                return None
            
            # Convertir expires_at a string para consistencia
            session_copy = session.copy()
            session_copy['expires_at'] = session['expires_at'].isoformat()
            return session_copy
        
        return None
    
    async def delete_session(self, session_id: str):
        """
        Elimina una sesión.
        
        Args:
            session_id: ID de la sesión a eliminar
        """
        redis = await self._get_redis()
        
        if redis:
            await self._delete_session_redis(redis, session_id)
        else:
            self._delete_session_memory(session_id)
    
    async def _delete_session_redis(self, redis, session_id: str):
        """Eliminar sesión de Redis"""
        try:
            key = f"live_session:{session_id}"
            await redis.delete(key)
            logger.info(f"Session deleted from Redis: {session_id}")
        except Exception as e:
            logger.error(f"Redis session delete error: {e}")
    
    def _delete_session_memory(self, session_id: str):
        """Eliminar sesión de memoria"""
        if session_id in self._memory_sessions:
            del self._memory_sessions[session_id]
            logger.info(f"Session deleted from memory: {session_id}")
    
    async def cleanup_expired_sessions(self):
        """
        Limpia sesiones expiradas (solo necesario para memoria).
        Redis maneja esto automáticamente con TTL.
        """
        redis = await self._get_redis()
        
        if redis:
            # Redis maneja expiración automáticamente
            logger.debug("Redis handles session expiration automatically")
            return
        
        # Limpiar memoria
        now = datetime.utcnow()
        expired = [
            sid for sid, sess in self._memory_sessions.items()
            if now > sess['expires_at']
        ]
        
        for session_id in expired:
            del self._memory_sessions[session_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions from memory")


# Instancia singleton
_live_sessions_service: Optional[LiveSessionsRedisService] = None

def get_live_sessions_service() -> LiveSessionsRedisService:
    """Obtiene instancia singleton del servicio"""
    global _live_sessions_service
    if _live_sessions_service is None:
        _live_sessions_service = LiveSessionsRedisService()
    return _live_sessions_service
