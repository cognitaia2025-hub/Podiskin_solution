"""
Live Sessions API - Secure Session Management
Endpoints para manejo seguro de sesiones de Gemini Live
"""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import uuid
import secrets
import os

router = APIRouter(prefix="/api/live", tags=["live_sessions"])

# In-memory session store (use Redis in production)
active_sessions = {}

# Models
class SessionConfig(BaseModel):
    """Configuration for starting a new voice session"""
    patientId: str = Field(..., description="ID del paciente")
    appointmentId: str = Field(..., description="ID de la cita")
    userId: str = Field(..., description="ID del usuario (médico)")

class SessionToken(BaseModel):
    """Ephemeral session token"""
    token: str = Field(..., description="Token efímero")
    sessionId: str = Field(..., description="ID de sesión")
    expiresAt: datetime = Field(..., description="Timestamp de expiración")

class SessionCredentials(BaseModel):
    """Temporary credentials for Gemini API"""
    apiKey: str = Field(..., description="API key temporal")
    sessionId: str = Field(..., description="ID de sesión")

class ToolCallRequest(BaseModel):
    """Request to execute a tool call"""
    sessionId: str = Field(..., description="ID de sesión")
    toolName: str = Field(..., description="Nombre de la tool")
    args: dict = Field(..., description="Argumentos de la tool")

class ToolCallResponse(BaseModel):
    """Response from tool execution"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


# Helper functions
def create_session_token(session_id: str, ttl_seconds: int = 3600) -> SessionToken:
    """Create an ephemeral session token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    return SessionToken(
        token=token,
        sessionId=session_id,
        expiresAt=expires_at
    )

def validate_session_token(session_id: str, token: str) -> bool:
    """Validate a session token"""
    if session_id not in active_sessions:
        return False
    
    session = active_sessions[session_id]
    
    # Check token matches
    if session['token'] != token:
        return False
    
    # Check not expired
    if datetime.utcnow() > session['expires_at']:
        del active_sessions[session_id]
        return False
    
    return True

def get_current_user_id(authorization: str = Header(...)) -> str:
    """Extract user ID from authorization header"""
    # TODO: Implement proper JWT validation
    # For now, this is a placeholder
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # In production, decode JWT and extract user_id
    # token = authorization.split(" ")[1]
    # payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    # return payload['user_id']
    
    return "user_123"  # Placeholder


# Endpoints
@router.post("/session/start", response_model=SessionToken)
async def start_session(
    config: SessionConfig,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a secure voice session with ephemeral token
    
    - Validates user permissions
    - Creates session with TTL
    - Returns ephemeral token for client
    """
    # Validate user has access to this patient
    # TODO: Check permissions in database
    
    # Create unique session ID
    session_id = str(uuid.uuid4())
    
    # Create ephemeral token
    session_token = create_session_token(session_id, ttl_seconds=3600)
    
    # Store session data
    active_sessions[session_id] = {
        'session_id': session_id,
        'token': session_token.token,
        'user_id': user_id,
        'patient_id': config.patientId,
        'appointment_id': config.appointmentId,
        'created_at': datetime.utcnow(),
        'expires_at': session_token.expiresAt,
        'active': True
    }
    
    # Log session creation
    print(f"Session created: {session_id} for user {user_id}")
    
    return session_token


@router.post("/session/stop")
async def stop_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Stop and cleanup a voice session
    
    - Validates session belongs to user
    - Revokes token
    - Cleans up resources
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Validate ownership
    if session['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mark as inactive and remove
    session['active'] = False
    del active_sessions[session_id]
    
    print(f"Session stopped: {session_id}")
    
    return {"status": "closed", "sessionId": session_id}


@router.post("/session/refresh", response_model=SessionToken)
async def refresh_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Refresh a session token before expiration
    
    - Extends session TTL
    - Returns new token
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Validate ownership
    if session['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if expired
    if datetime.utcnow() > session['expires_at']:
        del active_sessions[session_id]
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Create new token
    new_token = create_session_token(session_id, ttl_seconds=3600)
    
    # Update session
    active_sessions[session_id].update({
        'token': new_token.token,
        'expires_at': new_token.expiresAt
    })
    
    return new_token


@router.get("/session/{session_id}/credentials", response_model=SessionCredentials)
async def get_session_credentials(
    session_id: str,
    x_session_token: str = Header(...),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get temporary Gemini API credentials for a session
    
    ⚠️ SECURITY: This endpoint should only return scoped/temporary API keys
    In production, use Google's session token API or create restricted keys
    
    For now, returns the main API key (NOT RECOMMENDED FOR PRODUCTION)
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Validate token
    if not validate_session_token(session_id, x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Validate ownership
    if session['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # TODO: In production, create a temporary/scoped API key instead
    # For now, return the main key (SECURITY RISK)
    
    return SessionCredentials(
        apiKey=api_key,
        sessionId=session_id
    )


@router.post("/tool/call", response_model=ToolCallResponse)
async def execute_tool_call(
    request: ToolCallRequest,
    x_session_token: str = Header(...),
    user_id: str = Depends(get_current_user_id)
):
    """
    Execute a critical tool call on the backend
    
    - Validates session and permissions
    - Executes tool securely
    - Returns result
    
    This keeps sensitive operations server-side
    """
    if request.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[request.sessionId]
    
    # Validate token
    if not validate_session_token(request.sessionId, x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Validate ownership
    if session['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Execute tool based on name
    try:
        result = await execute_tool(
            request.toolName, 
            request.args,
            session
        )
        
        # Log tool execution
        print(f"Tool executed: {request.toolName} in session {request.sessionId}")
        
        return ToolCallResponse(
            success=True,
            data=result.get('data'),
            message=result.get('message')
        )
        
    except Exception as e:
        print(f"Tool execution error: {str(e)}")
        return ToolCallResponse(
            success=False,
            error=str(e)
        )


async def execute_tool(tool_name: str, args: dict, session: dict) -> dict:
    """
    Execute a tool call securely
    
    TODO: Implement actual tool execution logic
    Connect to database, orchestrator, etc.
    """
    # Placeholder implementation
    return {
        'data': {'result': 'Tool executed'},
        'message': f'Tool {tool_name} executed successfully'
    }


# Health check
@router.get("/health")
async def health_check():
    """Check API health and active sessions"""
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }
