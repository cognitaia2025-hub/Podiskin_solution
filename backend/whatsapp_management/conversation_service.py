"""
Servicios para gestión de conversaciones y mensajes
===================================================

Maneja la obtención y gestión de conversaciones de WhatsApp.
NO incluye lógica de LangGraph (eso se manejará por separado).
"""

import asyncpg
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from db import get_pool
from .models import (
    ConversacionListItem,
    ConversacionDetalle,
    ContactoInfo,
    MensajeItem,
    DudaPendienteItem,
    ConversacionesResponse,
)

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIONES DE CONVERSACIONES
# ============================================================================


async def get_conversaciones_recientes(
    limit: int = 50, estado: Optional[str] = None
) -> List[ConversacionListItem]:
    """
    Obtiene conversaciones atendidas recientemente.

    Args:
        limit: Número máximo de conversaciones
        estado: Filtrar por estado (Activa, Resuelta, etc.)

    Returns:
        Lista de conversaciones
    """
    pool = get_pool()

    query = """
        SELECT 
            c.id,
            co.nombre as contacto_nombre,
            co.telefono as contacto_telefono,
            co.id_paciente,
            CASE WHEN co.id_paciente IS NULL THEN true ELSE false END as es_nuevo_paciente,
            (
                SELECT m.contenido 
                FROM mensajes m 
                WHERE m.id_conversacion = c.id 
                ORDER BY m.fecha_envio DESC 
                LIMIT 1
            ) as ultimo_mensaje,
            c.fecha_ultima_actividad,
            c.requiere_atencion,
            (
                SELECT COUNT(*) 
                FROM mensajes m 
                WHERE m.id_conversacion = c.id 
                AND m.direccion = 'Entrante' 
                AND m.fecha_lectura IS NULL
            ) as numero_mensajes_sin_leer,
            c.estado
        FROM conversaciones c
        INNER JOIN contactos co ON c.id_contacto = co.id
        WHERE c.requiere_atencion = false
        AND ($1::text IS NULL OR c.estado = $1)
        ORDER BY c.fecha_ultima_actividad DESC
        LIMIT $2
    """

    try:
        rows = await pool.fetch(query, estado, limit)
        return [ConversacionListItem(**dict(row)) for row in rows]
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones recientes: {e}", exc_info=True)
        raise


async def get_conversacion_detalle(
    conversacion_id: int,
) -> Optional[ConversacionDetalle]:
    """
    Obtiene detalle completo de una conversación con todos sus mensajes.

    Args:
        conversacion_id: ID de la conversación

    Returns:
        Detalle de la conversación o None si no existe
    """
    pool = get_pool()

    try:
        # Obtener conversación
        conv_query = """
            SELECT 
                c.id,
                c.canal,
                c.estado,
                c.categoria,
                c.requiere_atencion,
                c.fecha_inicio,
                c.fecha_ultima_actividad,
                c.numero_mensajes,
                c.notas_internas,
                co.id as contacto_id,
                co.whatsapp_id as contacto_whatsapp_id,
                co.nombre as contacto_nombre,
                co.telefono as contacto_telefono,
                co.id_paciente as contacto_id_paciente,
                CASE WHEN co.id_paciente IS NULL THEN true ELSE false END as contacto_es_nuevo_paciente
            FROM conversaciones c
            INNER JOIN contactos co ON c.id_contacto = co.id
            WHERE c.id = $1
        """

        conv_row = await pool.fetchrow(conv_query, conversacion_id)

        if not conv_row:
            return None

        # Obtener mensajes
        msg_query = """
            SELECT 
                m.id,
                m.direccion,
                m.enviado_por_tipo,
                m.contenido,
                m.fecha_envio,
                m.estado_entrega,
                m.requiere_atencion_humana,
                a.sentimiento,
                a.tono
            FROM mensajes m
            LEFT JOIN analisis_sentimiento a ON a.id_mensaje = m.id
            WHERE m.id_conversacion = $1
            ORDER BY m.fecha_envio ASC
        """

        msg_rows = await pool.fetch(msg_query, conversacion_id)

        # Construir respuesta
        contacto = ContactoInfo(
            id=conv_row["contacto_id"],
            whatsapp_id=conv_row["contacto_whatsapp_id"],
            nombre=conv_row["contacto_nombre"],
            telefono=conv_row["contacto_telefono"],
            id_paciente=conv_row["contacto_id_paciente"],
            es_nuevo_paciente=conv_row["contacto_es_nuevo_paciente"],
        )

        mensajes = [MensajeItem(**dict(row)) for row in msg_rows]

        return ConversacionDetalle(
            id=conv_row["id"],
            contacto=contacto,
            canal=conv_row["canal"],
            estado=conv_row["estado"],
            categoria=conv_row["categoria"],
            requiere_atencion=conv_row["requiere_atencion"],
            fecha_inicio=conv_row["fecha_inicio"],
            fecha_ultima_actividad=conv_row["fecha_ultima_actividad"],
            numero_mensajes=conv_row["numero_mensajes"],
            mensajes=mensajes,
            notas_internas=conv_row["notas_internas"],
        )

    except Exception as e:
        logger.error(
            f"Error obteniendo conversación {conversacion_id}: {e}", exc_info=True
        )
        raise


