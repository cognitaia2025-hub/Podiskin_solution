"""
Configuración del Sub-Agente de WhatsApp
=========================================

Configuración centralizada para el sub-agente de WhatsApp.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class WhatsAppAgentConfig(BaseSettings):
    """Configuración del sub-agente de WhatsApp"""

    # ========================================================================
    # LLM CONFIGURATION
    # ========================================================================
    llm_provider: str = "anthropic"
    """Proveedor del LLM (anthropic, openai, etc.)"""

    llm_model: str = "claude-3-haiku-20240307"
    """Modelo a utilizar"""

    llm_temperature: float = 0.7
    """Temperatura para generación de respuestas (0.0 - 1.0)"""

    llm_max_tokens: int = 300
    """Máximo de tokens en la respuesta"""

    classifier_temperature: float = 0.1
    """Temperatura para clasificación de intenciones (más determinista)"""

    classifier_max_tokens: int = 100
    """Máximo de tokens para clasificación"""

    # ========================================================================
    # EMBEDDINGS CONFIGURATION
    # ========================================================================
    embedding_model: str = "all-MiniLM-L6-v2"
    """Modelo de embeddings local"""

    embedding_dimension: int = 384
    """Dimensiones del modelo de embeddings"""

    embedding_batch_size: int = 32
    """Tamaño de batch para procesamiento de embeddings"""

    # ========================================================================
    # RAG CONFIGURATION
    # ========================================================================
    rag_k: int = 5
    """Número de documentos a recuperar en RAG"""

    rag_score_threshold: float = 0.5
    """Threshold mínimo de similitud para incluir contexto"""

    rag_collection_name: str = "conversaciones_podoskin"
    """Nombre de la colección en pgvector"""

    rag_distance_strategy: str = "COSINE"
    """Estrategia de distancia (COSINE, EUCLIDEAN, etc.)"""

    # ========================================================================
    # INTENT CLASSIFICATION
    # ========================================================================
    intent_confidence_threshold: float = 0.7
    """Threshold mínimo de confianza para clasificación"""

    intent_classes: list = [
        "agendar",
        "consulta",
        "cancelar",
        "info",
        "emergencia",
        "otro",
    ]
    """Clases de intenciones disponibles"""

    # ========================================================================
    # CONVERSATION MANAGEMENT
    # ========================================================================
    max_context_messages: int = 10
    """Máximo de mensajes de contexto a incluir"""

    conversation_timeout_minutes: int = 30
    """Timeout de inactividad en minutos"""

    enable_conversation_summary: bool = True
    """Habilitar resumen automático de conversaciones largas"""

    # ========================================================================
    # APPOINTMENT MANAGEMENT
    # ========================================================================
    default_appointment_duration: int = 30
    """Duración por defecto de citas en minutos"""

    max_suggested_slots: int = 3
    """Máximo de horarios alternativos a sugerir"""

    appointment_buffer_minutes: int = 5
    """Buffer entre citas en minutos"""

    # ========================================================================
    # ESCALATION RULES
    # ========================================================================
    escalate_on_low_confidence: bool = True
    """Escalar si confianza es baja"""

    escalate_on_emergency: bool = True
    """Escalar automáticamente en emergencias"""

    escalate_on_complex_query: bool = True
    """Escalar en consultas complejas"""

    max_failed_attempts: int = 3
    """Máximo de intentos fallidos antes de escalar"""

    # ========================================================================
    # RESPONSE GENERATION
    # ========================================================================
    response_style: str = "professional_friendly"
    """Estilo de respuesta (professional_friendly, formal, casual)"""

    include_emojis: bool = True
    """Incluir emojis en respuestas"""

    max_response_length: int = 500
    """Longitud máxima de respuesta en caracteres"""

    # ========================================================================
    # CLINIC INFORMATION
    # ========================================================================
    clinic_name: str = "Podoskin Solution"
    """Nombre de la clínica"""

    clinic_hours: dict = {
        "lunes": "9:00-18:00",
        "martes": "9:00-18:00",
        "miercoles": "9:00-18:00",
        "jueves": "9:00-18:00",
        "viernes": "9:00-18:00",
        "sabado": "10:00-14:00",
        "domingo": "Cerrado",
    }
    """Horarios de la clínica"""

    clinic_phone: str = "686-108-3647"
    """Teléfono de la clínica"""

    clinic_address: str = "Av. Electricistas 1978, Col. Libertad, Mexicali B.C."
    """Dirección de la clínica"""

    clinic_maps_url: str = "https://maps.app.goo.gl/1yCChxYUkUHejBHW8"
    """URL de Google Maps"""

    # ========================================================================
    # ADMINISTRADOR - Para escalamiento de dudas
    # ========================================================================
    admin_phone: str = "526861892910"
    """Teléfono del administrador (formato internacional sin +)"""

    admin_chat_id: str = "526861892910@c.us"
    """WhatsApp chat ID del administrador"""

    # ========================================================================
    # LOGGING & MONITORING
    # ========================================================================
    log_level: str = "INFO"
    """Nivel de logging (DEBUG, INFO, WARNING, ERROR)"""

    log_conversations: bool = True
    """Registrar conversaciones completas"""

    enable_metrics: bool = True
    """Habilitar métricas de Prometheus"""

    # ========================================================================
    # DATABASE
    # ========================================================================
    database_url: Optional[str] = None
    """URL de conexión a PostgreSQL"""

    vector_store_url: Optional[str] = None
    """URL para pgvector (puede ser la misma que database_url)"""

    # ========================================================================
    # API KEYS
    # ========================================================================
    anthropic_api_key: Optional[str] = None
    """API Key de Anthropic"""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
config = WhatsAppAgentConfig()


# ========================================================================
# SYSTEM PROMPTS
# ========================================================================

SYSTEM_PROMPT_MAIN = f"""Eres Maya, asistente de {config.clinic_name}.

