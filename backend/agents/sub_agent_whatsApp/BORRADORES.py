# Borradores de Componentes - Sub-Agente WhatsApp
# ==================================================
# Este archivo contiene plantillas y borradores para los componentes
# que aún faltan por implementar

# ============================================================================
# GRAPH.PY - Grafo Principal
# ============================================================================

"""
graph.py - Grafo principal del sub-agente de WhatsApp

Componentes necesarios:
1. Importar todos los nodos
2. Crear StateGraph con WhatsAppAgentState
3. Definir nodos y edges
4. Implementar routing condicional
5. Configurar checkpointer con PostgreSQL
6. Compilar y exportar el grafo
"""

# Pseudocódigo:
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from .state import WhatsAppAgentState
from .nodes import *
from .config import config

# Crear grafo
workflow = StateGraph(WhatsAppAgentState)

# Agregar nodos
workflow.add_node("classify", classify_intent_node)
workflow.add_node("retrieve", retrieve_context_node)
workflow.add_node("check_patient", check_patient_node)
workflow.add_node("handle_appointment", handle_appointment_node)
workflow.add_node("handle_query", handle_query_node)
workflow.add_node("handle_cancellation", handle_cancellation_node)
workflow.add_node("escalate", escalate_to_human_node)
workflow.add_node("generate", generate_response_node)

# Entry point
workflow.set_entry_point("classify")


# Routing condicional
def route_by_intent(state):
    if state["confidence"] < config.intent_confidence_threshold:
        return "escalate"

    intent_routing = {
        "agendar": "check_patient",
        "consulta": "retrieve",
        "cancelar": "handle_cancellation",
        "info": "handle_query",
        "emergencia": "escalate",
    }
    return intent_routing.get(state["intent"], "generate")


workflow.add_conditional_edges("classify", route_by_intent)

# Edges secuenciales
workflow.add_edge("check_patient", "handle_appointment")
workflow.add_edge("retrieve", "handle_query")
workflow.add_edge("handle_appointment", "generate")
workflow.add_edge("handle_query", "generate")
workflow.add_edge("handle_cancellation", "generate")
workflow.add_edge("escalate", "generate")
workflow.add_edge("generate", END)

# Checkpointer
checkpointer = PostgresSaver(conn_string=config.database_url)

# Compilar
app = workflow.compile(checkpointer=checkpointer)


# ============================================================================
# NODES/RETRIEVE_CONTEXT.PY - Nodo de RAG
# ============================================================================

"""
retrieve_context.py - Recuperar contexto semántico

Responsabilidades:
1. Obtener último mensaje del usuario
2. Generar embedding del mensaje
3. Buscar en pgvector conversaciones similares
4. Filtrar por contact_id
5. Obtener historial de citas si es paciente
6. Actualizar estado con contexto recuperado
"""


# Pseudocódigo:
async def retrieve_context_node(state: WhatsAppAgentState):
    last_message = state["messages"][-1]["content"]
    contact_id = state["contact_id"]

    # Búsqueda semántica
    context_docs = await rag_tools.retrieve_context(
        query=last_message, contact_id=contact_id, k=config.rag_k
    )

    # Filtrar por score
    filtered_context = [
        doc for doc in context_docs if doc["score"] >= config.rag_score_threshold
    ]

    # Obtener historial de citas si es paciente
    appointment_history = []
    if state["patient_id"]:
        appointment_history = await patient_tools.get_patient_history(
            state["patient_id"]
        )

    return {
        **state,
        "retrieved_context": filtered_context,
        "appointment_history": appointment_history,
        "processing_stage": "handle_action",
    }


# ============================================================================
# NODES/CHECK_PATIENT.PY - Verificar Paciente
# ============================================================================

"""
check_patient.py - Verificar si el contacto es paciente

Responsabilidades:
1. Buscar paciente asociado al contact_id
2. Si existe, obtener información completa
3. Si no existe, marcar como prospecto
4. Actualizar estado con patient_info
"""


# Pseudocódigo:
async def check_patient_node(state: WhatsAppAgentState):
    contact_id = state["contact_id"]

    # Buscar paciente
    patient = await patient_tools.search_patient(contact_id=contact_id)

    if patient:
        patient_info = await patient_tools.get_patient_info(patient["id"])

        return {
            **state,
            "patient_id": patient["id"],
            "patient_info": patient_info,
            "processing_stage": "handle_action",
        }
    else:
        return {
            **state,
            "patient_id": None,
            "patient_info": None,
            "next_action": "register_patient",
            "processing_stage": "handle_action",
        }


# ============================================================================
# NODES/HANDLE_APPOINTMENT.PY - Gestionar Agendamiento
# ============================================================================

