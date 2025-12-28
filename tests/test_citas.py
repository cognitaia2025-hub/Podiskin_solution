"""
Tests for Citas (Appointments) Module
======================================

Tests for /citas endpoints according to SRS Section 9 and FSD Section 2.4
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
@pytest.mark.citas
@pytest.mark.api
class TestCitasDisponibilidad:
    """Tests for GET /citas/disponibilidad endpoint"""

    async def test_get_disponibilidad_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful availability check
        
        Expected behavior:
        - Status code: 200 OK
        - Returns available time slots
        """
        fecha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = await async_client.get(
            f"/citas/disponibilidad?id_podologo=1&fecha={fecha}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura
        assert "fecha" in data
        assert "podologo" in data
        assert "slots" in data
        
        # Verificar podologo
        assert data["podologo"]["id"] == 1
        assert "nombre" in data["podologo"]
        
        # Verificar slots
        assert isinstance(data["slots"], list)
        if len(data["slots"]) > 0:
            slot = data["slots"][0]
            assert "hora" in slot
            assert "disponible" in slot

    async def test_get_disponibilidad_missing_podologo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test availability check without podologo ID
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        fecha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = await async_client.get(
            f"/citas/disponibilidad?fecha={fecha}",
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_get_disponibilidad_missing_fecha(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test availability check without date
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.get(
            "/citas/disponibilidad?id_podologo=1",
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_get_disponibilidad_invalid_podologo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test availability check with non-existent podologo
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        fecha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = await async_client.get(
            f"/citas/disponibilidad?id_podologo=99999&fecha={fecha}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_get_disponibilidad_past_date(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test availability check for past date
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        fecha = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = await async_client.get(
            f"/citas/disponibilidad?id_podologo=1&fecha={fecha}",
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_get_disponibilidad_invalid_date_format(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test availability check with invalid date format
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.get(
            "/citas/disponibilidad?id_podologo=1&fecha=31-12-2025",
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.citas
@pytest.mark.api
class TestCitasCreate:
    """Tests for POST /citas endpoint"""

    async def test_create_cita_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_cita_data: dict
    ):
        """
        Test successful appointment creation
        
        Expected behavior:
        - Status code: 201 Created
        - Returns created appointment with all fields
        - Calculates fecha_hora_fin automatically
        - Determines es_primera_vez correctly
        """
        response = await async_client.post(
            "/citas",
            json=sample_cita_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar campos básicos
        assert "id" in data
        assert data["id_paciente"] == sample_cita_data["id_paciente"]
        assert data["id_podologo"] == sample_cita_data["id_podologo"]
        assert data["tipo_cita"] == sample_cita_data["tipo_cita"]
        
        # Verificar estado inicial
        assert data["estado"] == "Confirmada"
        
        # Verificar cálculo de fecha_hora_fin (30 minutos después)
        assert "fecha_hora_fin" in data
        inicio = datetime.fromisoformat(data["fecha_hora_inicio"])
        fin = datetime.fromisoformat(data["fecha_hora_fin"])
        assert (fin - inicio).total_seconds() == 1800  # 30 minutos
        
        # Verificar bandera es_primera_vez
        assert "es_primera_vez" in data
        assert isinstance(data["es_primera_vez"], bool)
        
        # Verificar datos del paciente incluidos
        assert "paciente" in data
        assert data["paciente"]["id"] == sample_cita_data["id_paciente"]

    async def test_create_cita_minimal_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment with minimal required fields
        
        Expected behavior:
        - Status code: 201 Created
        """
        minimal_data = {
            "id_paciente": 1,
            "id_podologo": 1,
            "fecha_hora_inicio": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        response = await async_client.post(
            "/citas",
            json=minimal_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201

    async def test_create_cita_missing_required_field(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment without required field
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        incomplete_data = {
            "id_paciente": 1,
            # Missing id_podologo and fecha_hora_inicio
            "tipo_cita": "Consulta"
        }
        
        response = await async_client.post(
            "/citas",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_cita_invalid_paciente(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment with non-existent patient
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        invalid_data = {
            "id_paciente": 99999,
            "id_podologo": 1,
            "fecha_hora_inicio": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        response = await async_client.post(
            "/citas",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_create_cita_invalid_podologo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment with non-existent podologo
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        invalid_data = {
            "id_paciente": 1,
            "id_podologo": 99999,
            "fecha_hora_inicio": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        response = await async_client.post(
            "/citas",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_create_cita_past_datetime(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment in the past
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        past_data = {
            "id_paciente": 1,
            "id_podologo": 1,
            "fecha_hora_inicio": (datetime.now() - timedelta(days=1)).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        response = await async_client.post(
            "/citas",
            json=past_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_cita_too_soon(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment less than 1 hour from now
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        too_soon = {
            "id_paciente": 1,
            "id_podologo": 1,
            "fecha_hora_inicio": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        response = await async_client.post(
            "/citas",
            json=too_soon,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_cita_conflict(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment in already occupied slot
        
        Expected behavior:
        - Status code: 409 Conflict
        """
        cita_data = {
            "id_paciente": 1,
            "id_podologo": 1,
            "fecha_hora_inicio": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        # Create first appointment
        first_response = await async_client.post(
            "/citas",
            json=cita_data,
            headers=auth_headers
        )
        assert first_response.status_code == 201
        
        # Try to create conflicting appointment
        conflict_data = cita_data.copy()
        conflict_data["id_paciente"] = 2  # Different patient, same slot
        
        second_response = await async_client.post(
            "/citas",
            json=conflict_data,
            headers=auth_headers
        )
        
        assert second_response.status_code == 409

    async def test_create_cita_duplicate_patient_same_day(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating second appointment for same patient on same day
        
        Expected behavior:
        - Status code: 409 Conflict
        """
        fecha_base = datetime.now() + timedelta(days=1)
        
        first_cita = {
            "id_paciente": 1,
            "id_podologo": 1,
            "fecha_hora_inicio": fecha_base.replace(hour=10, minute=0).isoformat(),
            "tipo_cita": "Consulta"
        }
        
        # Create first appointment
        first_response = await async_client.post(
            "/citas",
            json=first_cita,
            headers=auth_headers
        )
        assert first_response.status_code == 201
        
        # Try to create second appointment same day
        second_cita = first_cita.copy()
        second_cita["fecha_hora_inicio"] = fecha_base.replace(hour=14, minute=0).isoformat()
        
        second_response = await async_client.post(
            "/citas",
            json=second_cita,
            headers=auth_headers
        )
        
        assert second_response.status_code == 409

    async def test_create_cita_invalid_tipo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating appointment with invalid tipo_cita
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "id_paciente": 1,
            "id_podologo": 1,
            "fecha_hora_inicio": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
            "tipo_cita": "TipoInvalido"
        }
        
        response = await async_client.post(
            "/citas",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.citas
@pytest.mark.api
class TestCitasUpdate:
    """Tests for PUT /citas/{id} endpoint"""

    async def test_update_cita_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful appointment update
        
        Expected behavior:
        - Status code: 200 OK
        - Returns updated appointment
        """
        update_data = {
            "notas_recepcion": "Paciente confirmó asistencia",
            "estado": "Confirmada"
        }
        
        response = await async_client.put(
            "/citas/1",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["notas_recepcion"] == update_data["notas_recepcion"]
        assert data["estado"] == update_data["estado"]

    async def test_update_cita_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test updating non-existent appointment
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.put(
            "/citas/99999",
            json={"estado": "Confirmada"},
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_update_cita_change_estado(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test changing appointment status
        
        Expected behavior:
        - Status code: 200 OK
        - Estado is updated correctly
        """
        estados = ["Confirmada", "Completada", "Cancelada", "No_Asistio"]
        
        for estado in estados:
            response = await async_client.put(
                "/citas/1",
                json={"estado": estado},
                headers=auth_headers
            )
            
            # May succeed or fail depending on current state
            assert response.status_code in [200, 400, 409]

    async def test_update_cita_invalid_estado(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test updating appointment with invalid estado
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.put(
            "/citas/1",
            json={"estado": "EstadoInvalido"},
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.citas
@pytest.mark.api
class TestCitasCancel:
    """Tests for DELETE /citas/{id} endpoint"""

    async def test_cancel_cita_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful appointment cancellation
        
        Expected behavior:
        - Status code: 200 OK
        - Estado changed to Cancelada
        """
        response = await async_client.delete(
            "/citas/1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "Cancelada"

    async def test_cancel_cita_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test cancelling non-existent appointment
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.delete(
            "/citas/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_cancel_cita_already_completed(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test cancelling already completed appointment
        
        Expected behavior:
        - Status code: 400 or 409 (cannot cancel completed appointment)
        """
        # First update to completed
        await async_client.put(
            "/citas/1",
            json={"estado": "Completada"},
            headers=auth_headers
        )
        
        # Try to cancel
        response = await async_client.delete(
            "/citas/1",
            headers=auth_headers
        )
        
        assert response.status_code in [400, 409]


@pytest.mark.asyncio
@pytest.mark.citas
@pytest.mark.api
class TestCitasList:
    """Tests for GET /citas endpoint"""

    async def test_get_citas_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful retrieval of appointments list
        
        Expected behavior:
        - Status code: 200 OK
        - Returns paginated list
        """
        response = await async_client.get(
            "/citas",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_get_citas_filter_by_date(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test filtering appointments by date
        
        Expected behavior:
        - Returns only appointments for specified date
        """
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        response = await async_client.get(
            f"/citas?fecha={fecha}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all appointments are for the specified date
        for cita in data["items"]:
            cita_fecha = cita["fecha_hora_inicio"].split("T")[0]
            assert cita_fecha == fecha

    async def test_get_citas_filter_by_paciente(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test filtering appointments by patient
        
        Expected behavior:
        - Returns only appointments for specified patient
        """
        response = await async_client.get(
            "/citas?id_paciente=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for cita in data["items"]:
            assert cita["id_paciente"] == 1

    async def test_get_citas_filter_by_podologo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test filtering appointments by podologo
        
        Expected behavior:
        - Returns only appointments for specified podologo
        """
        response = await async_client.get(
            "/citas?id_podologo=1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        for cita in data["items"]:
            assert cita["id_podologo"] == 1


@pytest.mark.asyncio
@pytest.mark.citas
@pytest.mark.integration
class TestCitasIntegration:
    """Integration tests for appointment workflows"""

    async def test_complete_appointment_workflow(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_cita_data: dict
    ):
        """
        Test complete appointment workflow: check availability, create, confirm, complete
        
        Expected behavior:
        - All operations succeed in sequence
        """
        # 1. Check availability
        fecha = sample_cita_data["fecha_hora_inicio"].split("T")[0]
        avail_response = await async_client.get(
            f"/citas/disponibilidad?id_podologo={sample_cita_data['id_podologo']}&fecha={fecha}",
            headers=auth_headers
        )
        assert avail_response.status_code == 200
        
        # 2. Create appointment
        create_response = await async_client.post(
            "/citas",
            json=sample_cita_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        cita_id = create_response.json()["id"]
        
        # 3. Confirm appointment
        confirm_response = await async_client.put(
            f"/citas/{cita_id}",
            json={"estado": "Confirmada"},
            headers=auth_headers
        )
        assert confirm_response.status_code == 200
        
        # 4. Complete appointment
        complete_response = await async_client.put(
            f"/citas/{cita_id}",
            json={"estado": "Completada"},
            headers=auth_headers
        )
        assert complete_response.status_code == 200

    async def test_appointment_reminder_scheduling(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_cita_data: dict
    ):
        """
        Test that reminders are scheduled when appointment is created
        
        Expected behavior:
        - Appointment created with reminder flags
        - Reminder jobs are created (24h and 2h before)
        """
        response = await async_client.post(
            "/citas",
            json=sample_cita_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify reminder flags exist
        assert "recordatorio_24h_enviado" in data
        assert "recordatorio_2h_enviado" in data
        
        # Initially should be False
        assert data["recordatorio_24h_enviado"] is False
        assert data["recordatorio_2h_enviado"] is False
