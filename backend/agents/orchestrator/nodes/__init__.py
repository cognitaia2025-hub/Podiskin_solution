"""
Orchestrator Nodes
Nodos del grafo del Agente Padre Orquestador
"""

from typing import Dict, Any
from datetime import datetime
import importlib

from ..state import OrchestratorState
from ..config import (
    SIMPLE_FUNCTIONS,
    COMPLEX_FUNCTIONS_MAPPING,
    SUBAGENTS_CONFIG,
    VALIDATION_RULES
)


def classify_query(state: OrchestratorState) -> OrchestratorState:
    """
    Nodo 1: Clasificar la consulta
    
    Determina si la función es simple o compleja
    y si requiere un SubAgente
    """
    function_name = state["function_name"]
    
    # Log
    state["messages"].append(f"Clasificando función: {function_name}")
    
    # Classify
    if function_name in SIMPLE_FUNCTIONS:
        state["query_type"] = "simple"
        state["complexity_score"] = 0.2
        state["requires_subagent"] = False
        state["target_subagent"] = None
        state["messages"].append(f"✓ Función simple - no requiere SubAgente")
        
    elif function_name in COMPLEX_FUNCTIONS_MAPPING:
        mapping = COMPLEX_FUNCTIONS_MAPPING[function_name]
        state["query_type"] = "complex"
        state["complexity_score"] = 0.8
        state["requires_subagent"] = True
        state["target_subagent"] = mapping["subagent"]
        state["messages"].append(
            f"✓ Función compleja - requiere SubAgente: {mapping['subagent']}"
        )
    else:
        # Unknown function - treat as simple by default
        state["query_type"] = "simple"
        state["complexity_score"] = 0.5
        state["requires_subagent"] = False
        state["messages"].append(f"⚠️ Función desconocida - tratando como simple")
    
    # Audit log
    state["audit_log"].append({
        "step": "classify_query",
        "timestamp": datetime.utcnow().isoformat(),
        "function_name": function_name,
        "query_type": state["query_type"],
        "requires_subagent": state["requires_subagent"]
    })
    
    return state


def route_to_subagent(state: OrchestratorState) -> OrchestratorState:
    """
    Nodo 2: Delegar a SubAgente
    
    Invoca el SubAgente correspondiente con el request
    """
    if not state["requires_subagent"]:
        state["messages"].append("No requiere SubAgente - saltando routing")
        return state
    
    target_subagent = state["target_subagent"]
    state["messages"].append(f"Delegando a SubAgente: {target_subagent}")
    
    # Get subagent configuration
    if target_subagent not in SUBAGENTS_CONFIG:
        state["subagent_error"] = f"SubAgente no configurado: {target_subagent}"
        state["response_status"] = "error"
        return state
    
    subagent_config = SUBAGENTS_CONFIG[target_subagent]
    
    if not subagent_config["enabled"]:
        state["subagent_error"] = f"SubAgente deshabilitado: {target_subagent}"
        state["response_status"] = "error"
        return state
    
    # Prepare subagent request
    state["subagent_request"] = {
        "function_name": state["function_name"],
        "args": state["args"],
        "patient_id": state["patient_id"],
        "appointment_id": state["appointment_id"],
        "user_id": state["user_id"],
        "context": state.get("context_data", {})
    }
    
    try:
        # Dynamic import of subagent graph
        module_path = subagent_config["graph_path"]
        module = importlib.import_module(module_path)
        
        # Get compiled graph
        if hasattr(module, "compiled_graph"):
            subagent_graph = module.compiled_graph
        elif hasattr(module, "graph"):
            subagent_graph = module.graph
        else:
            raise AttributeError(f"No graph found in {module_path}")
        
        # Invoke subagent
        state["messages"].append(f"Invocando SubAgente {target_subagent}...")
        
        # Execute subagent graph
        result = subagent_graph.invoke(state["subagent_request"])
        
        state["subagent_response"] = result
        state["messages"].append(f"✓ SubAgente respondió exitosamente")
        
        # Audit log
        state["audit_log"].append({
            "step": "route_to_subagent",
            "timestamp": datetime.utcnow().isoformat(),
            "target_subagent": target_subagent,
            "success": True
        })
        
    except Exception as e:
        error_msg = f"Error en SubAgente {target_subagent}: {str(e)}"
        state["subagent_error"] = error_msg
        state["messages"].append(f"✗ {error_msg}")
        state["response_status"] = "error"
        
        # Audit log
        state["audit_log"].append({
            "step": "route_to_subagent",
            "timestamp": datetime.utcnow().isoformat(),
            "target_subagent": target_subagent,
            "success": False,
            "error": str(e)
        })
    
    return state


