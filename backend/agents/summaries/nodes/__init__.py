"""
Summaries SubAgent Nodes
Nodos del grafo del SubAgente de Resúmenes
"""

from typing import Dict, Any, List
from datetime import datetime

from ..state import SummaryState
from ..config import SUMMARY_TEMPLATES, MIN_SUMMARY_LENGTH, MAX_SUMMARY_LENGTH


def fetch_patient_data(state: SummaryState) -> SummaryState:
    """
    Nodo 1: Obtener datos del paciente
    
    Consulta base de datos para obtener información necesaria
    """
    patient_id = state["patient_id"]
    state["messages"].append(f"Obteniendo datos del paciente: {patient_id}")
    
    # TODO: Implement actual database queries
    # For now, use mock data
    
    state["patient_data"] = {
        "id": patient_id,
        "nombre_completo": "Juan Pérez",
        "edad": 45,
        "fecha_registro": "2023-01-15"
    }
    
    state["appointments_data"] = [
        {
            "id": 1,
            "fecha": "2024-12-20",
            "motivo_consulta": "Dolor en talón derecho",
            "diagnostico": "Fascitis plantar"
        }
    ]
    
    state["clinical_notes"] = [
        {
            "fecha": "2024-12-20",
            "motivo_consulta": "Dolor en talón derecho desde hace 3 semanas",
            "exploracion_fisica": "Dolor a la palpación de fascia plantar",
            "diagnostico": "Fascitis plantar",
            "plan_tratamiento": "Plantillas ortopédicas, antiinflamatorios"
        }
    ]
    
    state["vital_signs"] = [
        {
            "fecha": "2024-12-20",
            "peso_kg": 78.5,
            "talla_cm": 175,
            "presion_arterial": "120/80"
        }
    ]
    
    state["messages"].append("✓ Datos del paciente obtenidos")
    
    # Audit log
    state["audit_log"].append({
        "step": "fetch_patient_data",
        "timestamp": datetime.utcnow().isoformat(),
        "patient_id": patient_id,
        "data_fetched": True
    })
    
    return state


def search_history(state: SummaryState) -> SummaryState:
    """
    Nodo 2: Buscar en historial (para search_patient_history)
    
    Realiza búsqueda semántica en el historial del paciente
    """
    if state["function_name"] != "search_patient_history":
        state["messages"].append("No es búsqueda de historial - saltando")
        return state
    
    search_query = state.get("search_query")
    search_limit = state.get("search_limit", 5)
    
    state["messages"].append(f"Buscando en historial: '{search_query}'")
    
    # TODO: Implement semantic search with embeddings
    # For now, use simple mock search
    
    # Mock search results
    state["search_results"] = [
        {
            "fecha": "2024-11-15",
            "tipo": "nota_clinica",
            "contenido": "Tratamiento para onicomicosis en uña del pie derecho",
            "relevancia": 0.85
        },
        {
            "fecha": "2024-09-20",
            "tipo": "tratamiento",
            "contenido": "Aplicación de láser para hongos en uñas",
            "relevancia": 0.78
        }
    ][:search_limit]
    
    state["messages"].append(f"✓ Encontrados {len(state['search_results'])} resultados")
    
    # Audit log
    state["audit_log"].append({
        "step": "search_history",
        "timestamp": datetime.utcnow().isoformat(),
        "search_query": search_query,
        "results_count": len(state["search_results"])
    })
    
    return state


