"""
Estado del Sub-Agente de Operaciones
====================================

Define el estado compartido entre nodos del grafo.
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class OperationsAgentState(TypedDict, total=False):
    """
    Estado del agente de operaciones.

    Este estado se comparte entre todos los nodos del grafo.
    """

    # ========================================================================
    # INFORMACIÓN DE LA SESIÓN
    # ========================================================================
    session_id: str
    """ID único de la sesión"""

    user_id: str
    """ID del usuario (personal de la clínica)"""

    user_name: str
    """Nombre del usuario"""

    # ========================================================================
    # MENSAJES
    # ========================================================================
    messages: List[Dict[str, Any]]
    """Historial de mensajes de la conversación"""

    current_message: str
    """Mensaje actual del usuario"""

    # ========================================================================
    # CLASIFICACIÓN
    # ========================================================================
    intent: str
    """Intención clasificada del mensaje"""

    confidence: float
    """Confianza de la clasificación (0.0 - 1.0)"""

    entities: Dict[str, Any]
    """Entidades extraídas del mensaje"""

    # ========================================================================
    # CONTEXTO
    # ========================================================================
    context: Optional[str]
    """Contexto adicional para la respuesta"""

    retrieved_data: Optional[Dict[str, Any]]
    """Datos recuperados de la base de datos"""

    # ========================================================================
    # ACCIONES
    # ========================================================================
    action_type: Optional[str]
    """Tipo de acción a realizar (create, update, delete, etc.)"""

    action_data: Optional[Dict[str, Any]]
    """Datos para la acción"""

    action_confirmed: bool
    """Si la acción fue confirmada por el usuario"""

    action_result: Optional[Dict[str, Any]]
    """Resultado de la acción ejecutada"""

    # ========================================================================
    # RESPUESTA
    # ========================================================================
    response: Optional[str]
    """Respuesta generada para el usuario"""

    response_type: Optional[str]
    """Tipo de respuesta (text, confirmation, report, etc.)"""

    # ========================================================================
    # CONTROL DE FLUJO
    # ========================================================================
    next_action: Optional[str]
    """Siguiente acción a ejecutar"""

    processing_stage: str
    """Etapa actual del procesamiento"""

    error: Optional[str]
    """Mensaje de error si ocurrió alguno"""

    # ========================================================================
    # METADATA
    # ========================================================================
    timestamp: str
    """Timestamp del mensaje"""

    metadata: Optional[Dict[str, Any]]
    """Metadata adicional"""
