# Setup Local - Twilio WhatsApp

Este documento detalla cómo configurar el entorno local para probar la integración de Twilio WhatsApp con el agente Maya.

## Requisitos

- Python 3.11+
- PostgreSQL 15+ con extensión pgvector
- Cuenta de Twilio (Trial o Production)
- Ngrok instalado (para desarrollo local)
- Node.js 18+ (opcional, solo si usas whatsapp-web.js en paralelo)

## Pasos de Instalación

### 1. Instalar Dependencias de Python

```bash
cd backend
pip install -r requirements.txt
```

**Dependencias críticas:**
- `twilio>=8.10.0` - Cliente oficial de Twilio
- `sentence-transformers>=2.2.0` - Para embeddings locales
- `asyncpg>=0.29.0` - Driver async de PostgreSQL
- `langchain>=0.1.0` y `langgraph>=0.0.20` - Framework de agentes

### 2. Configurar Base de Datos

#### a) Crear base de datos PostgreSQL

```bash
psql -U postgres
CREATE DATABASE podoskin_db;
\c podoskin_db
CREATE EXTENSION IF NOT EXISTS pgvector;
\q
```

#### b) Ejecutar migración de Twilio

```bash
psql -U postgres -d podoskin_db -f backend/database/migrations/20_twilio_maya_integration.sql
```

Esto creará:
- ✅ `conversaciones_embeddings` (contexto aislado por paciente)
- ✅ `knowledge_base_validated` (KB sin datos operativos)
- ✅ `behavior_rules` (reglas dinámicas)
- ✅ `whatsapp_filters` (blacklist/whitelist)
- ✅ `twilio_webhook_logs` (auditoría)

### 3. Generar Embeddings Iniciales

```bash
cd backend
python scripts/generate_initial_embeddings.py
```

Este script genera embeddings para las 3 reglas de comportamiento iniciales:
1. Consultar precios en SQL (Prioridad 1)
2. Consultar horarios en SQL (Prioridad 1)
3. Tono empático (Prioridad 3)

### 4. Configurar Variables de Entorno

Copia `.env.example` a `.env` y configura:

```env
# Base de datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/podoskin_db

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+16206986058

# Anthropic (para agente Maya)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Configuración del agente
AGENT_CONFIDENCE_THRESHOLD=0.80
AGENT_MODEL=claude-3-5-sonnet-20241022
AGENT_MAX_TOKENS=1024

# Entorno
ENVIRONMENT=development
```

### 5. Iniciar Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

El servidor iniciará en `http://localhost:8000`

### 6. Exponer con Ngrok

En otra terminal:

```bash
ngrok http 8000
```

Ngrok generará una URL pública:

```
Forwarding   https://xxxx-xxx-xxx.ngrok.io -> http://localhost:8000
```

**⚠️ IMPORTANTE:** Copia la URL HTTPS generada (ej: `https://abc123.ngrok.io`)

### 7. Configurar Webhook en Twilio Console

#### a) Ir a Twilio Console

1. Inicia sesión en https://console.twilio.com/
2. Ve a **Messaging** > **Try it out** > **Send a WhatsApp message**
3. En el menú lateral, selecciona **Sandbox settings**

#### b) Configurar Webhook de entrada

En la sección "When a message comes in":

```
URL: https://abc123.ngrok.io/webhook/twilio
HTTP Method: POST
```

**Nota:** Reemplaza `abc123.ngrok.io` con tu URL de Ngrok.

#### c) Guardar configuración

Click en **Save** al final de la página.

### 8. Conectar WhatsApp al Sandbox

#### a) Obtener código del sandbox

En la página de **Sandbox Settings**, verás:

```
To connect to your sandbox, send:
join shoulder-try
to WhatsApp number: +1 (620) 698-6058
```

#### b) Conectar desde tu WhatsApp

1. Abre WhatsApp en tu teléfono
2. Crea un nuevo chat con: **+1 620 698 6058**
3. Envía el mensaje: **join shoulder-try**
4. Recibirás confirmación: "Your Sandbox: You are all set!"

### 9. Probar el Sistema

Ahora puedes enviar mensajes de prueba:

#### Prueba 1: Consulta de precios (SQL - Prioridad 1)

