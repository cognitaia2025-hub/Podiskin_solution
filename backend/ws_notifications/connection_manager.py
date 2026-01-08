"""
Gestor de conexiones WebSocket
Maneja conexiones activas y broadcast de notificaciones
"""

from typing import Dict, Set
from fastapi import WebSocket
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Administrador de conexiones WebSocket para notificaciones en tiempo real
    """
    
    def __init__(self):
        # Diccionario: usuario_id -> Set de WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Contador de conexiones totales
        self.total_connections = 0
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Acepta y registra una nueva conexión WebSocket
        
        Args:
            websocket: Conexión WebSocket
            user_id: ID del usuario conectado
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.total_connections += 1
        
        logger.info(
            f"[WebSocket] Usuario {user_id} conectado. "
            f"Conexiones activas: {len(self.active_connections[user_id])} "
            f"(Total: {self.total_connections})"
        )
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remueve una conexión WebSocket
        
        Args:
            websocket: Conexión WebSocket
            user_id: ID del usuario
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            self.total_connections -= 1
            
            # Limpiar si no quedan conexiones
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            logger.info(
                f"[WebSocket] Usuario {user_id} desconectado. "
                f"Conexiones restantes: {len(self.active_connections.get(user_id, []))} "
                f"(Total: {self.total_connections})"
            )
    
    async def send_personal_message(self, message: dict, user_id: int):
        """
        Envía un mensaje a un usuario específico en todas sus conexiones
        
        Args:
            message: Diccionario con el mensaje
            user_id: ID del usuario destinatario
        """
        if user_id not in self.active_connections:
            logger.warning(f"[WebSocket] Usuario {user_id} no tiene conexiones activas")
            return
        
        # Mensaje con timestamp
        message_with_timestamp = {
            **message,
            "timestamp": datetime.now().isoformat()
        }
        
        message_text = json.dumps(message_with_timestamp)
        disconnected = set()
        
        # Enviar a todas las conexiones del usuario
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"[WebSocket] Error enviando a usuario {user_id}: {e}")
                disconnected.add(connection)
        
        # Limpiar conexiones fallidas
        for connection in disconnected:
            self.disconnect(connection, user_id)
    
    async def broadcast_to_users(self, message: dict, user_ids: list[int]):
        """
        Envía un mensaje a múltiples usuarios
        
        Args:
            message: Diccionario con el mensaje
            user_ids: Lista de IDs de usuarios destinatarios
        """
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def broadcast_all(self, message: dict):
        """
        Envía un mensaje a todos los usuarios conectados
        
        Args:
            message: Diccionario con el mensaje
        """
        user_ids = list(self.active_connections.keys())
        await self.broadcast_to_users(message, user_ids)
    
    def get_user_connection_count(self, user_id: int) -> int:
        """
        Obtiene el número de conexiones activas de un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Número de conexiones activas
        """
        return len(self.active_connections.get(user_id, []))
    
    def is_user_connected(self, user_id: int) -> bool:
        """
        Verifica si un usuario tiene al menos una conexión activa
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si el usuario está conectado
        """
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de conexiones
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "total_connections": self.total_connections,
            "connected_users": len(self.active_connections),
            "users": {
                user_id: len(connections) 
                for user_id, connections in self.active_connections.items()
            }
        }


# Instancia global del gestor de conexiones
manager = ConnectionManager()
