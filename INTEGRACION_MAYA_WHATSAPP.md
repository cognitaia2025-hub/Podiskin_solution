# 🔗 Guía de Integración: Notificaciones → WhatsApp → Maya (LangGraph)

**Fecha:** 06/01/2026  
**Estado:** Preparado para integración futura  
**Componentes:** Celery + Redis + WhatsApp API + Maya (LangGraph)

---

## 📋 Resumen Ejecutivo

Este documento describe cómo integrar el sistema de notificaciones automáticas con WhatsApp y el agente de IA Maya para conversaciones bidireccionales con pacientes.

### Estado Actual (Implementado ✅)

1. **Notificaciones Automáticas:**
   - ✅ Recordatorio 24 horas antes de la cita
   - ✅ Recordatorio 2 horas antes de la cita
   - ✅ Mensajes humanos y naturales
   - ✅ Almacenamiento en BD (tabla `notificaciones`)
   - ✅ WebSocket para notificaciones internas (dashboard)

2. **Agente Maya (LangGraph):**
   - ✅ Grafo completo con clasificación de intenciones
   - ✅ Herramientas para agendar, consultar, cancelar citas
   - ✅ Escalamiento a humanos cuando es necesario
   - ✅ Persistencia de conversaciones en PostgreSQL

### Pendiente de Integración (❌)

1. **API de WhatsApp:** Conexión con whatsapp-web.js o Twilio
2. **Webhook de WhatsApp:** Recibir mensajes entrantes
3. **Puente Notificaciones → WhatsApp:** Enviar recordatorios por WhatsApp
4. **Contexto Conversacional:** Cargar estado de notificaciones para Maya

---

## 🏗️ Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                    CELERY BEAT (Scheduler)                      │
│  - Cada hora: enviar_recordatorios_citas (24h antes)          │
│  - Cada 30 min: enviar_recordatorios_2h (2h antes)            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            TAREA CELERY: notifications.py                       │
│  1. Query BD: Citas próximas sin recordatorio                  │
│  2. INSERT en tabla `notificaciones`                            │
│  3. Llama: enviar_notificacion_whatsapp() ◀── TODO: Implementar│
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│     MÓDULO: notification_handler.py (A CREAR)                   │
│  1. Envía mensaje por API de WhatsApp                          │
│  2. Crea registro en tabla `conversaciones`                    │
│  3. Guarda contexto para Maya (cita_id, intent esperado)       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│             API DE WHATSAPP (Externa)                           │
│  - whatsapp-web.js (autohospedado, Node.js)                   │
│  - Twilio API (SaaS, pago por mensaje)                         │
│  - WhatsApp Business API (oficial, complejo)                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Mensaje enviado al paciente
                     │ "Hola Juan, ¿qué tal? Solo para recordarte..."
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 PACIENTE (WhatsApp)                             │
│  Recibe: "Hola Juan, recuerda tu cita mañana..."              │
│  Responde: "Sí, ahí estaré" o "¿Puedo reagendar?"             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│        WEBHOOK: /api/webhook/whatsapp (A CREAR)                 │
│  1. Recibe POST con mensaje del paciente                       │
│  2. Busca conversación activa por teléfono                     │
│  3. Carga contexto de la notificación (cita_id, etc.)         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│        AGENTE MAYA (LangGraph) - YA IMPLEMENTADO ✅             │
│  1. classify_intent: Identifica intención del mensaje          │
│  2. retrieve_context: Obtiene info de cita desde BD            │
│  3. check_patient: Valida paciente existente                   │
│  4. handle_appointment: Procesa confirmación/reagendado        │
│  5. generate_response: Respuesta natural                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│         RESPUESTA POR WHATSAPP AL PACIENTE                      │
│  "¡Perfecto Juan! Tu cita quedó confirmada ✅"                 │
│  O: "Claro, ¿qué horario te viene mejor?"                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Paso a Paso: Integración Completa

