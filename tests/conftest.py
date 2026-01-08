import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Windows specific event loop fix for Psycopg3
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Mock user data (move to top so it's available for early patches)
MOCK_USER_DATA = {
    "id": 1,
    "nombre_usuario": "dr.santiago",
    "nombre_completo": "Dr. Santiago de la Cruz",
    "email": "santiago@example.com",
    "rol": "Podologo",
    "activo": True,
    "password_hash": "mocked_hash"
}

MOCK_ADMIN_DATA = {
    "id": 999,
    "nombre_usuario": "admin",
    "nombre_completo": "Administrador Sistema",
    "email": "admin@example.com",
    "rol": "Admin",
    "activo": True,
    "password_hash": "mocked_hash"
}

# Pre-patch database to avoid connection issues during import/lifespan
async def mocked_get_user_by_username(username):
    if username == "dr.santiago":
        return MOCK_USER_DATA
    if username == "admin":
        return MOCK_ADMIN_DATA
    return None

# Apply global patches BEFORE any backend imports
patcher_init_pool = patch("backend.auth.database.init_db_pool", return_value=None)
patcher_db_connect = patch("backend.db.database.connect", return_value=None)

# Patch get_user_by_username in multiple potential import paths
patcher_get_user = patch("backend.auth.database.get_user_by_username", side_effect=mocked_get_user_by_username)
patcher_get_user_alt = patch("auth.database.get_user_by_username", side_effect=mocked_get_user_by_username, create=True)
patcher_get_user_middleware = patch("backend.auth.middleware.get_user_by_username", side_effect=mocked_get_user_by_username)
patcher_get_user_middleware_alt = patch("auth.middleware.get_user_by_username", side_effect=mocked_get_user_by_username, create=True)
patcher_get_user_router = patch("backend.auth.router.get_user_by_username", side_effect=mocked_get_user_by_username)
patcher_get_user_router_alt = patch("auth.router.get_user_by_username", side_effect=mocked_get_user_by_username, create=True)

# Patch verify_password and crypt context
patcher_verify_pw = patch("backend.auth.jwt_handler.verify_password", return_value=True)
patcher_verify_pw_alt = patch("auth.jwt_handler.verify_password", return_value=True, create=True)
patcher_pwd_context = patch("backend.auth.jwt_handler.pwd_context")
patcher_pwd_context_alt = patch("auth.jwt_handler.pwd_context", create=True)

# Add mocks for psycopg2, psycopg (v3) and asyncpg to avoid real DB connections
mock_conn = MagicMock()
mock_cursor = MagicMock()
mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
mock_cursor.fetchone.return_value = None
mock_cursor.fetchall.return_value = []
mock_cursor.rowcount = 1

patcher_psycopg2 = patch("psycopg2.connect", return_value=mock_conn)

# Mock psycopg (v3)
from unittest.mock import AsyncMock, MagicMock
mock_async_conn = AsyncMock()
mock_async_cur = AsyncMock()

# Setup async context managers
mock_async_conn.cursor = MagicMock(return_value=mock_async_cur)
mock_async_conn.rollback = AsyncMock()
mock_async_conn.commit = AsyncMock()

mock_async_cur.execute = AsyncMock()
mock_async_cur.fetchone = AsyncMock(return_value=None)
mock_async_cur.fetchall = AsyncMock(return_value=[])

async def mocked_async_connect(*args, **kwargs):
    return mock_async_conn

patcher_psycopg3 = patch("psycopg.AsyncConnection.connect", side_effect=mocked_async_connect)

# Mock psycopg_pool
mock_pool_v3 = MagicMock()
async def mocked_pool_open(): pass
async def mocked_pool_getconn(): return mock_async_conn
async def mocked_pool_putconn(conn): pass
mock_pool_v3.open = mocked_pool_open
mock_pool_v3.getconn = mocked_pool_getconn
mock_pool_v3.putconn = mocked_pool_putconn
patcher_psycopg_pool = patch("psycopg_pool.AsyncConnectionPool", return_value=mock_pool_v3)

# Mock asyncpg
mock_pool = MagicMock()
mock_pool.acquire.return_value.__aenter__.return_value = MagicMock()
patcher_asyncpg = patch("asyncpg.create_pool", return_value=mock_pool)

patcher_init_pool.start()
patcher_db_connect.start()
patcher_get_user.start()
patcher_get_user_alt.start()
patcher_get_user_middleware.start()
patcher_get_user_middleware_alt.start()
patcher_get_user_router.start()
patcher_get_user_router_alt.start()
patcher_verify_pw.start()
patcher_verify_pw_alt.start()
mock_pwd_context = patcher_pwd_context.start()
mock_pwd_context.verify.return_value = True
mock_pwd_context_alt = patcher_pwd_context_alt.start()
if mock_pwd_context_alt:
    mock_pwd_context_alt.verify.return_value = True
patcher_psycopg2.start()
patcher_psycopg3.start()
patcher_psycopg_pool.start()
patcher_asyncpg.start()

# Test configuration
TEST_BASE_URL = "http://test"
TEST_SECRET_KEY = "your-secret-key-change-in-production-PLEASE"  # Match default in jwt_handler.py
TEST_ALGORITHM = "HS256"

# Set environment variables for testing before importing app
os.environ["JWT_SECRET_KEY"] = TEST_SECRET_KEY
os.environ["DB_HOST"] = "localhost"
os.environ["DB_NAME"] = "test_db"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

"""
Pytest configuration and fixtures for Podoskin Solution tests
"""
import pytest
from httpx import AsyncClient
from typing import AsyncGenerator, Dict
from datetime import datetime, timedelta
from jose import jwt


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
        "rol": "Podologo",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)


@pytest.fixture
def test_admin_token() -> str:
    """Generate test admin JWT token"""
    payload = {
        "sub": "admin",
        "user_id": 999,
        "rol": "Admin",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)


@pytest.fixture
def expired_token() -> str:
    """Generate expired JWT token"""
    payload = {
        "sub": "test_user",
        "user_id": 1,
        "rol": "Podologo",
        "exp": datetime.utcnow() - timedelta(hours=1),
        "iat": datetime.utcnow() - timedelta(hours=2)
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


from httpx import AsyncClient, ASGITransport
from backend.auth.models import User

# Mock user data
MOCK_USER_DATA = {
    "id": 1,
    "nombre_usuario": "dr.santiago",
    "nombre_completo": "Dr. Santiago de la Cruz",
    "email": "santiago@example.com",
    "rol": "Podologo",
    "activo": True
}

MOCK_ADMIN_DATA = {
    "id": 999,
    "nombre_usuario": "admin",
    "nombre_completo": "Administrador Sistema",
    "email": "admin@example.com",
    "rol": "Admin",
    "activo": True
}

@pytest.fixture
def mock_user():
    return User(**MOCK_USER_DATA)

@pytest.fixture
def mock_admin():
    return User(**MOCK_ADMIN_DATA)

# Mock app fixture
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client for testing with mocked authentication
    """
    from backend.main import app
    from backend.auth.middleware import get_current_user, security
    from backend.auth.models import User
    from fastapi import Depends, HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from typing import Optional
    
    # Mock user for dependency override
    async def mocked_get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        if not credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = credentials.credentials
        try:
            # Decode token to see which user it is
            payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
            username = payload.get("sub")
            if username == "admin":
                return User(**MOCK_ADMIN_DATA)
            return User(**MOCK_USER_DATA)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    # Apply override
    app.dependency_overrides[get_current_user] = mocked_get_current_user
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        
    # Clear overrides
    app.dependency_overrides = {}


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
