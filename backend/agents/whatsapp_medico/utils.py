"""
Utilidades para WhatsApp
========================

Funciones helper para enviar mensajes y notificaciones.
"""

import logging
import httpx

logger = logging.getLogger(__name__)


async def enviar_whatsapp(chat_id: str, mensaje: str) -> bool:
    """
    Envía mensaje a WhatsApp vía cliente Node.js.

    Args:
        chat_id: ID del chat de WhatsApp
        mensaje: Mensaje a enviar

    Returns:
        True si se envió correctamente
    """
    try:
        # TODO: Integrar con whatsapp-web-js
        # Por ahora solo logueamos
        logger.info(f"📱 Enviando a {chat_id}: {mensaje[:50]}...")

        # Cuando integres whatsapp-web-js:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "http://localhost:3000/send-message",
        #         json={"chatId": chat_id, "message": mensaje}
        #     )
        #     return response.status_code == 200

        return True

    except Exception as e:
        logger.error(f"Error enviando WhatsApp: {e}")
        return False


async def notificar_escalado(data: dict) -> bool:
    """
    Notifica al frontend que hay una duda escalada.

    Args:
        data: Datos de la duda escalada

    Returns:
        True si se notificó correctamente
    """
    try:
        logger.info(f"🚨 Escalamiento: {data.get('chat_id')}")

        # TODO: Implementar notificación WebSocket o polling
        # Por ahora solo logueamos

        return True

    except Exception as e:
        logger.error(f"Error notificando escalado: {e}")
        return False