### PASO 1: Configurar API de WhatsApp

#### Opción A: whatsapp-web.js (Recomendado para desarrollo)

**Ventajas:** Gratuito, fácil de configurar, sin límites  
**Desventajas:** Requiere escanear QR, menos estable, no oficial

```bash
# 1. Clonar proyecto whatsapp-web.js en carpeta separada
cd ../whatsapp-web-js
npm install

# 2. Crear servidor webhook simple
# Ver archivo: whatsapp-server.js (ejemplo abajo)

# 3. Iniciar servidor
node whatsapp-server.js

# 4. Escanear QR en WhatsApp Web
```

**Archivo `whatsapp-server.js` (ejemplo):**

```javascript
const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const client = new Client();

client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('WhatsApp client is ready!');
});

client.on('message', async msg => {
    // Enviar mensaje a webhook de FastAPI
    const response = await fetch('http://localhost:8000/api/webhook/whatsapp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            from_phone: msg.from,
            message_text: msg.body,
            timestamp: msg.timestamp
        })
    });
    
    const data = await response.json();
    
    // Enviar respuesta de Maya de vuelta al paciente
    if (data.reply) {
        await client.sendMessage(msg.from, data.reply);
    }
});

client.initialize();

// Endpoint para enviar mensajes (llamado desde Python)
app.post('/send', async (req, res) => {
    const { phone, message } = req.body;
    try {
        await client.sendMessage(`52${phone}@c.us`, message);
        res.json({ status: 'sent' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('WhatsApp webhook server running on port 3000');
});
```

#### Opción B: Twilio API (Producción)

**Ventajas:** Oficial, estable, soporte empresarial  
**Desventajas:** De pago (~$0.005 USD por mensaje)

```python
# 1. Instalar SDK
pip install twilio

# 2. Configurar en .env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# 3. Código de envío (ejemplo)
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    from_=f'whatsapp:{twilio_number}',
    body='Hola Juan, recordatorio de cita...',
    to=f'whatsapp:+52{paciente_telefono}'
)
```

---

### PASO 2: Crear Módulo `notification_handler.py`

**Ubicación:** `backend/agents/sub_agent_whatsApp/notification_handler.py`

```python
"""
Manejador de notificaciones → WhatsApp → Maya
"""

import asyncio
import asyncpg
import os
import httpx
from typing import Optional
from datetime import datetime

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'podoskin_db'),
    'user': os.getenv('POSTGRES_USER', 'podoskin_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'podoskin_password_123'),
}

WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'http://localhost:3000/send')


async def enviar_notificacion_whatsapp(
    paciente_id: int,
    telefono: str,
    mensaje: str,
    tipo_notificacion: str,
    cita_id: Optional[int] = None,
    requiere_respuesta: bool = True
):
    """
    Envía notificación por WhatsApp y prepara contexto para Maya
    
    Args:
        paciente_id: ID del paciente
        telefono: Teléfono del paciente (10 dígitos)
        mensaje: Mensaje a enviar
        tipo_notificacion: 'recordatorio_cita_24h', 'recordatorio_cita_2h', etc.
        cita_id: ID de la cita relacionada
        requiere_respuesta: Si se espera respuesta del paciente
    """
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 1. Crear conversación en BD
        conversation_id = await conn.fetchval(
            \"\"\"
            INSERT INTO conversaciones 
            (id_contacto, origen_notificacion, estado, fecha_inicio)
            VALUES (
                (SELECT id FROM contactos WHERE id_paciente = $1 LIMIT 1),
                $2,
                'activa',
                NOW()
            )
            RETURNING id
            \"\"\",
            paciente_id, tipo_notificacion
        )
        
        # 2. Guardar contexto para Maya
        contexto_maya = {
            "tipo_interaccion": tipo_notificacion,
            "cita_id": cita_id,
            "estado_inicial": "esperando_confirmacion",
            "intent_esperado": "confirmacion_cita" if "recordatorio" in tipo_notificacion else None,
            "mensaje_original": mensaje
        }
        
        await conn.execute(
            \"\"\"
            UPDATE conversaciones 
            SET contexto_maya = $1
            WHERE id = $2
            \"\"\",
            contexto_maya, conversation_id
        )
        
        # 3. Registrar mensaje en tabla mensajes
        await conn.execute(
            \"\"\"
            INSERT INTO mensajes (id_conversacion, rol, contenido, fecha_envio)
            VALUES ($1, 'asistente', $2, NOW())
            \"\"\",
            conversation_id, mensaje
        )
        
        # 4. Enviar por WhatsApp API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WHATSAPP_API_URL,
                json={
                    "phone": telefono,
                    "message": mensaje
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                # Actualizar notificación como enviada
                await conn.execute(
                    \"\"\"
                    UPDATE notificaciones 
                    SET enviado_whatsapp = TRUE, 
                        conversation_id = $1
                    WHERE referencia_id = $2 AND tipo = $3
                    \"\"\",
                    conversation_id, str(cita_id), tipo_notificacion
                )
                
                return {
                    "status": "success",
                    "conversation_id": conversation_id,
                    "mensaje_enviado": True
                }
            else:
                return {
                    "status": "error",
                    "error": f"Error WhatsApp API: {response.status_code}"
                }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    
    finally:
        await conn.close()
```

