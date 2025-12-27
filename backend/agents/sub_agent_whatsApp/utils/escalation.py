"""
Módulo de Escalamiento de Dudas
=================================

Gestiona el escalamiento de dudas a administradores cuando Maya no sabe algo.
"""

import logging
from typing import Dict, Optional

from .database import _get_connection, _put_connection

logger = logging.getLogger(__name__)


def create_pending_question(
    paciente_chat_id: str,
    paciente_nombre: str,
    paciente_telefono: str,
    duda: str,
    contexto: Optional[str] = None,
) -> int:
    """
    Crea una nueva duda pendiente en la BD.

    Args:
        paciente_chat_id: WhatsApp chat ID del paciente
        paciente_nombre: Nombre del paciente
        paciente_telefono: Teléfono del paciente
        duda: La pregunta/duda
        contexto: Contexto de la conversación (opcional)

    Returns:
        ID de la duda creada
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dudas_pendientes 
                (paciente_chat_id, paciente_nombre, paciente_telefono, duda, contexto, fecha_expiracion)
                VALUES (%s, %s, %s, %s, %s, NOW() + INTERVAL '24 hours')
                RETURNING id
                """,
                (paciente_chat_id, paciente_nombre, paciente_telefono, duda, contexto),
            )
            result = cur.fetchone()
            conn.commit()

            duda_id = result[0]
            logger.info(f"Duda #{duda_id} creada para {paciente_nombre}")
            return duda_id
    finally:
        _put_connection(conn)


def get_pending_question(duda_id: int) -> Optional[Dict]:
    """
    Obtiene una duda pendiente por ID.

    Args:
        duda_id: ID de la duda

    Returns:
        Diccionario con datos de la duda o None
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM dudas_pendientes WHERE id = %s",
                (duda_id,),
            )
            result = cur.fetchone()
            if result:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, result))
            return None
    finally:
        _put_connection(conn)


def answer_pending_question(duda_id: int, respuesta: str, admin_chat_id: str) -> bool:
    """
    Marca una duda como respondida y la guarda en la base de conocimiento.

    Args:
        duda_id: ID de la duda
        respuesta: Respuesta del administrador
        admin_chat_id: Chat ID del admin que respondió

    Returns:
        True si se actualizó correctamente
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            # Obtener la duda primero
            cur.execute("SELECT duda FROM dudas_pendientes WHERE id = %s", (duda_id,))
            duda_row = cur.fetchone()

            if not duda_row:
                return False

            pregunta = duda_row[0]

            # Marcar como respondida
            cur.execute(
                """
                UPDATE dudas_pendientes 
                SET estado = 'respondida',
                    respuesta_admin = %s,
                    admin_chat_id = %s,
                    fecha_respuesta = NOW()
                WHERE id = %s AND estado = 'pendiente'
                RETURNING id
                """,
                (respuesta, admin_chat_id, duda_id),
            )
            result = cur.fetchone()
            conn.commit()

            if result:
                logger.info(f"Duda #{duda_id} respondida por admin")

                # Guardar en knowledge_base automáticamente
                try:
                    from ..tools.knowledge_tools import save_to_knowledge_base

                    kb_id = save_to_knowledge_base(
                        pregunta=pregunta,
                        respuesta=respuesta,
                        categoria="admin_escalado",
                    )
                    logger.info(f"Respuesta guardada en KB #{kb_id}")
                except Exception as e:
                    logger.error(f"Error guardando en KB: {e}", exc_info=True)
                    # No fallar si no se puede guardar en KB

                return True
            return False
    finally:
        _put_connection(conn)


def expire_old_questions():
    """
    Marca como expiradas las dudas que pasaron de 24 horas sin respuesta.
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE dudas_pendientes 
                SET estado = 'expirada'
                WHERE estado = 'pendiente' 
                  AND fecha_expiracion < NOW()
                RETURNING id
                """
            )
            expired = cur.fetchall()
            conn.commit()

            if expired:
                logger.info(f"{len(expired)} dudas expiradas")
    finally:
        _put_connection(conn)


def format_question_for_admin(
    duda_id: int, paciente_nombre: str, paciente_telefono: str, duda: str
) -> str:
    """
    Formatea el mensaje que se enviará al administrador.

    Args:
        duda_id: ID de la duda
        paciente_nombre: Nombre del paciente
        paciente_telefono: Teléfono del paciente
        duda: La pregunta

    Returns:
        Mensaje formateado para el admin
    """
    return f"""🔔 *DUDA DE PACIENTE*

👤 *Paciente:* {paciente_nombre}
📞 *Tel:* {paciente_telefono}
❓ *Pregunta:* {duda}

Para responder, escribe:
#RESPUESTA_{duda_id}
[Tu respuesta aquí]"""


def parse_admin_response(message: str) -> Optional[tuple]:
    """
    Parsea la respuesta del administrador.

    Args:
        message: Mensaje del admin

    Returns:
        Tupla (duda_id, respuesta) o None si no es válido
    """
    if not message.startswith("#RESPUESTA_"):
        return None

    try:
        # Extraer ID
        parts = message.split("\n", 1)
        header = parts[0]  # #RESPUESTA_123
        duda_id = int(header.replace("#RESPUESTA_", ""))

        # Extraer respuesta
        if len(parts) > 1:
            respuesta = parts[1].strip()
        else:
            return None

        return (duda_id, respuesta)
    except (ValueError, IndexError):
        return None
