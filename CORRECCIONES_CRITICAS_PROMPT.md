
# 🔧 PROMPT DE CORRECCIONES - Para Agente Copilot

**Archivo:** `CORRECCIONES_CRITICAS_PROMPT.md`

---

## 🎯 Objetivo

Aplicar 6 correcciones críticas al sistema de integración Twilio + Maya basándose en el archivo `INTEGRACION_TWILIO_MAYA_COMPLETO.md`.

**Tiempo estimado:** 2-3 horas

---

## ✅ CORRECCIÓN 1: Uso Correcto de ToolRuntime en RAG Manager

### **Problema Identificado:**

```python
# ❌ INCORRECTO (línea ~80-90 en node_rag_manager. py):
result = await consultar_tratamientos_sql(termino, runtime=None)
#                                                  ^^^^^^^^^^^^
# Pasa None pero la tool necesita acceso al state
```

### **Acción Requerida:**

**Archivo:** `backend/agents/sub_agent_whatsApp/nodes/rag_manager. py`

**Línea ~5 - Agregar import:**
```python
from langchain.tools import ToolRuntime
```

**Línea ~65-70 - Modificar TODAS las llamadas a tools:**

```python
# ANTES:
result = await consultar_tratamientos_sql(termino, runtime=None)

# DESPUÉS:
# Crear ToolRuntime con acceso al state
tool_runtime = ToolRuntime(state=state)

# Pasar runtime a todas las tools
result = await consultar_tratamientos_sql(termino, runtime=tool_runtime)
```

**Aplicar este cambio en:**
- [ ] `consultar_tratamientos_sql()` (línea ~70)
- [ ] `consultar_horarios_sql()` (línea ~95)
- [ ] `consultar_citas_sql()` (línea ~115)
- [ ] `buscar_knowledge_base_validada()` (línea ~135)
- [ ] `buscar_conversaciones_previas()` (línea ~155)

**Validación:**
```python
# Verificar que todas las llamadas tengan: 
assert tool_runtime is not None
assert isinstance(tool_runtime, ToolRuntime)
```

---

## ✅ CORRECCIÓN 2: Normalización de Similitud Coseno en KB

### **Problema Identificado:**

```python
# ❌ INCORRECTO (kb_tools.py, línea ~60):
similarity = float(np. dot(query_embedding, kb_embedding))
# Solo dot product, no normaliza vectores (puede dar valores >1)
```

### **Acción Requerida:**

**Archivo:** `backend/agents/sub_agent_whatsApp/tools/kb_tools.py`

**Línea ~3 - Agregar import:**
```python
from numpy.linalg import norm
```

**Línea ~60-70 - Reemplazar el bucle completo:**

```python
# ANTES:
for row in rows:
    kb_embedding = pickle.loads(row['pregunta_embedding'])
    
    # ❌ INCORRECTO
    similarity = float(np.dot(query_embedding, kb_embedding))
    
    if similarity > best_similarity:
        best_similarity = similarity
        best_match = row

# DESPUÉS:
for row in rows:
    kb_embedding = pickle.loads(row['pregunta_embedding'])
    
    # ✅ CORRECTO:  Cosine similarity normalizado
    similarity = float(
        np.dot(query_embedding, kb_embedding) / 
        (norm(query_embedding) * norm(kb_embedding) + 1e-10)  # +epsilon evita división por cero
    )
    
    if similarity > best_similarity:
        best_similarity = similarity
        best_match = row
```

**Validación:**
```python
# Verificar que similarity esté siempre entre -1 y 1
assert -1.0 <= best_similarity <= 1.0
```

---

## ✅ CORRECCIÓN 3: Script de Generación de Embeddings Iniciales

### **Problema Identificado:**

```bash
# ❌ FALTA:  Mencionado en SETUP_LOCAL_TWILIO. md pero no existe
python scripts/generate_initial_embeddings.py
```

### **Acción Requerida:**

**Crear archivo:** `backend/scripts/generate_initial_embeddings.py`

