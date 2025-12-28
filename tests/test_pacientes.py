"""
Tests for Pacientes (Patients) Module
======================================

Tests for /pacientes endpoints according to SRS Section 9 and FSD Section 2.2
"""
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
@pytest.mark.pacientes
@pytest.mark.api
class TestPacientesList:
    """Tests for GET /pacientes endpoint"""

    async def test_get_pacientes_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful retrieval of patients list
        
        Expected behavior:
        - Status code: 200
        - Returns paginated list with items and metadata
        """
        response = await async_client.get(
            "/pacientes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de paginación
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data
        
        # Verificar estructura de items
        assert isinstance(data["items"], list)

    async def test_get_pacientes_with_pagination(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test patients list with pagination parameters
        
        Expected behavior:
        - Respects page and limit parameters
        - Returns correct pagination metadata
        """
        response = await async_client.get(
            "/pacientes?page=1&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["items"]) <= 10

    async def test_get_pacientes_with_search(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test patients search by name or phone
        
        Expected behavior:
        - Filters results based on search term
        """
        response = await async_client.get(
            "/pacientes?search=Juan",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Results should contain search term
        for item in data["items"]:
            nombre = item.get("nombre_completo", "").lower()
            telefono = item.get("telefono_principal", "")
            assert "juan" in nombre or "Juan" in telefono

    async def test_get_pacientes_filter_by_activo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test filtering patients by active status
        
        Expected behavior:
        - Only returns active/inactive patients based on filter
        """
        response = await async_client.get(
            "/pacientes?activo=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned patients should be active
        for item in data["items"]:
            assert item["activo"] is True

    async def test_get_pacientes_ordering(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test ordering patients by field
        
        Expected behavior:
        - Results are ordered by specified field and direction
        """
        response = await async_client.get(
            "/pacientes?orden=nombre&direccion=asc",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify ordering
        nombres = [item["nombre_completo"] for item in data["items"]]
        assert nombres == sorted(nombres)

    async def test_get_pacientes_invalid_page(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test with invalid page number
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.get(
            "/pacientes?page=0",
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_get_pacientes_invalid_limit(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test with limit exceeding maximum
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        response = await async_client.get(
            "/pacientes?limit=101",
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_get_pacientes_unauthorized(self, async_client: AsyncClient):
        """
        Test accessing patients without authentication
        
        Expected behavior:
        - Status code: 401 Unauthorized
        """
        response = await async_client.get("/pacientes")
        
        assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.pacientes
@pytest.mark.api
class TestPacienteCreate:
    """Tests for POST /pacientes endpoint"""

    async def test_create_paciente_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_paciente_data: dict
    ):
        """
        Test successful patient creation
        
        Expected behavior:
        - Status code: 201 Created
        - Returns created patient with ID
        - All fields are correctly stored
        """
        response = await async_client.post(
            "/pacientes",
            json=sample_paciente_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar que se asignó un ID
        assert "id" in data
        assert data["id"] > 0
        
        # Verificar que los datos coinciden
        assert data["primer_nombre"] == sample_paciente_data["primer_nombre"]
        assert data["primer_apellido"] == sample_paciente_data["primer_apellido"]
        assert data["fecha_nacimiento"] == sample_paciente_data["fecha_nacimiento"]
        assert data["sexo"] == sample_paciente_data["sexo"]
        assert data["telefono_principal"] == sample_paciente_data["telefono_principal"]
        
        # Verificar campos calculados
        assert "edad" in data
        assert "nombre_completo" in data

    async def test_create_paciente_minimal_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient with minimal required fields
        
        Expected behavior:
        - Status code: 201 Created
        """
        minimal_data = {
            "primer_nombre": "María",
            "primer_apellido": "López",
            "fecha_nacimiento": "1985-03-20",
            "sexo": "F",
            "telefono_principal": "6869876543"
        }
        
        response = await async_client.post(
            "/pacientes",
            json=minimal_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data

    async def test_create_paciente_missing_required_field(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient without required field
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        incomplete_data = {
            "primer_nombre": "Pedro",
            # Missing primer_apellido and other required fields
            "fecha_nacimiento": "1980-01-01"
        }
        
        response = await async_client.post(
            "/pacientes",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_paciente_invalid_fecha_nacimiento(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient with invalid birth date format
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "primer_nombre": "Ana",
            "primer_apellido": "Martínez",
            "fecha_nacimiento": "31-12-1990",  # Wrong format
            "sexo": "F",
            "telefono_principal": "6861234567"
        }
        
        response = await async_client.post(
            "/pacientes",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_paciente_invalid_sexo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient with invalid sexo value
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "primer_nombre": "Luis",
            "primer_apellido": "Hernández",
            "fecha_nacimiento": "1992-06-15",
            "sexo": "X",  # Invalid value
            "telefono_principal": "6861234567"
        }
        
        response = await async_client.post(
            "/pacientes",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_paciente_invalid_telefono(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient with invalid phone number
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "primer_nombre": "Carlos",
            "primer_apellido": "Ramírez",
            "fecha_nacimiento": "1988-09-10",
            "sexo": "M",
            "telefono_principal": "123"  # Too short
        }
        
        response = await async_client.post(
            "/pacientes",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_paciente_invalid_email(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient with invalid email format
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "primer_nombre": "Sofia",
            "primer_apellido": "Torres",
            "fecha_nacimiento": "1995-04-25",
            "sexo": "F",
            "telefono_principal": "6861234567",
            "email": "invalid-email"  # Invalid format
        }
        
        response = await async_client.post(
            "/pacientes",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_paciente_future_fecha_nacimiento(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating patient with future birth date
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "primer_nombre": "Futuro",
            "primer_apellido": "Paciente",
            "fecha_nacimiento": "2030-01-01",  # Future date
            "sexo": "M",
            "telefono_principal": "6861234567"
        }
        
        response = await async_client.post(
            "/pacientes",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.pacientes
@pytest.mark.api
class TestPacienteUpdate:
    """Tests for PUT /pacientes/{id} endpoint"""

    async def test_update_paciente_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful patient update
        
        Expected behavior:
        - Status code: 200 OK
        - Returns updated patient data
        """
        update_data = {
            "telefono_principal": "6869999999",
            "email": "nuevo.email@test.com"
        }
        
        response = await async_client.put(
            "/pacientes/1",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["telefono_principal"] == update_data["telefono_principal"]
        assert data["email"] == update_data["email"]

    async def test_update_paciente_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test updating non-existent patient
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.put(
            "/pacientes/99999",
            json={"telefono_principal": "6869999999"},
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_update_paciente_invalid_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test updating patient with invalid data
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "email": "not-an-email",
            "sexo": "Invalid"
        }
        
        response = await async_client.put(
            "/pacientes/1",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.pacientes
@pytest.mark.api
class TestPacienteDelete:
    """Tests for DELETE /pacientes/{id} endpoint (soft delete)"""

    async def test_delete_paciente_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test successful patient soft delete
        
        Expected behavior:
        - Status code: 200 OK
        - Patient marked as inactive
        """
        response = await async_client.delete(
            "/pacientes/1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["activo"] is False

    async def test_delete_paciente_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test deleting non-existent patient
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.delete(
            "/pacientes/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.pacientes
@pytest.mark.api
class TestPacienteAlergias:
    """Tests for /pacientes/{id}/alergias endpoints"""

    async def test_get_alergias_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test retrieving patient allergies
        
        Expected behavior:
        - Status code: 200 OK
        - Returns list of allergies
        """
        response = await async_client.get(
            "/pacientes/1/alergias",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_create_alergia_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_alergia_data: dict
    ):
        """
        Test adding allergy to patient
        
        Expected behavior:
        - Status code: 201 Created
        - Returns created allergy with ID
        """
        response = await async_client.post(
            "/pacientes/1/alergias",
            json=sample_alergia_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["tipo"] == sample_alergia_data["tipo"]
        assert data["nombre"] == sample_alergia_data["nombre"]
        assert data["severidad"] == sample_alergia_data["severidad"]

    async def test_create_alergia_invalid_tipo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test adding allergy with invalid tipo
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "tipo": "TipoInvalido",
            "nombre": "Alergia Test",
            "severidad": "Leve"
        }
        
        response = await async_client.post(
            "/pacientes/1/alergias",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_alergia_patient_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_alergia_data: dict
    ):
        """
        Test adding allergy to non-existent patient
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.post(
            "/pacientes/99999/alergias",
            json=sample_alergia_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.pacientes
@pytest.mark.integration
class TestPacienteIntegration:
    """Integration tests for patient workflows"""

    async def test_complete_patient_workflow(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_paciente_data: dict,
        sample_alergia_data: dict
    ):
        """
        Test complete patient workflow: create, read, add allergy, update, list
        
        Expected behavior:
        - All operations succeed in sequence
        """
        # 1. Create patient
        create_response = await async_client.post(
            "/pacientes",
            json=sample_paciente_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        patient_id = create_response.json()["id"]
        
        # 2. Get patient details
        get_response = await async_client.get(
            f"/pacientes/{patient_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        
        # 3. Add allergy
        allergy_response = await async_client.post(
            f"/pacientes/{patient_id}/alergias",
            json=sample_alergia_data,
            headers=auth_headers
        )
        assert allergy_response.status_code == 201
        
        # 4. Update patient
        update_response = await async_client.put(
            f"/pacientes/{patient_id}",
            json={"telefono_principal": "6869999999"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        
        # 5. Search for patient
        search_response = await async_client.get(
            f"/pacientes?search={sample_paciente_data['primer_nombre']}",
            headers=auth_headers
        )
        assert search_response.status_code == 200
        assert any(p["id"] == patient_id for p in search_response.json()["items"])