---

### PASO 3: Actualizar `notifications.py` con Integración WhatsApp

**Ubicación:** `backend/tasks/notifications.py`

**Descomentar líneas TODO y actualizar:**

```python
# En función _enviar_recordatorios_citas_async():

# REEMPLAZAR:
# TODO FUTURO: Integración con WhatsApp + Maya (LangGraph)
# from backend.agents.sub_agent_whatsApp.notification_handler import enviar_notificacion_whatsapp

# POR:
from backend.agents.sub_agent_whatsApp.notification_handler import enviar_notificacion_whatsapp

# Y después del INSERT en notificaciones:
await enviar_notificacion_whatsapp(
    paciente_id=cita['paciente_id'],
    telefono=cita['paciente_telefono'],
    mensaje=mensaje,
    tipo_notificacion='recordatorio_cita_24h',
    cita_id=cita['cita_id']
)
```

---

### PASO 4: Crear Webhook de WhatsApp

**Ubicación:** `backend/api/whatsapp_webhook.py`

```python
"""
Webhook para recibir mensajes de WhatsApp y enrutarlos a Maya
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncpg
import os
from backend.agents.sub_agent_whatsApp.graph import create_whatsapp_graph
from backend.agents.sub_agent_whatsApp.state import WhatsAppAgentState

router = APIRouter()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'podoskin_db'),
    'user': os.getenv('POSTGRES_USER', 'podoskin_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'podoskin_password_123'),
}


class WhatsAppWebhookPayload(BaseModel):
    from_phone: str
    message_text: str
    timestamp: int


@router.post("/api/webhook/whatsapp")
async def recibir_mensaje_whatsapp(payload: WhatsAppWebhookPayload):
    """
    Recibe mensaje de WhatsApp, lo procesa con Maya y devuelve respuesta
    """
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 1. Buscar conversación activa por teléfono
        conversation = await conn.fetchrow(
            \"\"\"
            SELECT c.id, c.contexto_maya, co.id_paciente
            FROM conversaciones c
            JOIN contactos co ON c.id_contacto = co.id
            WHERE co.telefono = $1 
              AND c.estado = 'activa'
              AND c.fecha_inicio > NOW() - INTERVAL '24 hours'
            ORDER BY c.fecha_inicio DESC
            LIMIT 1
            \"\"\",
            payload.from_phone.replace('@c.us', '').replace('52', '')[-10:]  # Últimos 10 dígitos
        )
        
        if not conversation:
            return {
                "status": "no_conversation",
                "reply": "Lo siento, no encuentro una conversación activa. ¿En qué puedo ayudarte?"
            }
        
        # 2. Registrar mensaje del paciente
        await conn.execute(
            \"\"\"
            INSERT INTO mensajes (id_conversacion, rol, contenido, fecha_envio)
            VALUES ($1, 'usuario', $2, NOW())
            \"\"\",
            conversation['id'], payload.message_text
        )
        
        # 3. Cargar contexto para Maya
        contexto = conversation['contexto_maya'] or {}
        
        # 4. Crear estado para Maya
        state = WhatsAppAgentState(
            conversation_id=str(conversation['id']),
            messages=[
                {"role": "user", "content": payload.message_text}
            ],
            patient_phone=payload.from_phone,
            patient_id=conversation['id_paciente'],
            # Contexto precargado de la notificación
            **contexto
        )
        
        # 5. Ejecutar grafo de Maya
        graph = create_whatsapp_graph()
        result = await graph.ainvoke(
            state,
            config={"configurable": {"thread_id": str(conversation['id'])}}
        )
        
        # 6. Obtener respuesta de Maya
        respuesta = result.get("final_response", "Lo siento, no pude procesar tu mensaje.")
        
        # 7. Registrar respuesta de Maya
        await conn.execute(
            \"\"\"
            INSERT INTO mensajes (id_conversacion, rol, contenido, fecha_envio)
            VALUES ($1, 'asistente', $2, NOW())
            \"\"\",
            conversation['id'], respuesta
        )
        
        # 8. Devolver respuesta para enviar por WhatsApp
        return {
            "status": "success",
            "conversation_id": conversation['id'],
            "reply": respuesta
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "reply": "Disculpa, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?"
        }
    
    finally:
        await conn.close()
```

