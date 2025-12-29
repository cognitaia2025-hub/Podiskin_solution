"""
Pytest configuration and fixtures for Podoskin Solution tests
"""
import pytest
from httpx import AsyncClient
from typing import AsyncGenerator, Dict
from datetime import datetime, timedelta
import jwt


# Test configuration
TEST_BASE_URL = "http://test"
TEST_SECRET_KEY = "test_secret_key_for_testing_only"
TEST_ALGORITHM = "HS256"


@pytest.fixture
def test_config() -> Dict:
    """Test configuration fixture"""
    return {
        "base_url": TEST_BASE_URL,
        "secret_key": TEST_SECRET_KEY,
        "algorithm": TEST_ALGORITHM,
    }


@pytest.fixture
def test_token() -> str:
    """Generate test JWT token"""
    payload = {
        "sub": "dr.santiago",
        "user_id": 1,
        "rol": "podologo",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)


@pytest.fixture
def test_admin_token() -> str:
    """Generate test admin JWT token"""
    payload = {
        "sub": "admin",
        "user_id": 999,
        "rol": "administrador",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)


@pytest.fixture
def expired_token() -> str:
    """Generate expired JWT token"""
    payload = {
        "sub": "test_user",
        "user_id": 1,
        "rol": "podologo",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)


@pytest.fixture
def auth_headers(test_token: str) -> Dict[str, str]:
    """Authentication headers with valid token"""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def sample_paciente_data() -> Dict:
    """Sample patient data for testing"""
    return {
        "primer_nombre": "Juan",
        "segundo_nombre": "Carlos",
        "primer_apellido": "Pérez",
        "segundo_apellido": "García",
        "fecha_nacimiento": "1990-05-15",
        "sexo": "M",
        "telefono_principal": "6861234567",
        "email": "juan.perez@email.com",
        "curp": "PEGC900515HDFRRN01",  # Updated to match Juan Carlos Pérez García
        "tipo_sangre": "O+",
        "estado_civil": "Soltero",
        "ocupacion": "Ingeniero",
        "activo": True
    }


@pytest.fixture
def sample_cita_data() -> Dict:
    """Sample appointment data for testing"""
    # Use dynamic date that's always 7 days in the future
    future_date = (datetime.now() + timedelta(days=7)).replace(hour=10, minute=0, second=0, microsecond=0)
    return {
        "id_paciente": 1,
        "id_podologo": 1,
        "fecha_hora_inicio": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "tipo_cita": "Consulta",
        "motivo_consulta": "Dolor en pie derecho",
        "notas_recepcion": "Primera vez"
    }


@pytest.fixture
def sample_signos_vitales_data() -> Dict:
    """Sample vital signs data for testing"""
    return {
        "peso_kg": 75.5,
        "talla_cm": 170,
        "presion_sistolica": 120,
        "presion_diastolica": 80,
        "frecuencia_cardiaca": 72,
        "frecuencia_respiratoria": 16,
        "temperatura_celsius": 36.5,
        "saturacion_oxigeno": 98,
        "glucosa_capilar": 95
    }


@pytest.fixture
def sample_diagnostico_data() -> Dict:
    """Sample diagnosis data for testing"""
    return {
        "tipo": "Definitivo",
        "descripcion": "Fascitis plantar bilateral",
        "codigo_cie10": "M72.2",
        "notas": "Tratamiento recomendado: fisioterapia y uso de plantillas"
    }


@pytest.fixture
def sample_alergia_data() -> Dict:
    """Sample allergy data for testing"""
    return {
        "tipo": "Medicamento",
        "nombre": "Penicilina",
        "reaccion": "Rash cutáneo",
        "severidad": "Moderada",
        "fecha_diagnostico": "2020-03-15",
        "activo": True
    }


# Mock app fixture - to be implemented when FastAPI app structure is available
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client for testing
    Note: This requires the actual FastAPI app to be implemented
    """
    # TODO: Import actual app when available
    # from app.main import app
    # async with AsyncClient(app=app, base_url=TEST_BASE_URL) as client:
    #     yield client
    
    # For now, create a basic client
    async with AsyncClient(base_url=TEST_BASE_URL) as client:
        yield client


# Database fixtures - to be implemented when DB structure is available
@pytest.fixture
async def db_session():
    """
    Database session fixture
    Note: This requires actual database connection to be implemented
    """
    # TODO: Implement database session
    # async with async_session_maker() as session:
    #     yield session
    #     await session.rollback()
    pass


@pytest.fixture
async def clean_database(db_session):
    """
    Clean test database before each test
    """
    # TODO: Implement database cleanup
    pass


@pytest.fixture
def test_patient_id() -> int:
    """Test patient ID fixture"""
    return 1


@pytest.fixture
def test_appointment_id() -> int:
    """Test appointment ID fixture"""
    return 1


@pytest.fixture
def sample_tratamiento_data() -> Dict:
    """Sample treatment data for testing"""
    return {
        "id_paciente": 1,
        "id_podologo": 1,
        "tipo_tratamiento": "Consulta general",
        "descripcion": "Tratamiento de fascitis plantar",
        "duracion_minutos": 45,
        "costo": 800.00,
        "notas": "Aplicar hielo después del tratamiento"
    }


@pytest.fixture
def sample_session_data() -> Dict:
    """Sample voice session data for testing"""
    return {
        "patientId": "1",
        "appointmentId": "1",
        "userId": "1"
    }


@pytest.fixture
def sample_tool_call_data() -> Dict:
    """Sample tool call data for testing"""
    return {
        "sessionId": "test-session-id",
        "toolName": "query_patient_data",
        "args": {
            "patient_id": "1",
            "field": "nombre"
        }
    }
