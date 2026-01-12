"""
Puente WhatsApp: Backend Python ↔ Node.js
==========================================

Conecta el servicio Node.js de WhatsApp.js con el backend Python.
Reutiliza los servicios existentes de whatsapp_management.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
import httpx
import logging
from datetime import datetime

from auth import get_current_user, User
from db import get_pool

# Importar servicios existentes
from whatsapp_management import qr_service, conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp-bridge", tags=["WhatsApp Bridge"])

# URL del servicio Node.js
WHATSAPP_SERVICE_URL = "http://localhost:3000"


# ============================================================================
# MODELOS
# ============================================================================


class ContactoEspecial(BaseModel):
    telefono: str
    nombre: str
    etiqueta: str
    descripcion: Optional[str] = None
    comportamiento: str = "normal"
    contexto_ia: Optional[str] = None
    notificar_admin: bool = False


class WhatsAppConfig(BaseModel):
    telefono_admin: str
    telefonos_respaldo: List[str] = []
    grupos_activos: bool = True


class MensajeEntrante(BaseModel):
    """Mensaje entrante desde Node.js (interno)"""
    from_number: str
    body: str
    timestamp: Optional[str] = None
    is_group: bool = False
    message_id: Optional[str] = None


# ============================================================================
# ENDPOINTS INTERNOS (Node.js → Backend, sin auth, solo localhost)
# ============================================================================


def verify_internal_request(request: Request):
    """Verifica que la solicitud venga de localhost (servicio interno)"""
    client_host = request.client.host if request.client else None
    allowed_hosts = ["127.0.0.1", "localhost", "::1"]

    if client_host not in allowed_hosts:
        logger.warning(f"Intento de acceso interno desde IP no permitida: {client_host}")
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: solo servicios internos"
        )
    return True


@router.post("/internal/message")
async def receive_message_from_nodejs(
    mensaje: MensajeEntrante,
    request: Request,
    _: bool = Depends(verify_internal_request)
):
    """
    Recibe mensajes desde Node.js (WhatsApp.js).

    Este endpoint NO requiere autenticación JWT porque:
    1. Solo acepta conexiones desde localhost
    2. Es comunicación interna entre servicios

    Flujo:
    1. Node.js recibe mensaje de WhatsApp
    2. Node.js llama a este endpoint
    3. Backend procesa y decide respuesta
    4. Retorna respuesta a Node.js
    5. Node.js envía respuesta a WhatsApp
    """
    pool = get_pool()

    logger.info(f"📨 Mensaje interno recibido de {mensaje.from_number}")

    try:
        # 1. Buscar o crear contacto
        async with pool.acquire() as conn:
            # Buscar contacto existente
            contacto = await conn.fetchrow(
                "SELECT * FROM contactos WHERE telefono = $1 OR whatsapp_id = $1",
                mensaje.from_number
            )

            if not contacto:
                # Crear nuevo contacto
                contacto_id = await conn.fetchval(
                    """
                    INSERT INTO contactos (telefono, whatsapp_id, nombre, tipo, origen)
                    VALUES ($1, $1, 'Nuevo contacto', 'Prospecto', 'WhatsApp')
                    RETURNING id
                    """,
                    mensaje.from_number
                )
                logger.info(f"✨ Nuevo contacto creado: {contacto_id}")
            else:
                contacto_id = contacto['id']

            # 2. Buscar o crear conversación activa
            conversacion = await conn.fetchrow(
                """
                SELECT * FROM conversaciones
                WHERE id_contacto = $1 AND estado = 'Activa'
                ORDER BY fecha_ultima_actividad DESC LIMIT 1
                """,
                contacto_id
            )

            if not conversacion:
                # Crear nueva conversación
                conv_id = await conn.fetchval(
                    """
                    INSERT INTO conversaciones (id_contacto, canal, estado, categoria)
                    VALUES ($1, 'WhatsApp', 'Activa', 'Consulta')
                    RETURNING id
                    """,
                    contacto_id
                )
                logger.info(f"💬 Nueva conversación creada: {conv_id}")
            else:
                conv_id = conversacion['id']

            # 3. Guardar mensaje entrante
            await conn.execute(
                """
                INSERT INTO mensajes (id_conversacion, direccion, enviado_por_tipo, contenido, fecha_envio)
                VALUES ($1, 'Entrante', 'Contacto', $2, $3)
                """,
                conv_id,
                mensaje.body,
                datetime.now()
            )

            # 4. Actualizar fecha de última actividad
            await conn.execute(
                "UPDATE conversaciones SET fecha_ultima_actividad = $1 WHERE id = $2",
                datetime.now(),
                conv_id
            )

        # 5. Por ahora, respuesta simple (TODO: integrar con agente LangGraph)
        # Aquí es donde conectarías con el agente IA
        respuesta = f"Gracias por tu mensaje. Un momento por favor, estamos procesando tu consulta."

        return {
            "status": "received",
            "respuesta": respuesta,
            "contacto_id": contacto_id,
            "conversacion_id": conv_id,
            "debe_responder": True  # Node.js usará esto para saber si enviar respuesta
        }

    except Exception as e:
        logger.error(f"❌ Error procesando mensaje interno: {e}")
        return {
            "status": "error",
            "error": str(e),
            "debe_responder": False
        }


# ============================================================================
# ENDPOINTS DE CONTROL
# ============================================================================


@router.post("/control/start")
async def start_whatsapp(current_user: User = Depends(get_current_user)):
    """Inicia servicio WhatsApp.js"""
    pool = get_pool()

    try:
        # Llamar a Node.js
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{WHATSAPP_SERVICE_URL}/control/start")
            result = response.json()

        # Registrar en logs
        async with pool.acquire() as conn:
            await conn.execute(
                "SELECT registrar_accion_control($1, $2, $3, $4)",
                "start",
                current_user.id,
                None,
                "Servicio WhatsApp iniciado",
            )

            # Actualizar estado en config
            await conn.execute(
                """
                UPDATE whatsapp_config 
                SET estado = 'starting', fecha_ultimo_inicio = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM whatsapp_config ORDER BY id DESC LIMIT 1)
                """
            )

        return result

    except httpx.RequestError as e:
        logger.error(f"Error conectando con servicio WhatsApp: {e}")
        raise HTTPException(status_code=503, detail="Servicio WhatsApp no disponible")


@router.post("/control/stop")
async def stop_whatsapp(current_user: User = Depends(get_current_user)):
    """Pausa el servicio (Mantiene sesión)"""
    pool = get_pool()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{WHATSAPP_SERVICE_URL}/control/stop")
            result = response.json()

        async with pool.acquire() as conn:
            await conn.execute(
                "SELECT registrar_accion_control($1, $2, $3, $4)",
                "stop",
                current_user.id,
                None,
                "Servicio pausado",
            )
            await conn.execute(
                "UPDATE whatsapp_config SET estado = 'stopped' WHERE id = (SELECT id FROM whatsapp_config ORDER BY id DESC LIMIT 1)"
            )
        return result
    except httpx.RequestError as e:
        logger.error(f"Error pausando servicio: {e}")
        raise HTTPException(status_code=503, detail="Error al pausar servicio")


@router.post("/control/logout")
async def logout_whatsapp(current_user: User = Depends(get_current_user)):
    """Cierra sesión y elimina datos (Reset) - Robust Mode"""
    pool = get_pool()
    node_error = None

    # 1. Intentar limpiar Node.js (Best Effort)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{WHATSAPP_SERVICE_URL}/control/logout")
    except Exception as e:
        logger.error(f"Error partial logout Node.js: {e}")
        node_error = str(e)

    # 2. LIMPIEZA CRÍTICA: Base de datos (Always Run)
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "SELECT registrar_accion_control($1, $2, $3, $4)",
                "logout",
                current_user.id,
                None,
                f"Sesión cerrada (Node status: {'Error' if node_error else 'OK'})",
            )
            # Forzar estado stopped incompatible con sesión viva
            await conn.execute(
                "UPDATE whatsapp_config SET estado = 'stopped' WHERE id = (SELECT id FROM whatsapp_config ORDER BY id DESC LIMIT 1)"
            )

        if node_error:
            return {
                "status": "partial_success",
                "warning": "Sesión backend eliminada, pero Node.js no respondió. Se recomienda reiniciar contenedor.",
            }

        return {"status": "success", "message": "Sesión eliminada correctamente"}

    except Exception as e:
        logger.critical(f"Error crítico en DB Logout: {e}")
        raise HTTPException(
            status_code=500, detail="Fallo crítico al limpiar base de datos"
        )


@router.get("/control/status")
async def get_status(current_user: User = Depends(get_current_user)):
    """Estado actual del servicio"""
    pool = get_pool()

    try:
        # Estado del servicio Node.js
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{WHATSAPP_SERVICE_URL}/control/status")
            node_status = response.json()

        # Estado de la BD
        async with pool.acquire() as conn:
            db_status = await conn.fetchrow("SELECT * FROM get_whatsapp_config()")

        return {
            "service": node_status,
            "config": {
                "telefono_admin": db_status["telefono_admin"],
                "estado": db_status["estado"],
                "grupos_activos": db_status["grupos_activos"],
            },
        }

    except httpx.RequestError:
        return {"service": {"status": "offline"}, "config": {"estado": "stopped"}}


# ============================================================================
# CONFIGURACIÓN
# ============================================================================


@router.post("/config")
async def save_config(
    config: WhatsAppConfig, current_user: User = Depends(get_current_user)
):
    """Guarda configuración de WhatsApp"""
    pool = get_pool()

    async with pool.acquire() as conn:
        # Actualizar o insertar configuración
        await conn.execute(
            """
            INSERT INTO whatsapp_config (
                telefono_admin, telefonos_respaldo, grupos_activos, configurado_por
            ) VALUES ($1, $2, $3, $4)
            ON CONFLICT ((id IS NOT NULL))
            DO UPDATE SET
                telefono_admin = EXCLUDED.telefono_admin,
                telefonos_respaldo = EXCLUDED.telefonos_respaldo,
                grupos_activos = EXCLUDED.grupos_activos,
                fecha_actualizacion = CURRENT_TIMESTAMP
            """,
            config.telefono_admin,
            config.telefonos_respaldo,
            config.grupos_activos,
            current_user.id,
        )

        # Registrar acción
        await conn.execute(
            "SELECT registrar_accion_control($1, $2, $3, $4)",
            "config_updated",
            current_user.id,
            None,
            "Configuración actualizada",
        )

    return {"status": "success", "message": "Configuración guardada"}


@router.get("/config")
async def get_config(current_user: User = Depends(get_current_user)):
    """Obtiene configuración actual"""
    pool = get_pool()

    async with pool.acquire() as conn:
        config = await conn.fetchrow("SELECT * FROM get_whatsapp_config()")

    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    return dict(config)


# ============================================================================
# CONTACTOS ESPECIALES
# ============================================================================


@router.post("/contacts")
async def save_contacts(
    contacts: List[ContactoEspecial], current_user: User = Depends(get_current_user)
):
    """Guarda contactos especiales"""
    pool = get_pool()

    async with pool.acquire() as conn:
        for contact in contacts:
            await conn.execute(
                """
                INSERT INTO whatsapp_contactos_especiales (
                    telefono, nombre, etiqueta, descripcion,
                    comportamiento, contexto_ia, notificar_admin, creado_por
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (telefono)
                DO UPDATE SET
                    nombre = EXCLUDED.nombre,
                    etiqueta = EXCLUDED.etiqueta,
                    descripcion = EXCLUDED.descripcion,
                    comportamiento = EXCLUDED.comportamiento,
                    contexto_ia = EXCLUDED.contexto_ia,
                    notificar_admin = EXCLUDED.notificar_admin,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                """,
                contact.telefono,
                contact.nombre,
                contact.etiqueta,
                contact.descripcion,
                contact.comportamiento,
                contact.contexto_ia,
                contact.notificar_admin,
                current_user.id,
            )

    return {"status": "success", "count": len(contacts)}


@router.get("/contacts/{telefono}")
async def get_contact(telefono: str):
    """Obtiene comportamiento de un contacto"""
    pool = get_pool()

    async with pool.acquire() as conn:
        contact = await conn.fetchrow(
            """
            SELECT * FROM whatsapp_contactos_especiales
            WHERE telefono = $1 AND activo = true
            """,
            telefono,
        )

    if not contact:
        return {"comportamiento": "normal"}

    return dict(contact)


# ============================================================================
# GRUPOS
# ============================================================================


@router.get("/groups/{group_id}")
async def get_group(group_id: str):
    """Verifica si un grupo tiene bot activo"""
    pool = get_pool()

    async with pool.acquire() as conn:
        activo = await conn.fetchval("SELECT is_grupo_bot_activo($1)", group_id)

    return {"bot_activo": activo or False}


# ============================================================================
# QR (Reutiliza servicio existente)
# ============================================================================


@router.get("/qr")
async def get_qr(current_user: User = Depends(get_current_user)):
    """Obtiene QR actual desde Node.js"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{WHATSAPP_SERVICE_URL}/qr")
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=404, detail="No QR available")
    except httpx.RequestError as e:
        logger.error(f"Error obteniendo QR: {e}")
        raise HTTPException(status_code=503, detail="WhatsApp service unavailable")