"""
handle_appointment.py - Gestionar proceso de agendamiento

Responsabilidades:
1. Verificar si tiene fecha y hora en entities
2. Si no, solicitar fecha y hora
3. Verificar disponibilidad
4. Si disponible, crear cita pendiente
5. Si no disponible, sugerir alternativas
6. Actualizar estado con pending_appointment
"""


# Pseudocódigo:
async def handle_appointment_node(state: WhatsAppAgentState):
    entities = state["entities"]
    patient_id = state["patient_id"]

    # Si no es paciente, necesita registro
    if not patient_id:
        return {
            **state,
            "next_action": "register_patient",
            "requires_human": True,
            "escalation_reason": "Nuevo paciente requiere registro",
        }

    # Verificar si tiene fecha y hora
    if "fecha" not in entities or "hora" not in entities:
        return {**state, "next_action": "request_datetime"}

    # Verificar disponibilidad
    available = await appointment_tools.check_availability(
        fecha=entities["fecha"], hora=entities["hora"]
    )

    if available:
        # Crear cita pendiente
        pending = {
            "fecha": entities["fecha"],
            "hora": entities["hora"],
            "tratamiento_id": 1,  # Default: Consulta General
            "podologo_id": 1,
            "disponible": True,
        }

        return {
            **state,
            "pending_appointment": pending,
            "next_action": "confirm_appointment",
        }
    else:
        # Sugerir alternativas
        slots = await appointment_tools.get_available_slots(fecha=entities["fecha"])

        return {
            **state,
            "suggested_slots": slots[: config.max_suggested_slots],
            "next_action": "suggest_alternatives",
        }


# ============================================================================
# NODES/HANDLE_QUERY.PY - Responder Consultas
# ============================================================================

"""
handle_query.py - Responder consultas sobre tratamientos/precios

Responsabilidades:
1. Analizar tipo de consulta
2. Buscar información relevante
3. Usar contexto recuperado de RAG
4. Preparar información para generar respuesta
"""


# Pseudocódigo:
async def handle_query_node(state: WhatsAppAgentState):
    last_message = state["messages"][-1]["content"].lower()

    # Detectar tipo de consulta
    if "precio" in last_message or "costo" in last_message:
        info = await query_tools.get_prices()
        info_type = "prices"
    elif "tratamiento" in last_message or "servicio" in last_message:
        info = await query_tools.get_treatment_info()
        info_type = "treatments"
    elif "horario" in last_message or "ubicación" in last_message:
        info = await query_tools.get_clinic_info()
        info_type = "clinic_info"
    else:
        # Búsqueda general en FAQs
        info = await query_tools.search_faq(last_message)
        info_type = "faq"

    return {
        **state,
        "entities": {
            **state["entities"],
            "query_type": info_type,
            "query_result": info,
        },
        "next_action": "provide_info",
    }


# ============================================================================
# NODES/HANDLE_CANCELLATION.PY - Gestionar Cancelaciones
# ============================================================================

"""
handle_cancellation.py - Gestionar cancelación/reagendamiento

Responsabilidades:
1. Buscar citas activas del paciente
2. Si tiene citas, preguntar cuál cancelar
3. Procesar cancelación o reagendamiento
4. Actualizar estado
"""


# Pseudocódigo:
async def handle_cancellation_node(state: WhatsAppAgentState):
    patient_id = state["patient_id"]

    if not patient_id:
        return {**state, "next_action": "no_appointments", "requires_human": False}

    # Buscar citas activas
    active_appointments = await appointment_tools.get_active_appointments(
        patient_id=patient_id
    )

    if not active_appointments:
        return {**state, "next_action": "no_appointments"}

    # Si tiene múltiples citas, necesita especificar
    if len(active_appointments) > 1:
        return {
            **state,
            "entities": {
                **state["entities"],
                "active_appointments": active_appointments,
            },
            "next_action": "select_appointment",
        }

    # Si solo tiene una, proceder con cancelación
    appointment = active_appointments[0]

    return {
        **state,
        "pending_appointment": appointment,
        "next_action": "confirm_cancellation",
    }


# ============================================================================
# NODES/ESCALATE_HUMAN.PY - Escalar a Humano
# ============================================================================

"""
escalate_human.py - Escalar conversación a humano

Responsabilidades:
1. Marcar conversación como requiere atención
2. Notificar al equipo
3. Preparar mensaje de escalamiento
4. Actualizar estado
"""


