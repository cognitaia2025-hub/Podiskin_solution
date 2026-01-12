# 🚀 Guía de Implementación - Correcciones Críticas WhatsApp/Twilio

## 📋 Resumen

Se implementaron **6 correcciones críticas** para mejorar la integración de WhatsApp con Twilio y LangGraph. Todas las correcciones están completas y listas para usar.

---

## ✅ Correcciones Implementadas

### 1. ToolRuntime en RAG Manager ✅
- **Estado:** Verificado - Ya implementado correctamente
- **Archivos:** `backend/agents/whatsapp_medico/nodes/rag_manager.py`

### 2. Normalización Coseno en KB ✅
- **Estado:** Mejorado con epsilon
- **Archivos:** `backend/agents/whatsapp_medico/tools/kb_tools.py`

### 3. Script de Embeddings ✅
- **Estado:** Verificado y listo para usar
- **Archivos:** `backend/scripts/generate_initial_embeddings.py`

### 4. Endpoints de Management API ✅
- **Estado:** Creado e integrado
- **Archivos:** `backend/api/whatsapp_management_api.py`

### 5. Checkpointer Persistente ✅
- **Estado:** Configurado con fallback
- **Archivos:** `backend/agents/whatsapp_medico/config.py`

### 6. Rate Limiting Middleware ✅
- **Estado:** Implementado y activado
- **Archivos:** `backend/middleware/rate_limit.py`

---

## 🎯 Nuevas Funcionalidades

### API de Gestión de WhatsApp

```bash
# Endpoints disponibles en /api/whatsapp:

# Simulación de conversaciones
POST /api/whatsapp/sandbox/simulate

# Gestión de dudas pendientes
GET /api/whatsapp/learning/dudas-pendientes
POST /api/whatsapp/learning/responder-duda

# Gestión de knowledge base
GET /api/whatsapp/learning/knowledge-base
PUT /api/whatsapp/learning/knowledge-base/{kb_id}
```

### Rate Limiting

El sistema ahora protege contra spam y bucles:
- ⏱️ 5 mensajes por minuto
- 🕐 20 mensajes por hora  
- 🔄 Detecta mensajes repetidos (bucles)

### Checkpointer Persistente

El estado de las conversaciones ahora persiste en PostgreSQL en producción:

```bash
# Desarrollo (default)
export ENVIRONMENT=development

# Producción
export ENVIRONMENT=production
```

---

## 🔧 Configuración

### Variables de Entorno

Agregar al archivo `.env`:

```bash
# Entorno (development o production)
ENVIRONMENT=development

# Rate limiting (opcional, usa defaults)
RATE_LIMIT_PER_MINUTE=5
RATE_LIMIT_PER_HOUR=20

# Confidence threshold para el agente
AGENT_CONFIDENCE_THRESHOLD=0.80

# Base de datos (para checkpointer)
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Dependencias

Las siguientes dependencias son requeridas (ya deberían estar en `requirements.txt`):

```txt
fastapi>=0.100.0
langgraph>=0.1.0
langchain>=0.1.0
langchain-anthropic>=0.1.0
sentence-transformers>=2.2.0
numpy>=1.24.0
asyncpg>=0.29.0
```

---

## 🚀 Comandos de Inicialización

### 1. Generar Embeddings Iniciales

Ejecutar **una sola vez** después de crear las tablas:

```bash
python backend/scripts/generate_initial_embeddings.py
```

Debería mostrar:
```
🔧 Iniciando generación de embeddings...
📊 Consultando behavior_rules sin embeddings...
📝 Encontradas X reglas pendientes
✅ Embedding generado (384 dims)
🎉 Proceso completado
```

### 2. Verificar Instalación

```bash
python backend/scripts/validate_corrections.py
```

Debería mostrar:
```
✅ TODAS LAS VALIDACIONES PASARON
```

### 3. Iniciar Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verificar Endpoints

Abrir en navegador:
```
http://localhost:8000/docs
```

Buscar sección "WhatsApp Management" en la documentación de Swagger.

---

## 🧪 Pruebas

### Test Manual del Rate Limiting

```bash
# Enviar 6 mensajes rápidos al webhook
for i in {1..6}; do
  curl -X POST http://localhost:8000/webhook/twilio \
    -d "From=whatsapp:+5215551234567" \
    -d "Body=Hola, necesito información"
  echo ""
done

# El 6to debería retornar HTTP 429
```

### Test de Endpoints de Management

```bash
# Simular conversación (requiere autenticación)
curl -X POST http://localhost:8000/api/whatsapp/sandbox/simulate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "contact_id": 1}'

# Listar dudas pendientes
curl -X GET http://localhost:8000/api/whatsapp/learning/dudas-pendientes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Verificar Base de Datos

