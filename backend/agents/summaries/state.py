"""
Summaries SubAgent State
TypedDict para el estado del SubAgente de Resúmenes
"""

from typing import TypedDict, Optional, Literal, List, Dict, Any
from datetime import datetime


class SummaryState(TypedDict):
    """
    Estado del SubAgente de Resúmenes
    
    Genera resúmenes de consultas, evolución de tratamientos,
    e historial completo del paciente
    """
    
    # Request context
    function_name: str  # Debe ser 'generate_summary' o 'search_patient_history'
    args: Dict[str, Any]  # Argumentos de la función
    patient_id: str  # ID del paciente
    appointment_id: Optional[str]  # ID de cita actual (si aplica)
    user_id: str  # ID del médico
    context: Optional[Dict[str, Any]]  # Contexto adicional del orquestador
    
    # Summary type
    summary_type: Optional[Literal["consulta_actual", "evolucion_tratamiento", "historial_completo"]]
    summary_format: Optional[Literal["breve", "detallado", "para_paciente"]]
    
    # Data fetching
    patient_data: Optional[Dict[str, Any]]  # Datos del paciente
    appointments_data: Optional[List[Dict[str, Any]]]  # Citas del paciente
    clinical_notes: Optional[List[Dict[str, Any]]]  # Notas clínicas
    treatments: Optional[List[Dict[str, Any]]]  # Tratamientos
    vital_signs: Optional[List[Dict[str, Any]]]  # Signos vitales históricos
    
    # For search_patient_history
    search_query: Optional[str]  # Query de búsqueda semántica
    search_results: Optional[List[Dict[str, Any]]]  # Resultados de búsqueda
    search_limit: Optional[int]  # Límite de resultados
    
    # Summary generation
    summary_content: Optional[str]  # Contenido del resumen generado
    summary_sections: Optional[Dict[str, str]]  # Secciones del resumen
    summary_metadata: Optional[Dict[str, Any]]  # Metadata del resumen
    
    # Validation
    validation_passed: Optional[bool]
    validation_errors: Optional[List[str]]
    
    # Response
    response_data: Optional[Dict[str, Any]]
    response_message: Optional[str]
    response_status: Optional[Literal["success", "error", "partial"]]
    
    # Metadata
    messages: List[str]  # Log de pasos
    created_at: datetime
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    
    # Audit
    audit_log: List[Dict[str, Any]]


def create_initial_summary_state(
    function_name: str,
    args: Dict[str, Any],
    patient_id: str,
    user_id: str,
    appointment_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> SummaryState:
    """Create initial state for summaries subagent"""
    return SummaryState(
        function_name=function_name,
        args=args,
        patient_id=patient_id,
        appointment_id=appointment_id,
        user_id=user_id,
        context=context,
        summary_type=args.get("tipo_resumen"),
        summary_format=args.get("formato", "breve"),
        patient_data=None,
        appointments_data=None,
        clinical_notes=None,
        treatments=None,
        vital_signs=None,
        search_query=args.get("query"),
        search_results=None,
        search_limit=args.get("limite_resultados", 5),
        summary_content=None,
        summary_sections=None,
        summary_metadata=None,
        validation_passed=None,
        validation_errors=None,
        response_data=None,
        response_message=None,
        response_status=None,
        messages=[],
        created_at=datetime.utcnow(),
        completed_at=None,
        execution_time_ms=None,
        audit_log=[]
    )