# Pseudocódigo:
async def escalate_to_human_node(state: WhatsAppAgentState):
    conversation_id = state["conversation_id"]
    reason = state.get("escalation_reason", "Confianza baja en clasificación")

    # Actualizar conversación en BD
    await database.execute(
        """
        UPDATE conversaciones 
        SET estado = 'Esperando_Humano',
            categoria = 'Escalado'
        WHERE id = $1
    """,
        conversation_id,
    )

    # Notificar al equipo (webhook, email, etc.)
    await notify_staff(
        conversation_id=conversation_id, contact_id=state["contact_id"], reason=reason
    )

    return {
        **state,
        "requires_human": True,
        "escalation_reason": reason,
        "next_action": "send_escalation_message",
    }


# ============================================================================
# NODES/GENERATE_RESPONSE.PY - Generar Respuesta
# ============================================================================

"""
generate_response.py - Generar respuesta final con LLM

Responsabilidades:
1. Construir contexto completo
2. Seleccionar prompt según next_action
3. Invocar LLM con contexto
4. Procesar respuesta
5. Agregar mensaje al estado
"""


# Pseudocódigo:
async def generate_response_node(state: WhatsAppAgentState):
    # Construir contexto
    context_parts = []

    if state.get("patient_info"):
        context_parts.append(f"Paciente: {state['patient_info']['nombre']}")

    if state.get("retrieved_context"):
        context_parts.append(
            "Contexto previo:\n"
            + "\n".join([c["content"] for c in state["retrieved_context"][:3]])
        )

    if state.get("appointment_history"):
        context_parts.append(
            "Historial de citas:\n"
            + "\n".join(
                [
                    f"- {a['fecha_hora']}: {a['tratamiento']}"
                    for a in state["appointment_history"][:3]
                ]
            )
        )

    context = "\n\n".join(context_parts)

    # Construir mensajes para LLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT_MAIN}]

    if context:
        messages.append({"role": "system", "content": f"Contexto:\n{context}"})

    # Agregar historial de conversación
    for msg in state["messages"][-config.max_context_messages :]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Generar respuesta
    response = await llm.ainvoke(messages)

    # Agregar al estado
    new_messages = state["messages"] + [
        {
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat(),
        }
    ]

    return {**state, "messages": new_messages, "processing_stage": "complete"}


# ============================================================================
# TOOLS/PATIENT_TOOLS.PY - Herramientas de Pacientes
# ============================================================================

"""
patient_tools.py - Herramientas para gestión de pacientes

Funciones:
- search_patient(nombre, telefono, contact_id)
- get_patient_info(patient_id)
- create_patient(data)
- get_patient_history(patient_id)
"""

# Pseudocódigo:
from langchain.tools import tool


@tool
async def search_patient(
    nombre: str = None, telefono: str = None, contact_id: int = None
) -> dict:
    """Busca un paciente por nombre, teléfono o contact_id"""
    query = """
    SELECT p.*, c.telefono as telefono_contacto
    FROM pacientes p
    LEFT JOIN contactos c ON c.id_paciente = p.id
    WHERE ($1 IS NULL OR p.primer_nombre ILIKE $1 || '%')
       OR ($2 IS NULL OR c.telefono = $2)
       OR ($3 IS NULL OR c.id = $3)
    LIMIT 5
    """
    results = await db.fetch(query, nombre, telefono, contact_id)
    return [dict(r) for r in results]


@tool
async def get_patient_info(patient_id: int) -> dict:
    """Obtiene información completa de un paciente"""
    query = """
    SELECT p.*, 
           COUNT(c.id) as total_citas,
           MAX(c.fecha_hora_inicio) as ultima_cita
    FROM pacientes p
    LEFT JOIN citas c ON p.id = c.id_paciente
    WHERE p.id = $1
    GROUP BY p.id
    """
    result = await db.fetchrow(query, patient_id)
    return dict(result) if result else None


# ============================================================================
# TOOLS/APPOINTMENT_TOOLS.PY - Herramientas de Citas
# ============================================================================

"""
appointment_tools.py - Herramientas para gestión de citas

Funciones:
- check_availability(fecha, hora, podologo_id)
- book_appointment(patient_id, fecha, hora, tratamiento_id)
- cancel_appointment(appointment_id)
- get_available_slots(fecha, podologo_id)
- get_active_appointments(patient_id)
"""


# Pseudocódigo:
@tool
async def check_availability(fecha: str, hora: str, podologo_id: int = 1) -> dict:
    """Verifica disponibilidad de un horario"""
    query = """
    SELECT * FROM obtener_horarios_disponibles($1, $2::date)
    WHERE hora_slot = $3::time
    """
    result = await db.fetchrow(query, podologo_id, fecha, hora)

    return {
        "available": result["disponible"] if result else False,
        "reason": result.get("motivo_no_disponible"),
    }