@router.post("/qr")
async def generate_qr(current_user: User = Depends(get_current_user)):
    """Genera nuevo QR (proxy a Node.js)"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{WHATSAPP_SERVICE_URL}/control/start")
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=500, detail="Failed to start WhatsApp")
    except httpx.RequestError as e:
        logger.error(f"Error iniciando WhatsApp: {e}")
        raise HTTPException(status_code=503, detail="WhatsApp service unavailable")


# ============================================================================
# CONVERSACIONES
# ============================================================================


@router.get("/conversaciones")
async def get_conversaciones(
    limit: int = 50,
    estado: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Obtiene conversaciones de WhatsApp"""
    pool = get_pool()

    try:
        query = """
            SELECT
                c.id,
                c.id_contacto,
                co.nombre AS contacto_nombre,
                co.telefono,
                c.canal,
                c.estado,
                c.categoria,
                c.prioridad,
                c.fecha_ultima_actividad,
                c.id_paciente,
                (c.id_paciente IS NULL) AS es_nuevo_paciente,
                COALESCE(
                    (SELECT m.contenido
                     FROM mensajes m
                     WHERE m.id_conversacion = c.id
                     ORDER BY m.fecha_envio DESC
                     LIMIT 1),
                    ''
                ) AS ultimo_mensaje,
                COALESCE(
                    (SELECT COUNT(*)
                     FROM mensajes m
                     WHERE m.id_conversacion = c.id
                     AND m.fecha_lectura IS NULL
                     AND m.direccion = 'Entrante'),
                    0
                )::integer AS numero_mensajes_sin_leer
            FROM conversaciones c
            LEFT JOIN contactos co ON c.id_contacto = co.id
            WHERE 1=1
        """
        params = []

        if estado:
            query += " AND c.estado = $1"
            params.append(estado)

        query += " ORDER BY c.fecha_ultima_actividad DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)

        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [dict(row) for row in rows]

    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {e}")
        return []  # Retornar array vacío en lugar de error