---

### PASO 5: Actualizar Esquema de BD

**Agregar columnas a tablas existentes:**

```sql
-- En conversaciones
ALTER TABLE conversaciones ADD COLUMN IF NOT EXISTS 
    origen_notificacion VARCHAR(50);

ALTER TABLE conversaciones ADD COLUMN IF NOT EXISTS 
    contexto_maya JSONB;

-- En notificaciones
ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS 
    enviado_whatsapp BOOLEAN DEFAULT FALSE;

ALTER TABLE notificaciones ADD COLUMN IF NOT EXISTS 
    conversation_id BIGINT REFERENCES conversaciones(id);
```

---

### PASO 6: Registrar Webhook en main.py

```python
# En backend/main.py:

from api.whatsapp_webhook import router as whatsapp_webhook_router

# ...

app.include_router(whatsapp_webhook_router)
```

---

## 🧪 Pruebas de Integración

### Prueba 1: Envío Manual de Recordatorio

```bash
# 1. Conectar a PostgreSQL
psql -U podoskin_user -d podoskin_db

# 2. Crear cita de prueba para mañana
INSERT INTO citas (paciente_id, podologo_id, fecha_cita, hora_inicio, hora_fin, estado)
VALUES (1, 1, CURRENT_DATE + INTERVAL '1 day', '10:00', '10:30', 'confirmada');

# 3. Ejecutar tarea Celery manualmente
python -c "from backend.tasks.notifications import enviar_recordatorios_citas; enviar_recordatorios_citas()"

# 4. Verificar mensaje en WhatsApp
# Debe llegar: "Hola Juan, ¿qué tal? Solo para recordarte que tenemos tu cita..."
```

### Prueba 2: Respuesta del Paciente

```
PACIENTE (WhatsApp): "Sí confirmo"

ESPERADO (Maya responde):
"¡Perfecto Juan! Tu cita quedó confirmada para mañana a las 10:00 AM ✅"

BD (tabla citas):
estado = 'confirmada' (sin cambios)
confirmado_por_paciente = TRUE (nuevo campo opcional)
```

### Prueba 3: Reagendamiento

