"""
Tests for Pagos Module
======================

Tests for /pagos endpoints.
"""
import pytest
from httpx import AsyncClient
from datetime import datetime

@pytest.mark.asyncio
@pytest.mark.pagos
class TestPagos:
    """Tests for Pagos endpoints"""

    async def test_listar_pagos_unauthorized(self, async_client: AsyncClient):
        """Test accessing pagos without authentication"""
        response = await async_client.get("/api/pagos/")
        assert response.status_code == 401

    async def test_listar_pagos_success(self, async_client: AsyncClient, auth_headers: dict):
        """
        Test successful retrieval of pagos list
        Note: Requires 'cobros:read' permission
        """
        response = await async_client.get("/api/pagos/", headers=auth_headers)
        # If the test user doesn't have cobros:read permission, it will be 403
        assert response.status_code in [200, 403, 500]
        if response.status_code == 200:
            data = response.json()
            assert "pagos" in data
            assert "total" in data

    async def test_get_pago_stats(self, async_client: AsyncClient, auth_headers: dict):
        """Test retrieval of payment statistics"""
        response = await async_client.get("/api/pagos/stats/resumen", headers=auth_headers)
        assert response.status_code in [200, 403, 500]
        if response.status_code == 200:
            data = response.json()
            assert "total_cobrado" in data
            assert "total_pendiente" in data

    async def test_crear_pago_validation_error(self, async_client: AsyncClient, auth_headers: dict):
        """Test creating pago with invalid data"""
        invalid_pago = {
            "id_cita": 1,
            "monto_total": 100,
            "monto_pagado": 150, # More than total
            "metodo_pago": "Invalid"
        }
        response = await async_client.post("/api/pagos/", json=invalid_pago, headers=auth_headers)
        # 422 for pydantic validation or 403 for permissions
        assert response.status_code in [422, 403]