def validate_response(state: OrchestratorState) -> OrchestratorState:
    """
    Nodo 3: Validar respuesta del SubAgente
    
    Aplica reglas de validación según el tipo de función
    """
    function_name = state["function_name"]
    
    # If error occurred, skip validation
    if state.get("subagent_error"):
        state["validation_passed"] = False
        state["validation_errors"] = [state["subagent_error"]]
        return state
    
    # If no subagent was used, skip validation
    if not state["requires_subagent"]:
        state["validation_passed"] = True
        state["messages"].append("No requiere validación de SubAgente")
        return state
    
    state["messages"].append(f"Validando respuesta para: {function_name}")
    
    # Get validation rules
    validation_rules = VALIDATION_RULES.get(function_name, {})
    validation_errors = []
    
    response = state.get("subagent_response", {})
    
    # Apply validation rules
    if "min_length" in validation_rules:
        content = str(response.get("content", ""))
        if len(content) < validation_rules["min_length"]:
            validation_errors.append(
                f"Contenido muy corto (mínimo {validation_rules['min_length']} caracteres)"
            )
    
    if "max_length" in validation_rules:
        content = str(response.get("content", ""))
        if len(content) > validation_rules["max_length"]:
            validation_errors.append(
                f"Contenido muy largo (máximo {validation_rules['max_length']} caracteres)"
            )
    
    if "required_sections" in validation_rules:
        for section in validation_rules["required_sections"]:
            if section not in str(response).lower():
                validation_errors.append(f"Falta sección requerida: {section}")
    
    if "forbidden_keywords" in validation_rules:
        content_lower = str(response).lower()
        for keyword in validation_rules["forbidden_keywords"]:
            if keyword.lower() in content_lower:
                validation_errors.append(f"Contiene palabra prohibida: {keyword}")
    
    # Set validation result
    state["validation_passed"] = len(validation_errors) == 0
    state["validation_errors"] = validation_errors if validation_errors else None
    
    if state["validation_passed"]:
        state["messages"].append("✓ Validación exitosa")
    else:
        state["messages"].append(f"✗ Errores de validación: {validation_errors}")
    
    # Audit log
    state["audit_log"].append({
        "step": "validate_response",
        "timestamp": datetime.utcnow().isoformat(),
        "validation_passed": state["validation_passed"],
        "validation_errors": validation_errors
    })
    
    return state


def build_response(state: OrchestratorState) -> OrchestratorState:
    """
    Nodo 4: Construir respuesta final
    
    Formatea la respuesta para retornar al cliente
    """
    state["messages"].append("Construyendo respuesta final")
    
    # If validation failed, return error
    if state.get("validation_passed") is False:
        state["response_status"] = "error"
        state["response_message"] = "La respuesta no pasó las validaciones"
        state["response_data"] = {
            "errors": state.get("validation_errors", [])
        }
    
    # If subagent error, return error
    elif state.get("subagent_error"):
        state["response_status"] = "error"
        state["response_message"] = state["subagent_error"]
        state["response_data"] = None
    
    # Success case
    else:
        state["response_status"] = "success"
        
        if state.get("subagent_response"):
            # Complex function - use subagent response
            subagent_response = state["subagent_response"]
            state["response_data"] = subagent_response.get("data", subagent_response)
            state["response_message"] = subagent_response.get(
                "message",
                "Operación completada exitosamente"
            )
        else:
            # Simple function - placeholder response
            state["response_data"] = {"status": "processed"}
            state["response_message"] = "Operación procesada"
    
    # Set completion timestamp
    state["completed_at"] = datetime.utcnow()
    
    # Calculate execution time
    if state["created_at"]:
        delta = state["completed_at"] - state["created_at"]
        state["execution_time_ms"] = int(delta.total_seconds() * 1000)
    
    state["messages"].append(
        f"✓ Respuesta construida - Status: {state['response_status']}"
    )
    
    # Final audit log
    state["audit_log"].append({
        "step": "build_response",
        "timestamp": datetime.utcnow().isoformat(),
        "response_status": state["response_status"],
        "execution_time_ms": state.get("execution_time_ms")
    })
    
    return state
