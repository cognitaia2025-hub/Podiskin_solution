"""
Servicios para gestión de sesiones de QR de WhatsApp
=====================================================

Maneja la generación, tracking y gestión de sesiones de QR.
"""

import asyncpg
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from db import get_pool
from .models import (
    QRSessionInfo,
    QRSessionCreate,
    QRSessionUpdate,
    EstadoQR,
    ProveedorMensajeria,
)

logger = logging.getLogger(__name__)

# URL del cliente Node.js de WhatsApp
WHATSAPP_CLIENT_URL = "http://localhost:3000"

# ============================================================================
# FUNCIONES DE COMUNICACIÓN CON CLIENTE WHATSAPP
# ============================================================================


async def solicitar_qr_whatsapp() -> Dict[str, Any]:
    """
    Solicita al cliente Node.js que genere un QR.

    Returns:
        Dict con qr_code y metadata

    Raises:
        Exception: Si hay error en la comunicación
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{WHATSAPP_CLIENT_URL}/api/qr/generar",
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Error generando QR: {response.status} - {error_text}"
                    )
    except aiohttp.ClientError as e:
        logger.error(f"Error de conexión con cliente WhatsApp: {e}")
        raise Exception(f"No se pudo conectar con el cliente de WhatsApp: {str(e)}")
    except Exception as e:
        logger.error(f"Error solicitando QR: {e}", exc_info=True)
        raise


async def verificar_estado_conexion() -> Dict[str, Any]:
    """
    Verifica el estado de la conexión de WhatsApp.

    Returns:
        Dict con estado de conexión
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{WHATSAPP_CLIENT_URL}/api/estado",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {"conectado": False, "error": "No se pudo verificar estado"}
    except Exception as e:
        logger.error(f"Error verificando estado: {e}")
        return {"conectado": False, "error": str(e)}


# ============================================================================
# FUNCIONES DE GESTIÓN DE SESIONES QR
# ============================================================================


async def crear_sesion_qr(
    proveedor: ProveedorMensajeria = ProveedorMensajeria.WHATSAPP_WEB_JS,
    user_id: Optional[int] = None,
) -> QRSessionInfo:
    """
    Crea una nueva sesión de QR para sincronización de WhatsApp.

    Args:
        proveedor: Proveedor de mensajería
        user_id: ID del usuario que inicia la sesión

    Returns:
        Información de la sesión creada
    """
    pool = get_pool()

    try:
        # Solicitar QR al cliente
        qr_data = await solicitar_qr_whatsapp()

        # Calcular fecha de expiración (60 minutos)
        fecha_expiracion = datetime.now() + timedelta(minutes=60)

        # Insertar en BD
        query = """
            INSERT INTO whatsapp_qr_sessions (
                qr_code,
                qr_image_url,
                estado,
                proveedor,
                fecha_expiracion,
                iniciado_por
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING 
                id, qr_code, qr_image_url, estado, telefono_conectado,
                nombre_dispositivo, whatsapp_id, proveedor,
                fecha_generacion, fecha_expiracion, fecha_escaneo,
                fecha_conexion, fecha_desconexion, fecha_generacion as fecha_creacion
        """

        row = await pool.fetchrow(
            query,
            qr_data.get("qr_code"),
            qr_data.get("qr_image_url"),
            EstadoQR.PENDIENTE.value,
            proveedor.value,
            fecha_expiracion,
            user_id,
        )

        logger.info(f"Sesión QR creada: {row['id']}")

        return QRSessionInfo(**dict(row))

    except Exception as e:
        logger.error(f"Error creando sesión QR: {e}", exc_info=True)
        raise


async def get_sesion_qr_by_id(session_id: int) -> Optional[QRSessionInfo]:
    """
    Obtiene una sesión de QR por ID.

    Args:
        session_id: ID de la sesión

    Returns:
        Información de la sesión o None si no existe
    """
    pool = get_pool()

    query = """
        SELECT 
            id, qr_code, qr_image_url, estado, telefono_conectado,
            nombre_dispositivo, whatsapp_id, proveedor,
            fecha_generacion, fecha_expiracion, fecha_escaneo,
            fecha_conexion, fecha_desconexion, fecha_generacion as fecha_creacion
        FROM whatsapp_qr_sessions
        WHERE id = $1
    """

    row = await pool.fetchrow(query, session_id)

    if not row:
        return None

    return QRSessionInfo(**dict(row))


async def get_sesion_qr_activa() -> Optional[QRSessionInfo]:
    """
    Obtiene la sesión de QR activa (pendiente o conectada).

    Returns:
        Sesión activa o None si no hay ninguna
    """
    pool = get_pool()

    query = """
        SELECT 
            id, qr_code, qr_image_url, estado, telefono_conectado,
            nombre_dispositivo, whatsapp_id, proveedor,
            fecha_generacion, fecha_expiracion, fecha_escaneo,
            fecha_conexion, fecha_desconexion, fecha_generacion as fecha_creacion
        FROM whatsapp_qr_sessions
        WHERE estado IN ('pendiente', 'conectado')
        ORDER BY fecha_generacion DESC
        LIMIT 1
    """

    row = await pool.fetchrow(query)

    if not row:
        return None

    return QRSessionInfo(**dict(row))