def generate_summary(state: SummaryState) -> SummaryState:
    """
    Nodo 3: Generar resumen con LLM
    
    Usa LLM para generar resumen estructurado
    """
    function_name = state["function_name"]
    
    if function_name == "search_patient_history":
        # For search, format results
        state["messages"].append("Formateando resultados de búsqueda")
        
        results = state.get("search_results", [])
        formatted_results = "\n\n".join([
            f"**{r['fecha']}** ({r['tipo']})\n{r['contenido']}"
            for r in results
        ])
        
        state["summary_content"] = formatted_results
        state["summary_sections"] = {
            "resultados": formatted_results,
            "total": str(len(results))
        }
        
    elif function_name == "generate_summary":
        # Generate actual summary
        summary_type = state.get("summary_type", "consulta_actual")
        summary_format = state.get("summary_format", "breve")
        
        state["messages"].append(f"Generando resumen: {summary_type} ({summary_format})")
        
        # Get template
        template = SUMMARY_TEMPLATES.get(summary_type, {}).get(summary_format, "")
        
        # TODO: Use LLM to generate summary with actual patient data
        # For now, use template with mock data
        
        patient_data = state.get("patient_data", {})
        clinical_notes = state.get("clinical_notes", [])
        
        if clinical_notes:
            last_note = clinical_notes[-1]
            
            summary_content = template.format(
                fecha=last_note.get("fecha", "N/A"),
                paciente=patient_data.get("nombre_completo", "N/A"),
                edad=patient_data.get("edad", "N/A"),
                motivo_consulta=last_note.get("motivo_consulta", "N/A"),
                hallazgos=last_note.get("exploracion_fisica", "N/A"),
                exploracion_fisica=last_note.get("exploracion_fisica", "N/A"),
                diagnostico_presuntivo=last_note.get("diagnostico", "N/A"),
                diagnostico_definitivo=last_note.get("diagnostico", "N/A"),
                plan_tratamiento=last_note.get("plan_tratamiento", "N/A"),
                indicaciones_paciente=last_note.get("plan_tratamiento", "N/A"),
                padecimiento_actual=last_note.get("motivo_consulta", "N/A"),
                signos_vitales="Ver sección de signos vitales",
                diagnostico_simple=last_note.get("diagnostico", "N/A"),
                seguimiento="Revisar en 15 días"
            )
        else:
            summary_content = "No hay datos suficientes para generar el resumen"
        
        state["summary_content"] = summary_content
        state["summary_sections"] = {
            "tipo": summary_type,
            "formato": summary_format,
            "contenido": summary_content
        }
    
    state["messages"].append("✓ Resumen generado")
    
    # Audit log
    state["audit_log"].append({
        "step": "generate_summary",
        "timestamp": datetime.utcnow().isoformat(),
        "function_name": function_name,
        "summary_length": len(state.get("summary_content", ""))
    })
    
    return state


def validate_summary(state: SummaryState) -> SummaryState:
    """
    Nodo 4: Validar resumen generado
    
    Verifica que el resumen cumple criterios de calidad
    """
    state["messages"].append("Validando resumen")
    
    summary_content = state.get("summary_content", "")
    validation_errors = []
    
    # Check minimum length
    if len(summary_content) < MIN_SUMMARY_LENGTH:
        validation_errors.append(
            f"Resumen muy corto (mínimo {MIN_SUMMARY_LENGTH} caracteres)"
        )
    
    # Check maximum length
    if len(summary_content) > MAX_SUMMARY_LENGTH:
        validation_errors.append(
            f"Resumen muy largo (máximo {MAX_SUMMARY_LENGTH} caracteres)"
        )
    
    # Check not empty
    if not summary_content.strip():
        validation_errors.append("Resumen vacío")
    
    # Check for sensitive data keywords (basic check)
    sensitive_keywords = ["password", "api_key", "token", "secret"]
    for keyword in sensitive_keywords:
        if keyword.lower() in summary_content.lower():
            validation_errors.append(f"Contiene dato sensible: {keyword}")
    
    # Set validation result
    state["validation_passed"] = len(validation_errors) == 0
    state["validation_errors"] = validation_errors if validation_errors else None
    
    if state["validation_passed"]:
        state["messages"].append("✓ Validación exitosa")
    else:
        state["messages"].append(f"✗ Errores: {validation_errors}")
    
    # Audit log
    state["audit_log"].append({
        "step": "validate_summary",
        "timestamp": datetime.utcnow().isoformat(),
        "validation_passed": state["validation_passed"],
        "validation_errors": validation_errors
    })
    
    return state


def build_response(state: SummaryState) -> SummaryState:
    """
    Nodo 5: Construir respuesta final
    
    Formatea la respuesta para retornar al Orquestador
    """
    state["messages"].append("Construyendo respuesta")
    
    if not state.get("validation_passed"):
        # Validation failed
        state["response_status"] = "error"
        state["response_message"] = "El resumen no pasó las validaciones"
        state["response_data"] = {
            "errors": state.get("validation_errors", [])
        }
    else:
        # Success
        state["response_status"] = "success"
        state["response_data"] = {
            "content": state.get("summary_content"),
            "sections": state.get("summary_sections"),
            "metadata": {
                "patient_id": state["patient_id"],
                "function_name": state["function_name"],
                "summary_type": state.get("summary_type"),
                "summary_format": state.get("summary_format")
            }
        }
        
        if state["function_name"] == "search_patient_history":
            state["response_message"] = f"Encontrados {len(state.get('search_results', []))} resultados"
        else:
            state["response_message"] = "Resumen generado exitosamente"
    
    # Set completion timestamp
    state["completed_at"] = datetime.utcnow()
    
    # Calculate execution time
    if state["created_at"]:
        delta = state["completed_at"] - state["created_at"]
        state["execution_time_ms"] = int(delta.total_seconds() * 1000)
    
    state["messages"].append(f"✓ Respuesta lista - Status: {state['response_status']}")
    
    # Final audit log
    state["audit_log"].append({
        "step": "build_response",
        "timestamp": datetime.utcnow().isoformat(),
        "response_status": state["response_status"],
        "execution_time_ms": state.get("execution_time_ms")
    })
    
    return state