```
PACIENTE (WhatsApp): "¿Puedo cambiarla para el viernes?"

ESPERADO (Maya responde):
"Claro Juan, te ayudo a reagendar. ¿Te viene bien el viernes a la misma hora (10:00 AM)?"

PACIENTE: "Sí perfecto"

MAYA: "Listo, cambié tu cita para el viernes 10/01 a las 10:00 AM con Dr. Ornelas ✅"
```

---

## 📊 Monitoreo y Logs

### Logs de Celery

```bash
# Ver logs de tareas
tail -f logs/celery.log

# Verificar tareas ejecutadas
celery -A backend.tasks.celery_app inspect active
```

### Logs de WhatsApp

```bash
# Ver logs del servidor Node.js
tail -f whatsapp-web-js/logs/server.log

# Verificar conexión
curl http://localhost:3000/status
```

### Logs de Maya

```python
# En backend/agents/sub_agent_whatsApp/graph.py
logger.info(f"[Maya] Procesando mensaje de {patient_phone}")
logger.info(f"[Maya] Intent detectado: {state['intent']}")
logger.info(f"[Maya] Respuesta generada: {state['final_response']}")
```

---

## 🔧 Configuración de Producción

### Variables de Entorno

```bash
# .env
WHATSAPP_API_URL=http://localhost:3000/send
WHATSAPP_WEBHOOK_SECRET=secret_key_here

# Para Twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Seguridad del Webhook

```python
# En whatsapp_webhook.py:

from fastapi import Header, HTTPException

@router.post("/api/webhook/whatsapp")
async def recibir_mensaje_whatsapp(
    payload: WhatsAppWebhookPayload,
    x_webhook_secret: str = Header(None)
):
    if x_webhook_secret != os.getenv('WHATSAPP_WEBHOOK_SECRET'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # ... resto del código
```

---

## 📈 Métricas y Análisis

### Queries Útiles

```sql
-- Conversiones de recordatorios
SELECT 
    tipo,
    COUNT(*) as total_enviadas,
    COUNT(*) FILTER (WHERE conversation_id IS NOT NULL) as con_respuesta,
    COUNT(*) FILTER (WHERE enviado_whatsapp = TRUE) as enviadas_whatsapp
FROM notificaciones
WHERE fecha_envio > NOW() - INTERVAL '7 days'
GROUP BY tipo;

-- Tiempo promedio de respuesta
SELECT 
    AVG(EXTRACT(EPOCH FROM (m2.fecha_envio - m1.fecha_envio))/60) as minutos_promedio
FROM mensajes m1
JOIN mensajes m2 ON m1.id_conversacion = m2.id_conversacion
WHERE m1.rol = 'asistente' AND m2.rol = 'usuario'
  AND m2.fecha_envio > m1.fecha_envio
  AND m1.fecha_envio > NOW() - INTERVAL '7 days';
```

---

## ✅ Checklist de Integración

- [ ] WhatsApp API configurada (whatsapp-web.js o Twilio)
- [ ] Servidor webhook de WhatsApp corriendo (puerto 3000)
- [ ] Módulo `notification_handler.py` creado
- [ ] Función `enviar_notificacion_whatsapp()` integrada en `notifications.py`
- [ ] Webhook `/api/webhook/whatsapp` implementado
- [ ] Columnas BD agregadas (`origen_notificacion`, `contexto_maya`, etc.)
- [ ] Celery + Redis corriendo
- [ ] Pruebas manuales exitosas
- [ ] Logs configurados
- [ ] Variables de entorno en `.env`
- [ ] Documentación actualizada

---

## 📞 Soporte

**Dudas técnicas:** Revisar logs de Celery, WhatsApp API y Maya  
**Errores de integración:** Verificar conexiones BD, APIs externas  
**Problemas de mensajes:** Revisar formato de teléfonos (debe ser 10 dígitos)

---

**Última actualización:** 06/01/2026  
**Versión:** 1.0  
**Autor:** Sistema de IA
