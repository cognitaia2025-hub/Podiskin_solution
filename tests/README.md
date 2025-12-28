# Podoskin Solution - Backend Tests

Suite completa de tests para el backend de Podoskin Solution, implementada según especificaciones del SRS (Sección 9) y FSD.

## 📋 Contenido

### Test Files

- **`test_auth.py`** - Tests de autenticación y autorización
  - Login con credenciales válidas/inválidas
  - Validación de tokens JWT
  - Control de acceso basado en roles
  - Seguridad de contraseñas

- **`test_pacientes.py`** - Tests del módulo de pacientes
  - CRUD completo de pacientes
  - Paginación y búsqueda
  - Gestión de alergias
  - Validaciones de datos

- **`test_citas.py`** - Tests del sistema de citas
  - Verificación de disponibilidad
  - Creación y gestión de citas
  - Detección de conflictos de horario
  - Programación de recordatorios

- **`test_tratamientos.py`** - Tests de tratamientos médicos
  - Registro de signos vitales
  - Cálculo automático de IMC
  - Gestión de diagnósticos
  - Validación de códigos CIE-10

### Configuration Files

- **`conftest.py`** - Fixtures y configuración compartida
- **`pytest.ini`** - Configuración de pytest

## 🚀 Instalación

### Prerrequisitos

```bash
Python 3.10+
PostgreSQL 16+ con extensión pgvector
```

### Instalar Dependencias

```bash
cd /home/runner/work/Podiskin_solution/Podiskin_solution
pip install -r backend/requirements.txt
```

Las dependencias de testing incluyen:
- `pytest>=7.4.0`
- `pytest-asyncio>=0.21.0`
- `pytest-cov>=4.1.0`
- `pytest-mock>=3.12.0`
- `pytest-httpx>=0.21.0`

## 🧪 Ejecutar Tests

### Todos los Tests

```bash
# Desde el directorio raíz del proyecto
pytest

# Con output verbose
pytest -v

# Con output detallado de cada test
pytest -vv
```

### Tests por Módulo

```bash
# Solo tests de autenticación
pytest tests/test_auth.py

# Solo tests de pacientes
pytest tests/test_pacientes.py

# Solo tests de citas
pytest tests/test_citas.py

# Solo tests de tratamientos
pytest tests/test_tratamientos.py
```

### Tests por Marca (Marker)

```bash
# Solo tests unitarios
pytest -m unit

# Solo tests de integración
pytest -m integration

# Solo tests de API
pytest -m api

# Solo tests específicos de un módulo
pytest -m auth
pytest -m pacientes
pytest -m citas
pytest -m tratamientos
```

### Tests Específicos

```bash
# Ejecutar una clase de tests
pytest tests/test_auth.py::TestAuthLogin

# Ejecutar un test específico
pytest tests/test_auth.py::TestAuthLogin::test_login_successful

# Ejecutar tests que coincidan con un patrón
pytest -k "login"
pytest -k "create_paciente"
```

## 📊 Cobertura de Código

### Generar Reporte de Cobertura

```bash
# Ejecutar tests con cobertura
pytest --cov=backend --cov-report=html --cov-report=term

# Ver reporte en terminal
pytest --cov=backend --cov-report=term-missing

# Generar reporte HTML (se guarda en htmlcov/)
pytest --cov=backend --cov-report=html
```

### Ver Reporte HTML

```bash
# El reporte se genera en htmlcov/index.html
# Abrirlo en el navegador para ver detalles de cobertura línea por línea
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Reporte XML (para CI/CD)

```bash
pytest --cov=backend --cov-report=xml
# Genera coverage.xml para integración con herramientas de CI/CD
```

## 🏗️ Estructura de Tests

### Organización

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── test_auth.py            # Tests de autenticación (300+ líneas)
├── test_pacientes.py       # Tests de pacientes (600+ líneas)
├── test_citas.py           # Tests de citas (700+ líneas)
└── test_tratamientos.py    # Tests de tratamientos (700+ líneas)
```

### Fixtures Disponibles

#### Configuración
- `test_config` - Configuración de prueba
- `async_client` - Cliente HTTP asíncrono

#### Autenticación
- `test_token` - Token JWT válido (podologo)
- `test_admin_token` - Token JWT de administrador
- `expired_token` - Token JWT expirado
- `auth_headers` - Headers con autenticación

#### Datos de Prueba
- `sample_paciente_data` - Datos de paciente de ejemplo
- `sample_cita_data` - Datos de cita de ejemplo
- `sample_signos_vitales_data` - Datos de signos vitales
- `sample_diagnostico_data` - Datos de diagnóstico
- `sample_alergia_data` - Datos de alergia

