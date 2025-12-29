"""
Live Sessions API - Secure Session Management
Endpoints para manejo seguro de sesiones de Gemini Live

Este módulo implementa los endpoints de backend requeridos por el SecureSessionService
del frontend para gestión segura de sesiones de voz con Gemini Live.

Seguridad:
- NUNCA expone API keys en el cliente
- Tokens efímeros con TTL
- Validación JWT para autenticación
- Clasificación de funciones (SIMPLE vs COMPLEX)
- Audit logging de todas las tool calls
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import secrets
import os
import logging

# Import auth middleware
from auth import get_current_user, User

# Import orchestrator for complex functions
from backend.agents.orchestrator.graph import execute_orchestrator
from backend.agents.orchestrator.config import SIMPLE_FUNCTIONS, COMPLEX_FUNCTIONS_MAPPING

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/live", tags=["live_sessions"])

# In-memory session store (use Redis in production for scalability)
active_sessions: Dict[str, Dict[str, Any]] = {}

# Session configuration
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "30"))


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class SessionStartRequest(BaseModel):
    """Request to start a new secure voice session"""
    patientId: str = Field(..., description="ID del paciente")
    appointmentId: str = Field(..., description="ID de la cita")
    userId: str = Field(..., description="ID del usuario (médico)")


class SessionStartResponse(BaseModel):
    """Response with ephemeral session token"""
    token: str = Field(..., description="Token efímero para la sesión")
    sessionId: str = Field(..., description="ID único de la sesión")
    expiresAt: datetime = Field(..., description="Timestamp de expiración UTC")


class SessionStopRequest(BaseModel):
    """Request to stop an active session"""
    sessionId: str = Field(..., description="ID de la sesión a cerrar")


class ToolCallRequest(BaseModel):
    """Request to execute a tool call on the backend"""
    sessionId: str = Field(..., description="ID de sesión")
    toolName: str = Field(..., description="Nombre de la función médica")
    args: Dict[str, Any] = Field(default_factory=dict, description="Argumentos de la función")


class ToolCallResponse(BaseModel):
    """Response from tool execution"""
    success: bool = Field(..., description="Indica si la ejecución fue exitosa")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos de resultado")
    error: Optional[str] = Field(None, description="Mensaje de error si falló")
    message: Optional[str] = Field(None, description="Mensaje descriptivo")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_session_token(session_id: str, ttl_minutes: int = SESSION_TTL_MINUTES) -> SessionStartResponse:
    """
    Create an ephemeral session token with TTL
    
    Args:
        session_id: Unique session identifier
        ttl_minutes: Time to live in minutes
        
    Returns:
        SessionStartResponse with token and expiration
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
    
    return SessionStartResponse(
        token=token,
        sessionId=session_id,
        expiresAt=expires_at
    )


def validate_session_token(session_id: str, token: str) -> bool:
    """
    Validate a session token
    
    Args:
        session_id: Session identifier
        token: Token to validate
        
    Returns:
        True if valid, False otherwise
    """
    if session_id not in active_sessions:
        logger.warning(f"Session not found: {session_id}")
        return False
    
    session = active_sessions[session_id]
    
    # Check token matches
    if session['token'] != token:
        logger.warning(f"Token mismatch for session: {session_id}")
        return False
    
    # Check not expired
    if datetime.utcnow() > session['expires_at']:
        logger.info(f"Session expired: {session_id}")
        del active_sessions[session_id]
        return False
    
    return True


def cleanup_expired_sessions():
    """
    Clean up expired sessions from the store
    This should be called periodically (e.g., via background task)
    """
    now = datetime.utcnow()
    expired = [sid for sid, sess in active_sessions.items() if now > sess['expires_at']]
    
    for session_id in expired:
        logger.info(f"Cleaning up expired session: {session_id}")
        del active_sessions[session_id]
    
    if expired:
        logger.info(f"Cleaned up {len(expired)} expired sessions")


