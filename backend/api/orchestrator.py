"""
Orchestrator API Endpoint
Expone el Agente Padre Orquestador como endpoint REST
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from agents.orchestrator import execute_orchestrator

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])


class OrchestratorRequest(BaseModel):
    """Request to execute orchestrator"""
    function_name: str = Field(..., description="Nombre de la función médica")
    args: Dict[str, Any] = Field(..., description="Argumentos de la función")
    context: Dict[str, Any] = Field(..., description="Contexto (patient_id, appointment_id, user_id)")


class OrchestratorResponse(BaseModel):
    """Response from orchestrator"""
    data: Optional[Dict[str, Any]] = None
    message: str
    status: str
    execution_time_ms: Optional[int] = None
    messages: list = []
    audit_log: list = []


def get_current_user_id(authorization: str = Header(...)) -> str:
    """Extract user ID from authorization header"""
    # TODO: Implement proper JWT validation
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return "user_123"  # Placeholder


@router.post("/execute", response_model=OrchestratorResponse)
async def execute_orchestrator_endpoint(
    request: OrchestratorRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Execute orchestrator for complex medical functions
    
    - Classifies query as simple or complex
    - Routes to appropriate SubAgent if needed
    - Validates and returns response
    """
    try:
        # Extract context
        patient_id = request.context.get("patient_id")
        appointment_id = request.context.get("appointment_id")
        
        if not patient_id:
            raise HTTPException(status_code=400, detail="patient_id required in context")
        
        # Execute orchestrator
        result = await execute_orchestrator(
            function_name=request.function_name,
            args=request.args,
            patient_id=patient_id,
            user_id=user_id,
            appointment_id=appointment_id
        )
        
        return OrchestratorResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator execution failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Check orchestrator health"""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "subagents_available": ["summaries", "whatsapp"]
    }