## 📝 Escribir Nuevos Tests

### Ejemplo de Test Básico

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
@pytest.mark.api
async def test_mi_endpoint(async_client: AsyncClient, auth_headers: dict):
    """
    Test description
    
    Expected behavior:
    - Status code: 200
    - Returns expected data
    """
    response = await async_client.get(
        "/mi-endpoint",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "campo_esperado" in data
```

### Ejemplo de Test con Fixture Personalizada

```python
@pytest.fixture
def mi_dato_de_prueba():
    return {
        "campo1": "valor1",
        "campo2": 123
    }

@pytest.mark.asyncio
async def test_con_fixture(async_client: AsyncClient, mi_dato_de_prueba: dict):
    response = await async_client.post(
        "/endpoint",
        json=mi_dato_de_prueba
    )
    assert response.status_code == 201
```

## 🔧 Configuración Avanzada

### Variables de Entorno para Tests

```bash
# .env.test
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db
TEST_SECRET_KEY=test_secret_key_for_testing_only
TEST_ALGORITHM=HS256
```

### Configurar Base de Datos de Test

```bash
# Crear base de datos de test
createdb podoskin_test

# Ejecutar migraciones
# (cuando estén disponibles)
alembic upgrade head

# Ejecutar tests con BD de test
DATABASE_URL=postgresql://localhost/podoskin_test pytest
```

## 📈 Métricas y Objetivos

### Cobertura de Código
- **Objetivo**: ≥ 80% de cobertura
- **Mínimo aceptable**: 70%

### Categorías de Tests

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| Unitarios | 100+ | Tests de funciones individuales |
| Integración | 20+ | Tests de flujos completos |
| API | 120+ | Tests de endpoints REST |

### Áreas Cubiertas

✅ **Autenticación**
- Login y validación de credenciales
- Gestión de tokens JWT
- Control de acceso basado en roles
- Seguridad de contraseñas

✅ **Pacientes**
- CRUD completo
- Paginación y búsqueda
- Gestión de alergias
- Validaciones de datos personales

✅ **Citas**
- Verificación de disponibilidad
- Creación con validaciones
- Detección de conflictos
- Gestión de estados
- Programación de recordatorios

✅ **Tratamientos**
- Registro de signos vitales
- Cálculo automático de IMC (4 clasificaciones)
- Gestión de diagnósticos
- Validación de códigos CIE-10

## 🐛 Debugging

### Ejecutar con Debugging

```bash
# Ejecutar con output de print()
pytest -s

# Ejecutar y detener en el primer error
pytest -x

# Ejecutar con PDB en el primer error
pytest --pdb

# Ver logs completos
pytest --log-cli-level=DEBUG
```

### Debugging de Tests Específicos

```bash
# Ver el motivo de tests que fallan
pytest --tb=short

# Ver traceback completo
pytest --tb=long

# Ver solo una línea por error
pytest --tb=line
```

## 🔄 Integración Continua (CI/CD)

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📚 Referencias

- **SRS**: `SRS_Podoskin_Solution.md` - Sección 9: Testing
- **FSD**: `FSD_Podoskin_Solution.md` - Secciones 2.1-2.6: API Contracts
- **PRD**: `PRD_Podoskin_Solution.md` - Requisitos Funcionales
- **OpenAPI**: `docs/api.yaml` - Especificación completa de la API

## 💡 Tips

1. **Usar markers**: Organiza tests con `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
2. **Fixtures reutilizables**: Define fixtures en `conftest.py` para compartir entre tests
3. **Datos realistas**: Usa datos de ejemplo que reflejen casos de uso reales
4. **Tests independientes**: Cada test debe poder ejecutarse independientemente
5. **Nombres descriptivos**: Nombres de tests deben describir qué se está probando
6. **Documentación**: Incluye docstrings explicando el comportamiento esperado

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Asegurar que el directorio está en PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Error: "Database connection failed"
```bash
# Verificar que PostgreSQL está corriendo
pg_isready

# Verificar credenciales en .env
cat .env | grep DATABASE_URL
```

### Error: "asyncio event loop"
```bash
# Verificar configuración en pytest.ini
# Debe incluir: asyncio_mode = auto
```

## 📞 Soporte

Para preguntas o problemas:
- Revisar documentación en `docs/`
- Consultar issues en GitHub
- Contactar al equipo de desarrollo

---

**Última actualización**: Diciembre 2024
**Versión**: 1.0.0
