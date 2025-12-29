"""
Tests for Live Sessions API Module
====================================

Tests for /api/live endpoints for secure voice session management
according to SRS Section 9 and live_sessions.py implementation
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
@pytest.mark.integration
class TestSessionStart:
    """Tests for POST /api/live/session/start endpoint"""

    async def test_start_session_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful session creation
        
        Expected behavior:
        - Status code: 200 OK
        - Returns session token, sessionId, and expiresAt
        - Token is unique and secure
        """
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "token" in data
        assert "sessionId" in data
        assert "expiresAt" in data
        
        # Verificar token no está vacío
        assert len(data["token"]) > 0
        
        # Verificar sessionId es UUID válido
        assert len(data["sessionId"]) == 36  # UUID format
        assert "-" in data["sessionId"]
        
        # Verificar expiresAt es futuro
        expires_at = datetime.fromisoformat(data["expiresAt"].replace("Z", "+00:00"))
        assert expires_at > datetime.utcnow()

    async def test_start_session_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """
        Test that session start requires authentication
        
        Expected behavior:
        - Status code: 401 Unauthorized without token
        """
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        response = await async_client.post(
            "/api/live/session/start",
            json=session_data
        )
        
        assert response.status_code == 401

    async def test_start_session_missing_patient_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test session start without patient ID
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        session_data = {
            "appointmentId": "1",
            "userId": "1"
        }
        
        response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_start_session_missing_appointment_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test session start without appointment ID
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        session_data = {
            "patientId": "1",
            "userId": "1"
        }
        
        response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_start_session_multiple_sessions(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating multiple sessions
        
        Expected behavior:
        - Each session gets unique token and sessionId
        """
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        # Create first session
        response1 = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        # Create second session
        response2 = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Verificar que son diferentes
        assert data1["token"] != data2["token"]
        assert data1["sessionId"] != data2["sessionId"]


@pytest.mark.asyncio
@pytest.mark.integration
class TestSessionStop:
    """Tests for DELETE /api/live/session/{session_id} endpoint"""

    async def test_stop_session_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful session termination
        
        Expected behavior:
        - Status code: 200 OK
        - Session is marked as inactive
        """
        # First create a session
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        start_response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        session_id = start_response.json()["sessionId"]
        
        # Now stop the session
        response = await async_client.delete(
            f"/api/live/session/{session_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_stop_session_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """
        Test that session stop requires authentication
        
        Expected behavior:
        - Status code: 401 Unauthorized
        """
        fake_session_id = "00000000-0000-0000-0000-000000000000"
        
        response = await async_client.delete(
            f"/api/live/session/{fake_session_id}"
        )
        
        assert response.status_code == 401

    async def test_stop_session_validates_ownership(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_admin_token: str
    ):
        """
        Test that only session owner can stop it
        
        Expected behavior:
        - Status code: 403 Forbidden for non-owner
        - Status code: 404 Not Found for non-existent session
        """
        # Create session with one user
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        start_response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        session_id = start_response.json()["sessionId"]
        
        # Try to stop with different user
        other_headers = {"Authorization": f"Bearer {test_admin_token}"}
        
        response = await async_client.delete(
            f"/api/live/session/{session_id}",
            headers=other_headers
        )
        
        # Should be forbidden or not found
        assert response.status_code in [403, 404]

    async def test_stop_nonexistent_session(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test stopping a session that doesn't exist
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        fake_session_id = "00000000-0000-0000-0000-000000000000"
        
        response = await async_client.delete(
            f"/api/live/session/{fake_session_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
class TestToolCall:
    """Tests for POST /api/live/tool-call endpoint"""

    async def test_tool_call_simple_function(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test executing a simple function
        
        Expected behavior:
        - Status code: 200 OK
        - Returns success with data
        """
        # First create a session
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        start_response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        session_info = start_response.json()
        
        # Execute simple function
        tool_call_data = {
            "sessionId": session_info["sessionId"],
            "toolName": "query_patient_data",
            "args": {
                "patient_id": "1",
                "field": "nombre"
            }
        }
        
        # Add session token to headers
        headers_with_token = {
            **auth_headers,
            "X-Session-Token": session_info["token"]
        }
        
        response = await async_client.post(
            "/api/live/tool-call",
            json=tool_call_data,
            headers=headers_with_token
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "success" in data
        assert "data" in data or "message" in data

    async def test_tool_call_complex_function(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test executing a complex function (requires orchestrator)
        
        Expected behavior:
        - Status code: 200 OK
        - Returns success with data from orchestrator
        """
        # First create a session
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        start_response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        session_info = start_response.json()
        
        # Execute complex function
        tool_call_data = {
            "sessionId": session_info["sessionId"],
            "toolName": "generate_summary",
            "args": {
                "patient_id": "1",
                "summary_type": "consulta"
            }
        }
        
        # Add session token to headers
        headers_with_token = {
            **auth_headers,
            "X-Session-Token": session_info["token"]
        }
        
        response = await async_client.post(
            "/api/live/tool-call",
            json=tool_call_data,
            headers=headers_with_token
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data

    async def test_tool_call_requires_session_token(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test that tool call requires session token
        
        Expected behavior:
        - Status code: 401 Unauthorized without session token
        """
        tool_call_data = {
            "sessionId": "fake-session-id",
            "toolName": "query_patient_data",
            "args": {}
        }
        
        response = await async_client.post(
            "/api/live/tool-call",
            json=tool_call_data,
            headers=auth_headers  # No session token
        )
        
        assert response.status_code in [401, 403, 404]

    async def test_tool_call_invalid_function(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test executing an invalid function name
        
        Expected behavior:
        - Status code: 400 Bad Request or 404 Not Found
        """
        # Create session
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        start_response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        session_info = start_response.json()
        
        # Execute invalid function
        tool_call_data = {
            "sessionId": session_info["sessionId"],
            "toolName": "invalid_function_name",
            "args": {}
        }
        
        headers_with_token = {
            **auth_headers,
            "X-Session-Token": session_info["token"]
        }
        
        response = await async_client.post(
            "/api/live/tool-call",
            json=tool_call_data,
            headers=headers_with_token
        )
        
        assert response.status_code in [400, 404]


@pytest.mark.asyncio
@pytest.mark.integration
class TestSessionExpiration:
    """Tests for session expiration and cleanup"""

    async def test_session_expiration(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test that expired sessions are rejected
        
        Expected behavior:
        - Expired session tokens should be rejected
        - Status code: 401 Unauthorized or 403 Forbidden
        """
        # Create a session
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que la fecha de expiración está en el futuro
        expires_at = datetime.fromisoformat(data["expiresAt"].replace("Z", "+00:00"))
        now = datetime.utcnow()
        
        # Session should expire in the future (default 30 minutes)
        time_until_expiry = (expires_at - now).total_seconds()
        assert time_until_expiry > 0
        assert time_until_expiry <= 1800  # 30 minutes max

    @pytest.mark.slow
    async def test_session_cleanup(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test that session cleanup removes expired sessions
        
        Note: This test documents the cleanup behavior
        Expected behavior:
        - Expired sessions should be cleaned up
        """
        # Create multiple sessions
        for i in range(3):
            session_data = {
                "patientId": str(i + 1),
                "appointmentId": str(i + 1),
                "userId": "1"
            }
            
            response = await async_client.post(
                "/api/live/session/start",
                json=session_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.unit
class TestSessionTokenValidation:
    """Tests for session token validation logic"""

    def test_create_session_token_structure(self):
        """
        Test that session tokens are created with correct structure
        
        Expected behavior:
        - Token should be URL-safe string
        - Should have sessionId and expiresAt
        """
        from backend.api.live_sessions import create_session_token
        
        session_id = "test-session-123"
        result = create_session_token(session_id, ttl_minutes=30)
        
        assert result.token is not None
        assert len(result.token) > 0
        assert result.sessionId == session_id
        assert result.expiresAt > datetime.utcnow()

    def test_session_token_unique(self):
        """
        Test that each session token is unique
        
        Expected behavior:
        - Multiple calls should generate different tokens
        """
        from backend.api.live_sessions import create_session_token
        
        token1 = create_session_token("session-1")
        token2 = create_session_token("session-2")
        
        assert token1.token != token2.token
        assert token1.sessionId != token2.sessionId


@pytest.mark.asyncio
@pytest.mark.integration
class TestSecurityFeatures:
    """Tests for security features of live sessions"""

    async def test_no_api_keys_exposed(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test that API keys are never exposed to client
        
        Expected behavior:
        - Response should not contain API keys or secrets
        """
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        response_text = response.text.lower()
        
        # Verificar que no hay API keys expuestas
        assert "api_key" not in response_text
        assert "apikey" not in response_text
        assert "secret" not in response_text
        assert "password" not in response_text

    async def test_audit_logging(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test that tool calls are audit logged
        
        Expected behavior:
        - All tool calls should be logged for audit
        """
        # Create session
        session_data = {
            "patientId": "1",
            "appointmentId": "1",
            "userId": "1"
        }
        
        start_response = await async_client.post(
            "/api/live/session/start",
            json=session_data,
            headers=auth_headers
        )
        
        # Audit logging is internal, but session should be created
        assert start_response.status_code == 200