```python
"""
Genera embeddings para behavior_rules iniciales. 

Ejecutar después de la migración SQL para actualizar los embeddings placeholder. 

Uso:
    python backend/scripts/generate_initial_embeddings.py
"""

import asyncio
import pickle
import sys
import os

# Agregar path del backend al sys.path
sys.path. insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db import get_pool, init_db_pool, close_db_pool
from agents.sub_agent_whatsApp. utils.embeddings import get_embeddings_service


async def generate_embeddings():
    """Genera embeddings para behavior_rules con placeholder."""
    
    print("🔧 Iniciando generación de embeddings...")
    
    try:
        await init_db_pool()
        pool = get_pool()
        embeddings_service = get_embeddings_service()
        
        # Obtener reglas sin embeddings reales (placeholder = E'\\x00')
        print("📊 Consultando behavior_rules sin embeddings...")
        
        rules = await pool.fetch(
            "SELECT id, pattern FROM behavior_rules WHERE embedding = E'\\\\x00'"
        )
        
        if not rules:
            print("✅ No hay reglas pendientes de embeddings")
            return
        
        print(f"📝 Encontradas {len(rules)} reglas pendientes")
        
        for rule in rules:
            print(f"\n🔄 Procesando regla #{rule['id']}:  {rule['pattern'][: 50]}...")
            
            # Generar embedding
            embedding = embeddings_service.embed_query(rule['pattern'])
            embedding_bytes = pickle.dumps(embedding)
            
            # Actualizar en BD
            await pool.execute(
                "UPDATE behavior_rules SET embedding = $1 WHERE id = $2",
                embedding_bytes, rule['id']
            )
            
            print(f"   ✅ Embedding generado ({len(embedding)} dims)")
        
        print("\n" + "="*60)
        print(f"🎉 Proceso completado:  {len(rules)} embeddings generados")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error:  {e}")
        raise
    
    finally:
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(generate_embeddings())
```

**Crear también:** `backend/scripts/__init__.py` (vacío)

**Validación:**
```bash
# Ejecutar y verificar output
python backend/scripts/generate_initial_embeddings.py

# Debe mostrar:
# ✅ Embedding generado (384 dims)
# ✅ Embedding generado (384 dims)
# ✅ Embedding generado (384 dims)
```

---

## ✅ CORRECCIÓN 4: Endpoints de Backend para Frontend

### **Problema Identificado:**

```typescript
// ❌ FALTA: Frontend menciona estos endpoints pero no existen
POST /api/whatsapp/sandbox/simulate
GET /api/whatsapp/learning/dudas-pendientes
POST /api/whatsapp/learning/responder-duda
GET /api/whatsapp/learning/knowledge-base
PUT /api/whatsapp/learning/knowledge-base/{id}
```

### **Acción Requerida:**

**Crear archivo:** `backend/api/whatsapp_management_api.py`

