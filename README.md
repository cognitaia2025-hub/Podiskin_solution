# 🦶 Podoskin Solution

> **⚠️ NOTA IMPORTANTE - NO MOVER DEL ENCABEZADO**  
> Este proyecto utiliza datos de prueba (mock data) para desarrollo y testing.  
> Ver sección "Datos de Prueba" más abajo para detalles completos.  
> **Solicitado por el usuario:** Mantener esta nota siempre al inicio del README.

Sistema web full-stack con IA integrada para gestión clínica de podología.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Datos de Prueba (Mock Data)](#-datos-de-prueba-mock-data)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Rápida](#-instalación-rápida)
- [Uso Básico](#-uso-básico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Documentación Adicional](#-documentación-adicional)
- [Testing](#-testing)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🎯 Descripción del Proyecto

Podoskin Solution es una plataforma integral para clínicas de podología que combina:

- **Backend FastAPI**: API REST con autenticación JWT y RBAC
- **Frontend React**: Interfaz moderna con TypeScript y Tailwind CSS
- **IA Integrada**: Agentes LangGraph para automatización y asistencia
- **Base de Datos PostgreSQL**: Con pgvector para búsquedas semánticas
- **WhatsApp Integration**: Bot de atención 24/7

### Características Principales

✅ Gestión de pacientes y expedientes médicos  
✅ Sistema de citas con recordatorios automáticos  
✅ Gestión de tratamientos y planes de tratamiento  
✅ Autenticación JWT con roles (Admin, Podólogo, Recepcionista)  
✅ Asistente de voz con Gemini Live  
✅ Bot de WhatsApp con escalamiento inteligente  
✅ Reportes y análisis clínicos/financieros  

---

## 🧪 Datos de Prueba (Mock Data)

> **⚠️ IMPORTANTE:** Los siguientes datos son SOLO para desarrollo y testing.  
> **NO usar en producción.** Cambiar todas las credenciales antes de desplegar.

### Credenciales de Prueba

#### Usuario de Prueba Principal
```
Username: dr.santiago
Password: password123
Email: santiago@podoskin.com
Rol: Podologo
Nombre: Dr. Santiago Ornelas
```

Para crear el usuario de prueba:
```bash
cd backend
python create_test_user.py
```

### Pacientes de Prueba

Los siguientes pacientes ficticios están disponibles en modo demo:

| ID | Nombre | Teléfono | Email |
|----|--------|----------|-------|
| 1 | María Fernández | 686-123-4567 | maria.f@email.com |
| 2 | Juan Ramírez | 686-234-5678 | juan.r@email.com |
| 3 | Sofía Gómez | 686-345-6789 | sofia.g@email.com |
| 4 | Pedro Díaz | 686-456-7890 | pedro.d@email.com |

**Ubicación del código:** `backend/agents/sub_agent_operator/utils/mock_data.py`

### Configuración de Prueba

```env
# .env de ejemplo (NO usar en producción)
JWT_SECRET_KEY=tu-clave-secreta-cambiar-en-produccion
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/podoskin_db
```

**⚠️ RECORDATORIO:** Generar una clave JWT secreta segura para producción:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE PRESENTACIÓN                        │
│  React 18.3 + TypeScript + Vite + Tailwind CSS              │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE APLICACIÓN                          │
│  FastAPI (Python 3.11+)                                      │
│  - Endpoints REST con JWT Auth                               │
│  - Middleware RBAC                                           │
│  - Validación Pydantic                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Agentes  │   │ WhatsApp │   │ Gemini   │
   │ LangGraph│   │ Bridge   │   │ Live     │
   └─────┬────┘   └─────┬────┘   └────┬─────┘
         │              │              │
         └──────────────┴──────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              CAPA DE DATOS                                   │
│  PostgreSQL 16 + pgvector                                    │
└─────────────────────────────────────────────────────────────┘
```

### Tecnologías Clave

- **Backend:** FastAPI, Python 3.11+, Pydantic
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Base de Datos:** PostgreSQL 16 con pgvector
- **IA:** LangGraph, Claude API, Gemini API
- **Autenticación:** JWT (JSON Web Tokens) con bcrypt
- **Mensajería:** WhatsApp Web.js (Node.js bridge)

---

## 📦 Requisitos Previos

### Software Requerido

- **Python 3.11+**
- **Node.js 18+** (para frontend y WhatsApp bridge)
- **PostgreSQL 16+** (con extensión pgvector)
- **Git**

### Opcional

- **Docker & Docker Compose** (para despliegue containerizado)
- **Redis** (para rate limiting distribuido - recomendado en producción)

---

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio

```bash
git clone https://github.com/cognitaia2025-hub/Podiskin_solution.git
cd Podiskin_solution
```

### 2. Configurar Backend

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Crear usuario de prueba
python create_test_user.py

# Iniciar servidor
python main.py
```

El servidor estará disponible en: http://localhost:8000

### 3. Configurar Frontend (Opcional)

```bash
cd Frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: http://localhost:5173

### 4. Verificar Instalación

```bash
# Test de login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr.santiago","password":"password123"}'
```

Si recibes un token JWT, ¡todo está funcionando! ✅

---

## 💻 Uso Básico

### Autenticación

```bash
# Login y obtener token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr.santiago","password":"password123"}' \
  | jq -r '.access_token')

# Usar el token en requests
curl -X GET http://localhost:8000/protected \
  -H "Authorization: Bearer $TOKEN"
```

### Documentación Interactiva API

Abrir en navegador: http://localhost:8000/docs

Aquí encontrarás:
- Todos los endpoints disponibles
- Ejemplos de request/response
- Posibilidad de probar endpoints directamente

### Proteger un Endpoint (Ejemplo de Código)

```python
from fastapi import APIRouter, Depends
from auth import get_current_user, User, require_role

router = APIRouter()

# Endpoint protegido (requiere autenticación)
@router.get("/mi-endpoint")
async def mi_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hola {current_user.nombre_completo}"}

# Endpoint con rol específico (solo Admin)
@router.delete("/usuarios/{id}")
@require_role(["Admin"])
async def eliminar_usuario(
    id: int,
    current_user: User = Depends(get_current_user)
):
    return {"status": "deleted"}
```

---

## 📁 Estructura del Proyecto

```
Podiskin_solution/
├── backend/                      # Backend FastAPI
│   ├── auth/                     # Módulo de autenticación
│   │   ├── router.py            # Endpoints REST
│   │   ├── middleware.py        # Middleware JWT
│   │   ├── authorization.py     # RBAC
│   │   ├── models.py            # Modelos Pydantic
│   │   ├── jwt_handler.py       # Manejo de JWT
│   │   └── database.py          # Acceso a BD
│   ├── agents/                  # Agentes de IA
│   │   ├── sub_agent_operator/  # Agente operador
│   │   └── sub_agent_whatsApp/  # Agente WhatsApp
│   ├── main.py                  # Entry point
│   ├── requirements.txt         # Dependencias Python
│   └── create_test_user.py      # Script de usuario de prueba
├── Frontend/                     # Frontend React
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── data/                         # Scripts SQL y datos
│   └── README.md
├── gemini-live-voice-controller/ # Controlador de voz
├── whatsapp-web-js/             # Bridge WhatsApp
├── .gitignore
└── README.md                     # Este archivo
```

---

## 📚 Documentación Adicional

### Documentación Técnica

- **[FSD_Podoskin_Solution.md](FSD_Podoskin_Solution.md)** - Especificación funcional detallada
- **[SRS_Podoskin_Solution.md](SRS_Podoskin_Solution.md)** - Especificación de requisitos de software
- **[PRD_Podoskin_Solution.md](PRD_Podoskin_Solution.md)** - Documento de requisitos de producto
- **[BRD_Podoskin_Solution.md](BRD_Podoskin_Solution.md)** - Documento de requisitos de negocio

### Documentación de Agentes

- **[SUBAGENTES_CONFIG.md](SUBAGENTES_CONFIG.md)** - Configuración de agentes de desarrollo
- **[recomendacionesLangGraph.md](recomendacionesLangGraph.md)** - Patrones LangGraph

### Documentación de Módulos

- **[backend/auth/README.md](backend/auth/README.md)** - Guía completa del módulo de autenticación
- **[backend/QUICK_START.md](backend/QUICK_START.md)** - Guía de inicio rápido
- **[backend/ENDPOINTS.md](backend/ENDPOINTS.md)** - Lista de endpoints REST

---

## 🧪 Testing

### Tests Backend

```bash
cd backend

# Test de autenticación
python test_auth.py

# Test de agente operador
python test_operations_agent.py
```

### Tests Manuales con curl

```bash
# Health check
curl http://localhost:8000/auth/health

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr.santiago","password":"password123"}'
```

---

## 🛠️ Troubleshooting

### Error: "Failed to initialize auth database pool"

**Solución:** Verificar que PostgreSQL esté corriendo y que DATABASE_URL sea correcto.

```bash
# Verificar conexión
psql postgresql://postgres:password@localhost:5432/podoskin_db -c "SELECT 1"
```

### Error: "Token inválido o expirado"

**Solución:** El token expiró (1 hora de vida). Hacer login nuevamente para obtener un nuevo token.

### Error: "Usuario inactivo"

**Solución:** El usuario existe pero está marcado como inactivo en la BD.

```sql
-- Activar usuario
UPDATE usuarios SET activo = true WHERE nombre_usuario = 'dr.santiago';
```

### Error: Módulo no encontrado al importar `auth`

**Solución:** Asegúrate de estar en el directorio correcto y que las dependencias estén instaladas:

```bash
cd backend
pip install -r requirements.txt
```

---

## 🤝 Contribuir

Este proyecto sigue un flujo de desarrollo estructurado:

1. **Fork** el repositorio
2. Crear una **rama de feature** (`git checkout -b feature/AmazingFeature`)
3. **Commit** los cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un **Pull Request**

### Convenciones de Código

- **Python:** Seguir PEP 8
- **TypeScript/React:** Usar ESLint y Prettier
- **Commits:** Mensajes claros y descriptivos
- **Documentación:** Actualizar README y docs cuando sea necesario

---

## 📄 Licencia

Este proyecto es privado y confidencial. Todos los derechos reservados.

---

## 👥 Equipo

**Desarrollo:** Equipo Técnico Podoskin  
**Fecha de Inicio:** Diciembre 2024  
**Versión:** 1.0.0

---

## 📞 Contacto y Soporte

Para preguntas o soporte, contactar al equipo de desarrollo.

---

## 🔄 Estado del Proyecto

### Completado ✅

- ✅ Sistema de autenticación JWT con RBAC
- ✅ Módulo de base de datos con PostgreSQL
- ✅ Endpoints REST de usuarios y autenticación
- ✅ Middleware de autorización
- ✅ Tests básicos de autenticación

### En Progreso 🔨

- 🔨 Endpoints CRUD de pacientes
- 🔨 Sistema de citas
- 🔨 Agentes de IA (WhatsApp, Gemini Live)
- 🔨 Frontend React

### Pendiente 📋

- 📋 Gestión de tratamientos
- 📋 Reportes y análisis
- 📋 Integración completa de WhatsApp
- 📋 Dashboard administrativo
- 📋 Tests end-to-end

---

## ⚡ Quick Links

- 🌐 **API Docs:** http://localhost:8000/docs
- 📖 **Backend README:** [backend/auth/README.md](backend/auth/README.md)
- 🚀 **Quick Start:** [backend/QUICK_START.md](backend/QUICK_START.md)
- 📊 **Endpoints:** [backend/ENDPOINTS.md](backend/ENDPOINTS.md)

---

**Última actualización:** Diciembre 2024  
**Versión del documento:** 1.0