```sql
-- Verificar tabla de checkpoints (producción)
SELECT EXISTS (
    SELECT FROM pg_tables 
    WHERE tablename = 'langgraph_checkpoints'
);

-- Verificar embeddings generados
SELECT COUNT(*) 
FROM behavior_rules 
WHERE embedding != E'\\x00';

-- Ver dudas pendientes
SELECT id, pregunta_original, estado 
FROM dudas_pendientes 
ORDER BY fecha_creacion DESC 
LIMIT 5;
```

---

## 📊 Monitoreo

### Logs Importantes

El sistema ahora genera logs estructurados:

```
# Rate limiting
📊 Rate limit check passed: +5215551234567 (2/min, 5/hour)
⚠️ Rate limit excedido (por minuto): +5215551234567

# Checkpointer
✅ Usando PostgresSaver (persistente)
⚠️ Usando MemorySaver (desarrollo)

# RAG Manager
🔍 [RAG Manager] Procesando consulta del contacto 123
✅ Servicios encontrados en SQL: 3
⚠️ No se encontró información para: 'consulta xyz'
```

### Health Check

Verificar que el sistema esté funcionando:

```bash
# Backend corriendo
curl http://localhost:8000/health

# Base de datos accesible
psql -h localhost -U podoskin_user -d podoskin_db -c "SELECT 1;"
```

---

## 🔄 Próximos Pasos

### Implementaciones Pendientes (TODOs en el código)

1. **Sandbox de Simulación**
   - Integrar con el agente real de WhatsApp
   - Archivo: `backend/api/whatsapp_management_api.py` (línea ~60)

2. **Learning Curator**
   - Implementar generalización de conocimiento
   - Archivo: `backend/api/whatsapp_management_api.py` (línea ~145)

3. **Rate Limiting con Redis**
   - Reemplazar dicts en memoria por Redis
   - Archivo: `backend/middleware/rate_limit.py` (línea ~20)

4. **Regenerar Embeddings en KB**
   - Auto-regenerar al editar pregunta
   - Archivo: `backend/api/whatsapp_management_api.py` (línea ~235)

---

## 📁 Archivos Creados/Modificados

### Nuevos Archivos (5)
```
backend/
├── api/
│   └── whatsapp_management_api.py      # API de gestión
├── middleware/
│   ├── __init__.py                     # Package init
│   └── rate_limit.py                   # Rate limiting
└── scripts/
    └── __init__.py                     # Package init
```

### Archivos Modificados (3)
```
backend/
├── main.py                             # +2 imports, +2 routers, +1 middleware
├── agents/whatsapp_medico/
│   ├── config.py                       # Checkpointer condicional
│   └── tools/kb_tools.py               # Coseno con epsilon
```

### Archivos de Documentación (2)
```
INTEGRACION_TWILIO_MAYA_COMPLETA.md     # Resumen de implementación
backend/scripts/validate_corrections.py  # Script de validación
```

---

## 🆘 Solución de Problemas

### Error: "No module named 'langgraph'"

```bash
pip install -r backend/requirements.txt
```

### Error: "Failed to initialize PostgresSaver"

Verificar:
1. PostgreSQL está corriendo
2. Variables de entorno correctas
3. Usuario tiene permisos para crear tablas

```bash
# Verificar conexión
psql $DATABASE_URL -c "SELECT 1;"
```

### Error: Rate limiting no funciona

Verificar que el middleware esté registrado en `main.py`:

```python
app.middleware("http")(rate_limit_middleware)
```

### Checkpointer usa MemorySaver en producción

Verificar variable de entorno:

```bash
echo $ENVIRONMENT
# Debe mostrar: production
```

---

## 📞 Soporte

Si encuentras problemas con las correcciones implementadas:

1. Revisar logs del backend
2. Ejecutar `validate_corrections.py`
3. Verificar variables de entorno
4. Consultar documentación en `INTEGRACION_TWILIO_MAYA_COMPLETA.md`

---

## ✅ Checklist de Implementación

- [x] Corrección 1: ToolRuntime verificado
- [x] Corrección 2: Coseno normalizado
- [x] Corrección 3: Script de embeddings verificado
- [x] Corrección 4: API de management creada
- [x] Corrección 5: Checkpointer persistente configurado
- [x] Corrección 6: Rate limiting implementado
- [ ] Generar embeddings iniciales (ejecutar script)
- [ ] Configurar ENVIRONMENT en producción
- [ ] Probar endpoints de management
- [ ] Verificar rate limiting con tests
- [ ] Monitorear logs en producción

---

**Versión:** 1.0  
**Fecha:** 2026-01-12  
**Implementado por:** GitHub Copilot  
**Basado en:** `CORRECCIONES_CRITICAS_PROMPT.md`