async def actualizar_estado_sesion_qr(
    session_id: int, update_data: QRSessionUpdate
) -> Optional[QRSessionInfo]:
    """
    Actualiza el estado de una sesión de QR.

    Args:
        session_id: ID de la sesión
        update_data: Datos a actualizar

    Returns:
        Sesión actualizada o None si no existe
    """
    pool = get_pool()

    # Construir query dinámicamente
    updates = ["estado = $1"]
    params = [update_data.estado.value]
    param_count = 2

    if update_data.telefono_conectado:
        updates.append(f"telefono_conectado = ${param_count}")
        params.append(update_data.telefono_conectado)
        param_count += 1

    if update_data.nombre_dispositivo:
        updates.append(f"nombre_dispositivo = ${param_count}")
        params.append(update_data.nombre_dispositivo)
        param_count += 1

    if update_data.whatsapp_id:
        updates.append(f"whatsapp_id = ${param_count}")
        params.append(update_data.whatsapp_id)
        param_count += 1

    # Actualizar timestamps según el estado
    if update_data.estado == EstadoQR.ESCANEADO:
        updates.append(f"fecha_escaneo = CURRENT_TIMESTAMP")
    elif update_data.estado == EstadoQR.CONECTADO:
        updates.append(f"fecha_conexion = CURRENT_TIMESTAMP")
    elif update_data.estado == EstadoQR.DESCONECTADO:
        updates.append(f"fecha_desconexion = CURRENT_TIMESTAMP")

    params.append(session_id)

    query = f"""
        UPDATE whatsapp_qr_sessions
        SET {', '.join(updates)}
        WHERE id = ${param_count}
        RETURNING 
            id, qr_code, qr_image_url, estado, telefono_conectado,
            nombre_dispositivo, whatsapp_id, proveedor,
            fecha_generacion, fecha_expiracion, fecha_escaneo,
            fecha_conexion, fecha_desconexion, fecha_generacion as fecha_creacion
    """

    row = await pool.fetchrow(query, *params)

    if not row:
        return None

    logger.info(
        f"Sesión QR {session_id} actualizada a estado: {update_data.estado.value}"
    )

    return QRSessionInfo(**dict(row))


async def expirar_sesiones_antiguas() -> int:
    """
    Marca como expiradas las sesiones que pasaron su fecha de expiración.

    Returns:
        Número de sesiones expiradas
    """
    pool = get_pool()

    query = """
        UPDATE whatsapp_qr_sessions
        SET estado = 'expirado'
        WHERE estado = 'pendiente'
        AND fecha_expiracion < CURRENT_TIMESTAMP
        RETURNING id
    """

    rows = await pool.fetch(query)
    count = len(rows)

    if count > 0:
        logger.info(f"Expiradas {count} sesiones de QR antiguas")

    return count


async def verificar_y_actualizar_conexion() -> Dict[str, Any]:
    """
    Verifica el estado de conexión actual y actualiza la sesión activa.

    Returns:
        Dict con información de la verificación
    """
    try:
        # Obtener sesión activa
        sesion_activa = await get_sesion_qr_activa()

        if not sesion_activa:
            return {
                "success": False,
                "message": "No hay sesión activa",
                "conectado": False,
            }

        # Verificar estado con el cliente
        estado_cliente = await verificar_estado_conexion()

        if estado_cliente.get("conectado"):
            # Actualizar a conectado si no lo está
            if sesion_activa.estado != EstadoQR.CONECTADO:
                await actualizar_estado_sesion_qr(
                    sesion_activa.id,
                    QRSessionUpdate(
                        estado=EstadoQR.CONECTADO,
                        telefono_conectado=estado_cliente.get("telefono"),
                        whatsapp_id=estado_cliente.get("whatsapp_id"),
                    ),
                )

            return {
                "success": True,
                "message": "WhatsApp conectado",
                "conectado": True,
                "session_id": sesion_activa.id,
            }
        else:
            # Actualizar a desconectado si estaba conectado
            if sesion_activa.estado == EstadoQR.CONECTADO:
                await actualizar_estado_sesion_qr(
                    sesion_activa.id, QRSessionUpdate(estado=EstadoQR.DESCONECTADO)
                )

            return {
                "success": False,
                "message": "WhatsApp desconectado",
                "conectado": False,
            }

    except Exception as e:
        logger.error(f"Error verificando conexión: {e}", exc_info=True)
        return {"success": False, "message": f"Error: {str(e)}", "conectado": False}

