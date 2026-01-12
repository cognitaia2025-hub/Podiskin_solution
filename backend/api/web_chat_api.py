"""
Web Chat API - Integración con Agente WhatsApp
===============================================

Permite que el agente Maya que maneja WhatsApp también atienda
conversaciones desde la página web.

REUTILIZA TABLAS EXISTENTES:
- pacientes: Tabla principal compartida por todos los canales
- contactos: Relación entre canales y pacientes
- conversaciones: Sesiones de chat multi-canal
- mensajes: Historial de mensajes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import uuid

from db import get_pool
from auth import get_optional_current_user, User

# Importar el agente de WhatsApp
from agents.whatsapp_medico.graph import whatsapp_graph
from agents.whatsapp_medico.state import AgentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Web Chat"])

# ============================================================================
# MODELOS
# ============================================================================

class PatientInfo(BaseModel):
    """Información del paciente desde el frontend"""
    patient_id: Optional[str] = None
    first_name: Optional[str] = None
    first_last_name: Optional[str] = None
    is_registered: bool = False
    partial_id: Optional[str] = None

class UserContext(BaseModel):
    """Contexto del usuario desde el navegador"""
    page: str = "/"
    previous_messages: int = 0
    user_agent: str = ""

class ChatbotRequest(BaseModel):
    """Request del chatbot web"""
    message: str = Field(..., min_length=1, max_length=500)
    session_id: str = Field(..., description="UUID v4 de sesión")
    timestamp: str
    patient_info: Optional[PatientInfo] = None
    user_context: Optional[UserContext] = None

class ChatAction(BaseModel):
    """Acción sugerida al usuario"""
    type: str  # schedule_appointment, call, whatsapp, redirect
    label: str
    data: Dict[str, Any]

class ChatbotResponse(BaseModel):
    """Response del chatbot"""
    response: str
    session_id: str
    timestamp: str
    patient_id: Optional[str] = None
    actions: Optional[List[ChatAction]] = None
    suggestions: Optional[List[str]] = None

class PatientRegistrationRequest(BaseModel):
    """Registro de nuevo paciente"""
    first_name: str
    second_name: Optional[str] = None
    first_last_name: str
    second_last_name: Optional[str] = None
    birth_date: str  # YYYY-MM-DD

class PatientRegistrationResponse(BaseModel):
    """Respuesta de registro"""
    success: bool
    patient_id: str
    message: str

class PatientLookupRequest(BaseModel):
    """Búsqueda de paciente"""
    patient_id: Optional[str] = None
    first_name: Optional[str] = None
    first_last_name: Optional[str] = None
    birth_date: Optional[str] = None

class PatientLookupResponse(BaseModel):
    """Respuesta de búsqueda"""
    found: bool
    patient_id: Optional[str] = None
    first_name: Optional[str] = None
    first_last_name: Optional[str] = None
    registration_date: Optional[str] = None

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def extract_response_from_result(result: Dict[str, Any]) -> str:
    """Extrae la respuesta del resultado del agente"""
    
    # El agente retorna en 'messages' o 'message'
    if 'messages' in result and result['messages']:
        last_msg = result['messages'][-1]
        if hasattr(last_msg, 'content'):
            return last_msg.content
        elif isinstance(last_msg, dict):
            return last_msg.get('content', 'No pude procesar tu mensaje.')
    
    if 'message' in result:
        return result['message']
    
    # Fallback
    return "Mensaje recibido. ¿En qué más puedo ayudarte?"

def generate_suggestions(user_message: str, fuente: str) -> List[str]:
    """Genera sugerencias contextuales"""
    
    keywords = user_message.lower()
    suggestions = []
    
    if 'cita' in keywords or 'agendar' in keywords:
        suggestions.extend([
            "¿Qué servicios ofrecen?",
            "Ver horarios disponibles",
            "Confirmar mi cita"
        ])
    elif 'precio' in keywords or 'costo' in keywords:
        suggestions.extend([
            "¿Qué servicios incluye?",
            "¿Aceptan seguro?",
            "Ver planes de pago"
        ])
    elif 'ubicación' in keywords or 'dirección' in keywords:
        suggestions.extend([
            "¿Tienen estacionamiento?",
            "¿Cómo llego en transporte público?",
            "Contactar por WhatsApp"
        ])
    else:
        suggestions.extend([
            "Agendar una cita",
            "Ver servicios",
            "Hablar con un asesor"
        ])
    
    return suggestions[:3]  # Máximo 3 sugerencias

# ============================================================================
# ENDPOINT 1: CHATBOT MESSAGE (Principal)
# ============================================================================

@router.post("/chatbot/message", response_model=ChatbotResponse)
async def handle_chatbot_message(
    request: ChatbotRequest,
    x_session_id: Optional[str] = Header(None),
    x_client_type: Optional[str] = Header(None)
):
    """
    Procesa mensajes del chatbot web usando el agente de WhatsApp.
    
    REUTILIZA:
    - Tabla contactos para vincular sesión web con paciente
    - Tabla conversaciones con canal='web'
    - Tabla mensajes para historial
    """
    
    logger.info(f"💬 [Web Chat] Mensaje recibido (sesión: {request.session_id[:8]}...)")
    logger.info(f"   Mensaje: {request.message[:50]}...")
    logger.info(f"   Paciente: {request.patient_info.patient_id if request.patient_info else 'No identificado'}")
    
    pool = get_pool()
    
    try:
        # 1. BUSCAR O CREAR CONTACTO Y CONVERSACIÓN
        id_paciente = None
        id_contacto = None
        id_conversacion = None
        
        if request.patient_info and request.patient_info.patient_id:
            # Buscar paciente por patient_id
            paciente = await pool.fetchrow("""
                SELECT id, patient_id, primer_nombre, primer_apellido
                FROM pacientes
                WHERE patient_id = $1
            """, request.patient_info.patient_id)
            
            if paciente:
                id_paciente = paciente['id']
                
                # Buscar o crear contacto web
                contacto = await pool.fetchrow("""
                    INSERT INTO contactos (id_paciente, nombre, tipo, origen, activo)
                    VALUES ($1, $2, 'Lead_Calificado', 'web', true)
                    ON CONFLICT (id_paciente) 
                    DO UPDATE SET fecha_ultima_interaccion = CURRENT_TIMESTAMP
                    RETURNING id
                """, id_paciente, f"{paciente['primer_nombre']} {paciente['primer_apellido']}")
                
                id_contacto = contacto['id']
        
        # 2. BUSCAR O CREAR CONVERSACIÓN
        conversacion = await pool.fetchrow("""
            INSERT INTO conversaciones (
                id_contacto, canal, estado, session_id, 
                fecha_inicio, fecha_ultima_actividad, numero_mensajes
            )
            VALUES ($1, 'web', 'Activa', $2::uuid, NOW(), NOW(), 0)
            ON CONFLICT (session_id)
            DO UPDATE SET 
                fecha_ultima_actividad = NOW(),
                numero_mensajes = conversaciones.numero_mensajes + 1
            RETURNING id, session_id
        """, id_contacto, request.session_id)
        
        id_conversacion = conversacion['id']
        
        # 3. GUARDAR MENSAJE DEL USUARIO
        await pool.execute("""
            INSERT INTO mensajes (
                id_conversacion, direccion, enviado_por_tipo, 
                tipo_contenido, contenido, estado_entrega
            )
            VALUES ($1, 'Entrante', 'Contacto', 'Texto', $2, 'Recibido')
        """, id_conversacion, request.message)
        
        # 4. CREAR ESTADO INICIAL PARA EL AGENTE
        initial_state = AgentState(
            messages=[],
            contact_id=request.patient_info.patient_id if request.patient_info else request.session_id,
            conversation_id=str(conversacion['session_id']),
            message=request.message,
            retrieved_context="",
            fuente="",
            confidence=0.0,
            metadata={
                "channel": "web",
                "session_id": request.session_id,
                "id_paciente": id_paciente,
                "id_contacto": id_contacto,
                "id_conversacion": id_conversacion,
                "patient_info": request.patient_info.dict() if request.patient_info else None,
                "user_context": request.user_context.dict() if request.user_context else None,
                "client_type": x_client_type or "web",
                "timestamp": request.timestamp
            },
            requires_human=False
        )
        
        # 5. EJECUTAR AGENTE MAYA
        logger.info("🤖 Ejecutando agente Maya (web)...")
        
        config = {
            "configurable": {
                "thread_id": f"web_{request.session_id}"
            }
        }
        
        result = await whatsapp_graph.ainvoke(initial_state, config=config)
        
        # 6. EXTRAER RESPUESTA
        bot_response = extract_response_from_result(result)
        
        logger.info(f"✅ Respuesta generada: {bot_response[:50]}...")
        
        # 7. GUARDAR RESPUESTA DEL BOT
        await pool.execute("""
            INSERT INTO mensajes (
                id_conversacion, direccion, enviado_por_tipo,
                tipo_contenido, contenido, estado_entrega
            )
            VALUES ($1, 'Saliente', 'Bot', 'Texto', $2, 'Enviado')
        """, id_conversacion, bot_response)
        
        # 8. ACTUALIZAR CONTADOR DE MENSAJES BOT
        await pool.execute("""
            UPDATE conversaciones
            SET numero_mensajes_bot = numero_mensajes_bot + 1
            WHERE id = $1
        """, id_conversacion)
        
        # 9. GENERAR SUGERENCIAS
        suggestions = generate_suggestions(request.message, result.get('fuente', ''))
        
        # 10. CONSTRUIR RESPUESTA
        response = ChatbotResponse(
            response=bot_response,
            session_id=request.session_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            patient_id=request.patient_info.patient_id if request.patient_info else None,
            suggestions=suggestions
        )
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje web: {e}", exc_info=True)
        
        return ChatbotResponse(
            response="Disculpa, tuve un problema procesando tu mensaje. 😔\n\nPuedes intentar:\n• Reformular tu pregunta\n• Llamar al: 686 108 3647\n• Intentar de nuevo en unos momentos",
            session_id=request.session_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            patient_id=request.patient_info.patient_id if request.patient_info else None
        )

# ============================================================================
# ENDPOINT 2: REGISTRO DE PACIENTE
# ============================================================================

@router.post("/patient/register", response_model=PatientRegistrationResponse)
async def register_patient(request: PatientRegistrationRequest):
    """
    Registra un nuevo paciente en la tabla pacientes.
    
    El trigger generate_patient_id() generará automáticamente el patient_id
    en formato: [AP]-[NO]-[MMDD]-[####]
    """
    
    logger.info(f"📝 [Registro] Nuevo paciente: {request.first_name} {request.first_last_name}")
    
    pool = get_pool()
    
    try:
        # Validaciones básicas
        if not request.first_name or not request.first_last_name:
            raise HTTPException(status_code=400, detail="Nombre y apellido son requeridos")
        
        # Insertar en tabla pacientes (el trigger generará patient_id automáticamente)
        result = await pool.fetchrow("""
            INSERT INTO pacientes (
                primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                fecha_nacimiento, activo
            ) 
            VALUES ($1, $2, $3, $4, $5, true)
            RETURNING id, patient_id, primer_nombre, primer_apellido
        """,
            request.first_name, request.second_name,
            request.first_last_name, request.second_last_name,
            request.birth_date
        )
        
        patient_id = result['patient_id']
        
        logger.info(f"✅ Paciente registrado exitosamente: {patient_id}")
        
        return PatientRegistrationResponse(
            success=True,
            patient_id=patient_id,
            message="Paciente registrado exitosamente"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error registrando paciente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar paciente: {str(e)}")

# ============================================================================
# ENDPOINT 3: BÚSQUEDA DE PACIENTE
# ============================================================================

@router.post("/patient/lookup", response_model=PatientLookupResponse)
async def lookup_patient(request: PatientLookupRequest):
    """
    Busca un paciente existente por ID o datos personales.
    """
    
    pool = get_pool()
    
    try:
        patient = None
        
        # Opción 1: Búsqueda por patient_id
        if request.patient_id:
            patient = await pool.fetchrow("""
                SELECT id, patient_id, primer_nombre, primer_apellido, fecha_creacion
                FROM pacientes
                WHERE patient_id = $1
            """, request.patient_id)
        
        # Opción 2: Búsqueda por nombre, apellido y fecha de nacimiento
        elif request.first_name and request.first_last_name and request.birth_date:
            patient = await pool.fetchrow("""
                SELECT id, patient_id, primer_nombre, primer_apellido, fecha_creacion
                FROM pacientes
                WHERE LOWER(primer_nombre) = LOWER($1)
                  AND LOWER(primer_apellido) = LOWER($2)
                  AND fecha_nacimiento = $3
                LIMIT 1
            """, request.first_name, request.first_last_name, request.birth_date)
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Debe proporcionar patient_id o (first_name + first_last_name + birth_date)"
            )
        
        # Retornar resultado
        if patient:
            return PatientLookupResponse(
                found=True,
                patient_id=patient['patient_id'],
                first_name=patient['primer_nombre'],
                first_last_name=patient['primer_apellido'],
                registration_date=patient['fecha_creacion'].isoformat() if patient.get('fecha_creacion') else None
            )
        else:
            return PatientLookupResponse(
                found=False,
                patient_id=None,
                first_name=None,
                first_last_name=None,
                registration_date=None
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error buscando paciente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al buscar paciente: {str(e)}")

# ============================================================================
# ENDPOINT 4: ESTADÍSTICAS DE SESIÓN (Opcional)
# ============================================================================

@router.get("/chatbot/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Obtiene información de una sesión de chat web.
    """
    
    pool = get_pool()
    
    try:
        # Usar la vista web_chat_sessions
        session = await pool.fetchrow("""
            SELECT * FROM web_chat_sessions
            WHERE session_id = $1::uuid
        """, session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Obtener mensajes de la sesión
        messages = await pool.fetch("""
            SELECT * FROM web_chat_messages
            WHERE session_id = $1::uuid
            ORDER BY timestamp ASC
        """, session_id)
        
        return {
            "session": dict(session),
            "messages": [dict(msg) for msg in messages]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo sesión: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener sesión: {str(e)}")

# ============================================================================
# ENDPOINT 5: HEALTH CHECK
# ============================================================================

@router.get("/chatbot/health")
async def health_check():
    """
    Verifica que el servicio de chatbot web esté funcionando.
    """
    
    pool = get_pool()
    
    try:
        # Verificar conexión a BD
        await pool.fetchval("SELECT 1")
        
        # Verificar que las tablas existan
        tables_check = await pool.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name IN ('pacientes', 'contactos', 'conversaciones', 'mensajes')
        """)
        
        if tables_check != 4:
            return {
                "status": "degraded",
                "message": "Faltan tablas en la base de datos",
                "tables_found": tables_check
            }
        
        return {
            "status": "ok",
            "message": "Web Chat API funcionando correctamente",
            "agent": "whatsapp_medico (Maya)",
            "channel": "web",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"❌ Health check falló: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
