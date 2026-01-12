# 📘 PROMPT COMPLETO:  Integración Twilio + Agente Maya Optimizado con LangGraph v1+

**Archivo:** `INTEGRACION_TWILIO_MAYA_COMPLETO.md`

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura de Datos](#arquitectura-de-datos)
3. [Migraciones de Base de Datos](#migraciones-de-base-de-datos)
4. [Integración con Twilio](#integracion-con-twilio)
5. [Agente Maya - LangGraph v1+ Optimizado](#agente-maya-langgraph-v1-optimizado)
6. [Tools Especializadas](#tools-especializadas)
7. [Node RAG Manager Mejorado](#node-rag-manager-mejorado)
8. [System Prompt Dinámico](#system-prompt-dinamico)
9. [Frontend - Módulo de Gestión](#frontend-modulo-de-gestion)
10. [Configuración y Deployment](#configuracion-y-deployment)
11. [Testing y Validación](#testing-y-validacion)
12. [Checklist de Implementación](#checklist-de-implementacion)

---

## 🎯 Resumen Ejecutivo

Este documento detalla la implementación completa de: 

1. ✅ **Limpieza de whatsapp-web.js** (ya ejecutada según `PLAN_LIMPIEZA_WHATSAPP. md`)
2. ✅ **Integración con Twilio WhatsApp API** (webhook + envío)
3. ✅ **Optimización del Agente Maya** con LangGraph v1+ patterns
4. ✅ **Separación estricta de fuentes de datos** (SQL → KB → Contexto)
5. ✅ **Aislamiento de conversaciones por paciente** (`id_contacto` como thread)
6. ✅ **Frontend de gestión** (Sandbox, Aprendizajes, Disponibilidad)

### **Principios Arquitectónicos Clave:**

```python
# 🏆 JERARQUÍA DE FUENTES (INMUTABLE)
PRIORIDAD_1 = "SQL estructurado"      # ← FUENTE DE VERDAD ÚNICA
PRIORIDAD_2 = "Knowledge Base validada"  # ← Aprendizajes aprobados
PRIORIDAD_3 = "Contexto conversacional"  # ← Aislado por id_contacto

# ⚠️ REGLAS CRÍTICAS
- NUNCA usar vectores para precios/horarios/servicios
- SIEMPRE filtrar conversaciones por id_contacto
- ESCALAMIENTO automático si confidence < 0.80
- System Prompt dinámico con behavior_rules
```

---

## 🗄️ Arquitectura de Datos

### **Jerarquía Completa de Fuentes de Información**

```
┌─────────────────────────────────────────────────────────────────┐
│         NIVEL 1: BASE DE DATOS ESTRUCTURADA (SQL)               │
│                    ✅ FUENTE DE VERDAD ÚNICA                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─ tratamientos         → Servicios, precios, duraciones
    ├─ horarios_trabajo     → Disponibilidad de podólogos
    ├─ bloqueos_agenda      → Días bloqueados, vacaciones
    ├─ citas                → Agenda de citas existentes
    ├─ podologos            → Personal disponible
    └─ 🔒 NUNCA usar vectores para estos datos

┌─────────────────────────────────────────────────────────────────┐
│      NIVEL 2: KNOWLEDGE BASE VALIDADA (pgvector compartido)    │
│              ✅ Aprendizajes aprobados por admin                │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─ knowledge_base_validated  → FAQs, políticas, procesos
    ├─ Categorías permitidas: 
    │   • FAQ_Proceso
    │   • Politica_Clinica
    │   • Informacion_General
    │   • Procedimiento_Medico
    │
    └─ ⚠️ contiene_datos_operativos = FALSE

┌─────────────────────────────────────────────────────────────────┐
│   NIVEL 3: CONTEXTO CONVERSACIONAL (pgvector aislado)          │
│              ✅ Aislado por id_contacto (thread-scoped)         │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─ conversaciones_embeddings → Historial individual
    ├─ Filtro obligatorio:   WHERE id_contacto = $1
    ├─ metadata JSON por conversación
    └─ 🔒 NO compartido entre pacientes

┌─────────────────────────────────────────────────────────────────┐
│         NIVEL 4: BEHAVIOR RULES (Reglas dinámicas)             │
│              ✅ Inyectadas al System Prompt                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ├─ behavior_rules → Instrucciones de comportamiento
    ├─ Prioridad 1-10
    └─ Consultadas en Node_Router al inicio
```

---

## 💾 Migraciones de Base de Datos

### **Archivo 1: `backend/database/migrations/20_twilio_maya_integration.sql`**

```sql
-- ============================================================================
-- MIGRACIÓN: Integración Twilio + Maya Optimizado
-- Fecha: 2026-01-12
-- Descripción: Tablas para separación de datos vectoriales y Twilio
-- ============================================================================

BEGIN;

-- ============================================================================
-- TABLA 1: conversaciones_embeddings (Contexto por paciente - AISLADO)
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversaciones_embeddings (
    id SERIAL PRIMARY KEY,
    
    -- 🔑 AISLAMIENTO POR PACIENTE (thread-scoped)
    id_contacto BIGINT NOT NULL REFERENCES contactos(id) ON DELETE CASCADE,
    id_conversacion BIGINT NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    
    -- Resumen de la conversación
    resumen_conversacion TEXT NOT NULL,
    
    -- Embedding del resumen (384 dims, all-MiniLM-L6-v2)
    embedding BYTEA NOT NULL,
    
    -- Metadata estructurada (JSON)
    metadata JSONB DEFAULT '{}'::jsonb,
    /* Estructura recomendada:
    {
        "topicos": ["cita_agendada", "consulta_precio"],
        "fecha_conversacion": "2026-01-12",
        "duracion_minutos": 5,
        "resuelto": true,
        "tipo_consulta": "agendar_cita",
        "sentimiento": "positivo"
    }
    */
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_ultima_consulta TIMESTAMP,
    
    -- Constraint:  Una conversación = un embedding
    UNIQUE(id_conversacion)
);

-- ✅ ÍNDICE CRÍTICO:  Buscar SOLO conversaciones de un contacto
CREATE INDEX idx_conv_embeddings_contacto 
ON conversaciones_embeddings(id_contacto);

CREATE INDEX idx_conv_embeddings_fecha 
ON conversaciones_embeddings(fecha_creacion DESC);

CREATE INDEX idx_conv_embeddings_metadata 
ON conversaciones_embeddings USING gin(metadata);

COMMENT ON TABLE conversaciones_embeddings IS 
'Contexto conversacional aislado POR PACIENTE.  NO compartido entre contactos';

COMMENT ON COLUMN conversaciones_embeddings.id_contacto IS 
'CRÍTICO: Filtro para aislar conversaciones por paciente (thread-scoped memory)';

-- ============================================================================
-- TABLA 2: knowledge_base_validated (KB Compartida - Sin datos operativos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_base_validated (
    id SERIAL PRIMARY KEY,
    
    -- Pregunta y respuesta
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    
    -- Embedding de la pregunta (384 dims)
    pregunta_embedding BYTEA NOT NULL,
    
    -- Categorización
    categoria TEXT NOT NULL CHECK (categoria IN (
        'FAQ_Proceso',           -- "¿Cómo agendar una cita?"
        'Politica_Clinica',      -- "¿Puedo cancelar?"
        'Informacion_General',   -- "¿Dónde están ubicados?"
        'Procedimiento_Medico',  -- "¿Duele el tratamiento X?"
        'Regla_Comportamiento'   -- Cómo responder en situaciones
    )),
    
    -- ⚠️ RESTRICCIÓN: NO contiene precios, horarios ni servicios
    contiene_datos_operativos BOOLEAN DEFAULT false 
        CHECK (contiene_datos_operativos = false),
    
    -- Aprobación y origen
    aprobado BOOLEAN DEFAULT false,
    origen TEXT CHECK (origen IN (
        'admin_manual',          -- Agregado manualmente
        'escalamiento_aprendido', -- Aprendido de escalamiento
        'importado'              -- Importado desde otra fuente
    )),
    
    -- Métricas de uso
    veces_consultada INT DEFAULT 0,
    efectividad_score FLOAT DEFAULT 1.0 CHECK (efectividad_score BETWEEN 0.0 AND 1.0),
    feedback_positivo INT DEFAULT 0,
    feedback_negativo INT DEFAULT 0,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    fecha_aprobacion TIMESTAMP,
    aprobado_por BIGINT REFERENCES usuarios(id),
    fecha_ultimo_uso TIMESTAMP
);

-- Índices optimizados
CREATE INDEX idx_kb_validated_categoria 
ON knowledge_base_validated(categoria) 
WHERE aprobado = true;

CREATE INDEX idx_kb_validated_aprobado 
ON knowledge_base_validated(aprobado, efectividad_score DESC) 
WHERE aprobado = true;

CREATE INDEX idx_kb_validated_fecha 
ON knowledge_base_validated(fecha_creacion DESC);

COMMENT ON TABLE knowledge_base_validated IS 
'Knowledge base de aprendizajes validados. NO contiene precios, horarios ni servicios (solo SQL)';

COMMENT ON COLUMN knowledge_base_validated.contiene_datos_operativos IS 
'Debe ser siempre FALSE.  Los datos operativos están en tablas SQL estructuradas';

COMMENT ON COLUMN knowledge_base_validated.efectividad_score IS 
'Score de efectividad basado en feedback:  (positivo - negativo) / total';

-- ============================================================================
-- TABLA 3: behavior_rules (Reglas Dinámicas - System Prompt)
-- ============================================================================

CREATE TABLE IF NOT EXISTS behavior_rules (
    id SERIAL PRIMARY KEY,
    
    -- Descripción del patrón
    pattern TEXT NOT NULL,
    /* Ejemplo:  
    "Cuando un paciente pregunte por precios de servicios"
    */
    
    -- Instrucción de corrección
    correction_logic TEXT NOT NULL,
    /* Ejemplo:
    "SIEMPRE consultar la tabla 'tratamientos' en PostgreSQL.   
     NUNCA inventar precios ni basarse en conversaciones previas. 
     Usar la tool 'consultar_tratamientos_sql' con el término extraído."
    */
    
    -- Embedding del patrón (384 dims)
    embedding BYTEA NOT NULL,
    
    -- Metadata
    categoria TEXT CHECK (categoria IN (
        'datos_operativos',      -- Precios, horarios, servicios
        'politicas',             -- Políticas de la clínica
        'tono_comunicacion',     -- Cómo responder
        'escalamiento',          -- Cuándo escalar
        'validacion'             -- Validaciones necesarias
    )),
    
    prioridad INT DEFAULT 5 CHECK (prioridad BETWEEN 1 AND 10), -- 1 (máxima) - 10 (mínima)
    
    -- Estado
    activo BOOLEAN DEFAULT true,
    aprobado BOOLEAN DEFAULT false,
    
    -- Métricas
    veces_utilizada INT DEFAULT 0,
    ultima_utilizacion TIMESTAMP,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    creado_por BIGINT REFERENCES usuarios(id),
    aprobado_por BIGINT REFERENCES usuarios(id)
);

-- Índices
CREATE INDEX idx_behavior_rules_activo 
ON behavior_rules(activo, prioridad) 
WHERE aprobado = true;

CREATE INDEX idx_behavior_rules_categoria 
ON behavior_rules(categoria, activo);

COMMENT ON TABLE behavior_rules IS 
'Reglas de comportamiento inyectadas dinámicamente al System Prompt del agente';

COMMENT ON COLUMN behavior_rules.prioridad IS 
'1 = Máxima prioridad (se aplica primero), 10 = Mínima prioridad';

-- ============================================================================
-- TABLA 4: whatsapp_filters (Blacklist/Whitelist/Grupos)
-- ============================================================================

CREATE TABLE IF NOT EXISTS whatsapp_filters (
    id SERIAL PRIMARY KEY,
    
    -- Tipo de filtro
    tipo TEXT NOT NULL CHECK (tipo IN (
        'blacklist',          -- Número bloqueado
        'whitelist',          -- Número permitido (modo restrictivo)
        'grupo_bloqueado'     -- Grupo bloqueado
    )),
    
    -- Valor del filtro
    valor TEXT NOT NULL, -- Número de teléfono o ID de grupo
    
    -- Información adicional
    razon TEXT,
    notas TEXT,
    
    -- Estado
    activo BOOLEAN DEFAULT true,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP,
    creado_por BIGINT REFERENCES usuarios(id),
    
    -- Constraint: Un valor solo puede tener un tipo activo
    UNIQUE(valor, tipo) WHERE activo = true
);

-- Índices
CREATE INDEX idx_whatsapp_filters_tipo 
ON whatsapp_filters(tipo, activo) 
WHERE activo = true;

CREATE INDEX idx_whatsapp_filters_valor 
ON whatsapp_filters(valor) 
WHERE activo = true;

COMMENT ON TABLE whatsapp_filters IS 
'Filtros de entrada:  blacklist, whitelist, grupos bloqueados';

-- ============================================================================
-- TABLA 5: twilio_webhook_logs (Auditoría de webhooks)
-- ============================================================================

CREATE TABLE IF NOT EXISTS twilio_webhook_logs (
    id SERIAL PRIMARY KEY,
    
    -- Datos del webhook
    message_sid TEXT NOT NULL UNIQUE,
    from_number TEXT NOT NULL,
    to_number TEXT NOT NULL,
    body TEXT,
    
    -- Validación
    signature_valid BOOLEAN,
    
    -- Procesamiento
    procesado BOOLEAN DEFAULT false,
    error TEXT,
    tiempo_procesamiento_ms INT,
    
    -- Respuesta generada
    respuesta_enviada TEXT,
    fuente_respuesta TEXT, -- 'sql_estructurado', 'knowledge_base', etc.
    confidence_score FLOAT,
    
    -- Metadata
    raw_payload JSONB,
    
    -- Timestamps
    fecha_recepcion TIMESTAMP DEFAULT NOW(),
    fecha_procesamiento TIMESTAMP
);

-- Índices
CREATE INDEX idx_twilio_logs_fecha 
ON twilio_webhook_logs(fecha_recepcion DESC);

CREATE INDEX idx_twilio_logs_from 
ON twilio_webhook_logs(from_number, fecha_recepcion DESC);

CREATE INDEX idx_twilio_logs_procesado 
ON twilio_webhook_logs(procesado) 
WHERE procesado = false;

COMMENT ON TABLE twilio_webhook_logs IS 
'Log completo de webhooks de Twilio para auditoría y debugging';

-- ============================================================================
-- MODIFICAR TABLA:  mensajes (Agregar metadata JSON)
-- ============================================================================

ALTER TABLE mensajes 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Índice para búsquedas por metadata
CREATE INDEX IF NOT EXISTS idx_mensajes_metadata 
ON mensajes USING gin(metadata);

COMMENT ON COLUMN mensajes.metadata IS 
'Metadata estructurada del mensaje:  fuente_respuesta, confidence, tabla_consultada, etc.';

-- ============================================================================
-- FUNCIÓN: Actualizar efectividad de KB
-- ============================================================================

CREATE OR REPLACE FUNCTION actualizar_efectividad_kb()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE knowledge_base_validated
        SET efectividad_score = CASE 
            WHEN (feedback_positivo + feedback_negativo) > 0 
            THEN (feedback_positivo:: float - feedback_negativo::float) / (feedback_positivo + feedback_negativo)
            ELSE 1.0
        END,
        fecha_actualizacion = NOW()
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_efectividad_kb
AFTER INSERT OR UPDATE OF feedback_positivo, feedback_negativo
ON knowledge_base_validated
FOR EACH ROW
EXECUTE FUNCTION actualizar_efectividad_kb();

-- ============================================================================
-- INSERTAR REGLAS DE COMPORTAMIENTO INICIALES
-- ============================================================================

-- Regla 1: Consultar precios en SQL
INSERT INTO behavior_rules (pattern, correction_logic, embedding, categoria, prioridad, activo, aprobado)
VALUES (
    'Cuando un paciente pregunte por precios, costos o tarifas de servicios',
    'SIEMPRE consultar la tabla "tratamientos" usando la tool consultar_tratamientos_sql(). NUNCA inventar precios ni basarse en conversaciones previas.  Si no encuentras el servicio, escala a humano.',
    E'\\x00',  -- Placeholder, se actualizará con embedding real
    'datos_operativos',
    1,  -- Máxima prioridad
    true,
    true
);

-- Regla 2: Consultar horarios en SQL
INSERT INTO behavior_rules (pattern, correction_logic, embedding, categoria, prioridad, activo, aprobado)
VALUES (
    'Cuando un paciente pregunte por horarios de atención o disponibilidad',
    'SIEMPRE consultar la tabla "horarios_trabajo" usando la tool consultar_horarios_sql(). NUNCA asumir horarios ni basarse en memoria conversacional. Los horarios pueden cambiar.',
    E'\\x00',
    'datos_operativos',
    1,
    true,
    true
);

-- Regla 3: Tono empático
INSERT INTO behavior_rules (pattern, correction_logic, embedding, categoria, prioridad, activo, aprobado)
VALUES (
    'Cuando detectes frustración, molestia o urgencia en el paciente',
    'Responde con tono EMPÁTICO y PROFESIONAL. Usa frases como "Entiendo tu situación", "Lamento las molestias", "Permíteme ayudarte inmediatamente".  Prioriza la escalación a humano si el tono es muy negativo.',
    E'\\x00',
    'tono_comunicacion',
    3,
    true,
    true
);

COMMIT;

-- ============================================================================
-- VERIFICACIÓN POST-MIGRACIÓN
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migración completada exitosamente';
    RAISE NOTICE 'Tablas creadas:';
    RAISE NOTICE '  - conversaciones_embeddings (contexto aislado por paciente)';
    RAISE NOTICE '  - knowledge_base_validated (KB sin datos operativos)';
    RAISE NOTICE '  - behavior_rules (reglas dinámicas para System Prompt)';
    RAISE NOTICE '  - whatsapp_filters (blacklist/whitelist)';
    RAISE NOTICE '  - twilio_webhook_logs (auditoría)';
    RAISE NOTICE '';
    RAISE NOTICE 'Modificaciones: ';
    RAISE NOTICE '  - mensajes. metadata (columna JSONB agregada)';
    RAISE NOTICE '';
    RAISE NOTICE '🔧 Siguiente paso: Generar embeddings iniciales para behavior_rules';
END $$;
```

---

## 🔌 Integración con Twilio

### **Archivo 2: `backend/api/twilio_webhook.py`**

```python
"""
Twilio WhatsApp Webhook
=======================

Endpoint para recibir mensajes de Twilio y procesarlos con el Agente Maya. 

Referencias:
- https://www.twilio.com/docs/whatsapp/api
- https://docs.langchain.com/oss/python/langgraph/workflows-agents
"""

from fastapi import APIRouter, Form, Response, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import logging
from datetime import datetime
import os

from db import get_pool
from agents.sub_agent_whatsApp. graph import create_whatsapp_agent, WhatsAppAgentState
from agents.sub_agent_whatsApp.tools. filter_tools import check_filters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["Twilio Webhook"])

# Validador de firma Twilio
validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))

# ============================================================================
# VALIDACIÓN DE FIRMA TWILIO
# ============================================================================

def validate_twilio_signature(request: Request) -> bool:
    """
    Valida que el webhook venga de Twilio verificando la firma X-Twilio-Signature. 
    
    Referencias:
    - https://www.twilio.com/docs/usage/security#validating-requests
    """
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    
    # En desarrollo, skip validation
    if os.getenv("ENVIRONMENT") == "development":
        logger.warning("Skipping Twilio signature validation (development mode)")
        return True
    
    # Obtener parámetros del form
    params = {}
    for key, value in request.form.items():
        params[key] = value
    
    is_valid = validator.validate(url, params, signature)
    
    if not is_valid: 
        logger.error(f"Invalid Twilio signature from {request.client.host}")
    
    return is_valid

# ============================================================================
# WEBHOOK PRINCIPAL
# ============================================================================

@router.post("/twilio")
async def twilio_webhook_handler(
    request: Request,
    From: str = Form(...),      # whatsapp: +5216862262377
    To: str = Form(...),        # whatsapp:+16206986058
    Body: str = Form(... ),      # "Hola, quiero una cita"
    MessageSid: str = Form(...) # SMxxxxxxxxxxxx
):
    """
    Webhook principal de Twilio para WhatsApp.
    
    Flujo:
    1. Validar firma de Twilio
    2. Limpiar número de teléfono
    3. Aplicar filtros (blacklist/whitelist)
    4. Buscar/crear contacto en BD
    5. Buscar/crear conversación
    6. Guardar mensaje entrante
    7. Ejecutar Agente Maya (LangGraph)
    8. Guardar respuesta en BD
    9. Retornar TwiML con respuesta
    
    Referencias:
    - https://www.twilio.com/docs/sms/twiml
    - https://docs.langchain.com/oss/python/langgraph/agentic-rag
    """
    pool = get_pool()
    
    # Log del webhook
    await pool.execute(
        """
        INSERT INTO twilio_webhook_logs 
        (message_sid, from_number, to_number, body, signature_valid, raw_payload)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        MessageSid, From, To, Body, True, {}  # TODO: Agregar raw_payload completo
    )
    
    # 1. Validar firma
    if not validate_twilio_signature(request):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    
    # 2. Limpiar número (quitar "whatsapp: +")
    phone = From.replace("whatsapp:+", "").replace("whatsapp:", "")
    logger.info(f"📨 Mensaje de Twilio: {phone} → '{Body[: 50]}...'")
    
    try:
        # 3. Aplicar filtros
        filter_result = await check_filters(phone, is_group=False)
        
        if filter_result['blocked']:
            logger.warning(f"⛔ Número bloqueado: {phone} - Razón: {filter_result['reason']}")
            
            # Retornar sin respuesta (silent drop)
            resp = MessagingResponse()
            return Response(content=str(resp), media_type="application/xml")
        
        # 4. Buscar/crear contacto
        contacto = await pool.fetchrow(
            "SELECT * FROM contactos WHERE telefono = $1 OR whatsapp_id = $1",
            phone
        )
        
        if not contacto:
            contacto_id = await pool.fetchval(
                """
                INSERT INTO contactos (telefono, whatsapp_id, nombre, tipo, origen)
                VALUES ($1, $1, 'Usuario WhatsApp', 'Prospecto', 'WhatsApp')
                RETURNING id
                """,
                phone
            )
            logger.info(f"✨ Nuevo contacto creado:  {contacto_id}")
        else:
            contacto_id = contacto['id']
        
        # 5. Buscar/crear conversación activa
        conversacion = await pool.fetchrow(
            """
            SELECT * FROM conversaciones
            WHERE id_contacto = $1 AND estado = 'Activa'
            ORDER BY fecha_ultima_actividad DESC LIMIT 1
            """,
            contacto_id
        )
        
        if not conversacion:
            conv_id = await pool.fetchval(
                """
                INSERT INTO conversaciones (id_contacto, canal, estado, categoria)
                VALUES ($1, 'WhatsApp', 'Activa', 'Consulta')
                RETURNING id
                """,
                contacto_id
            )
            logger. info(f"💬 Nueva conversación creada: {conv_id}")
        else:
            conv_id = conversacion['id']
        
        # 6. Guardar mensaje entrante
        mensaje_id = await pool.fetchval(
            """
            INSERT INTO mensajes (
                id_conversacion, direccion, enviado_por_tipo, contenido, fecha_envio,
                metadata
            )
            VALUES ($1, 'Entrante', 'Contacto', $2, $3, $4)
            RETURNING id
            """,
            conv_id,
            Body,
            datetime.now(),
            {
                "twilio_message_sid": MessageSid,
                "from_number": phone,
                "timestamp_recepcion": datetime.now().isoformat()
            }
        )
        
        # 7. Ejecutar Agente Maya con LangGraph
        logger.info(f"🤖 Ejecutando Agente Maya para contacto {contacto_id}")
        
        # Crear state inicial
        initial_state = WhatsAppAgentState(
            messages=[],  # LangGraph lo gestiona internamente
            contact_id=str(contacto_id),
            conversation_id=str(conv_id),
            message=Body,
            retrieved_context="",
            fuente="",
            confidence=0.0,
            metadata={},
            requires_human=False
        )
        
        # Crear agente con checkpointer (persiste por thread/contact_id)
        agent = create_whatsapp_agent()
        
        # Ejecutar agente con thread_id = contact_id (aislamiento)
        config = {"configurable": {"thread_id":  str(contacto_id)}}
        result = await agent.ainvoke(initial_state, config=config)
        
        # Extraer respuesta generada
        respuesta = result.get('response', result['messages'][-1]. content if result['messages'] else "")
        fuente = result.get('fuente', 'unknown')
        confidence = result.get('confidence', 0.0)
        requires_human = result.get('requires_human', False)
        
        logger.info(f"✅ Respuesta generada (fuente: {fuente}, confidence: {confidence:. 2f})")
        
        # 8. Guardar respuesta en BD
        await pool.execute(
            """
            INSERT INTO mensajes (
                id_conversacion, direccion, enviado_por_tipo, contenido, fecha_envio,
                metadata
            )
            VALUES ($1, 'Saliente', 'Bot', $2, $3, $4)
            """,
            conv_id,
            respuesta,
            datetime.now(),
            {
                "fuente_respuesta": fuente,
                "confidence_score": confidence,
                "requires_human": requires_human,
                "tabla_consultada": result.get('metadata', {}).get('tabla'),
                "twilio_response_to": MessageSid
            }
        )
        
        # Actualizar conversación
        await pool.execute(
            """
            UPDATE conversaciones 
            SET fecha_ultima_actividad = $1,
                requiere_atencion = $2
            WHERE id = $3
            """,
            datetime.now(),
            requires_human,
            conv_id
        )
        
        # Actualizar log de webhook
        await pool.execute(
            """
            UPDATE twilio_webhook_logs
            SET procesado = true,
                respuesta_enviada = $1,
                fuente_respuesta = $2,
                confidence_score = $3,
                fecha_procesamiento = $4
            WHERE message_sid = $5
            """,
            respuesta, fuente, confidence, datetime.now(), MessageSid
        )
        
        # 9. Construir respuesta TwiML
        twiml_resp = MessagingResponse()
        twiml_resp.message(respuesta)
        
        logger.info(f"📤 Respuesta enviada a {phone}")
        
        return Response(content=str(twiml_resp), media_type="application/xml")
    
    except Exception as e: 
        logger.error(f"❌ Error procesando webhook de Twilio: {e}", exc_info=True)
        
        # Actualizar log con error
        await pool.execute(
            """
            UPDATE twilio_webhook_logs
            SET procesado = true,
                error = $1,
                fecha_procesamiento = $2
            WHERE message_sid = $3
            """,
            str(e), datetime.now(), MessageSid
        )
        
        # Responder con mensaje de error genérico
        twiml_resp = MessagingResponse()
        twiml_resp.message("Disculpe, tenemos problemas técnicos temporales. Por favor intente más tarde.")
        
        return Response(content=str(twiml_resp), media_type="application/xml")
```

### **Archivo 3: `backend/services/twilio_service.py`**

```python
"""
Twilio Service
==============

Servicio para enviar mensajes de WhatsApp vía Twilio.

Referencias:
- https://www.twilio.com/docs/whatsapp/api#send-a-message
"""

from twilio.rest import Client
import os
import logging

logger = logging.getLogger(__name__)

class TwilioService:
    """Servicio de mensajería usando Twilio WhatsApp API."""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_PHONE_NUMBER")  # +16206986058
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_from]):
            raise ValueError("Twilio credentials not configured in environment")
        
        self.client = Client(self.account_sid, self. auth_token)
        logger.info(f"✅ TwilioService initialized with number {self.whatsapp_from}")
    
    async def enviar_mensaje(self, to_number: str, mensaje: str) -> dict:
        """
        Envía mensaje de WhatsApp via Twilio.
        
        Args:
            to_number:  Número de teléfono (sin "whatsapp:" prefix)
            mensaje: Texto a enviar
            
        Returns: 
            Dict con resultado:  {
                "success": bool,
                "message_sid": str,
                "status":  str,
                "error": Optional[str]
            }
        """
        try:
            # Normalizar número
            if not to_number.startswith("+"):
                to_number = f"+{to_number}"
            
            # Enviar mensaje
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_from}',
                body=mensaje,
                to=f'whatsapp:{to_number}'
            )
            
            logger.info(f"📤 Mensaje enviado a {to_number}: {message. sid}")
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status":  message.status,
                "to":  to_number
            }
        
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje a {to_number}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "to": to_number
            }
    
    async def enviar_recordatorio_cita(
        self,
        paciente_telefono: str,
        paciente_nombre: str,
        fecha_cita: str,
        hora_cita: str,
        tratamiento: str
    ) -> dict:
        """
        Envía recordatorio de cita estructurado.
        
        Args:
            paciente_telefono: Teléfono del paciente
            paciente_nombre: Nombre del paciente
            fecha_cita: Fecha de la cita (formato: "15/01/2026")
            hora_cita:  Hora de la cita (formato: "14:00")
            tratamiento: Nombre del tratamiento
            
        Returns:
            Dict con resultado del envío
        """
        mensaje = f"""Hola {paciente_nombre}, le recordamos su cita: 

📅 Fecha: {fecha_cita}
🕐 Hora: {hora_cita}
👨‍⚕️ Tratamiento: {tratamiento}
📍 Clínica Podoskin

Para confirmar responda:  SÍ
Para cancelar responda: NO"""
        
        return await self. enviar_mensaje(paciente_telefono, mensaje)


# Instancia global
_twilio_service = None

def get_twilio_service() -> TwilioService: 
    """Obtiene instancia singleton del servicio Twilio."""
    global _twilio_service
    
    if _twilio_service is None:
        _twilio_service = TwilioService()
    
    return _twilio_service
```

---

## 🤖 Agente Maya - LangGraph v1+ Optimizado

### **Archivo 4: `backend/agents/sub_agent_whatsApp/state.py` (MODIFICADO)**

```python
"""
WhatsApp Agent State
====================

TypedDict para el estado del agente con LangGraph v1+. 

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents
- https://docs.langchain.com/oss/python/concepts/memory
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, AnyMessage
from operator import add

class WhatsAppAgentState(TypedDict):
    """
    Estado del agente WhatsApp con memory thread-scoped.
    
    🔑 CLAVE: contact_id se usa como thread_id para aislar conversaciones por paciente. 
    """
    
    # Messages (gestionado por LangGraph)
    messages: Annotated[Sequence[BaseMessage], add]
    
    # 🔑 Thread-scoped identifiers
    contact_id: str        # ID del contacto (usado como thread_id)
    conversation_id: str   # ID de la conversación actual
    
    # Mensaje actual a procesar
    message: str
    
    # Contexto recuperado
    retrieved_context: str
    fuente: str  # 'sql_estructurado', 'knowledge_base_validated', 'contexto_conversacional'
    confidence: float
    
    # Metadata estructurada
    metadata: dict
    
    # Control de flujo
    requires_human: bool
    escalation_reason: Optional[str]
    next_action: Optional[str]
    
    # Respuesta final
    response: Optional[str]
```

### **Archivo 5: `backend/agents/sub_agent_whatsApp/graph.py` (MODIFICADO)**

```python
"""
WhatsApp Agent Graph - LangGraph v1+
====================================

Grafo optimizado con: 
- ToolRuntime para acceso a state/context
- Checkpointer para persistence
- Conditional routing por confidence
- Interrupt/resume para human-in-the-loop

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents
- https://docs.langchain.com/oss/python/langgraph/agentic-rag
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
import logging

from .state import WhatsAppAgentState
from .nodes import (
    node_router,
    node_rag_manager,
    node_human_escalation,
    node_learning_curator,
    node_generate_response
)

logger = logging.getLogger(__name__)

# ============================================================================
# ROUTING CONDICIONAL
# ============================================================================

def route_by_confidence(state: WhatsAppAgentState) -> str:
    """
    Enruta basado en confidence y requires_human.
    
    Flujo:
    - confidence >= 0.80 → generate_response
    - confidence < 0.80 → human_escalation
    - requires_human = True → human_escalation
    """
    if state. get('requires_human', False):
        return "human_escalation"
    
    confidence = state.get('confidence', 0.0)
    
    if confidence >= 0.80:
        return "generate_response"
    else:
        logger.warning(f"⚠️ Confidence baja ({confidence:.2f}), escalando a humano")
        return "human_escalation"

# ============================================================================
# CREAR AGENTE
# ============================================================================

def create_whatsapp_agent():
    """
    Crea el agente WhatsApp con LangGraph v1+.
    
    Retorna:
        CompiledGraph con checkpointer para persistence
        
    Referencias:
    - https://docs.langchain.com/oss/python/langgraph/workflows-agents#create-agent
    """
    
    # Crear grafo
    graph = StateGraph(WhatsAppAgentState)
    
    # Agregar nodos
    graph.add_node("router", node_router)
    graph.add_node("rag_manager", node_rag_manager)
    graph.add_node("generate_response", node_generate_response)
    graph.add_node("human_escalation", node_human_escalation)
    graph.add_node("learning_curator", node_learning_curator)
    
    # Edges fijos
    graph.add_edge(START, "router")
    graph.add_edge("router", "rag_manager")
    
    # Conditional edge basado en confidence
    graph.add_conditional_edges(
        "rag_manager",
        route_by_confidence,
        {
            "generate_response": "generate_response",
            "human_escalation": "human_escalation"
        }
    )
    
    # generate_response → END
    graph.add_edge("generate_response", END)
    
    # human_escalation → learning_curator (después de admin responde)
    graph.add_edge("human_escalation", "learning_curator")
    
    # learning_curator → END
    graph.add_edge("learning_curator", END)
    
    # Compilar con checkpointer (persistence por thread_id)
    checkpointer = MemorySaver()
    
    app = graph.compile(checkpointer=checkpointer)
    
    logger.info("✅ Agente WhatsApp compilado con LangGraph v1+")
    
    return app
```

---

## 🛠️ Tools Especializadas

### **Archivo 6: `backend/agents/sub_agent_whatsApp/tools/__init__.py`**

```python
"""
Tools para el Agente Maya
=========================

Tools especializadas con ToolRuntime para acceso a state. 

Referencias:
- https://docs.langchain.com/oss/python/langchain/tools
"""

from .sql_tools import (
    consultar_tratamientos_sql,
    consultar_horarios_sql,
    consultar_citas_sql,
    calcular_disponibilidad
)

from .kb_tools import (
    buscar_knowledge_base_validada,
    registrar_feedback_kb
)

from .context_tools import (
    buscar_conversaciones_previas,
    guardar_resumen_conversacion
)

from .filter_tools import (
    check_filters
)

from .behavior_tools import (
    get_active_behavior_rules
)

__all__ = [
    "consultar_tratamientos_sql",
    "consultar_horarios_sql",
    "consultar_citas_sql",
    "calcular_disponibilidad",
    "buscar_knowledge_base_validada",
    "registrar_feedback_kb",
    "buscar_conversaciones_previas",
    "guardar_resumen_conversacion",
    "check_filters",
    "get_active_behavior_rules"
]
```

### **Archivo 7: `backend/agents/sub_agent_whatsApp/tools/sql_tools. py` (NUEVO)**

```python
"""
SQL Tools - Prioridad 1
=======================

Tools para consultar base de datos estructurada (FUENTE DE VERDAD).

⚠️ CRÍTICO: Estas tools tienen prioridad MÁXIMA sobre cualquier búsqueda vectorial.
"""

from langchain. tools import tool, ToolRuntime
from typing import Annotated
import logging
import re

from db import get_pool

logger = logging.getLogger(__name__)

# ============================================================================
# TOOL 1: Consultar Tratamientos/Servicios/Precios
# ============================================================================

@tool
async def consultar_tratamientos_sql(
    query:  Annotated[str, "Término de búsqueda del tratamiento/servicio"],
    runtime: ToolRuntime
) -> str:
    """
    🔑 PRIORIDAD 1: Consulta servicios, tratamientos y precios desde SQL estructurado.
    
    ⚠️ NUNCA usar embeddings para precios/servicios.
    
    Args:
        query:  Término de búsqueda (ej: "onicomicosis", "plantillas", "láser")
        runtime: Contexto de ejecución (acceso a state)
        
    Returns:
        JSON string con servicios encontrados
        
    Referencias:
    - https://docs.langchain.com/oss/python/langchain/tools#tool-runtime
    """
    pool = get_pool()
    
    # Limpiar término de búsqueda
    search_term = query.strip().lower()
    
    logger.info(f"🔍 [SQL Tool] Buscando tratamientos:  '{search_term}'")
    
    try:
        sql_query = """
            SELECT 
                nombre_servicio,
                descripcion,
                precio_base,
                duracion_minutos,
                requiere_anestesia,
                sesiones_estimadas,
                categoria_servicio
            FROM catalogo_servicios
            WHERE activo = true
            AND (
                LOWER(nombre_servicio) ILIKE $1
                OR LOWER(descripcion) ILIKE $1
                OR LOWER(categoria_servicio) ILIKE $1
            )
            ORDER BY 
                CASE 
                    WHEN LOWER(nombre_servicio) = $2 THEN 1  -- Exact match primero
                    WHEN LOWER(nombre_servicio) ILIKE $1 THEN 2
                    ELSE 3
                END,
                nombre_servicio
            LIMIT 5
        """
        
        rows = await pool.fetch(sql_query, f"%{search_term}%", search_term)
        
        if not rows:
            logger.warning(f"⚠️ No se encontraron tratamientos para:  '{search_term}'")
            return "No se encontraron servicios con ese término.  Por favor, solicita información al equipo de la clínica."
        
        # Formatear resultados
        resultados = []
        for row in rows:
            resultado = {
                "nombre":  row['nombre_servicio'],
                "descripcion": row['descripcion'],
                "precio":  f"${row['precio_base']: ,.2f} MXN",
                "duracion": f"{row['duracion_minutos']} minutos",
                "requiere_anestesia": "Sí" if row['requiere_anestesia'] else "No",
                "sesiones":  row['sesiones_estimadas'] or "1",
                "categoria": row['categoria_servicio']
            }
            resultados.append(resultado)
        
        logger.info(f"✅ [SQL Tool] Encontrados {len(resultados)} servicios")
        
        # Actualizar state metadata
        if runtime.state: 
            runtime.state['metadata']['tabla_consultada'] = 'catalogo_servicios'
            runtime.state['metadata']['resultados_count'] = len(resultados)
        
        import json
        return json.dumps(resultados, ensure_ascii=False, indent=2)
    
    except Exception as e: 
        logger.error(f"❌ Error consultando tratamientos: {e}", exc_info=True)
        return f"Error consultando servicios: {str(e)}"


# ============================================================================
# TOOL 2: Consultar Horarios
# ============================================================================

@tool
async def consultar_horarios_sql(
    dia_semana: Annotated[int, "Día de la semana (0=Domingo, 6=Sábado)"],
    runtime: ToolRuntime
) -> str:
    """
    🔑 PRIORIDAD 1: Consulta horarios de atención desde SQL estructurado.
    
    Args:
        dia_semana:  0=Domingo, 1=Lunes, ..., 6=Sábado
        runtime: Contexto de ejecución
        
    Returns:
        JSON string con horarios disponibles
    """
    pool = get_pool()
    
    logger.info(f"🔍 [SQL Tool] Consultando horarios para día {dia_semana}")
    
    try:
        sql_query = """
            SELECT 
                p.nombre_completo as podologo,
                ht.hora_inicio,
                ht. hora_fin,
                ht.duracion_cita_minutos,
                ht. tiempo_buffer_minutos
            FROM horarios_trabajo ht
            INNER JOIN podologos p ON ht.id_podologo = p.id
            WHERE ht.dia_semana = $1
            AND ht.activo = true
            AND p.activo = true
            AND (
                ht.fecha_fin_vigencia IS NULL 
                OR ht.fecha_fin_vigencia >= CURRENT_DATE
            )
            ORDER BY ht.hora_inicio
        """
        
        rows = await pool.fetch(sql_query, dia_semana)
        
        if not rows:
            return f"No hay horarios de atención disponibles para ese día."
        
        # Formatear resultados
        resultados = []
        for row in rows:
            resultado = {
                "podologo": row['podologo'],
                "hora_inicio": str(row['hora_inicio']),
                "hora_fin": str(row['hora_fin']),
                "duracion_cita": row['duracion_cita_minutos']
            }
            resultados. append(resultado)
        
        logger.info(f"✅ [SQL Tool] Encontrados {len(resultados)} horarios")
        
        if runtime.state:
            runtime. state['metadata']['tabla_consultada'] = 'horarios_trabajo'
        
        import json
        return json.dumps(resultados, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error consultando horarios: {e}", exc_info=True)
        return f"Error consultando horarios: {str(e)}"


# ============================================================================
# TOOL 3: Consultar Citas del Paciente
# ============================================================================

@tool
async def consultar_citas_sql(
    contact_id: Annotated[int, "ID del contacto/paciente"],
    runtime: ToolRuntime
) -> str:
    """
    🔑 PRIORIDAD 1: Consulta citas del paciente desde SQL estructurado. 
    
    Args:
        contact_id: ID del contacto
        runtime: Contexto de ejecución
        
    Returns: 
        JSON string con citas del paciente
    """
    pool = get_pool()
    
    logger.info(f"🔍 [SQL Tool] Consultando citas del contacto {contact_id}")
    
    try:
        # Obtener id_paciente del contacto
        paciente_id = await pool.fetchval(
            "SELECT id_paciente FROM contactos WHERE id = $1",
            contact_id
        )
        
        if not paciente_id:
            return "No se encontró información del paciente asociado a este contacto."
        
        sql_query = """
            SELECT 
                c.id,
                c.fecha_hora_inicio,
                c.fecha_hora_fin,
                c.tipo_cita,
                c. estado,
                c.motivo_consulta,
                p.nombre_completo as podologo,
                t.nombre_servicio as tratamiento
            FROM citas c
            INNER JOIN podologos p ON c.id_podologo = p.id
            LEFT JOIN tratamientos_cita tc ON tc.id_cita = c.id
            LEFT JOIN tratamientos t ON tc.id_tratamiento = t.id
            WHERE c.id_paciente = $1
            AND c.estado NOT IN ('Cancelada', 'No_Asistio')
            AND c.fecha_hora_inicio >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY c.fecha_hora_inicio DESC
            LIMIT 10
        """
        
        rows = await pool. fetch(sql_query, paciente_id)
        
        if not rows:
            return "No se encontraron citas recientes o próximas para este paciente."
        
        # Formatear resultados
        resultados = []
        for row in rows:
            resultado = {
                "id": row['id'],
                "fecha":  row['fecha_hora_inicio']. strftime("%d/%m/%Y"),
                "hora":  row['fecha_hora_inicio']. strftime("%H:%M"),
                "tipo":  row['tipo_cita'],
                "estado": row['estado'],
                "podologo": row['podologo'],
                "tratamiento": row['tratamiento'] or "No especificado"
            }
            resultados.append(resultado)
        
        logger. info(f"✅ [SQL Tool] Encontradas {len(resultados)} citas")
        
        if runtime. state:
            runtime.state['metadata']['tabla_consultada'] = 'citas'
        
        import json
        return json.dumps(resultados, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"❌ Error consultando citas: {e}", exc_info=True)
        return f"Error consultando citas:  {str(e)}"


# ============================================================================
# TOOL 4: Calcular Disponibilidad
# ============================================================================

@tool
async def calcular_disponibilidad(
    fecha:  Annotated[str, "Fecha en formato YYYY-MM-DD"],
    id_podologo: Annotated[int, "ID del podólogo (opcional)"] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    🔑 PRIORIDAD 1: Calcula slots disponibles para una fecha.
    
    Args:
        fecha: Fecha en formato ISO (YYYY-MM-DD)
        id_podologo: ID del podólogo (opcional)
        runtime: Contexto de ejecución
        
    Returns: 
        JSON string con slots disponibles
    """
    pool = get_pool()
    
    logger.info(f"🔍 [SQL Tool] Calculando disponibilidad para {fecha}")
    
    try:
        # Llamar a función PostgreSQL (reutilizar l��gica existente)
        sql_query = """
            SELECT * FROM calcular_disponibilidad($1, $2)
        """
        
        rows = await pool.fetch(sql_query, fecha, id_podologo)
        
        slots_disponibles = [
            {
                "hora":  str(row['hora_slot']),
                "disponible":  row['disponible'],
                "podologo_id": row. get('id_podologo')
            }
            for row in rows
            if row['disponible']
        ]
        
        logger.info(f"✅ [SQL Tool] {len(slots_disponibles)} slots disponibles")
        
        import json
        return json.dumps(slots_disponibles, ensure_ascii=False, indent=2)
    
    except Exception as e: 
        logger.error(f"❌ Error calculando disponibilidad: {e}", exc_info=True)
        return f"Error calculando disponibilidad: {str(e)}"
```

---

# 📘 PROMPT COMPLETO - PARTE 2/2

---

## 🛠️ Tools Especializadas (Continuación)

### **Archivo 8: `backend/agents/sub_agent_whatsApp/tools/kb_tools.py` (NUEVO)**

```python
"""
Knowledge Base Tools - Prioridad 2
===================================

Tools para consultar knowledge base validada (pgvector).

⚠️ Solo para FAQs, políticas y procedimientos.  NUNCA precios/horarios/servicios. 

Referencias:
- https://docs.langchain.com/oss/python/concepts/memory#vector-stores
"""

from langchain.tools import tool, ToolRuntime
from typing import Annotated
import logging
import numpy as np
import pickle

from db import get_pool
from .. utils.embeddings import get_embeddings_service

logger = logging.getLogger(__name__)

# ============================================================================
# TOOL:  Buscar en Knowledge Base Validada
# ============================================================================

@tool
async def buscar_knowledge_base_validada(
    query: Annotated[str, "Pregunta del usuario"],
    runtime: ToolRuntime
) -> str:
    """
    🔑 PRIORIDAD 2: Busca en knowledge base validada usando similitud coseno.
    
    ⚠️ Solo conocimiento general. NO precios, horarios ni servicios.
    
    Args:
        query: Pregunta del usuario
        runtime: Contexto de ejecución
        
    Returns:
        JSON string con respuesta encontrada o mensaje de no encontrado
        
    Referencias:
    - https://docs.langchain.com/oss/python/langgraph/agentic-rag#vector-search
    """
    pool = get_pool()
    embeddings_service = get_embeddings_service()
    
    logger.info(f"🔍 [KB Tool] Buscando en knowledge base:  '{query[: 50]}...'")
    
    try:
        # Generar embedding de la consulta
        query_embedding = embeddings_service.embed_query(query)
        query_embedding_bytes = pickle.dumps(query_embedding)
        
        # Buscar en KB con pgvector (cosine similarity)
        # Usando operador <=> de pgvector para distancia coseno
        sql_query = """
            SELECT 
                id,
                pregunta,
                respuesta,
                categoria,
                pregunta_embedding,
                veces_consultada,
                efectividad_score
            FROM knowledge_base_validated
            WHERE aprobado = true
            AND contiene_datos_operativos = false
            AND categoria IN ('FAQ_Proceso', 'Politica_Clinica', 'Informacion_General', 'Procedimiento_Medico')
            ORDER BY fecha_creacion DESC
            LIMIT 50
        """
        
        rows = await pool.fetch(sql_query)
        
        if not rows:
            logger.warning("⚠️ No hay entries en knowledge base validada")
            return "No se encontró información relevante en la base de conocimiento."
        
        # Calcular similitud coseno con cada entry
        best_match = None
        best_similarity = 0.0
        
        for row in rows:
            kb_embedding = pickle.loads(row['pregunta_embedding'])
            
            # Similitud coseno normalizada (0-1)
            similarity = float(np.dot(query_embedding, kb_embedding) / 
                             (np.linalg.norm(query_embedding) * np.linalg.norm(kb_embedding)))
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = row
        
        # Umbral de confianza:  0.85
        MIN_CONFIDENCE = 0.85
        
        if best_match and best_similarity >= MIN_CONFIDENCE:
            # Incrementar contador de uso
            await pool.execute(
                "UPDATE knowledge_base_validated SET veces_consultada = veces_consultada + 1, fecha_ultimo_uso = NOW() WHERE id = $1",
                best_match['id']
            )
            
            logger. info(f"✅ [KB Tool] Match encontrado (similarity: {best_similarity:.3f})")
            
            # Actualizar state metadata
            if runtime.state:
                runtime.state['metadata']['kb_id'] = best_match['id']
                runtime.state['metadata']['kb_categoria'] = best_match['categoria']
                runtime.state['metadata']['similarity'] = best_similarity
            
            import json
            return json.dumps({
                "encontrado": True,
                "pregunta": best_match['pregunta'],
                "respuesta": best_match['respuesta'],
                "categoria": best_match['categoria'],
                "confidence": round(best_similarity, 3)
            }, ensure_ascii=False, indent=2)
        else:
            logger.warning(f"⚠️ [KB Tool] Similarity muy baja:  {best_similarity:.3f} (min: {MIN_CONFIDENCE})")
            return json.dumps({
                "encontrado": False,
                "confidence": round(best_similarity, 3) if best_match else 0.0,
                "mensaje": "No se encontró información suficientemente relevante."
            })
    
    except Exception as e: 
        logger.error(f"❌ Error buscando en KB: {e}", exc_info=True)
        return f"Error consultando base de conocimiento: {str(e)}"


# ============================================================================
# TOOL: Registrar Feedback de KB
# ============================================================================

@tool
async def registrar_feedback_kb(
    kb_id:  Annotated[int, "ID de la entry de KB"],
    feedback: Annotated[str, "positivo o negativo"],
    runtime: ToolRuntime
) -> str:
    """
    Registra feedback de usuario sobre una respuesta de KB.
    
    Args:
        kb_id:  ID de la entry en knowledge_base_validated
        feedback: "positivo" o "negativo"
        runtime: Contexto de ejecución
        
    Returns:
        Mensaje de confirmación
    """
    pool = get_pool()
    
    try:
        if feedback == "positivo":
            await pool.execute(
                "UPDATE knowledge_base_validated SET feedback_positivo = feedback_positivo + 1 WHERE id = $1",
                kb_id
            )
        elif feedback == "negativo":
            await pool.execute(
                "UPDATE knowledge_base_validated SET feedback_negativo = feedback_negativo + 1 WHERE id = $1",
                kb_id
            )
        else:
            return "Feedback inválido. Use 'positivo' o 'negativo'."
        
        logger.info(f"✅ [KB Tool] Feedback '{feedback}' registrado para KB #{kb_id}")
        return f"Feedback '{feedback}' registrado correctamente."
    
    except Exception as e:
        logger.error(f"❌ Error registrando feedback: {e}", exc_info=True)
        return f"Error registrando feedback: {str(e)}"
```

### **Archivo 9: `backend/agents/sub_agent_whatsApp/tools/context_tools.py` (NUEVO)**

```python
"""
Context Tools - Prioridad 3
============================

Tools para contexto conversacional aislado por paciente.

⚠️ CRÍTICO: Siempre filtrar por id_contacto (thread-scoped).

Referencias:
- https://docs.langchain.com/oss/python/concepts/memory#user-specific-memory
"""

from langchain.tools import tool, ToolRuntime
from typing import Annotated
import logging
import numpy as np
import pickle

from db import get_pool
from ..utils.embeddings import get_embeddings_service

logger = logging.getLogger(__name__)

# ============================================================================
# TOOL: Buscar Conversaciones Previas (Aisladas por Paciente)
# ============================================================================

@tool
async def buscar_conversaciones_previas(
    query: Annotated[str, "Consulta del usuario"],
    contact_id: Annotated[int, "ID del contacto (thread-scoped)"],
    runtime: ToolRuntime
) -> str:
    """
    🔑 PRIORIDAD 3: Busca en conversaciones previas DEL MISMO paciente.
    
    ��️ AISLAMIENTO:  Solo busca conversaciones de contact_id especificado.
    
    Args:
        query: Consulta del usuario
        contact_id:  ID del contacto (thread-scoped)
        runtime: Contexto de ejecución
        
    Returns:
        JSON string con conversaciones similares o mensaje vacío
        
    Referencias: 
    - https://docs.langchain.com/oss/python/concepts/memory#isolation
    """
    pool = get_pool()
    embeddings_service = get_embeddings_service()
    
    logger.info(f"🔍 [Context Tool] Buscando contexto del contacto {contact_id}")
    
    try:
        # Generar embedding de la consulta
        query_embedding = embeddings_service. embed_query(query)
        
        # ⚠️ FILTRO CRÍTICO: WHERE id_contacto = $1
        sql_query = """
            SELECT 
                id,
                id_conversacion,
                resumen_conversacion,
                embedding,
                metadata,
                fecha_creacion
            FROM conversaciones_embeddings
            WHERE id_contacto = $1
            ORDER BY fecha_creacion DESC
            LIMIT 20
        """
        
        rows = await pool.fetch(sql_query, contact_id)
        
        if not rows:
            logger.info(f"ℹ️ No hay conversaciones previas del contacto {contact_id}")
            return json.dumps({
                "encontrado": False,
                "mensaje": "No hay conversaciones previas de este paciente."
            })
        
        # Calcular similitud coseno
        results = []
        
        for row in rows:
            conv_embedding = pickle.loads(row['embedding'])
            
            similarity = float(np.dot(query_embedding, conv_embedding) / 
                             (np.linalg.norm(query_embedding) * np.linalg.norm(conv_embedding)))
            
            if similarity >= 0.75:  # Umbral para contexto
                results.append({
                    'conversacion_id': row['id_conversacion'],
                    'resumen':  row['resumen_conversacion'],
                    'similarity': round(similarity, 3),
                    'fecha': row['fecha_creacion']. isoformat(),
                    'metadata': row['metadata']
                })
        
        # Ordenar por similitud
        results. sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:3]  # Top 3
        
        if results:
            logger.info(f"✅ [Context Tool] {len(results)} conversaciones similares encontradas")
            
            # Actualizar última consulta
            for r in results:
                await pool.execute(
                    "UPDATE conversaciones_embeddings SET fecha_ultima_consulta = NOW() WHERE id_conversacion = $1",
                    r['conversacion_id']
                )
            
            if runtime.state:
                runtime. state['metadata']['context_conversations'] = [r['conversacion_id'] for r in results]
            
            import json
            return json.dumps({
                "encontrado": True,
                "conversaciones": results,
                "contact_id": contact_id
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "encontrado": False,
                "mensaje": "No se encontraron conversaciones previas relevantes."
            })
    
    except Exception as e:
        logger.error(f"❌ Error buscando contexto:  {e}", exc_info=True)
        return f"Error consultando conversaciones previas: {str(e)}"


# ============================================================================
# TOOL: Guardar Resumen de Conversación
# ============================================================================

@tool
async def guardar_resumen_conversacion(
    contact_id: Annotated[int, "ID del contacto"],
    conversation_id: Annotated[int, "ID de la conversación"],
    resumen: Annotated[str, "Resumen de la conversación"],
    metadata: Annotated[dict, "Metadata adicional"],
    runtime: ToolRuntime
) -> str:
    """
    Guarda resumen de conversación con embedding para futuras búsquedas.
    
    Args:
        contact_id: ID del contacto (aislamiento)
        conversation_id: ID de la conversación
        resumen: Resumen textual de la conversación
        metadata:  Metadata adicional (topicos, tipo_consulta, etc.)
        runtime: Contexto de ejecución
        
    Returns:
        Mensaje de confirmación
    """
    pool = get_pool()
    embeddings_service = get_embeddings_service()
    
    try:
        # Generar embedding del resumen
        embedding = embeddings_service.embed_query(resumen)
        embedding_bytes = pickle.dumps(embedding)
        
        # Insertar en BD
        await pool.execute(
            """
            INSERT INTO conversaciones_embeddings 
            (id_contacto, id_conversacion, resumen_conversacion, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id_conversacion) 
            DO UPDATE SET 
                resumen_conversacion = EXCLUDED.resumen_conversacion,
                embedding = EXCLUDED. embedding,
                metadata = EXCLUDED.metadata
            """,
            contact_id, conversation_id, resumen, embedding_bytes, metadata
        )
        
        logger. info(f"✅ [Context Tool] Resumen guardado para conversación {conversation_id}")
        return "Resumen de conversación guardado correctamente."
    
    except Exception as e: 
        logger.error(f"❌ Error guardando resumen:  {e}", exc_info=True)
        return f"Error guardando resumen: {str(e)}"
```

### **Archivo 10: `backend/agents/sub_agent_whatsApp/tools/filter_tools.py` (NUEVO)**

```python
"""
Filter Tools
============

Tools para aplicar filtros de entrada (blacklist/whitelist/grupos).

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#conditional-routing
"""

import logging
from db import get_pool

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIÓN: Check Filters
# ============================================================================

async def check_filters(phone:  str, is_group: bool = False, group_id: str = None) -> dict:
    """
    Verifica si un número o grupo está en blacklist/whitelist. 
    
    Args:
        phone: Número de teléfono
        is_group: Si es un grupo
        group_id: ID del grupo (si aplica)
        
    Returns: 
        Dict con resultado:  {
            "blocked": bool,
            "reason": str,
            "filter_type": str
        }
    """
    pool = get_pool()
    
    try:
        # Verificar blacklist
        if is_group and group_id:
            blacklisted = await pool.fetchrow(
                "SELECT * FROM whatsapp_filters WHERE tipo = 'grupo_bloqueado' AND valor = $1 AND activo = true",
                group_id
            )
        else:
            blacklisted = await pool.fetchrow(
                "SELECT * FROM whatsapp_filters WHERE tipo = 'blacklist' AND valor = $1 AND activo = true",
                phone
            )
        
        if blacklisted:
            logger.warning(f"⛔ Bloqueado: {phone} - Razón: {blacklisted['razon']}")
            return {
                "blocked": True,
                "reason": blacklisted['razon'] or "Número en blacklist",
                "filter_type": "blacklist"
            }
        
        # Verificar si hay whitelist activa (modo restrictivo)
        whitelist_exists = await pool.fetchval(
            "SELECT EXISTS(SELECT 1 FROM whatsapp_filters WHERE tipo = 'whitelist' AND activo = true)"
        )
        
        if whitelist_exists:
            # Si hay whitelist, verificar que el número esté en ella
            in_whitelist = await pool.fetchval(
                "SELECT EXISTS(SELECT 1 FROM whatsapp_filters WHERE tipo = 'whitelist' AND valor = $1 AND activo = true)",
                phone
            )
            
            if not in_whitelist: 
                logger.warning(f"⛔ No en whitelist: {phone}")
                return {
                    "blocked":  True,
                    "reason": "Número no autorizado (whitelist activa)",
                    "filter_type": "whitelist"
                }
        
        # Permitido
        return {
            "blocked": False,
            "reason":  None,
            "filter_type":  None
        }
    
    except Exception as e: 
        logger.error(f"❌ Error verificando filtros: {e}", exc_info=True)
        # En caso de error, permitir (fail-open)
        return {
            "blocked": False,
            "reason": f"Error verificando filtros: {str(e)}",
            "filter_type":  "error"
        }
```

### **Archivo 11: `backend/agents/sub_agent_whatsApp/tools/behavior_tools.py` (NUEVO)**

```python
"""
Behavior Tools
==============

Tools para obtener reglas de comportamiento activas y dinámicas.

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#dynamic-prompts
"""

import logging
from db import get_pool

logger = logging.getLogger(__name__)

# ============================================================================
# FUNCIÓN: Get Active Behavior Rules
# ============================================================================

async def get_active_behavior_rules() -> list:
    """
    Obtiene reglas de comportamiento activas y aprobadas para inyectar al System Prompt.
    
    Returns:
        Lista de dicts con reglas:   [
            {
                "id": int,
                "pattern": str,
                "correction_logic": str,
                "categoria": str,
                "prioridad": int
            }
        ]
    """
    pool = get_pool()
    
    try:
        sql_query = """
            SELECT 
                id,
                pattern,
                correction_logic,
                categoria,
                prioridad
            FROM behavior_rules
            WHERE activo = true
            AND aprobado = true
            ORDER BY prioridad ASC, fecha_creacion DESC
            LIMIT 20
        """
        
        rows = await pool.fetch(sql_query)
        
        rules = [dict(row) for row in rows]
        
        logger.info(f"✅ [Behavior Tool] {len(rules)} reglas activas obtenidas")
        
        return rules
    
    except Exception as e: 
        logger.error(f"❌ Error obteniendo behavior rules: {e}", exc_info=True)
        return []


async def increment_behavior_rule_usage(rule_id: int):
    """Incrementa contador de uso de una regla."""
    pool = get_pool()
    
    try:
        await pool.execute(
            "UPDATE behavior_rules SET veces_utilizada = veces_utilizada + 1, ultima_utilizacion = NOW() WHERE id = $1",
            rule_id
        )
    except Exception as e:
        logger. error(f"❌ Error incrementando uso de regla: {e}")
```

---

## 📊 Node RAG Manager Mejorado

### **Archivo 12: `backend/agents/sub_agent_whatsApp/nodes/rag_manager.py` (MODIFICADO)**

```python
"""
RAG Manager Node - Búsqueda Dual Optimizada
============================================

Implementa búsqueda con prioridades estrictas: 
1. SQL estructurado (FUENTE DE VERDAD)
2. Knowledge Base validada (pgvector)
3. Contexto conversacional (aislado por contacto)

Referencias:
- https://docs.langchain.com/oss/python/langgraph/agentic-rag
"""

import logging
from typing import Dict, Any
import re

from .. state import WhatsAppAgentState
from ..tools import (
    consultar_tratamientos_sql,
    consultar_horarios_sql,
    consultar_citas_sql,
    buscar_knowledge_base_validada,
    buscar_conversaciones_previas
)

logger = logging.getLogger(__name__)

# ============================================================================
# NODE: RAG Manager
# ============================================================================

async def node_rag_manager(state: WhatsAppAgentState) -> Dict[str, Any]: 
    """
    Nodo de búsqueda dual con prioridades estrictas. 
    
    Flujo:
    1. Clasificar tipo de consulta
    2. PRIORIDAD 1: Buscar en SQL estructurado
    3. PRIORIDAD 2: Buscar en Knowledge Base validada
    4. PRIORIDAD 3: Buscar en contexto conversacional
    5. Si nada funciona:  Escalar a humano
    
    Args: 
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con contexto recuperado
    """
    query = state['message']
    contact_id = int(state['contact_id'])
    
    logger.info(f"🔍 [RAG Manager] Procesando consulta del contacto {contact_id}")
    
    # ========================================================================
    # PASO 1: Clasificar tipo de consulta
    # ========================================================================
    tipo_consulta = await clasificar_tipo_consulta(query)
    logger.info(f"📊 Tipo de consulta detectado: {tipo_consulta}")
    
    # ========================================================================
    # PASO 2: PRIORIDAD 1 - SQL Estructurado
    # ========================================================================
    
    if tipo_consulta in ['servicio', 'precio', 'tratamiento']: 
        logger.info("🔑 [PRIORIDAD 1] Consultando tabla estructurada:  tratamientos")
        
        # Extraer término de búsqueda
        termino = extraer_termino_tratamiento(query)
        
        if termino:
            result = await consultar_tratamientos_sql(termino, runtime=None)
            
            # Verificar si se encontró algo (parsear JSON)
            import json
            try:
                data = json.loads(result)
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"✅ Servicios encontrados en SQL: {len(data)}")
                    return {
                        **state,
                        'retrieved_context': result,
                        'fuente':  'sql_estructurado',
                        'confidence': 1.0,  # Máxima confianza
                        'metadata': {
                            'tipo_consulta': tipo_consulta,
                            'tabla':  'catalogo_servicios',
                            'termino_busqueda': termino
                        }
                    }
            except:
                pass
    
    if tipo_consulta in ['horario', 'disponibilidad']:
        logger.info("🔑 [PRIORIDAD 1] Consultando tabla estructurada: horarios_trabajo")
        
        # Extraer día de la semana
        dia_semana = extraer_dia_semana(query)
        
        if dia_semana is not None:
            result = await consultar_horarios_sql(dia_semana, runtime=None)
            
            import json
            try:
                data = json.loads(result)
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"✅ Horarios encontrados en SQL")
                    return {
                        **state,
                        'retrieved_context': result,
                        'fuente': 'sql_estructurado',
                        'confidence': 1.0,
                        'metadata': {
                            'tipo_consulta': tipo_consulta,
                            'tabla': 'horarios_trabajo',
                            'dia_semana': dia_semana
                        }
                    }
            except:
                pass
    
    if tipo_consulta == 'cita':
        logger.info("🔑 [PRIORIDAD 1] Consultando tabla estructurada: citas")
        
        result = await consultar_citas_sql(contact_id, runtime=None)
        
        import json
        try:
            data = json.loads(result)
            if "No se encontraron" not in result:
                logger.info(f"✅ Citas encontradas en SQL")
                return {
                    **state,
                    'retrieved_context': result,
                    'fuente': 'sql_estructurado',
                    'confidence': 1.0,
                    'metadata': {
                        'tipo_consulta': tipo_consulta,
                        'tabla': 'citas',
                        'contact_id': contact_id
                    }
                }
        except:
            pass
    
    # ========================================================================
    # PASO 3: PRIORIDAD 2 - Knowledge Base Validada (pgvector)
    # ========================================================================
    logger.info("🔑 [PRIORIDAD 2] Buscando en knowledge_base_validated")
    
    kb_result = await buscar_knowledge_base_validada(query, runtime=None)
    
    import json
    try: 
        kb_data = json.loads(kb_result)
        if kb_data.get('encontrado', False) and kb_data.get('confidence', 0) >= 0.85:
            logger.info(f"✅ Match en KB (confidence: {kb_data['confidence']})")
            return {
                **state,
                'retrieved_context': kb_result,
                'fuente': 'knowledge_base_validated',
                'confidence': kb_data['confidence'],
                'metadata': {
                    'tipo_consulta': tipo_consulta,
                    'kb_id': kb_data.get('kb_id'),
                    'categoria': kb_data.get('categoria')
                }
            }
    except:
        pass
    
    # ========================================================================
    # PASO 4: PRIORIDAD 3 - Contexto Conversacional (aislado)
    # ========================================================================
    logger.info(f"🔑 [PRIORIDAD 3] Buscando en conversaciones del contacto {contact_id}")
    
    context_result = await buscar_conversaciones_previas(query, contact_id, runtime=None)
    
    try:
        context_data = json.loads(context_result)
        if context_data.get('encontrado', False):
            conversations = context_data.get('conversaciones', [])
            if conversations:
                best_similarity = conversations[0]['similarity']
                logger.info(f"✅ Contexto conversacional encontrado (similarity: {best_similarity})")
                return {
                    **state,
                    'retrieved_context': context_result,
                    'fuente': 'contexto_conversacional',
                    'confidence':  best_similarity,
                    'metadata': {
                        'tipo_consulta': tipo_consulta,
                        'contact_id': contact_id,
                        'conversaciones_ids': [c['conversacion_id'] for c in conversations]
                    }
                }
    except:
        pass
    
    # ========================================================================
    # PASO 5: SI NADA FUNCIONA - Escalar a Humano
    # ========================================================================
    logger.warning(f"⚠️ No se encontró información para:  '{query[: 50]}...'")
    
    return {
        **state,
        'retrieved_context': "",
        'fuente': 'no_encontrado',
        'confidence': 0.0,
        'requires_human':  True,
        'escalation_reason': f'No se encontró información para la consulta: "{query}"',
        'metadata': {
            'tipo_consulta': tipo_consulta
        }
    }


# ============================================================================
# UTILIDADES
# ============================================================================

async def clasificar_tipo_consulta(query: str) -> str:
    """
    Clasifica el tipo de consulta del usuario.
    
    Returns:
        'servicio', 'precio', 'tratamiento', 'horario', 'disponibilidad', 'cita', 'general'
    """
    query_lower = query.lower()
    
    # Palabras clave por tipo
    keywords = {
        'servicio': ['servicio', 'tratamiento', 'ofrece', 'tratan', 'hacen'],
        'precio': ['precio', 'cuesta', 'costo', 'tarifa', 'cuánto', 'valor'],
        'tratamiento': ['onicomicosis', 'plantillas', 'callos', 'láser', 'uñas'],
        'horario': ['horario', 'hora', 'atienden', 'abierto', 'abren', 'cierran'],
        'disponibilidad': ['disponibilidad', 'disponible', 'cita', 'agendar', 'reservar'],
        'cita':  ['mi cita', 'mis citas', 'cita agendada', 'próxima cita']
    }
    
    # Verificar cada tipo
    for tipo, words in keywords.items():
        if any(word in query_lower for word in words):
            return tipo
    
    return 'general'


def extraer_termino_tratamiento(query: str) -> str:
    """
    Extrae término de búsqueda de tratamiento. 
    
    Returns:
        Término limpio o cadena vacía
    """
    query_lower = query.lower()
    
    # Quitar palabras comunes
    stop_words = ['cuánto', 'cuesta', 'precio', 'de', 'el', 'la', 'los', 'las', 'un', 'una', 
                  'tratamiento', 'servicio', 'para', 'qué', 'es']
    
    words = query_lower.split()
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    if filtered_words:
        return filtered_words[0]
    
    return ""


def extraer_dia_semana(query: str) -> int:
    """
    Extrae día de la semana de la consulta.
    
    Returns:
        0-6 (0=Domingo) o None si no se detecta
    """
    query_lower = query.lower()
    
    dias = {
        'domingo': 0,
        'lunes': 1,
        'martes':  2,
        'miércoles': 3,
        'miercoles': 3,
        'jueves': 4,
        'viernes':  5,
        'sábado': 6,
        'sabado': 6
    }
    
    for dia, num in dias.items():
        if dia in query_lower:
            return num
    
    # Si dice "hoy", calcular día actual
    if 'hoy' in query_lower:
        from datetime import datetime
        return datetime.now().weekday() + 1 if datetime.now().weekday() < 6 else 0
    
    return None
```

---
# 📘 PROMPT COMPLETO - PARTE 3/3 (INSTRUCCIONES PARA AGENTE)

---

## 🎯 INSTRUCCIONES PARA EL AGENTE COPILOT

### **Estilo de Implementación**

**⚠️ IMPORTANTE:** Este documento es una GUÍA de implementación, no código completo. El agente debe: 

1. ✅ **Analizar** la estructura propuesta
2. ✅ **Implementar** siguiendo los patrones de LangGraph v1+
3. ✅ **Adaptar** el código existente en `backend/agents/sub_agent_whatsApp/`
4. ✅ **Reutilizar** funciones y tools ya existentes
5. ✅ **Validar** cada componente antes de continuar

---

## 📊 Nodos Restantes a Implementar

### **NODO 1: Router (Filtros + Behavior Rules)**

**Ubicación:** `backend/agents/sub_agent_whatsApp/nodes/router.py`

**Responsabilidad:**
- Aplicar filtros (blacklist/whitelist)
- Consultar behavior rules activas
- Inyectar reglas al contexto del estado
- Clasificar intención inicial

**Estructura esperada:**

```python
"""
Node Router
===========

Primer nodo:  Aplica filtros y obtiene behavior rules. 

INSTRUCCIONES:
1. Importar check_filters de tools. filter_tools
2. Importar get_active_behavior_rules de tools.behavior_tools
3. Verificar si el número está bloqueado
4. Obtener reglas activas para inyectar después
5. Actualizar state con reglas y metadata
"""

async def node_router(state: WhatsAppAgentState) -> dict:
    """
    TODO: Implementar según las siguientes especificaciones:
    
    1. Extraer contact_id del state
    2. Llamar a check_filters() para validar
    3. Si blocked=True, retornar state con requires_human=True
    4. Llamar a get_active_behavior_rules()
    5. Guardar reglas en state['metadata']['behavior_rules']
    6. Retornar state actualizado
    
    Referencias:
    - https://docs.langchain.com/oss/python/langgraph/workflows-agents#nodes
    """
    
    # TODO: Implementar aquí
    pass
```

**Validación esperada:**
- [ ] Filtros aplicados correctamente
- [ ] Behavior rules obtenidas
- [ ] Metadata actualizada en state
- [ ] Números bloqueados rechazados

---

### **NODO 2: Generate Response**

**Ubicación:** `backend/agents/sub_agent_whatsApp/nodes/generate_response.py`

**Responsabilidad:**
- Construir System Prompt dinámico con behavior rules
- Llamar a Claude con contexto recuperado
- Generar respuesta natural
- Guardar metadata de generación

**System Prompt Dinámico - ESTRUCTURA:**

```python
"""
INSTRUCCIONES: 
1. Obtener behavior_rules del state['metadata']
2. Construir sección de reglas para el System Prompt
3. Incluir contexto recuperado en el prompt
4. Llamar a ChatAnthropic con prompt completo
5. Extraer respuesta y actualizar state
"""

def build_system_prompt(state: WhatsAppAgentState) -> str:
    """
    TODO: Construir System Prompt con la siguiente estructura:
    
    ## Rol
    Eres Maya, asistente virtual de Clínica Podoskin... 
    
    ## Reglas de Comportamiento Activas
    {Inyectar behavior_rules aquí}
    
    ## Contexto Recuperado
    {Inyectar retrieved_context aquí}
    
    ## Instrucciones
    - Responde en español mexicano
    - Tono profesional y empático
    - Si no tienes información, di "No tengo esa información..."
    
    Referencias:
    - https://docs.anthropic.com/claude/docs/system-prompts
    """
    
    # TODO: Implementar construcción dinámica
    pass


async def node_generate_response(state: WhatsAppAgentState) -> dict:
    """
    TODO:  Implementar según: 
    
    1. Construir system_prompt con build_system_prompt()
    2. Construir mensaje de usuario con state['message']
    3. Llamar a ChatAnthropic (claude-3-5-sonnet-20241022)
    4. Extraer respuesta del LLM
    5. Actualizar state['response']
    6. Guardar metadata de generación (tokens, tiempo, etc.)
    
    Referencias:
    - https://docs.langchain.com/oss/python/langchain/chat-models
    """
    
    # TODO: Implementar aquí
    pass
```

**Ejemplo de Behavior Rules inyectadas:**

```
## Reglas de Comportamiento Activas

1. [Prioridad 1] Consulta de Precios: 
   SIEMPRE consultar la tabla 'tratamientos' usando consultar_tratamientos_sql(). 
   NUNCA inventar precios ni basarse en conversaciones previas.

2. [Prioridad 1] Consulta de Horarios:
   SIEMPRE consultar 'horarios_trabajo' usando consultar_horarios_sql().
   NUNCA asumir horarios ni basarse en memoria.

3. [Prioridad 3] Tono Empático:
   Si detectas frustración o urgencia, responde con empatía.
   Usa frases como "Entiendo tu situación", "Permíteme ayudarte". 
```

---

### **NODO 3: Human Escalation**

**Ubicación:** `backend/agents/sub_agent_whatsApp/nodes/human_escalation.py`

**Responsabilidad:**
- Crear ticket en `dudas_pendientes`
- Actualizar conversación con `requiere_atencion=true`
- Notificar al frontend (opcional:  WebSocket)
- Usar `interrupt()` de LangGraph para pausar

**INSTRUCCIONES:**

```python
"""
INSTRUCCIONES:
1. Crear ticket en tabla dudas_pendientes con: 
   - id_conversacion
   - pregunta_original (state['message'])
   - contexto_mensaje (retrieved_context o vacío)
   - estado = 'pendiente'
   
2. Actualizar tabla conversaciones: 
   - requiere_atencion = true
   - notas_internas = escalation_reason
   
3. Generar respuesta al usuario:
   "Gracias por tu consulta. Un miembro de nuestro equipo 
    te responderá en breve con información específica."
   
4. Retornar state con response y requires_human=True

Referencias:
- https://docs.langchain.com/oss/python/langgraph/workflows-agents#human-in-the-loop
"""

async def node_human_escalation(state: WhatsAppAgentState) -> dict:
    # TODO: Implementar creación de ticket
    # TODO: Actualizar conversación
    # TODO: Generar respuesta de escalamiento
    # TODO: Retornar state actualizado
    pass
```

---

### **NODO 4: Learning Curator**

**Ubicación:** `backend/agents/sub_agent_whatsApp/nodes/learning_curator.py`

**Responsabilidad:**
- Procesar respuesta del admin (cuando responde)
- Aplicar `generalize_knowledge()` con LLM
- Aplicar `remove_pii()` 
- Guardar en `knowledge_base_validated` o `behavior_rules`

**INSTRUCCIONES:**

```python
"""
INSTRUCCIONES:
1. Recibir respuesta del admin desde dudas_pendientes
2. Llamar a generalize_knowledge() para sintetizar
3. Llamar a remove_pii() para anonimizar
4. Generar embedding de la regla sintetizada
5. Decidir si va a knowledge_base_validated o behavior_rules
6. Insertar en BD con aprobado=false (requiere aprobación)
7. Retornar state actualizado

Referencias:
- https://docs.langchain.com/oss/python/langgraph/agentic-rag#learning
"""

async def node_learning_curator(state: WhatsAppAgentState) -> dict:
    # TODO: Implementar curación de aprendizaje
    # TODO:  Llamar a utils.learning.generalize_knowledge()
    # TODO: Guardar en BD
    pass
```

---

## 🧰 Utilidades de Learning

### **Archivo: `backend/agents/sub_agent_whatsApp/utils/learning.py` (NUEVO)**

**INSTRUCCIONES DE IMPLEMENTACIÓN:**

```python
"""
Learning Utilities
==================

Funciones para generalizar conocimiento y remover PII. 

INSTRUCCIONES:
1. generalize_knowledge() debe:
   - Usar Claude para sintetizar respuesta específica en regla general
   - Ejemplo input: "El Dr.  Pérez no viene mañana"
   - Ejemplo output: "El Dr. Pérez no atiende los jueves"
   
2. remove_pii() debe:
   - Remover nombres propios (personas)
   - Remover números de teléfono
   - Remover direcciones específicas
   - Mantener información médica genérica
   
Referencias:
- https://docs.anthropic.com/claude/docs/prompt-engineering
"""

async def generalize_knowledge(respuesta_especifica: str) -> dict:
    """
    TODO: Implementar usando Claude con el siguiente prompt:
    
    System Prompt: 
    "Eres un experto en síntesis de conocimiento. Transforma 
    respuestas específicas en reglas generalizadas reutilizables."
    
    User Prompt:
    "Transforma esto en regla general: {respuesta_especifica}"
    
    Retornar:  {
        "regla_generalizada": str,
        "pattern": str,
        "categoria_sugerida": str
    }
    """
    pass


def remove_pii(text: str) -> str:
    """
    TODO: Implementar regex para remover: 
    - Nombres propios (detectar con NER básico o regex)
    - Teléfonos:  +52 XXX XXX XXXX
    - Emails
    - Direcciones completas
    
    Ejemplo: 
    Input:   "El paciente Juan Pérez vive en Calle 5 #123"
    Output: "El paciente [PACIENTE] vive en [DIRECCIÓN]"
    """
    pass
```

---

## 🎨 Frontend - Módulos de Gestión

### **MÓDULO 1: Sandbox de Simulación**

**Ubicación:** `Frontend/src/pages/WhatsAppSandbox.tsx`

**INSTRUCCIONES:**

```typescript
/*
REQUISITOS:
1. Interfaz de chat simulado (estilo WhatsApp)
2. Input para escribir mensaje como usuario
3. Botón "Enviar" que llama al agente
4. Mostrar respuesta del agente
5. Botones "👍 Útil" y "👎 No útil" por cada respuesta
6. Sidebar con metadata de la respuesta: 
   - Fuente (SQL, KB, Contexto)
   - Confidence score
   - Tiempo de respuesta
   - Tabla consultada
   
COMPONENTES SUGERIDOS:
- ChatMessage component (usuario vs bot)
- FeedbackButtons component
- MetadataPanel component
- InputBar component

ENDPOINTS A LLAMAR:
- POST /api/whatsapp/sandbox/simulate
  Body: { message: string, contact_id: number }
  Response: { response: string, metadata: {... } }

Referencias:
- https://react. dev/learn
- https://ui.shadcn.com/ (para componentes)
*/

// TODO: Implementar componente completo
export default function WhatsAppSandbox() {
  // TODO: Estado para mensajes, loading, metadata
  // TODO: Función para enviar mensaje
  // TODO: Función para registrar feedback
  // TODO: Renderizar chat + sidebar
}
```

---

### **MÓDULO 2: Gestión de Aprendizajes**

**Ubicación:** `Frontend/src/pages/WhatsAppLearning.tsx`

**INSTRUCCIONES:**

```typescript
/*
REQUISITOS:
1. Tabla de dudas_pendientes con:
   - Pregunta original
   - Fecha
   - Estado (pendiente, respondida)
   - Botón "Responder"
   
2. Modal para responder duda:
   - Mostrar pregunta original
   - Textarea para respuesta del admin
   - Checkbox "Aprobar y guardar en KB"
   - Botón "Enviar respuesta"
   
3. Tabla de knowledge_base_validated:
   - Pregunta
   - Respuesta
   - Categoría
   - Estado (aprobado, pendiente)
   - Efectividad (score)
   - Botones:  Editar, Aprobar, Desactivar
   
4. Tabla de behavior_rules:
   - Pattern
   - Correction logic
   - Prioridad
   - Veces utilizada
   - Botones:  Editar, Activar/Desactivar

ENDPOINTS A LLAMAR: 
- GET /api/whatsapp/learning/dudas-pendientes
- POST /api/whatsapp/learning/responder-duda
- GET /api/whatsapp/learning/knowledge-base
- PUT /api/whatsapp/learning/knowledge-base/{id}
- GET /api/whatsapp/learning/behavior-rules
- PUT /api/whatsapp/learning/behavior-rules/{id}

Referencias:
- https://tanstack.com/table/latest (para tablas)
*/

// TODO: Implementar componente completo
export default function WhatsAppLearning() {
  // TODO:  Implementar gestión de dudas
  // TODO: Implementar gestión de KB
  // TODO: Implementar gestión de behavior rules
}
```

---

### **MÓDULO 3: Visualizador de Disponibilidad**

**Ubicación:** `Frontend/src/pages/AgendaDisponibilidad.tsx`

**INSTRUCCIONES:**

```typescript
/*
REQUISITOS: 
1. Calendario mensual con disponibilidad
2. Selector de podólogo (dropdown)
3. Mostrar slots disponibles por día
4. Indicadores visuales:
   - Verde: Disponible
   - Amarillo: Pocos slots
   - Rojo: Sin disponibilidad
   
5. Panel lateral con detalles:
   - Horarios de atención
   - Bloqueos activos
   - Citas agendadas del día
   
6. Sincronización en tiempo real:
   - Lo que ve el admin = Lo que ve Maya
   - WebSocket opcional para actualizaciones

ENDPOINTS A LLAMAR: 
- GET /api/horarios/disponibilidad? fecha={YYYY-MM-DD}&podologo_id={id}
- GET /api/horarios/bloqueos
- GET /api/citas? fecha={YYYY-MM-DD}

Referencias:
- https://fullcalendar.io/ (para calendario)
*/

// TODO: Implementar visualizador
export default function AgendaDisponibilidad() {
  // TODO: Implementar calendario
  // TODO: Implementar panel de detalles
  // TODO:  Sincronizar con backend
}
```

---

## ⚙️ Configuración y Deployment

### **Archivo: `backend/.env.example` (ACTUALIZAR)**

```bash
# ============================================================================
# TWILIO WHATSAPP API
# ============================================================================
TWILIO_ACCOUNT_SID=ACb943723442316b803ef1caf3c23d54d1
TWILIO_AUTH_TOKEN=ff1bf2459e8c7ff64d23d69744e8c665
TWILIO_PHONE_NUMBER=+16206986058

# ============================================================================
# ANTHROPIC CLAUDE
# ============================================================================
ANTHROPIC_API_KEY=sk-ant-xxxxx

# ============================================================================
# BASE DE DATOS
# ============================================================================
DATABASE_URL=postgresql://user:pass@localhost: 5432/podoskin_db

# ============================================================================
# CONFIGURACIÓN DEL AGENTE
# ============================================================================
AGENT_CONFIDENCE_THRESHOLD=0.80
AGENT_MODEL=claude-3-5-sonnet-20241022
AGENT_MAX_TOKENS=1024

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT=development  # development | production
```

---

### **Instrucciones de Setup Local con Ngrok**

**Archivo: `SETUP_LOCAL_TWILIO.md` (CREAR)**

```markdown
# Setup Local - Twilio WhatsApp

## Requisitos
- Python 3.10+
- PostgreSQL 15+ con pgvector
- Cuenta de Twilio (Trial)
- Ngrok instalado

## Pasos

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements. txt
```

### 2. Ejecutar Migraciones

```bash
psql -U postgres -d podoskin_db -f database/migrations/20_twilio_maya_integration.sql
```

### 3. Generar Embeddings Iniciales

```bash
python scripts/generate_initial_embeddings.py
```

### 4. Iniciar Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Exponer con Ngrok

```bash
ngrok http 8000
```

Copiar URL:   `https://xxxx-xxx-xxx. ngrok. io`

### 6. Configurar Webhook en Twilio

1. Ir a:  https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click en "Sandbox settings"
3. When a message comes in:  `https://xxxx-xxx-xxx.ngrok.io/webhook/twilio`
4. Método: POST
5. Guardar

### 7. Probar desde WhatsApp

1. Agregar contacto:  +1 620 698 6058
2. Enviar:  "join shoulder-try"
3. Esperar confirmación
4. Enviar: "Hola, ¿cuánto cuesta el tratamiento de onicomicosis?"
5. Maya debe responder con precios desde SQL

## Troubleshooting

Ver logs en tiempo real:
```bash
tail -f logs/maya_agent.log
```

Ver webhooks en Twilio Console:
https://console.twilio.com/us1/monitor/logs/debugger
```

---

## 🧪 Testing y Validación

### **Script de Testing:  `backend/tests/test_maya_twilio.py`**

**INSTRUCCIONES:**

```python
"""
Test Suite - Maya + Twilio Integration

INSTRUCCIONES:
1. Crear tests para cada tool
2. Crear tests para cada nodo
3. Crear test de integración end-to-end
4. Usar pytest para ejecutar

Comandos: 
pytest backend/tests/test_maya_twilio.py -v
"""

import pytest
from agents.sub_agent_whatsApp.tools import (
    consultar_tratamientos_sql,
    buscar_knowledge_base_validada,
    buscar_conversaciones_previas
)

# TODO: Implementar tests según estructura: 

@pytest.mark.asyncio
async def test_consultar_tratamientos_encontrados():
    """
    VERIFICAR: 
    - Buscar "onicomicosis" retorna resultados
    - Response es JSON válido
    - Precios están presentes
    - Fuente es 'sql_estructurado'
    """
    pass

@pytest.mark.asyncio
async def test_kb_con_confidence_alta():
    """
    VERIFICAR:
    - Pregunta FAQ retorna respuesta
    - Confidence >= 0.85
    - Categoría correcta
    """
    pass

@pytest.mark.asyncio
async def test_contexto_aislado_por_contacto():
    """
    VERIFICAR:
    - Buscar conversaciones de contacto A no retorna de contacto B
    - Aislamiento funciona correctamente
    """
    pass

@pytest.mark.asyncio
async def test_escalamiento_confidence_baja():
    """
    VERIFICAR:
    - Confidence < 0.80 → requires_human=True
    - Ticket creado en dudas_pendientes
    - Respuesta de escalamiento generada
    """
    pass

@pytest.mark.asyncio
async def test_end_to_end_consulta_precio():
    """
    VERIFICAR:
    - Mensaje "¿Cuánto cuesta X?" 
    - Agente consulta SQL
    - Responde con precio correcto
    - Metadata completa
    """
    pass
```

---

## ✅ Checklist de Implementación Completa

### **Base de Datos**
- [ ] Migración `20_twilio_maya_integration.sql` ejecutada
- [ ] 5 tablas nuevas creadas
- [ ] Índices creados correctamente
- [ ] Triggers funcionando
- [ ] 3 behavior_rules iniciales insertadas
- [ ] Columna `metadata` agregada a `mensajes`

### **Backend - Twilio**
- [ ] `api/twilio_webhook.py` implementado
- [ ] Validación de firma funcionando
- [ ] `services/twilio_service.py` implementado
- [ ] Logs de webhook guardándose en `twilio_webhook_logs`
- [ ] Respuestas TwiML correctas

### **Backend - Tools**
- [ ] `tools/sql_tools.py` con 4 tools implementadas
- [ ] `tools/kb_tools.py` con búsqueda pgvector
- [ ] `tools/context_tools.py` con aislamiento por contacto
- [ ] `tools/filter_tools.py` con blacklist/whitelist
- [ ] `tools/behavior_tools.py` para reglas dinámicas
- [ ] Todas las tools con ToolRuntime

### **Backend - Nodes**
- [ ] `nodes/router.py` aplicando filtros + reglas
- [ ] `nodes/rag_manager.py` con búsqueda dual (prioridades)
- [ ] `nodes/generate_response.py` con System Prompt dinámico
- [ ] `nodes/human_escalation.py` con creación de tickets
- [ ] `nodes/learning_curator.py` con generalización

### **Backend - LangGraph**
- [ ] `graph.py` con StateGraph compilado
- [ ] Checkpointer (MemorySaver) configurado
- [ ] Conditional routing por confidence
- [ ] Interrupt/resume para human-in-the-loop
- [ ] State schema (`WhatsAppAgentState`) actualizado

### **Backend - Utilidades**
- [ ] `utils/learning.py` con `generalize_knowledge()`
- [ ] `utils/learning. py` con `remove_pii()`
- [ ] `utils/embeddings.py` reutilizado sin cambios

### **Frontend**
- [ ] `pages/WhatsAppSandbox.tsx` con chat simulado
- [ ] `pages/WhatsAppLearning. tsx` con gestión de aprendizajes
- [ ] `pages/AgendaDisponibilidad.tsx` con calendario
- [ ] Endpoints API creados para frontend
- [ ] WebSocket opcional para notificaciones

### **Configuración**
- [ ] `.env.example` actualizado
- [ ] Variables de Twilio configuradas
- [ ] Ngrok instalado y probado
- [ ] Webhook configurado en Twilio Console
- [ ] `SETUP_LOCAL_TWILIO.md` creado

### **Testing**
- [ ] Tests unitarios para cada tool
- [ ] Tests unitarios para cada nodo
- [ ] Test de integración end-to-end
- [ ] Test de aislamiento de conversaciones
- [ ] Test de escalamiento a humano
- [ ] Todos los tests pasando (pytest)

### **Documentación**
- [ ] README actualizado con nueva arquitectura
- [ ] Diagramas de flujo actualizados
- [ ] API docs generadas (OpenAPI/Swagger)
- [ ] Guía de troubleshooting

### **Validación Final**
- [ ] Mensaje de WhatsApp llega al webhook
- [ ] Filtros aplicados correctamente
- [ ] Búsqueda SQL funciona (precios/horarios)
- [ ] Búsqueda KB funciona (FAQs)
- [ ] Búsqueda contexto aislada por contacto
- [ ] Escalamiento crea ticket correctamente
- [ ] System Prompt dinámico con behavior rules
- [ ] Respuesta enviada correctamente vía Twilio
- [ ] Metadata guardada en BD
- [ ] No hay data leakage entre pacientes

---

## 📚 Referencias Críticas para el Agente

### **LangGraph v1+ Patterns**
- Workflows & Agents:  https://docs.langchain.com/oss/python/langgraph/workflows-agents
- Agentic RAG: https://docs.langchain.com/oss/python/langgraph/agentic-rag
- Human-in-the-loop: https://docs.langchain.com/oss/python/langgraph/human-in-the-loop
- Memory:  https://docs.langchain.com/oss/python/concepts/memory

### **LangChain Tools**
- Tools Overview: https://docs.langchain.com/oss/python/langchain/tools
- ToolRuntime: https://docs.langchain.com/oss/python/langchain/tools#tool-runtime
- Custom Tools: https://docs.langchain.com/oss/python/langchain/tools#custom-tools

### **Twilio WhatsApp API**
- Send Messages: https://www.twilio.com/docs/whatsapp/api#send-a-message
- Webhooks: https://www.twilio.com/docs/whatsapp/tutorial/send-and-receive-media-messages-whatsapp-python
- Security: https://www.twilio.com/docs/usage/security#validating-requests

### **PostgreSQL + pgvector**
- pgvector operators: https://github.com/pgvector/pgvector#querying
- Cosine distance: https://github.com/pgvector/pgvector#distances

---

## 🎯 Resultado Esperado Final

Después de implementar TODAS las instrucciones de este prompt, el sistema debe:

1. ✅ **Recibir mensajes de WhatsApp** vía webhook de Twilio
2. ✅ **Aplicar filtros** (blacklist/whitelist) automáticamente
3. ✅ **Buscar en SQL PRIMERO** para precios/horarios/servicios (FUENTE DE VERDAD)
4. ✅ **Buscar en KB validada** si no encuentra en SQL
5. ✅ **Buscar en contexto conversacional AISLADO** por paciente
6. ✅ **Escalar a humano** si confidence < 0.80
7. ✅ **Generar respuestas** con System Prompt dinámico (behavior rules)
8. ✅ **Enviar respuesta** vía Twilio WhatsApp API
9. ✅ **Guardar metadata completa** de cada interacción
10. ✅ **NO mezclar datos** entre pacientes (thread-scoped memory)
11. ✅ **Aprender de escalamientos** con curación de conocimiento
12. ✅ **Frontend funcional** para gestión (Sandbox, Aprendizajes, Agenda)

---

## ⚠️ Restricciones Críticas para el Agente

1. **NUNCA usar vectores para precios/horarios/servicios** → Solo SQL
2. **SIEMPRE filtrar por `id_contacto`** en búsquedas contextuales
3. **SIEMPRE validar firma de Twilio** en producción
4. **NUNCA modificar** el código existente de Maya sin necesidad
5. **SIEMPRE probar** cada componente antes de continuar
6. **SIEMPRE documentar** cambios realizados
7. **SIEMPRE seguir** los patrones de LangGraph v1+

---

## 📝 Notas Finales para el Agente

- Este prompt es una **GUÍA**, no código completo
- **Analiza** el código existente antes de modificar
- **Reutiliza** funciones y tools ya implementadas
- **Pregunta** si algo no está claro (en comentarios del PR)
- **Valida** cada paso con los checklists proporcionados
- **Consulta** las referencias de LangGraph/LangChain cuando sea necesario

---

**FIN DEL PROMPT DE INTEGRACIÓN TWILIO + MAYA**

**Versión:** 1.0  
**Fecha:** 2026-01-12  
**Autor:** Arquitecto de Sistema  
**Para:** Agente Copilot de GitHub  

🚀 **¡Buena suerte con la implementación!**