async def marcar_conversacion_atendida(
    conversacion_id: int, user_id: int, notas: Optional[str] = None
) -> bool:
    """
    Marca una conversación como atendida.

    Args:
        conversacion_id: ID de la conversación
        user_id: ID del usuario que atiende
        notas: Notas internas opcionales

    Returns:
        True si se actualizó correctamente
    """
    pool = get_pool()

    try:
        query = """
            UPDATE conversaciones
            SET requiere_atencion = false,
                atendido_por = $1,
                fecha_atencion = CURRENT_TIMESTAMP,
                notas_internas = COALESCE($2, notas_internas)
            WHERE id = $3
        """

        await pool.execute(query, user_id, notas, conversacion_id)
        logger.info(
            f"Conversación {conversacion_id} marcada como atendida por usuario {user_id}"
        )
        return True

    except Exception as e:
        logger.error(f"Error marcando conversación como atendida: {e}", exc_info=True)
        raise


# ============================================================================
# FUNCIONES DE DUDAS ESCALADAS
# ============================================================================


async def get_dudas_escaladas(solo_pendientes: bool = True) -> List[DudaPendienteItem]:
    """
    Obtiene dudas escaladas que requieren atención humana.

    Args:
        solo_pendientes: Si True, solo retorna dudas pendientes

    Returns:
        Lista de dudas escaladas
    """
    pool = get_pool()

    query = """
        SELECT 
            d.id,
            d.paciente_nombre,
            d.paciente_telefono,
            d.id_paciente,
            d.duda,
            d.contexto,
            d.estado,
            d.fecha_creacion,
            d.id_conversacion,
            d.aprendizaje_generado
        FROM dudas_pendientes d
        WHERE ($1 = false OR d.estado = 'pendiente')
        ORDER BY d.fecha_creacion DESC
    """

    try:
        rows = await pool.fetch(query, solo_pendientes)
        return [DudaPendienteItem(**dict(row)) for row in rows]
    except Exception as e:
        logger.error(f"Error obteniendo dudas escaladas: {e}", exc_info=True)
        raise


async def get_conversaciones_y_escaladas(
    limit: int = 50, estado: Optional[str] = None
) -> ConversacionesResponse:
    """
    Obtiene conversaciones atendidas y dudas escaladas en una sola llamada.

    Args:
        limit: Límite de conversaciones atendidas
        estado: Filtro de estado para conversaciones

    Returns:
        Respuesta con ambas listas
    """
    try:
        # Obtener en paralelo
        atendidas = await get_conversaciones_recientes(limit=limit, estado=estado)
        escaladas = await get_dudas_escaladas(solo_pendientes=True)

        return ConversacionesResponse(
            atendidas=atendidas,
            escaladas=escaladas,
            total_atendidas=len(atendidas),
            total_escaladas=len(escaladas),
        )
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones y escaladas: {e}", exc_info=True)
        raise


async def actualizar_notas_conversacion(
    conversacion_id: int, notas: str, user_id: int
) -> bool:
    """
    Actualiza las notas internas de una conversación.

    Args:
        conversacion_id: ID de la conversación
        notas: Notas a agregar/actualizar
        user_id: ID del usuario que actualiza

    Returns:
        True si se actualizó correctamente
    """
    pool = get_pool()

    try:
        query = """
            UPDATE conversaciones
            SET notas_internas = $1
            WHERE id = $2
        """

        await pool.execute(query, notas, conversacion_id)
        logger.info(
            f"Notas actualizadas en conversación {conversacion_id} por usuario {user_id}"
        )
        return True

    except Exception as e:
        logger.error(f"Error actualizando notas: {e}", exc_info=True)
        raise


async def marcar_mensajes_como_leidos(conversacion_id: int) -> int:
    """
    Marca todos los mensajes de una conversación como leídos.

    Args:
        conversacion_id: ID de la conversación

    Returns:
        Número de mensajes marcados como leídos
    """
    pool = get_pool()

    try:
        query = """
            UPDATE mensajes
            SET fecha_lectura = CURRENT_TIMESTAMP
            WHERE id_conversacion = $1
            AND direccion = 'Entrante'
            AND fecha_lectura IS NULL
            RETURNING id
        """

        rows = await pool.fetch(query, conversacion_id)
        count = len(rows)

        if count > 0:
            logger.info(
                f"Marcados {count} mensajes como leídos en conversación {conversacion_id}"
            )

        return count

    except Exception as e:
        logger.error(f"Error marcando mensajes como leídos: {e}", exc_info=True)
        raise