@tool
async def book_appointment(
    patient_id: int, fecha: str, hora: str, tratamiento_id: int = 1
) -> dict:
    """Agenda una nueva cita"""
    query = """
    INSERT INTO citas (
        id_paciente, id_podologo, fecha_hora_inicio,
        fecha_hora_fin, tipo_cita, estado, creado_por
    ) VALUES (
        $1, 1,
        ($2 || ' ' || $3)::timestamp,
        ($2 || ' ' || $3)::timestamp + INTERVAL '30 minutes',
        'Consulta', 'Confirmada', 1
    )
    RETURNING id, fecha_hora_inicio
    """
    result = await db.fetchrow(query, patient_id, fecha, hora)
    return dict(result)


# ============================================================================
# TOOLS/RAG_TOOLS.PY - Herramientas de RAG
# ============================================================================

"""
rag_tools.py - Herramientas para RAG con pgvector

Funciones:
- retrieve_context(query, contact_id, k)
- index_conversation(conversation_id)
- search_similar_conversations(query, k)
"""

# Pseudocódigo:
from ..utils.vector_store import vector_store


@tool
async def retrieve_context(query: str, contact_id: int, k: int = 5) -> List[dict]:
    """Recupera contexto relevante del vector store"""

    # Filtrar por contacto
    filter_dict = {"contact_id": contact_id}

    # Búsqueda de similitud
    docs = await vector_store.asimilarity_search_with_score(
        query, k=k, filter=filter_dict
    )

    return [
        {"content": doc.page_content, "score": score, "metadata": doc.metadata}
        for doc, score in docs
    ]


@tool
async def index_conversation(conversation_id: int):
    """Indexa una conversación en el vector store"""

    # Obtener mensajes
    messages = await db.fetch(
        """
        SELECT * FROM mensajes
        WHERE id_conversacion = $1
        ORDER BY fecha_envio
    """,
        conversation_id,
    )

    # Crear documentos
    documents = []
    for msg in messages:
        content = f"Rol: {msg['rol']}\nMensaje: {msg['contenido']}"
        metadata = {
            "conversation_id": conversation_id,
            "message_id": msg["id"],
            "role": msg["rol"],
        }
        documents.append(Document(page_content=content, metadata=metadata))

    # Indexar
    await vector_store.aadd_documents(documents)


# ============================================================================
# UTILS/EMBEDDINGS.PY - Servicio de Embeddings
# ============================================================================

"""
embeddings.py - Servicio de embeddings local

Clase:
- LocalEmbeddings: Wrapper para sentence-transformers
"""

# Pseudocódigo:
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings


class LocalEmbeddings(Embeddings):
    """Embeddings locales usando all-MiniLM-L6-v2"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeddings para múltiples documentos"""
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embedding para una consulta"""
        return self.model.encode([text], show_progress_bar=False)[0].tolist()


# ============================================================================
# UTILS/DATABASE.PY - Conexión a PostgreSQL
# ============================================================================

"""
database.py - Gestión de conexión a PostgreSQL

Funciones:
- get_db_connection()
- execute_query(query, *args)
- execute_transaction(queries)
"""

# Pseudocódigo:
import asyncpg
from ..config import config

_pool = None


async def get_db_pool():
    """Obtiene el pool de conexiones"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(config.database_url)
    return _pool


async def execute_query(query: str, *args):
    """Ejecuta una query"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute_transaction(queries: List[tuple]):
    """Ejecuta múltiples queries en una transacción"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            results = []
            for query, args in queries:
                result = await conn.fetch(query, *args)
                results.append(result)
            return results


# ============================================================================
# UTILS/VECTOR_STORE.PY - Gestión de pgvector
# ============================================================================

"""
vector_store.py - Wrapper para pgvector con LangChain

Clase:
- VectorStore: Gestión de pgvector
"""

# Pseudocódigo:
from langchain_community.vectorstores import PGVector
from .embeddings import LocalEmbeddings
from ..config import config


class VectorStore:
    """Wrapper para pgvector"""

    def __init__(self):
        self.embeddings = LocalEmbeddings()
        self.store = PGVector(
            collection_name=config.rag_collection_name,
            connection_string=config.vector_store_url or config.database_url,
            embedding_function=self.embeddings,
            distance_strategy=config.rag_distance_strategy,
        )

    async def add_documents(self, documents: List[Document]):
        """Agrega documentos al vector store"""
        return await self.store.aadd_documents(documents)

    async def similarity_search(self, query: str, k: int = 5, filter: dict = None):
        """Búsqueda de similitud"""
        return await self.store.asimilarity_search_with_score(query, k=k, filter=filter)


# Instancia global
vector_store = VectorStore()