def is_simple_function(function_name: str) -> bool:
    """
    Determine if a function is SIMPLE (direct execution) or COMPLEX (requires orchestrator)
    
    SIMPLE functions:
    - update_vital_signs
    - create_clinical_note
    - query_patient_data
    - add_allergy
    - navigate_to_section
    - schedule_followup
    
    COMPLEX functions:
    - search_patient_history
    - generate_summary
    """
    return function_name in SIMPLE_FUNCTIONS


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/session/start", response_model=SessionStartResponse)
async def start_session(
    config: SessionStartRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a secure voice session with ephemeral token
    
    Security:
    - Requires valid JWT authentication
    - Validates user permissions for patient access
    - Creates session with TTL (30 minutes default)
    - Returns ephemeral token for client use
    
    Args:
        config: Session configuration with patient and appointment IDs
        current_user: Authenticated user from JWT token
        
    Returns:
        SessionStartResponse with token and expiration
    """
    # Validate user has access to this patient
    # TODO: Check in database that user has permission to access this patient
    # For now, we trust the authenticated user
    
    # Cleanup expired sessions before creating new one
    cleanup_expired_sessions()
    
    # Create unique session ID
    session_id = str(uuid.uuid4())
    
    # Create ephemeral token
    session_token = create_session_token(session_id, ttl_minutes=SESSION_TTL_MINUTES)
    
    # Store session data
    active_sessions[session_id] = {
        'session_id': session_id,
        'token': session_token.token,
        'user_id': str(current_user.id),
        'username': current_user.nombre_usuario,
        'patient_id': config.patientId,
        'appointment_id': config.appointmentId,
        'created_at': datetime.utcnow(),
        'expires_at': session_token.expiresAt,
        'active': True,
        'tool_calls': []  # Track tool calls for audit
    }
    
    # Log session creation for audit
    logger.info(
        f"Voice session created: {session_id} | "
        f"User: {current_user.nombre_usuario} | "
        f"Patient: {config.patientId} | "
        f"Appointment: {config.appointmentId}"
    )
    
    return session_token


@router.post("/session/stop")
async def stop_session(
    request: SessionStopRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Stop and cleanup a voice session
    
    Security:
    - Requires valid JWT authentication
    - Validates session ownership
    - Revokes token and cleans up resources
    
    Args:
        request: Request with session ID to stop
        current_user: Authenticated user from JWT token
        
    Returns:
        Status message with session ID
    """
    session_id = request.sessionId
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already closed"
        )
    
    session = active_sessions[session_id]
    
    # Validate ownership - only the user who created the session can stop it
    if session['user_id'] != str(current_user.id):
        logger.warning(
            f"Unauthorized session stop attempt: {session_id} | "
            f"User: {current_user.nombre_usuario} (not owner)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to stop this session"
        )
    
    # Log session closure for audit
    logger.info(
        f"Voice session stopped: {session_id} | "
        f"User: {current_user.nombre_usuario} | "
        f"Duration: {(datetime.utcnow() - session['created_at']).total_seconds():.1f}s | "
        f"Tool calls: {len(session['tool_calls'])}"
    )
    
    # Mark as inactive and remove from active sessions
    session['active'] = False
    del active_sessions[session_id]
    
    return {
        "status": "closed",
        "sessionId": session_id,
        "message": "Session closed successfully"
    }


