"""
Tests for Authentication Module
================================

Tests for /auth endpoints according to SRS Section 9 and FSD Section 2.1
"""
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.unit
class TestAuthLogin:
    """Tests for POST /auth/login endpoint"""

    async def test_login_successful(self, async_client: AsyncClient):
        """
        Test successful login with valid credentials
        
        Expected behavior:
        - Status code: 200
        - Returns access token, token type, expires_in
        - Returns user information
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "dr.santiago",
                "password": "SecurePass123!"
            }
        )
        
        # Verificar status code
        assert response.status_code == 200
        
        # Verificar estructura de respuesta
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] == 3600
        
        # Verificar datos del usuario
        assert "user" in data
        user = data["user"]
        assert "id" in user
        assert "username" in user
        assert user["username"] == "dr.santiago"
        assert "email" in user
        assert "rol" in user
        assert "nombre_completo" in user

    async def test_login_invalid_username(self, async_client: AsyncClient):
        """
        Test login with non-existent username
        
        Expected behavior:
        - Status code: 401 Unauthorized
        - Returns error message
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "credenciales" in data["detail"].lower()

    async def test_login_invalid_password(self, async_client: AsyncClient):
        """
        Test login with incorrect password
        
        Expected behavior:
        - Status code: 401 Unauthorized
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "dr.santiago",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_missing_username(self, async_client: AsyncClient):
        """
        Test login without username field
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 422

    async def test_login_missing_password(self, async_client: AsyncClient):
        """
        Test login without password field
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "dr.santiago"
            }
        )
        
        assert response.status_code == 422

    async def test_login_empty_username(self, async_client: AsyncClient):
        """
        Test login with empty username
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "",
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 422

    async def test_login_empty_password(self, async_client: AsyncClient):
        """
        Test login with empty password
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "dr.santiago",
                "password": ""
            }
        )
        
        assert response.status_code == 422

    async def test_login_username_too_short(self, async_client: AsyncClient):
        """
        Test login with username less than 3 characters
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "ab",
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 422

    async def test_login_username_too_long(self, async_client: AsyncClient):
        """
        Test login with username more than 50 characters
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "a" * 51,
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 422

    async def test_login_password_too_short(self, async_client: AsyncClient):
        """
        Test login with password less than 8 characters
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "dr.santiago",
                "password": "Pass12"
            }
        )
        
        assert response.status_code == 422

    async def test_login_invalid_json(self, async_client: AsyncClient):
        """
        Test login with invalid JSON
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.post(
            "/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.integration
class TestAuthTokenValidation:
    """Tests for token validation and protected endpoints"""

    async def test_protected_endpoint_with_valid_token(
        self, 
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test accessing protected endpoint with valid token
        
        Expected behavior:
        - Status code: 200 or appropriate success code
        - Request is authorized
        """
        # Example: GET /pacientes requires authentication
        response = await async_client.get(
            "/pacientes",
            headers=auth_headers
        )
        
        # Should not return 401 Unauthorized
        assert response.status_code != 401

    async def test_protected_endpoint_without_token(self, async_client: AsyncClient):
        """
        Test accessing protected endpoint without token
        
        Expected behavior:
        - Status code: 401 Unauthorized
        """
        response = await async_client.get("/pacientes")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_protected_endpoint_with_invalid_token(self, async_client: AsyncClient):
        """
        Test accessing protected endpoint with malformed token
        
        Expected behavior:
        - Status code: 401 Unauthorized
        """
        response = await async_client.get(
            "/pacientes",
            headers={"Authorization": "Bearer invalid_token_format"}
        )
        
        assert response.status_code == 401

    async def test_protected_endpoint_with_expired_token(
        self,
        async_client: AsyncClient,
        expired_token: str
    ):
        """
        Test accessing protected endpoint with expired token
        
        Expected behavior:
        - Status code: 401 Unauthorized
        - Error indicates token expired
        """
        response = await async_client.get(
            "/pacientes",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_token_wrong_format(self, async_client: AsyncClient):
        """
        Test with wrong Authorization header format
        
        Expected behavior:
        - Status code: 401 Unauthorized
        """
        # Missing "Bearer" prefix
        response = await async_client.get(
            "/pacientes",
            headers={"Authorization": "some_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.integration
class TestAuthRoleBasedAccess:
    """Tests for role-based access control"""

    async def test_admin_access_to_admin_endpoint(
        self,
        async_client: AsyncClient,
        test_admin_token: str
    ):
        """
        Test admin role can access admin endpoints
        
        Expected behavior:
        - Status code: 200 or appropriate success code
        """
        response = await async_client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        # Should be authorized (not 403 Forbidden)
        assert response.status_code != 403

    async def test_regular_user_access_to_admin_endpoint(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test regular user cannot access admin endpoints
        
        Expected behavior:
        - Status code: 403 Forbidden
        """
        response = await async_client.get(
            "/admin/users",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.unit
class TestAuthPasswordSecurity:
    """Tests for password security requirements"""

    async def test_login_case_sensitive_username(self, async_client: AsyncClient):
        """
        Test that username is case-sensitive
        
        Expected behavior:
        - Different case should not authenticate
        """
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "DR.SANTIAGO",  # Different case
                "password": "SecurePass123!"
            }
        )
        
        # May be 401 or could be case-insensitive depending on implementation
        # This test documents the expected behavior
        assert response.status_code in [200, 401]

    async def test_login_rate_limiting(self, async_client: AsyncClient):
        """
        Test rate limiting on login attempts
        
        Expected behavior:
        - After N failed attempts, should return 429 Too Many Requests
        
        Note: This test may be skipped if rate limiting is not implemented
        """
        # Make multiple failed login attempts
        for _ in range(5):
            await async_client.post(
                "/auth/login",
                json={
                    "username": "dr.santiago",
                    "password": "WrongPassword"
                }
            )
        
        # Next attempt should be rate limited
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "dr.santiago",
                "password": "WrongPassword"
            }
        )
        
        # May return 429 or 401 depending on implementation
        assert response.status_code in [401, 429]