```python
"""
WhatsApp Management API
=======================

Endpoints para gestión de WhatsApp desde el frontend.

Incluye:
- Sandbox de simulación
- Gestión de dudas pendientes
- Gestión de knowledge base
- Gestión de behavior rules
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

from db import get_pool
from auth import get_current_user, User  # Asume que existe auth
from agents.sub_agent_whatsApp.graph import create_whatsapp_agent, WhatsAppAgentState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Management"])

# ============================================================================
# MODELOS
# ============================================================================

class SimulateRequest(BaseModel):
    message: str
    contact_id: int

class SimulateResponse(BaseModel):
    response: str
    metadata: dict
    confidence: float
    fuente:  str

class ResponderDudaRequest(BaseModel):
    duda_id: int
    respuesta:  str
    aprobar_y_aprender: bool = False

# ============================================================================
# SANDBOX
# ============================================================================

@router. post("/sandbox/simulate", response_model=SimulateResponse)
async def simulate_conversation(
    request: SimulateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Simula una conversación con el agente Maya en modo sandbox.
    
    TODO: 
    1. Crear state inicial con message y contact_id
    2. Ejecutar agente con create_whatsapp_agent()
    3. Extraer respuesta y metadata
    4. Retornar SimulateResponse
    """
    
    try:
        # Crear state inicial
        initial_state = WhatsAppAgentState(
            messages=[],
            contact_id=str(request.contact_id),
            conversation_id="sandbox",
            message=request.message,
            retrieved_context="",
            fuente="",
            confidence=0.0,
            metadata={},
            requires_human=False
        )
        
        # Ejecutar agente
        agent = create_whatsapp_agent()
        config = {"configurable": {"thread_id": f"sandbox_{request.contact_id}"}}
        result = await agent.ainvoke(initial_state, config=config)
        
        # Extraer respuesta
        response = result.get('response', result['messages'][-1]. content if result['messages'] else "")
        
        return SimulateResponse(
            response=response,
            metadata=result.get('metadata', {}),
            confidence=result.get('confidence', 0.0),
            fuente=result.get('fuente', 'unknown')
        )
    
    except Exception as e: 
        logger.error(f"Error en simulación: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DUDAS PENDIENTES
# ============================================================================

@router.get("/learning/dudas-pendientes")
async def get_dudas_pendientes(
    estado: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene lista de dudas pendientes. 
    
    TODO:
    1. Query a tabla dudas_pendientes
    2. Filtrar por estado si se proporciona
    3. JOIN con conversaciones y contactos para contexto
    4. Retornar lista
    """
    
    pool = get_pool()
    
    query = """
        SELECT 
            dp.id,
            dp.pregunta_original,
            dp.contexto_mensaje,
            dp.estado,
            dp.fecha_creacion,
            c.id as conversacion_id,
            co.nombre as contacto_nombre,
            co.telefono as contacto_telefono
        FROM dudas_pendientes dp
        INNER JOIN conversaciones c ON dp. id_conversacion = c.id
        INNER JOIN contactos co ON c.id_contacto = co.id
        WHERE ($1:: text IS NULL OR dp.estado = $1)
        ORDER BY dp. fecha_creacion DESC
        LIMIT 50
    """
    
    rows = await pool.fetch(query, estado)
    
    return [dict(row) for row in rows]


@router.post("/learning/responder-duda")
async def responder_duda(
    request: ResponderDudaRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Responde una duda pendiente y opcionalmente la aprende.
    
    TODO:
    1. Actualizar dudas_pendientes con respuesta
    2. Si aprobar_y_aprender=true: 
       a. Llamar a generalize_knowledge()
       b. Guardar en knowledge_base_validated con aprobado=false
       c. Generar embedding
    3. Enviar respuesta al paciente vía Twilio
    4. Retornar confirmación
    """
    
    pool = get_pool()
    
    try:
        # Actualizar duda
        await pool.execute(
            """
            UPDATE dudas_pendientes
            SET respuesta_admin = $1,
                estado = 'respondida',
                fecha_respuesta = NOW(),
                respondido_por = $2
            WHERE id = $3
            """,
            request.respuesta, current_user.id, request. duda_id
        )
        
        if request.aprobar_y_aprender:
            # TODO: Llamar a learning_curator
            # TODO: Guardar en knowledge_base_validated
            pass
        
        # TODO: Enviar respuesta al paciente vía Twilio
        
        return {
            "success": True,
            "message":  "Duda respondida correctamente",
            "aprendido": request.aprobar_y_aprender
        }
    
    except Exception as e: 
        logger.error(f"Error respondiendo duda: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# KNOWLEDGE BASE
# ============================================================================

@router.get("/learning/knowledge-base")
async def get_knowledge_base(
    categoria: Optional[str] = None,
    aprobado: Optional[bool] = None,
    current_user:  User = Depends(get_current_user)
):
    """
    Obtiene entries de knowledge base.
    
    TODO:
    1. Query a knowledge_base_validated
    2. Filtrar por categoria y aprobado si se proporciona
    3. Incluir métricas (veces_consultada, efectividad_score)
    4. Retornar lista
    """
    
    pool = get_pool()
    
    query = """
        SELECT 
            id, pregunta, respuesta, categoria,
            aprobado, origen, veces_consultada, efectividad_score,
            feedback_positivo, feedback_negativo,
            fecha_creacion, fecha_aprobacion
        FROM knowledge_base_validated
        WHERE ($1::text IS NULL OR categoria = $1)
        AND ($2::boolean IS NULL OR aprobado = $2)
        ORDER BY fecha_creacion DESC
        LIMIT 100
    """
    
    rows = await pool. fetch(query, categoria, aprobado)
    
    return [dict(row) for row in rows]


@router.put("/learning/knowledge-base/{kb_id}")
async def update_knowledge_base(
    kb_id: int,
    pregunta: Optional[str] = None,
    respuesta: Optional[str] = None,
    aprobado: Optional[bool] = None,
    current_user:  User = Depends(get_current_user)
):
    """
    Actualiza una entry de knowledge base.
    
    TODO:
    1. Validar permisos
    2. Actualizar campos proporcionados
    3. Si cambia pregunta, regenerar embedding
    4. Retornar entry actualizada
    """
    
    pool = get_pool()
    
    # TODO: Implementar lógica de actualización
    
    return {"success": True, "message": "KB actualizada"}

```

