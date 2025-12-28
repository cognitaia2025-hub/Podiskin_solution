"""
Tests for Tratamientos (Treatments) Module
==========================================

Tests for /citas/{id}/signos-vitales and /citas/{id}/diagnosticos endpoints
according to SRS Section 9 and FSD Sections 2.5 and 2.6
"""
import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
@pytest.mark.tratamientos
@pytest.mark.api
class TestSignosVitales:
    """Tests for POST /citas/{id}/signos-vitales endpoint"""

    async def test_create_signos_vitales_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_signos_vitales_data: dict
    ):
        """
        Test successful vital signs creation
        
        Expected behavior:
        - Status code: 201 Created
        - Returns vital signs with calculated IMC
        - IMC classification is correct
        """
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=sample_signos_vitales_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar campos básicos
        assert "id" in data
        assert data["id_cita"] == 1
        assert data["peso_kg"] == sample_signos_vitales_data["peso_kg"]
        assert data["talla_cm"] == sample_signos_vitales_data["talla_cm"]
        
        # Verificar cálculo de IMC
        assert "imc" in data
        expected_imc = 75.5 / ((170 / 100) ** 2)
        assert abs(data["imc"] - expected_imc) < 0.01
        
        # Verificar clasificación de IMC
        assert "imc_clasificacion" in data
        assert data["imc_clasificacion"] in ["Bajo peso", "Normal", "Sobrepeso", "Obesidad"]
        
        # Verificar presión arterial formateada
        assert "presion_arterial" in data
        assert data["presion_arterial"] == "120/80"
        
        # Verificar timestamp
        assert "fecha_medicion" in data

    async def test_create_signos_vitales_minimal_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with minimal data
        
        Expected behavior:
        - Status code: 201 Created
        - All fields are optional
        """
        minimal_data = {
            "peso_kg": 70.0,
            "talla_cm": 165
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=minimal_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # IMC should be calculated
        assert "imc" in data
        assert "imc_clasificacion" in data

    async def test_create_signos_vitales_only_pressure(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating only blood pressure measurements
        
        Expected behavior:
        - Status code: 201 Created
        - No IMC calculation without weight and height
        """
        pressure_only = {
            "presion_sistolica": 120,
            "presion_diastolica": 80,
            "frecuencia_cardiaca": 72
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=pressure_only,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["presion_arterial"] == "120/80"
        assert data["frecuencia_cardiaca"] == 72

    async def test_create_signos_vitales_imc_bajo_peso(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test IMC calculation for underweight
        
        Expected behavior:
        - IMC < 18.5 classified as "Bajo peso"
        """
        data = {
            "peso_kg": 50.0,
            "talla_cm": 170
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        
        # IMC = 50 / (1.7^2) = 17.3
        assert result["imc_clasificacion"] == "Bajo peso"

    async def test_create_signos_vitales_imc_normal(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test IMC calculation for normal weight
        
        Expected behavior:
        - 18.5 <= IMC < 25 classified as "Normal"
        """
        data = {
            "peso_kg": 68.0,
            "talla_cm": 170
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        
        # IMC = 68 / (1.7^2) = 23.5
        assert result["imc_clasificacion"] == "Normal"

    async def test_create_signos_vitales_imc_sobrepeso(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test IMC calculation for overweight
        
        Expected behavior:
        - 25 <= IMC < 30 classified as "Sobrepeso"
        """
        data = {
            "peso_kg": 75.0,
            "talla_cm": 170
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        
        # IMC = 75 / (1.7^2) = 25.95
        assert result["imc_clasificacion"] == "Sobrepeso"

    async def test_create_signos_vitales_imc_obesidad(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test IMC calculation for obesity
        
        Expected behavior:
        - IMC >= 30 classified as "Obesidad"
        """
        data = {
            "peso_kg": 95.0,
            "talla_cm": 170
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        
        # IMC = 95 / (1.7^2) = 32.87
        assert result["imc_clasificacion"] == "Obesidad"

    async def test_create_signos_vitales_invalid_peso(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid weight
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "peso_kg": 0.05,  # Too low
            "talla_cm": 170
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_invalid_talla(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid height
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "peso_kg": 70,
            "talla_cm": 300  # Too high
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_invalid_presion(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid blood pressure
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "presion_sistolica": 300,  # Too high
            "presion_diastolica": 80
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_invalid_frecuencia_cardiaca(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid heart rate
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "frecuencia_cardiaca": 250  # Too high
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_invalid_temperatura(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid temperature
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "temperatura_celsius": 45.0  # Too high
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_invalid_saturacion(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid oxygen saturation
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "saturacion_oxigeno": 65  # Too low
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_invalid_glucosa(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating vital signs with invalid glucose level
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "glucosa_capilar": 650  # Too high
        }
        
        response = await async_client.post(
            "/citas/1/signos-vitales",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_signos_vitales_cita_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_signos_vitales_data: dict
    ):
        """
        Test creating vital signs for non-existent appointment
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.post(
            "/citas/99999/signos-vitales",
            json=sample_signos_vitales_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.tratamientos
@pytest.mark.api
class TestDiagnosticos:
    """Tests for /citas/{id}/diagnosticos endpoints"""

    async def test_create_diagnostico_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_diagnostico_data: dict
    ):
        """
        Test successful diagnosis creation
        
        Expected behavior:
        - Status code: 201 Created
        - Returns diagnosis with CIE-10 description
        - Includes diagnosticado_por information
        """
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=sample_diagnostico_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verificar campos básicos
        assert "id" in data
        assert data["id_cita"] == 1
        assert data["tipo"] == sample_diagnostico_data["tipo"]
        assert data["descripcion"] == sample_diagnostico_data["descripcion"]
        assert data["codigo_cie10"] == sample_diagnostico_data["codigo_cie10"]
        
        # Verificar descripción de CIE-10
        assert "codigo_cie10_descripcion" in data
        assert data["codigo_cie10_descripcion"] is not None
        
        # Verificar información del profesional
        assert "diagnosticado_por" in data
        assert "id" in data["diagnosticado_por"]
        assert "nombre" in data["diagnosticado_por"]
        
        # Verificar timestamp
        assert "fecha_diagnostico" in data

    async def test_create_diagnostico_presuntivo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating presumptive diagnosis
        
        Expected behavior:
        - Status code: 201 Created
        - Tipo is "Presuntivo"
        """
        data = {
            "tipo": "Presuntivo",
            "descripcion": "Posible fascitis plantar",
            "notas": "Requiere estudios complementarios"
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["tipo"] == "Presuntivo"

    async def test_create_diagnostico_definitivo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating definitive diagnosis
        
        Expected behavior:
        - Status code: 201 Created
        - Tipo is "Definitivo"
        """
        data = {
            "tipo": "Definitivo",
            "descripcion": "Fascitis plantar bilateral",
            "codigo_cie10": "M72.2"
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["tipo"] == "Definitivo"

    async def test_create_diagnostico_diferencial(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating differential diagnosis
        
        Expected behavior:
        - Status code: 201 Created
        - Tipo is "Diferencial"
        """
        data = {
            "tipo": "Diferencial",
            "descripcion": "Espolón calcáneo vs. Fascitis plantar",
            "notas": "Requiere radiografía para confirmar"
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["tipo"] == "Diferencial"

    async def test_create_diagnostico_without_cie10(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating diagnosis without CIE-10 code
        
        Expected behavior:
        - Status code: 201 Created
        - CIE-10 code is optional
        """
        data = {
            "tipo": "Presuntivo",
            "descripcion": "Dolor en pie derecho, causa por determinar"
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201

    async def test_create_diagnostico_invalid_tipo(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating diagnosis with invalid tipo
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "tipo": "TipoInvalido",
            "descripcion": "Test diagnosis"
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_diagnostico_missing_descripcion(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating diagnosis without description
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "tipo": "Definitivo",
            "codigo_cie10": "M72.2"
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_diagnostico_descripcion_too_long(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating diagnosis with description exceeding limit
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "tipo": "Definitivo",
            "descripcion": "x" * 501  # More than 500 characters
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_diagnostico_invalid_cie10_format(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating diagnosis with invalid CIE-10 format
        
        Expected behavior:
        - Status code: 422 Validation Error
        """
        invalid_data = {
            "tipo": "Definitivo",
            "descripcion": "Test diagnosis",
            "codigo_cie10": "INVALID"  # Invalid format
        }
        
        response = await async_client.post(
            "/citas/1/diagnosticos",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_diagnostico_valid_cie10_formats(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating diagnosis with various valid CIE-10 formats
        
        Expected behavior:
        - Status code: 201 Created for all valid formats
        """
        valid_codes = ["M72.2", "A00.1", "B15", "C50.9"]
        
        for code in valid_codes:
            data = {
                "tipo": "Definitivo",
                "descripcion": f"Diagnosis with code {code}",
                "codigo_cie10": code
            }
            
            response = await async_client.post(
                "/citas/1/diagnosticos",
                json=data,
                headers=auth_headers
            )
            
            assert response.status_code == 201
            result = response.json()
            assert result["codigo_cie10"] == code

    async def test_create_diagnostico_cita_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_diagnostico_data: dict
    ):
        """
        Test creating diagnosis for non-existent appointment
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.post(
            "/citas/99999/diagnosticos",
            json=sample_diagnostico_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_get_diagnosticos_list(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test retrieving list of diagnoses for appointment
        
        Expected behavior:
        - Status code: 200 OK
        - Returns list of diagnoses
        """
        response = await async_client.get(
            "/citas/1/diagnosticos",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_get_diagnosticos_cita_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test retrieving diagnoses for non-existent appointment
        
        Expected behavior:
        - Status code: 404 Not Found
        """
        response = await async_client.get(
            "/citas/99999/diagnosticos",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.tratamientos
@pytest.mark.integration
class TestTratamientosIntegration:
    """Integration tests for treatment workflows"""

    async def test_complete_treatment_workflow(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_signos_vitales_data: dict,
        sample_diagnostico_data: dict
    ):
        """
        Test complete treatment workflow: vital signs then diagnosis
        
        Expected behavior:
        - All operations succeed in sequence
        - Data is properly linked to appointment
        """
        # 1. Create vital signs
        signos_response = await async_client.post(
            "/citas/1/signos-vitales",
            json=sample_signos_vitales_data,
            headers=auth_headers
        )
        assert signos_response.status_code == 201
        signos_id = signos_response.json()["id"]
        
        # 2. Create diagnosis
        diagnostico_response = await async_client.post(
            "/citas/1/diagnosticos",
            json=sample_diagnostico_data,
            headers=auth_headers
        )
        assert diagnostico_response.status_code == 201
        diagnostico_id = diagnostico_response.json()["id"]
        
        # 3. Verify both are linked to same appointment
        assert signos_response.json()["id_cita"] == 1
        assert diagnostico_response.json()["id_cita"] == 1

    async def test_multiple_diagnosticos_same_cita(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """
        Test creating multiple diagnoses for same appointment
        
        Expected behavior:
        - All diagnoses are created successfully
        - Can create different types of diagnoses
        """
        diagnoses = [
            {
                "tipo": "Presuntivo",
                "descripcion": "Primera impresión diagnóstica"
            },
            {
                "tipo": "Definitivo",
                "descripcion": "Diagnóstico confirmado",
                "codigo_cie10": "M72.2"
            },
            {
                "tipo": "Diferencial",
                "descripcion": "Diagnóstico alternativo a considerar"
            }
        ]
        
        created_ids = []
        for diagnosis in diagnoses:
            response = await async_client.post(
                "/citas/1/diagnosticos",
                json=diagnosis,
                headers=auth_headers
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # Verify all were created with different IDs
        assert len(created_ids) == len(set(created_ids))
        
        # Verify we can retrieve all
        list_response = await async_client.get(
            "/citas/1/diagnosticos",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        assert len(list_response.json()["items"]) >= 3
