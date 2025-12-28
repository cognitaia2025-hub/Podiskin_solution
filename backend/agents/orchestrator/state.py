"""
Orchestrator State Definition
TypedDict para el estado del Agente Padre Orquestador
"""

from typing import TypedDict, Optional, Literal, List, Dict, Any
from datetime import datetime


class OrchestratorState(TypedDict):
    """
    Estado del Agente Padre Orquestador
    
    Maneja routing de consultas simples y complejas:
    - Consultas SIMPLES → Respuesta directa
    - Consultas COMPLEJAS → Delega a SubAgentes
    """
    
    # Request context
    function_name: str  # Nombre de la función llamada
    args: Dict[str, Any]  # Argumentos de la función
    patient_id: str  # ID del paciente
    appointment_id: Optional[str]  # ID de cita (si aplica)
    user_id: str  # ID del médico/usuario
    
    # Query classification
    query_type: Optional[Literal["simple", "complex"]]  # Tipo de consulta
    complexity_score: Optional[float]  # Score de complejidad (0-1)
    requires_subagent: Optional[bool]  # ¿Requiere SubAgente?
    target_subagent: Optional[str]  # SubAgente target (summaries, analysis, etc)
    
    # Data fetching
    fetched_data: Optional[Dict[str, Any]]  # Datos obtenidos de DB
    context_data: Optional[Dict[str, Any]]  # Contexto adicional
    
    # SubAgent delegation
    subagent_request: Optional[Dict[str, Any]]  # Request para SubAgente
    subagent_response: Optional[Dict[str, Any]]  # Response de SubAgente
    subagent_error: Optional[str]  # Error de SubAgente (si aplica)
    
    # Response building
    response_data: Optional[Dict[str, Any]]  # Datos de respuesta
    response_message: Optional[str]  # Mensaje para usuario
    response_status: Optional[Literal["success", "error", "partial"]]
    
    # Validation
    validation_passed: Optional[bool]  # ¿Validación pasó?
    validation_errors: Optional[List[str]]  # Errores de validación
    
    # Metadata
    messages: List[str]  # Log de mensajes/pasos
    created_at: datetime  # Timestamp de creación
    completed_at: Optional[datetime]  # Timestamp de completado
    execution_time_ms: Optional[int]  # Tiempo de ejecución
    
    # Audit
    audit_log: List[Dict[str, Any]]  # Log de auditoría


# Helper functions for state initialization
def create_initial_state(
    function_name: str,
    args: Dict[str, Any],
    patient_id: str,
    user_id: str,
    appointment_id: Optional[str] = None
) -> OrchestratorState:
    """Create initial orchestrator state"""
    return OrchestratorState(
        function_name=function_name,
        args=args,
        patient_id=patient_id,
        appointment_id=appointment_id,
        user_id=user_id,
        query_type=None,
        complexity_score=None,
        requires_subagent=None,
        target_subagent=None,
        fetched_data=None,
        context_data=None,
        subagent_request=None,
        subagent_response=None,
        subagent_error=None,
        response_data=None,
        response_message=None,
        response_status=None,
        validation_passed=None,
        validation_errors=None,
        messages=[],
        created_at=datetime.utcnow(),
        completed_at=None,
        execution_time_ms=None,
        audit_log=[]
    )
