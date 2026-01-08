---
description: Reumen deumen de Icfórmdción del Repositorio
alwaysApply: true
---

# Información de Información de Podoskin

## Resumen del Resumen del Reiokin Solution es un sistema integral de gestión clínica para podología que incluye capacidades de IA integradas (Maya), gestión de expedientes médicos, agenda de citas y control de inventarios. Utiliza una arquitectura de microservicios con un y un fronten FastAPenI y un frontend en React/Vite.

## Estructura del Repositorio
- **backend/**: Aplicación FastAPI que contiene la lógica central, agentes de IA (LangGraph) e integraciones de base de datos.
- **Frontend/**: Aplicación principal en React (Tachyon Aurora) construida con Vite y Tailwind CSS.
- **gemini-live-voice-controller/**: Aplicación independiente en React para la integración de vz eón vivo cenvoz en vivo con Google Gemini.
- **whatsapp-web-js/**: Puente en Node.js para la WhatsApp (Maya Bridge).
- **data/**: Scriptini dcialicación ceóbade base dee de doaay y migrccioenes (PostgreSQL).
- **tests/**: Suite de pruebas del backend utilizando Pytest.
- **docs/**: Dccómeación del proyecto e informes.

## Proyectoos

### Backend (FastAPI)
**Archivo de Archivo de Configuración**: `backend/requirements.txt`, `backend/.env.example`

#### Lenguaje y Entorno de Ejecución
- **Lenguaje**: Python
- **Versión**: 3.10+ (sugerido por la sintaxis moderna)
- **a de ConstrucciónSistema de Construcción**: Pip / Virtualenv
- **storGede Ptoquetde Psaquetes**: pip

#### Dependencias
**Dependencias Principalas Principales**:
- `fastapi`, `uvicorn`, `pydantic` (Framework Web Web)
- `langchain`, `langgraph`, `langgraph-checkpoint-postgres` (AIA/Agentees)
- `psycopg[binary]`, `asyncpg`, `pgvector` (Base de Base de o
- `pthon-jose`, `passlib`, `bcrypt` (Autenticccóón)
- `pandas`, `scikit-learn`, `matplotlib` (Analítica)

#### Construcción ecc ónsealaóción
```bash
cd backend
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python main.py
```

#### Pruebas- **Framework**: Pytest
- **Ubicación de Pruebas**: `tests/`
- **Convención de Nombres**: `test_*.py`
- **Configuración**: `pytest.ini`
- **Coo de Ejecuciónmando de Ejecución**:
```bash
pytest
```

---

### Frontend (Tachyon Aurora)
**Archivo de Archivo de Configuración**: `Frontend/package.json`

#### Lenguaje y Entorno de Ejecución
- **Lenguaje**: TypeScript / JavaScript
- **Versión**: Node.js 18+
- **SsteeConrucción de Construcción**: Vite
- **Gestor de Gequ Paqtess**: npm / package-lock.json

#### Dependencias Principalas
**Dependencias Principales**:
- `react` (18.3.1), `react-dom`
- `react-router-dom`, `react-hook-form`
- `axios` (Cliente API)
- `tailwindcss`, `lucide-react`, `recharts` (UI/Gráficos)
- `zod` (Validación)

#### Construcción ecc ónsealaóción
```bash
cd Frontend
npm install
npm run dev
```

---

### WhatsApp Maya Bridge
**Archivo de Configuración**: `whatsapp-web-js/package.json`

#### Lenguaje y Entorno de Ejecución
- **Lenguaje**: JavaScript (Node.js)
- **Versión**: >=18.0.0
- **Gestor de Gequ Paqtess**: npm

#### Dependencias
- `whatsapp-web.js`, `qrcode-terminal`, `axios`

#### ConConstruccióccnón enstalaic
ó``bash
cd whatsapp-web-js
npm install
npm start
```

---

### Gemini Live Voice Controller
**Archivo de Configuración**: `gemini-live-voice-controller/package.json`

#### Lenguaje y Entorno de Ejecución
- **Lenguaje**: TypeScript (React 19)
- **Sistema de Construcción**: Vite
- **Gestor de Paquetes**: npm

#### Dependencias
- `react` (19.2.0), `@google/genai`

---

## Configuración de Docker

**Dockerfile**: No presente (pueden faltar Dockerfiles específicos, pero el Compose estátá presentee).
**Configuración**: `docker-compose.yml` orquestra:
- **postgres:14**: Base de datos principal en el puerto 5432.
- **redis:7-alpine**: Caché/Cola en el puerto 6379.
- Inicialización automática de SQL mediante el mapeo del volumen `./data` a `/docker-entrypoint-initdb.d`.

## Archivos y Recursos Principales
- **backend/main.py**: Punto de entrada principal de la API.
- **Frontend/src/main.tsx**: Punto de entrada del Frontend.
- **data/00_inicializacion.sql**: Esquema inicial de la base de datos.
- a**lad/.env.example**: Plantilla de entorno para la configuración del backend del backend.