**Agregar a `backend/main.py`:**

```python
# Línea ~20 (después de otros imports de routers)
from api.whatsapp_management_api import router as whatsapp_mgmt_router

# Línea ~50 (después de otros include_router)
app.include_router(whatsapp_mgmt_router)
```

**Validación:**
```bash
# Verificar que los endpoints estén disponibles
curl http://localhost:8000/docs

# Debe mostrar: 
# POST /api/whatsapp/sandbox/simulate
# GET /api/whatsapp/learning/dudas-pendientes
# POST /api/whatsapp/learning/responder-duda
# GET /api/whatsapp/learning/knowledge-base
```

---

## ✅ CORRECCIÓN 5: Checkpointer Persistente para Producción

### **Problema Identificado:**

```python
# ❌ INCORRECTO (graph.py):
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()  # Se pierde al reiniciar
```

### **Acción Requerida:**

**Archivo:** `backend/agents/sub_agent_whatsApp/graph.py`

**Línea ~5 - Modificar import:**

```python
# ANTES:
from langgraph.checkpoint.memory import MemorySaver

# DESPUÉS: 
import os
from langgraph.checkpoint. memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
```

**Línea ~80-85 - Modificar creación de checkpointer:**

```python
# ANTES:
checkpointer = MemorySaver()

# DESPUÉS:
# Usar PostgreSQL en producción, Memory en desarrollo
if os.getenv("ENVIRONMENT") == "production":
    logger.info("✅ Usando PostgresSaver (persistente)")
    checkpointer = PostgresSaver. from_conn_string(
        os.getenv("DATABASE_URL")
    )
    # Crear tablas si no existen
    # checkpointer.setup()  # Descomentar en primera ejecución
else:
    logger.info("⚠️ Usando MemorySaver (desarrollo, no persistente)")
    checkpointer = MemorySaver()
```

**Agregar comentario:**
```python
# Nota: PostgresSaver requiere crear tabla 'checkpoints' en PostgreSQL
# Ejecutar una vez:  checkpointer.setup()
```

**Validación:**
```python
# En producción, verificar que existe la tabla: 
# SELECT EXISTS (
#     SELECT FROM pg_tables WHERE tablename = 'checkpoints'
# );
```

---

## ✅ CORRECCIÓN 6: Rate Limiting Middleware

### **Problema Identificado:**

```python
# ❌ FALTA: Mencionado en arquitectura pero no implementado
backend/middleware/rate_limit.py
```

### **Acción Requerida:**

**Crear archivo:** `backend/middleware/rate_limit.py`