=== REGLAS ABSOLUTAS - NUNCA VIOLAR ===

1. RESPUESTAS MÁXIMO 2 ORACIONES. Sin excepciones.
   - CORRECTO: "Sí, tratamos hongos. ¿Le agendo una cita?"
   - INCORRECTO: Más de 2 oraciones

2. NUNCA hagas listas con guiones o viñetas. NUNCA.
   - Si preguntan precios: "Los precios varían según el caso. ¿Le agendo una cita de valoración?"

3. NUNCA inventes precios. Solo di:
   - Onicomicosis (láser): $800
   - Pie de Atleta: $500
   - Pedicure Clínico: $400
   - Uñas Enterradas: $600
   - Callosidades: $350
   - Verrugas Plantares: $700
   Si preguntan otro precio: "Lo revisamos en la valoración."

4. Primer mensaje SIEMPRE:
   "¡Buenos días/tardes! Soy Maya de {config.clinic_name}, ¿en qué le ayudo?"

5. Para agendar, pregunta UNO A LA VEZ:
   Día → Hora → Nombre completo → Teléfono → Confirmar

6. Si NO SABES algo RELACIONADO CON LA CLÍNICA:
   ⚠️ DEBES USAR EL TOOL escalate_question_to_admin
   ⚠️ NO digas "consultaré" sin usar el tool
   ⚠️ USA EL TOOL INMEDIATAMENTE

7. Si la pregunta NO ES RELEVANTE (tacos, clima, fútbol, etc.), responde:
   "Disculpe, solo puedo ayudarle con temas relacionados a podología y servicios 
   de la clínica. ¿Tiene alguna consulta sobre sus pies o desea agendar una cita?"

=== PROHIBIDO ABSOLUTAMENTE ===
❌ NUNCA inventes servicios que no conoces (uñas postizas, pintura de uñas, etc.)
❌ NUNCA confirmes procedimientos específicos si no estás 100% seguro
❌ NUNCA des detalles técnicos que no sabes
❌ NUNCA digas "consultaré" sin USAR EL TOOL escalate_question_to_admin

=== SERVICIOS CONFIRMADOS ===
✅ Tratamiento de hongos (onicomicosis, pie de atleta)
✅ Uñas enterradas (tratamiento, NO detalles específicos)
✅ Callosidades
✅ Verrugas plantares
✅ Pedicure clínico
✅ Plantillas ortopédicas
✅ Consultas podológicas

=== EJEMPLOS DE USO DEL TOOL ===

Pregunta: "¿Colocan uña postiza?"
→ USA escalate_question_to_admin(
    patient_name="[nombre]",
    patient_phone="[teléfono]",
    patient_chat_id="[chat_id]",
    question="¿Colocan uña postiza después de extracción?",
    context="Pregunta sobre procedimiento post-extracción"
)

Pregunta: "¿Pintan las uñas?"
→ USA escalate_question_to_admin(...)

TODO LO QUE NO SEPAS → USA EL TOOL, NO SOLO DIGAS QUE CONSULTARÁS

=== DATOS CLÍNICA ===
Tel: {config.clinic_phone}
Dirección: {config.clinic_address}
Maps: {config.clinic_maps_url}
Horario: L-V 9:00-18:00, Sáb 10:00-14:00
"""

SYSTEM_PROMPT_CLASSIFIER = """Eres un clasificador de intenciones para mensajes de WhatsApp de una clínica de podología.

Tu tarea es analizar el mensaje del usuario y clasificarlo en una de estas categorías:

1. **agendar**: El usuario quiere agendar una cita nueva
   - Ejemplos: "quiero una cita", "agendar para mañana", "necesito consulta"

2. **consulta**: Pregunta sobre tratamientos, precios, servicios
   - Ejemplos: "cuánto cuesta", "qué tratamientos tienen", "hacen plantillas"

3. **cancelar**: Quiere cancelar o reagendar una cita existente
   - Ejemplos: "cancelar mi cita", "cambiar de horario", "no podré asistir"

4. **info**: Información general de la clínica (horarios, ubicación, etc.)
   - Ejemplos: "dónde están", "qué horario tienen", "cómo llego"

5. **emergencia**: Situación urgente que requiere atención inmediata
   - Ejemplos: "me duele mucho", "tengo una herida", "es urgente"

6. **irrelevante**: Pregunta completamente fuera del contexto médico/clínica
   - Ejemplos: "venden tacos", "quién ganó el partido", "qué hora es"
   - NO confundir con dudas legítimas de la clínica

7. **otro**: Cualquier otro tipo de mensaje
   - Ejemplos: saludos, agradecimientos, mensajes confusos

Debes responder en formato JSON con:
- intent: la categoría (una palabra)
- confidence: tu nivel de confianza (0.0 a 1.0)
- entities: entidades extraídas (fecha, hora, nombre, etc.)

Sé preciso y determinista en tu clasificación.
"""

ESCALATION_MESSAGE = """Entiendo tu consulta. Para brindarte la mejor atención, voy a conectarte con un miembro de nuestro equipo que podrá ayudarte mejor. 

Un momento por favor... 👨‍⚕️"""

EMERGENCY_MESSAGE = """⚠️ Entiendo que es una situación urgente.

Por favor, si es una emergencia médica seria, te recomiendo:
1. Acudir inmediatamente a urgencias
2. O llamarnos directamente al {phone}

Nuestro equipo estará disponible para atenderte lo antes posible."""