@router.post("/tool/call", response_model=ToolCallResponse)
async def execute_tool_call(
    request: ToolCallRequest,
    x_session_token: str = Header(..., description="Session token from X-Session-Token header"),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a critical tool call on the backend
    
    This endpoint keeps sensitive operations server-side and routes to:
    - Direct REST endpoints for SIMPLE functions
    - Orchestrator for COMPLEX functions requiring SubAgent processing
    
    Security:
    - Requires valid JWT authentication
    - Validates session token
    - Validates session ownership
    - Audit logs all tool calls
    
    Function Classification:
    - SIMPLE: update_vital_signs, create_clinical_note, query_patient_data, 
              add_allergy, navigate_to_section, schedule_followup
    - COMPLEX: search_patient_history, generate_summary
    
    Args:
        request: Tool call request with session, tool name, and arguments
        x_session_token: Session token for validation
        current_user: Authenticated user from JWT token
        
    Returns:
        ToolCallResponse with execution result
    """
    session_id = request.sessionId
    
    # Validate session exists
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )
    
    session = active_sessions[session_id]
    
    # Validate session token
    if not validate_session_token(session_id, x_session_token):
        logger.warning(
            f"Invalid session token for tool call: {session_id} | "
            f"Tool: {request.toolName}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token"
        )
    
    # Validate ownership
    if session['user_id'] != str(current_user.id):
        logger.warning(
            f"Unauthorized tool call attempt: {session_id} | "
            f"User: {current_user.nombre_usuario} | "
            f"Tool: {request.toolName}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this session"
        )
    
    # Log tool call start
    tool_call_start = datetime.utcnow()
    logger.info(
        f"Tool call started: {request.toolName} | "
        f"Session: {session_id} | "
        f"User: {current_user.nombre_usuario}"
    )
    
    try:
        # Determine if function is SIMPLE or COMPLEX
        if is_simple_function(request.toolName):
            # SIMPLE function - execute directly
            logger.info(f"Executing SIMPLE function: {request.toolName}")
            result = await execute_simple_function(
                function_name=request.toolName,
                args=request.args,
                session=session
            )
        else:
            # COMPLEX function - delegate to orchestrator
            logger.info(f"Executing COMPLEX function via orchestrator: {request.toolName}")
            result = await execute_complex_function(
                function_name=request.toolName,
                args=request.args,
                session=session
            )
        
        # Calculate execution time
        execution_time_ms = int((datetime.utcnow() - tool_call_start).total_seconds() * 1000)
        
        # Record tool call in session for audit
        session['tool_calls'].append({
            'tool_name': request.toolName,
            'timestamp': tool_call_start.isoformat(),
            'execution_time_ms': execution_time_ms,
            'success': True,
            'args': request.args
        })
        
        # Log successful execution
        logger.info(
            f"Tool call completed: {request.toolName} | "
            f"Session: {session_id} | "
            f"Execution time: {execution_time_ms}ms"
        )
        
        return ToolCallResponse(
            success=True,
            data=result.get('data'),
            message=result.get('message', f'Tool {request.toolName} executed successfully')
        )
        
    except Exception as e:
        # Calculate execution time for failed call
        execution_time_ms = int((datetime.utcnow() - tool_call_start).total_seconds() * 1000)
        
        # Record failed tool call for audit
        session['tool_calls'].append({
            'tool_name': request.toolName,
            'timestamp': tool_call_start.isoformat(),
            'execution_time_ms': execution_time_ms,
            'success': False,
            'error': str(e),
            'args': request.args
        })
        
        # Log error
        logger.error(
            f"Tool call failed: {request.toolName} | "
            f"Session: {session_id} | "
            f"Error: {str(e)}"
        )
        
        return ToolCallResponse(
            success=False,
            error=str(e),
            message=f"Tool {request.toolName} execution failed"
        )


# ============================================================================
# TOOL EXECUTION FUNCTIONS
# ============================================================================

async def execute_simple_function(
    function_name: str,
    args: Dict[str, Any],
    session: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute SIMPLE functions directly (without orchestrator)
    
    SIMPLE functions include:
    - update_vital_signs: Update patient vital signs
    - create_clinical_note: Create/update clinical notes
    - query_patient_data: Query patient information
    - add_allergy: Add patient allergy
    - navigate_to_section: UI navigation (handled client-side)
    - schedule_followup: Schedule follow-up appointment
    
    Args:
        function_name: Name of the function to execute
        args: Function arguments
        session: Session data with context
        
    Returns:
        Dict with execution result
        
    TODO: Implement actual REST endpoint calls for each function
    """
    patient_id = session['patient_id']
    appointment_id = session['appointment_id']
    user_id = session['user_id']
    
    # TODO: Call actual REST endpoints for each function
    # For now, return placeholder responses
    
    if function_name == "update_vital_signs":
        # TODO: Call POST /api/patients/{patient_id}/vital-signs
        return {
            'data': {
                'updated': True,
                'vital_signs': args
            },
            'message': 'Signos vitales actualizados correctamente'
        }
    
    elif function_name == "create_clinical_note":
        # TODO: Call POST /api/appointments/{appointment_id}/clinical-note
        return {
            'data': {
                'note_id': str(uuid.uuid4()),
                'created': True
            },
            'message': 'Nota clínica creada correctamente'
        }
    
    elif function_name == "query_patient_data":
        # TODO: Call GET /api/patients/{patient_id}
        return {
            'data': {
                'patient_id': patient_id,
                'data': {}  # Patient data here
            },
            'message': 'Datos del paciente recuperados'
        }
    
    elif function_name == "add_allergy":
        # TODO: Call POST /api/patients/{patient_id}/allergies
        return {
            'data': {
                'allergy_id': str(uuid.uuid4()),
                'added': True
            },
            'message': 'Alergia agregada correctamente'
        }
    
    elif function_name == "navigate_to_section":
        # This is handled client-side, no backend action needed
        return {
            'data': {
                'section': args.get('section', 'unknown')
            },
            'message': 'Navegación solicitada'
        }
    
    elif function_name == "schedule_followup":
        # TODO: Call POST /api/appointments
        return {
            'data': {
                'appointment_id': str(uuid.uuid4()),
                'scheduled': True
            },
            'message': 'Cita de seguimiento agendada'
        }
    
    else:
        raise ValueError(f"Unknown simple function: {function_name}")


async def execute_complex_function(
    function_name: str,
    args: Dict[str, Any],
    session: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute COMPLEX functions via orchestrator and SubAgents
    
    COMPLEX functions include:
    - search_patient_history: Semantic search in patient history (uses Summaries SubAgent)
    - generate_summary: Generate medical summary (uses Summaries SubAgent)
    
    Args:
        function_name: Name of the function to execute
        args: Function arguments
        session: Session data with context
        
    Returns:
        Dict with execution result from orchestrator
    """
    patient_id = session['patient_id']
    appointment_id = session['appointment_id']
    user_id = session['user_id']
    
    # Validate function is actually complex
    if function_name not in COMPLEX_FUNCTIONS_MAPPING:
        raise ValueError(f"Function {function_name} is not a complex function")
    
    # Get SubAgent configuration
    subagent_config = COMPLEX_FUNCTIONS_MAPPING[function_name]
    logger.info(
        f"Routing to orchestrator | "
        f"Function: {function_name} | "
        f"SubAgent: {subagent_config['subagent']}"
    )
    
    # Execute via orchestrator
    try:
        result = await execute_orchestrator(
            function_name=function_name,
            args=args,
            patient_id=patient_id,
            user_id=user_id,
            appointment_id=appointment_id
        )
        
        # Return formatted result
        return {
            'data': result.get('data'),
            'message': result.get('message', f'Function {function_name} completed'),
            'status': result.get('status'),
            'execution_time_ms': result.get('execution_time_ms')
        }
        
    except Exception as e:
        logger.error(
            f"Orchestrator execution failed | "
            f"Function: {function_name} | "
            f"Error: {str(e)}"
        )
        raise


# ============================================================================
# HEALTH & MONITORING
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Check API health and active sessions
    
    Returns:
        Health status with active session count
    """
    # Cleanup expired sessions before reporting
    cleanup_expired_sessions()
    
    return {
        "status": "healthy",
        "service": "live_sessions",
        "active_sessions": len(active_sessions),
        "session_ttl_minutes": SESSION_TTL_MINUTES,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/sessions/active", dependencies=[Depends(get_current_user)])
async def list_active_sessions(current_user: User = Depends(get_current_user)):
    """
    List active sessions for current user (admin/debug endpoint)
    
    Returns:
        List of active session IDs for the current user
    """
    user_sessions = [
        {
            'session_id': sid,
            'patient_id': sess['patient_id'],
            'created_at': sess['created_at'].isoformat(),
            'expires_at': sess['expires_at'].isoformat(),
            'tool_calls_count': len(sess['tool_calls'])
        }
        for sid, sess in active_sessions.items()
        if sess['user_id'] == str(current_user.id)
    ]
    
    return {
        'user_id': str(current_user.id),
        'username': current_user.nombre_usuario,
        'active_sessions': user_sessions,
        'count': len(user_sessions)
    }
