# 🛠️ Guía Pro: Setup Docker + Backend

Sigue estos pasos para levantar tu entorno de desarrollo usando los archivos en esta carpeta.

## 1. Preparación de la Carpeta

Asegúrate de que tu estructura de proyecto sea similar a esta:

```
podoskin-project/
├── data/               <-- Esta carpeta con los SQLs
│   ├── 00_inicializacion.sql
│   ├── 01_funciones.sql
│   ├── ...
├── backend/            <-- Tu código fuente
│   └── .env
└── docker-compose.yml
```

## 2. Archivo Docker Compose

Utiliza este archivo `docker-compose.yml` en la raíz de tu proyecto:

```yaml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: podoskin_db
    restart: always
    environment:
      POSTGRES_DB: podoskin_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: tu_password_seguro
    ports:
      - "5432:5432"
    volumes:
      - ./data:/docker-entrypoint-initdb.d
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 3. Levantar el Entorno

Ejecuta el siguiente comando en tu terminal:

```bash
docker-compose up -d
```

Puedes verificar que los scripts se ejecutaron correctamente revisando los logs:

```bash
docker logs -f podoskin_db
```

## 4. Configurar el Backend (.env)

En tu archivo `.env` del backend, usa la siguiente cadena de conexión:

```env
DATABASE_URL=postgresql://postgres:tu_password_seguro@localhost:5432/podoskin_db
```

## 🔍 Verificación en la Base de Datos

Puedes entrar al contenedor para verificar las tablas:

```bash
docker exec -it podoskin_db psql -U postgres -d podoskin_db -c "\dt"
```

Deberías ver una lista con las **26 tablas** principales del sistema.