```python
"""
Rate Limiting Middleware
========================

Limita mensajes por número de teléfono para prevenir spam y bucles. 

Configuración:
- 5 mensajes por minuto por número
- 20 mensajes por hora por número
- Detecta bucles (mismo mensaje 3+ veces)
"""

from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Storage en memoria (en producción usar Redis)
message_counts = defaultdict(list)  # {phone:  [timestamp1, timestamp2, ...]}
message_history = defaultdict(list)  # {phone: [message1, message2, ...]}

# Configuración
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_HOUR = 20
LOOP_DETECTION_THRESHOLD = 3


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware de rate limiting.
    
    TODO en producción:
    - Reemplazar dicts en memoria por Redis
    - Agregar lista blanca (whitelist) de números exentos
    - Agregar métricas/alertas
    """
    
    # Solo aplicar a webhook de Twilio
    if request.url.path != "/webhook/twilio":
        return await call_next(request)
    
    # Extraer número de teléfono del form data
    form = await request.form()
    phone = form.get("From", "").replace("whatsapp: +", "")
    message_body = form.get("Body", "")
    
    if not phone: 
        return await call_next(request)
    
    now = datetime.now()
    
    # Limpiar timestamps antiguos (>1 hora)
    cutoff_time = now - timedelta(hours=1)
    message_counts[phone] = [
        ts for ts in message_counts[phone] if ts > cutoff_time
    ]
    
    # Verificar límite por minuto
    recent_minute = [
        ts for ts in message_counts[phone] 
        if ts > now - timedelta(minutes=1)
    ]
    
    if len(recent_minute) >= RATE_LIMIT_PER_MINUTE:
        logger.warning(f"⚠️ Rate limit excedido (por minuto): {phone}")
        raise HTTPException(
            status_code=429,
            detail="Demasiados mensajes, por favor espera un momento."
        )
    
    # Verificar límite por hora
    if len(message_counts[phone]) >= RATE_LIMIT_PER_HOUR: 
        logger.warning(f"⚠️ Rate limit excedido (por hora): {phone}")
        raise HTTPException(
            status_code=429,
            detail="Límite de mensajes alcanzado, intenta más tarde."
        )
    
    # Detectar bucles (mismo mensaje repetido)
    recent_messages = message_history[phone][-LOOP_DETECTION_THRESHOLD:]
    if len(recent_messages) == LOOP_DETECTION_THRESHOLD:
        if all(msg == message_body for msg in recent_messages):
            logger.warning(f"⚠️ Bucle detectado: {phone} - '{message_body[: 30]}'")
            raise HTTPException(
                status_code=429,
                detail="Mensaje repetido detectado.  Si necesitas ayuda, contacta directamente a la clínica."
            )
    
    # Registrar mensaje
    message_counts[phone]. append(now)
    message_history[phone].append(message_body)
    
    # Limitar historial a últimos 10 mensajes
    if len(message_history[phone]) > 10:
        message_history[phone] = message_history[phone][-10:]
    
    # Continuar con el request
    response = await call_next(request)
    return response
```

**Agregar a `backend/main.py`:**

```python
# Línea ~10 (imports)
from middleware.rate_limit import rate_limit_middleware

# Línea ~35 (después de crear app)
app.middleware("http")(rate_limit_middleware)
```

**Validación:**
```bash
# Enviar 6 mensajes rápidos desde el mismo número
# El 6to debe retornar HTTP 429
```

---

## 📋 CHECKLIST DE VALIDACIÓN

Después de aplicar TODAS las correcciones, verificar: 

### **Tests Unitarios:**
- [ ] ToolRuntime se pasa correctamente a todas las tools
- [ ] Similitud coseno retorna valores entre -1 y 1
- [ ] Script de embeddings ejecuta sin errores
- [ ] Endpoints de management responden correctamente
- [ ] Checkpointer persiste en PostgreSQL (producción)
- [ ] Rate limiting bloquea después de 5 mensajes/min

### **Tests de Integración:**
- [ ] Mensaje desde WhatsApp llega al webhook
- [ ] Agente consulta SQL correctamente (con ToolRuntime)
- [ ] Búsqueda en KB retorna similarity normalizada
- [ ] Sandbox frontend recibe respuesta
- [ ] Dudas pendientes se muestran en frontend
- [ ] Rate limiting previene spam

### **Validación de BD:**
```sql
-- Verificar embeddings generados
SELECT COUNT(*) FROM behavior_rules WHERE embedding != E'\\x00';
-- Debe retornar:  3 (las reglas iniciales)

-- Verificar tabla de checkpoints (producción)
SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'checkpoints');
-- Debe retornar: true (si usas PostgresSaver)
```

---

## 🎯 RESULTADO ESPERADO

Después de estas 6 correcciones: 

1. ✅ **Tools tienen acceso al state** vía ToolRuntime
2. ✅ **Búsqueda KB es precisa** con cosine similarity normalizado
3. ✅ **Embeddings iniciales generados** automáticamente
4. ✅ **Frontend puede comunicarse** con backend (endpoints existen)
5. ✅ **Checkpointer persiste** en PostgreSQL (producción)
6. ✅ **Rate limiting previene** spam y bucles

---

## 📌 NOTAS PARA EL AGENTE

- Aplicar correcciones **en orden** (1 → 6)
- **Validar cada corrección** antes de continuar
- **No modificar** código que funcione correctamente
- **Comentar** cambios significativos en el código
- **Ejecutar tests** después de cada corrección
- Si algo no está claro, **dejar un TODO** con pregunta

---