```
Hola, ¿cuánto cuesta el tratamiento de onicomicosis?
```

**Respuesta esperada:**
Maya consultará la tabla `tratamientos` en PostgreSQL y responderá con precios reales.

#### Prueba 2: Consulta de horarios (SQL - Prioridad 1)

```
¿Qué horarios tienen el lunes?
```

**Respuesta esperada:**
Maya consultará `horarios_trabajo` y responderá con horarios disponibles.

#### Prueba 3: Consulta general (KB - Prioridad 2)

```
¿Dónde están ubicados?
```

**Respuesta esperada:**
Si existe en `knowledge_base_validated`, responderá. Si no, escalará a humano.

## Monitoreo y Debugging

### Ver logs del backend

```bash
tail -f logs/backend.log
```

### Ver logs de webhooks en Twilio

1. Ve a https://console.twilio.com/us1/monitor/logs/debugger
2. Filtra por "SMS & WhatsApp"
3. Verás todos los webhooks recibidos y enviados

### Ver registros en base de datos

```sql
-- Últimos webhooks procesados
SELECT * FROM twilio_webhook_logs ORDER BY fecha_recepcion DESC LIMIT 10;

-- Conversaciones recientes
SELECT * FROM conversaciones WHERE canal = 'WhatsApp' ORDER BY fecha_creacion DESC LIMIT 10;

-- Mensajes de una conversación
SELECT * FROM mensajes WHERE id_conversacion = 123 ORDER BY fecha_envio;
```

## Troubleshooting

### Problema: "Invalid Twilio signature"

**Causa:** La validación de firma está fallando.

**Solución temporal:** Asegúrate de que `ENVIRONMENT=development` en `.env`

**Solución producción:** Verifica que `TWILIO_AUTH_TOKEN` sea correcto.

### Problema: "Twilio validator not configured"

**Causa:** Las credenciales de Twilio no están en `.env`.

**Solución:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxx
```

### Problema: No llegan mensajes al webhook

**Verificar:**
1. ✅ Ngrok está corriendo y la URL es accesible
2. ✅ El webhook en Twilio está configurado correctamente
3. ✅ El número está conectado al sandbox con "join shoulder-try"
4. ✅ El backend está corriendo sin errores

### Problema: "No se encontró información"

**Causa:** Las tablas están vacías (no hay tratamientos, horarios, etc.).

**Solución:** Ejecutar los scripts de datos de prueba:
```bash
psql -U postgres -d podoskin_db -f data/seed_tratamientos.sql
psql -U postgres -d podoskin_db -f data/seed_horarios.sql
```

## Arquitectura del Flujo

```
WhatsApp
    ↓
Twilio API
    ↓
Ngrok (dev) / Servidor (prod)
    ↓
backend/api/twilio_webhook.py
    ↓
agents/whatsapp_medico/graph.py (LangGraph)
    ↓
Nodes: Router → RAG Manager → Generate Response
    ↓
Tools: SQL (P1) → KB (P2) → Context (P3)
    ↓
Response generada
    ↓
Twilio TwiML
    ↓
WhatsApp usuario
```

## Siguientes Pasos

1. ✅ **Probar flujos básicos** (precios, horarios)
2. ✅ **Poblar Knowledge Base** con FAQs
3. ✅ **Configurar reglas de comportamiento** adicionales
4. ✅ **Implementar frontend** de gestión
5. ✅ **Configurar monitoreo** y alertas
6. ✅ **Migrar a producción** (quitar Ngrok, usar dominio real)

## Notas de Seguridad

⚠️ **En producción:**
- Cambiar `ENVIRONMENT=production` para habilitar validación de firma
- Usar HTTPS con certificado válido (no Ngrok)
- Configurar whitelist si es necesario
- Rotar `TWILIO_AUTH_TOKEN` regularmente
- Monitorear logs de `twilio_webhook_logs` por actividad sospechosa

## Soporte

Para problemas o preguntas:
- Documentación de Twilio: https://www.twilio.com/docs/whatsapp
- Documentación de LangGraph: https://docs.langchain.com/oss/python/langgraph
- Issues del proyecto: [GitHub Issues]

---

**Última actualización:** 2026-01-12
**Autor:** Equipo Podoskin
