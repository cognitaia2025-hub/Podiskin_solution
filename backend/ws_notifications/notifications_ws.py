"""
Endpoint WebSocket para notificaciones en tiempo real
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from fastapi.responses import JSONResponse
from auth import decode_access_token
from ws_notifications.connection_manager import manager
import logging
import asyncpg
import os
from typing import Optional
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'podoskin_db'),
    'user': os.getenv('DB_USER', 'podoskin_user'),
    'password': os.getenv('DB_PASSWORD', 'podoskin_password_123'),
}


async def get_db_connection():
    """Obtiene conexión a la base de datos"""
    return await asyncpg.connect(**DB_CONFIG)


def verify_websocket_token(token: str) -> Optional[dict]:
    """
    Verifica el token JWT para WebSocket
    
    Args:
        token: Token JWT
        
    Returns:
        Payload del token si es válido, None en caso contrario
    """
    try:
        payload = decode_access_token(token)
        return payload
    except Exception as e:
        logger.error(f"[WebSocket] Error verificando token: {e}")
        return None


@router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token para autenticación")
):
    """
    WebSocket endpoint para notificaciones en tiempo real
    
    El cliente debe proporcionar el token JWT como query parameter:
    ws://localhost:8000/ws/notifications?token=<jwt_token>
    
    Mensajes enviados al cliente:
    - Tipo 'notification': Nueva notificación
    - Tipo 'update': Actualización de notificación existente
    - Tipo 'count': Contador de notificaciones no leídas
    - Tipo 'ping': Keep-alive del servidor
    
    El cliente puede enviar:
    - {"action": "mark_read", "notification_id": 123} - Marcar como leída
    - {"action": "get_count"} - Obtener contador de no leídas
    - {"action": "get_recent", "limit": 10} - Obtener notificaciones recientes
    """
    
    # Verificar token
    user_payload = verify_websocket_token(token)
    if not user_payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    user_id = user_payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Conectar usuario
    await manager.connect(websocket, user_id)
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado al sistema de notificaciones",
            "user_id": user_id
        })
        
        # Enviar contador inicial de notificaciones no leídas
        conn = await get_db_connection()
        try:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM notificaciones WHERE usuario_id = $1 AND leido = FALSE",
                user_id
            )
            await websocket.send_json({
                "type": "count",
                "count": count
            })
        finally:
            await conn.close()
        
        # Loop para recibir mensajes del cliente
        while True:
            # Recibir mensaje
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                conn = await get_db_connection()
                
                try:
                    # Marcar notificación como leída
                    if action == "mark_read":
                        notification_id = message.get("notification_id")
                        if notification_id:
                            await conn.execute(
                                """
                                UPDATE notificaciones 
                                SET leido = TRUE, fecha_lectura = NOW()
                                WHERE id = $1 AND usuario_id = $2
                                """,
                                notification_id, user_id
                            )
                            
                            # Enviar confirmación y nuevo contador
                            new_count = await conn.fetchval(
                                "SELECT COUNT(*) FROM notificaciones WHERE usuario_id = $1 AND leido = FALSE",
                                user_id
                            )
                            
                            await websocket.send_json({
                                "type": "mark_read_success",
                                "notification_id": notification_id,
                                "count": new_count
                            })
                    
                    # Obtener contador
                    elif action == "get_count":
                        count = await conn.fetchval(
                            "SELECT COUNT(*) FROM notificaciones WHERE usuario_id = $1 AND leido = FALSE",
                            user_id
                        )
                        await websocket.send_json({
                            "type": "count",
                            "count": count
                        })
                    
                    # Obtener notificaciones recientes
                    elif action == "get_recent":
                        limit = message.get("limit", 10)
                        notifications = await conn.fetch(
                            """
                            SELECT 
                                id,
                                tipo,
                                titulo,
                                mensaje,
                                referencia_id,
                                referencia_tipo,
                                fecha_envio,
                                leido
                            FROM notificaciones
                            WHERE usuario_id = $1
                            ORDER BY fecha_envio DESC
                            LIMIT $2
                            """,
                            user_id, limit
                        )
                        
                        notifications_list = [
                            {
                                "id": n["id"],
                                "tipo": n["tipo"],
                                "titulo": n["titulo"],
                                "mensaje": n["mensaje"],
                                "referencia_id": n["referencia_id"],
                                "referencia_tipo": n["referencia_tipo"],
                                "fecha_envio": n["fecha_envio"].isoformat(),
                                "leido": n["leido"]
                            }
                            for n in notifications
                        ]
                        
                        await websocket.send_json({
                            "type": "recent_notifications",
                            "notifications": notifications_list
                        })
                    
                    # Acción desconocida
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Acción desconocida: {action}"
                        })
                
                finally:
                    await conn.close()
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Formato JSON inválido"
                })
            except Exception as e:
                logger.error(f"[WebSocket] Error procesando mensaje: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Error procesando solicitud"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"[WebSocket] Usuario {user_id} desconectado")
    
    except Exception as e:
        logger.error(f"[WebSocket] Error en conexión de usuario {user_id}: {e}")
        manager.disconnect(websocket, user_id)


@router.get("/ws/stats")
async def websocket_stats():
    """
    Endpoint para obtener estadísticas de conexiones WebSocket
    Solo para administradores (agregar verificación de permisos)
    """
    stats = manager.get_stats()
    return JSONResponse(content=stats)


@router.post("/ws/broadcast")
async def broadcast_notification(notification_id: int):
    """
    Endpoint para enviar una notificación a través de WebSocket
    Llamado internamente después de crear una notificación en BD
    
    Args:
        notification_id: ID de la notificación a enviar
    """
    conn = await get_db_connection()
    
    try:
        # Obtener notificación de la BD
        notification = await conn.fetchrow(
            """
            SELECT 
                id,
                usuario_id,
                tipo,
                titulo,
                mensaje,
                referencia_id,
                referencia_tipo,
                fecha_envio
            FROM notificaciones
            WHERE id = $1
            """,
            notification_id
        )
        
        if not notification:
            return JSONResponse(
                status_code=404,
                content={"error": "Notificación no encontrada"}
            )
        
        user_id = notification["usuario_id"]
        
        # Enviar por WebSocket si el usuario está conectado
        if manager.is_user_connected(user_id):
            await manager.send_personal_message(
                {
                    "type": "notification",
                    "data": {
                        "id": notification["id"],
                        "tipo": notification["tipo"],
                        "titulo": notification["titulo"],
                        "mensaje": notification["mensaje"],
                        "referencia_id": notification["referencia_id"],
                        "referencia_tipo": notification["referencia_tipo"],
                        "fecha_envio": notification["fecha_envio"].isoformat()
                    }
                },
                user_id
            )
            
            # También enviar contador actualizado
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM notificaciones WHERE usuario_id = $1 AND leido = FALSE",
                user_id
            )
            
            await manager.send_personal_message(
                {
                    "type": "count",
                    "count": count
                },
                user_id
            )
            
            return JSONResponse(content={"status": "sent", "user_id": user_id})
        else:
            return JSONResponse(content={"status": "user_offline", "user_id": user_id})
    
    finally:
        await conn.close()
