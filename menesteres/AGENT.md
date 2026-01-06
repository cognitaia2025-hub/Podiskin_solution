¡Excelente idea! Docker es **mucho más fácil** y rápido.  Aquí está el prompt actualizado:

---

## 🐳 **PROMPT 1 (VERSIÓN DOCKER): SETUP COMPLETO CON DOCKER**

```
@workspace Necesito configurar y ejecutar Podoskin Solution usando Docker para la base de datos.

## CONTEXTO
- Proyecto en: C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution
- Sistema operativo: Windows
- Shell: PowerShell
- Usaré Docker para PostgreSQL (más fácil que instalación nativa)

---

## PARTE 1: BASE DE DATOS CON DOCKER

### 2. CREAR ARCHIVO docker-compose.yml
Crear este archivo en la raíz del proyecto:  `C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution\docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres: 
    image: pgvector/pgvector:pg14
    container_name: podoskin_postgres
    environment:
      POSTGRES_DB: podoskin_db
      POSTGRES_USER: podoskin_user
      POSTGRES_PASSWORD: podoskin_password_123
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes: 
      - postgres_data:/var/lib/postgresql/data
      - ./data:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U podoskin_user -d podoskin_db"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data: 
```

### 3. PREPARAR SCRIPTS SQL

Los scripts en `data/` deben ejecutarse en orden. Renombrarlos para que Docker los ejecute automáticamente:

```powershell
# Ir a la carpeta data
cd data

# Renombrar archivos para que se ejecuten en orden
# Docker ejecuta archivos . sql en orden alfabético
# Ya están numerados (01_, 02_, etc.) así que están listos
```

### 4. LEVANTAR POSTGRESQL CON DOCKER

```powershell
# Volver a la raíz del proyecto
cd C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution

# Levantar PostgreSQL
docker-compose up -d

# Verificar que está corriendo
docker ps

# Ver logs (opcional)
docker-compose logs -f postgres
```

### 5. VERIFICAR CONEXIÓN A LA BASE DE DATOS

```powershell
# Conectar al contenedor de PostgreSQL
docker exec -it podoskin_postgres psql -U podoskin_user -d podoskin_db

# Dentro de psql, ejecutar:
\dt   # Ver tablas
\q    # Salir
```

---

## PARTE 2: BACKEND (Python + FastAPI)

### 6. INSTALAR DEPENDENCIAS PYTHON

```powershell
# Ir a la carpeta backend
cd backend

# Verificar Python
python --version  # Necesitas Python 3.11+

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
pip install -r . .\requirements-test.txt
```

### 7. CONFIGURAR VARIABLES DE ENTORNO

Crear archivo `backend/.env`:

```env
# Base de datos (conecta a Docker)
DATABASE_URL=postgresql://podoskin_user:podoskin_password_123@localhost: 5432/podoskin_db

# JWT
SECRET_KEY=mi_clave_super_secreta_de_desarrollo_12345678901234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# APIs (opcional, dejar vacío si no tienes)
OPENAI_API_KEY=
GOOGLE_API_KEY=
GEMINI_API_KEY=

# Entorno
ENVIRONMENT=development
DEBUG=True
```

### 8. EJECUTAR MIGRACIONES (Si no se ejecutaron automáticamente)

```powershell
# Desde la raíz del proyecto
cd ..

# Ejecutar scripts SQL manualmente si es necesario
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/01_schema.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/02_tablas_principales.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/03_tablas_secundarias.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/04_relaciones.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/05_indices.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/06_vistas.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/07_funciones.sql
docker exec -i podoskin_postgres psql -U podoskin_user -d podoskin_db < data/08_triggers.sql
```

### 9. CREAR USUARIO DE PRUEBA

```powershell
cd backend
python create_test_user.py
```

### 10. EJECUTAR SERVIDOR FASTAPI

```powershell
# Desde backend/ con venv activado
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 11. VERIFICAR BACKEND

Abrir en navegador:

- API Docs: <http://localhost:8000/docs>
- Health:  <http://localhost:8000/health>

---

## PARTE 3: FRONTEND (React + Vite)

### 12. INSTALAR DEPENDENCIAS FRONTEND

```powershell
# Abrir NUEVA terminal PowerShell
cd C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution\Frontend

# Verificar Node.js
node --version  # Necesitas Node 18+
npm --version

# Instalar dependencias
npm install
```

### 13. CONFIGURAR VARIABLES DE ENTORNO FRONTEND

Crear archivo `Frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
```

### 14. EJECUTAR FRONTEND

```powershell
npm run dev
```

### 15. VERIFICAR FRONTEND

Abrir en navegador:  <http://localhost:5173>

---

## COMANDOS ÚTILES DE DOCKER

### Ver estado de contenedores

```powershell
docker ps
```

### Ver logs de PostgreSQL

```powershell
docker-compose logs -f postgres
```

### Detener PostgreSQL

```powershell
docker-compose down
```

### Detener Y eliminar datos

```powershell
docker-compose down -v
```

### Reiniciar PostgreSQL

```powershell
docker-compose restart postgres
```

### Conectar a la base de datos

```powershell
docker exec -it podoskin_postgres psql -U podoskin_user -d podoskin_db
```

---

## RESUMEN DE PUERTOS

- **PostgreSQL:** <http://localhost:5432>
- **Backend (FastAPI):** <http://localhost:8000>
- **Frontend (Vite):** <http://localhost:5173>

---

## VALIDACIONES FINALES

1. [ ] Docker Desktop está corriendo
2. [ ] `docker ps` muestra contenedor `podoskin_postgres` en estado `Up`
3. [ ] Backend arranca sin errores en <http://localhost:8000/docs>
4. [ ] Frontend arranca sin errores en <http://localhost:5173>
5. [ ] Puedo ver la página de login
6. [ ] Puedo conectarme a la base de datos desde backend

---

## TROUBLESHOOTING

**Error:  "docker:  command not found"**

- Instalar Docker Desktop y reiniciar PowerShell

**Error: "port 5432 is already in use"**

```powershell
# Ver qué está usando el puerto
netstat -ano | findstr : 5432
# Detener PostgreSQL nativo si lo tienes instalado
```

**Error: "Cannot connect to database"**

```powershell
# Verificar que el contenedor está corriendo
docker ps
# Ver logs del contenedor
docker-compose logs postgres
```

**Scripts SQL no se ejecutaron:**

```powershell
# Ejecutar manualmente (comandos en sección 8)
```

---

## RESULTADO ESPERADO

Al final deberías tener:

1. ✅ PostgreSQL corriendo en Docker
2. ✅ Backend FastAPI corriendo (puerto 8000)
3. ✅ Frontend React corriendo (puerto 5173)
4. ✅ Base de datos con 44 tablas creadas
5. ✅ Usuario de prueba creado
6. ✅ Login funcional desde la interfaz

Proporciona screenshots de:

- `docker ps` mostrando el contenedor
- <http://localhost:8000/docs>
- <http://localhost:5173> (página de login)

```

---

## 🎯 **VENTAJAS DE USAR DOCKER**

✅ No necesitas instalar PostgreSQL en Windows
✅ No hay conflictos con otras instalaciones
✅ Fácil de borrar y recrear (docker-compose down -v)
✅ Mismo entorno en cualquier máquina
✅ Imagen `pgvector/pgvector` ya incluye la extensión pgvector

---
