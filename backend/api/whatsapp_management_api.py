"""
WhatsApp Management API
=======================

Endpoints para gestión de WhatsApp desde el frontend.

Incluye:
- Sandbox de simulación
- Gestión de dudas pendientes
- Gestión de knowledge base
- Gestión de behavior rules
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime
import json

from db import get_pool
from auth import get_current_user, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Management"])

# ============================================================================
# MODELOS
# ============================================================================

class SimulateRequest(BaseModel):
    message: str
    contact_id: int

class SimulateResponse(BaseModel):
    response: str
    metadata: dict
    confidence: float
    fuente: str

class ResponderDudaRequest(BaseModel):
    duda_id: int
    respuesta: str
    aprobar_y_aprender: bool = False

# ============================================================================
# SANDBOX
# ============================================================================

@router.post("/sandbox/simulate", response_model=SimulateResponse)
async def simulate_conversation(
    request: SimulateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Simula una conversación con el agente Maya en modo sandbox.
    
    TODO: 
    1. Crear state inicial con message y contact_id
    2. Ejecutar agente con create_whatsapp_agent()
    3. Extraer respuesta y metadata
    4. Retornar SimulateResponse
    """
    
    try:
        # TODO: Integrar con el agente de WhatsApp
        # from agents.whatsapp_medico.graph import create_whatsapp_agent, AgentState
        
        # Por ahora, respuesta simulada
        logger.info(f"Simulando conversación: {request.message[:50]}...")
        
        return SimulateResponse(
            response=f"[SIMULADO] Respuesta a: {request.message}",
            metadata={
                "sandbox_mode": True,
                "contact_id": request.contact_id,
                "timestamp": datetime.now().isoformat()
            },
            confidence=0.8,
            fuente="sandbox"
        )
    
    except Exception as e: 
        logger.error(f"Error en simulación: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DUDAS PENDIENTES
# ============================================================================

@router.get("/learning/dudas-pendientes")
async def get_dudas_pendientes(
    estado: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene lista de dudas pendientes.
    
    Args:
        estado: Filtro por estado (pendiente, respondida, etc.)
        
    Returns:
        Lista de dudas pendientes
    """
    
    pool = get_pool()
    
    query = """
        SELECT 
            dp.id,
            dp.pregunta_original,
            dp.contexto_mensaje,
            dp.estado,
            dp.fecha_creacion,
            c.id as conversacion_id,
            co.nombre as contacto_nombre,
            co.telefono as contacto_telefono
        FROM dudas_pendientes dp
        INNER JOIN conversaciones c ON dp.id_conversacion = c.id
        INNER JOIN contactos co ON c.id_contacto = co.id
        WHERE ($1::text IS NULL OR dp.estado = $1)
        ORDER BY dp.fecha_creacion DESC
        LIMIT 50
    """
    
    rows = await pool.fetch(query, estado)
    
    return [dict(row) for row in rows]


@router.post("/learning/responder-duda")
async def responder_duda(
    request: ResponderDudaRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Responde una duda pendiente y opcionalmente la aprende.
    
    Args:
        request: Datos de la respuesta
        
    Returns:
        Confirmación de operación
    """
    
    pool = get_pool()
    
    try:
        # Actualizar duda
        await pool.execute(
            """
            UPDATE dudas_pendientes
            SET respuesta_admin = $1,
                estado = 'respondida',
                fecha_respuesta = NOW(),
                respondido_por = $2
            WHERE id = $3
            """,
            request.respuesta, current_user.id, request.duda_id
        )
        
        if request.aprobar_y_aprender:
            # TODO: Llamar a learning_curator para generalizar conocimiento
            # TODO: Guardar en knowledge_base_validated con aprobado=false
            # TODO: Generar embedding
            logger.info(f"Duda #{request.duda_id} marcada para aprendizaje")
        
        # TODO: Enviar respuesta al paciente vía Twilio
        
        return {
            "success": True,
            "message": "Duda respondida correctamente",
            "aprendido": request.aprobar_y_aprender
        }
    
    except Exception as e: 
        logger.error(f"Error respondiendo duda: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# KNOWLEDGE BASE
# ============================================================================

@router.get("/learning/knowledge-base")
async def get_knowledge_base(
    categoria: Optional[str] = None,
    aprobado: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene entries de knowledge base.
    
    Args:
        categoria: Filtro por categoría
        aprobado: Filtro por estado de aprobación
        
    Returns:
        Lista de entries de knowledge base
    """
    
    pool = get_pool()
    
    query = """
        SELECT 
            id, pregunta, respuesta, categoria,
            aprobado, origen, veces_consultada, efectividad_score,
            feedback_positivo, feedback_negativo,
            fecha_creacion, fecha_aprobacion
        FROM knowledge_base_validated
        WHERE ($1::text IS NULL OR categoria = $1)
        AND ($2::boolean IS NULL OR aprobado = $2)
        ORDER BY fecha_creacion DESC
        LIMIT 100
    """
    
    rows = await pool.fetch(query, categoria, aprobado)
    
    return [dict(row) for row in rows]


@router.put("/learning/knowledge-base/{kb_id}")
async def update_knowledge_base(
    kb_id: int,
    pregunta: Optional[str] = None,
    respuesta: Optional[str] = None,
    aprobado: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una entry de knowledge base.
    
    Args:
        kb_id: ID de la entry
        pregunta: Nueva pregunta (opcional)
        respuesta: Nueva respuesta (opcional)
        aprobado: Nuevo estado de aprobación (opcional)
        
    Returns:
        Confirmación de actualización
    """
    
    pool = get_pool()
    
    try:
        updates = []
        params = []
        param_counter = 1
        
        if pregunta is not None:
            updates.append(f"pregunta = ${param_counter}")
            params.append(pregunta)
            param_counter += 1
            # TODO: Regenerar embedding si cambia la pregunta
        
        if respuesta is not None:
            updates.append(f"respuesta = ${param_counter}")
            params.append(respuesta)
            param_counter += 1
        
        if aprobado is not None:
            updates.append(f"aprobado = ${param_counter}")
            params.append(aprobado)
            param_counter += 1
            
            if aprobado:
                updates.append(f"fecha_aprobacion = NOW()")
        
        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        
        params.append(kb_id)
        query = f"""
            UPDATE knowledge_base_validated
            SET {', '.join(updates)}
            WHERE id = ${param_counter}
        """
        
        await pool.execute(query, *params)
        
        return {
            "success": True,
            "message": "Knowledge base actualizada",
            "kb_id": kb_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando KB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
