# Herramientas Completadas - SubAgente WhatsApp

## ✅ FASE 3 Y 4: COMPLETADAS

Este documento lista todas las herramientas implementadas para el SubAgente WhatsApp.

---

## 📦 Patient Tools (`tools/patient_tools.py`)

Herramientas para gestión de pacientes.

### ✅ `search_patient(phone, name)`
Busca un paciente por teléfono o nombre.

**Parámetros:**
- `phone` (Optional[str]): Número de teléfono
- `name` (Optional[str]): Nombre del paciente

**Retorna:** Diccionario con información del paciente encontrado

### ✅ `get_patient_info(patient_id)`
Obtiene información completa de un paciente incluyendo historial de citas.

**Parámetros:**
- `patient_id` (int): ID del paciente

**Retorna:** Diccionario con información completa del paciente

### ✅ `create_patient()` / `register_patient()`
Registra un nuevo paciente en el sistema.

**Parámetros:**
- `contact_id` (int): ID del contacto existente
- `nombre_completo` (str): Nombre completo del paciente
- `fecha_nacimiento` (Optional[str]): Fecha de nacimiento (YYYY-MM-DD)
- `alergias` (Optional[str]): Alergias conocidas
- `condiciones_medicas` (Optional[str]): Condiciones médicas relevantes

**Retorna:** Diccionario con información del paciente registrado

### ✅ `get_patient_history(patient_id)`
Obtiene el historial completo de citas de un paciente.

**Parámetros:**
- `patient_id` (int): ID del paciente

**Retorna:** Diccionario con historial completo de citas y estadísticas

---

## 📅 Appointment Tools (`tools/appointment_tools.py`)

Herramientas para gestión de citas.

### ✅ `get_available_slots(date, duration_minutes)`
Obtiene los horarios disponibles para una fecha específica.

**Parámetros:**
- `date` (str): Fecha en formato YYYY-MM-DD
- `duration_minutes` (int): Duración de la cita en minutos (default: 30)

**Retorna:** Diccionario con horarios disponibles

### ✅ `book_appointment(patient_id, date, time, service_type, ...)`
Agenda una nueva cita para un paciente.

**Parámetros:**
- `patient_id` (int): ID del paciente
- `date` (str): Fecha en formato YYYY-MM-DD
- `time` (str): Hora en formato HH:MM
- `service_type` (str): Tipo de servicio
- `duration_minutes` (int): Duración en minutos (default: 30)
- `notes` (Optional[str]): Notas adicionales

**Retorna:** Diccionario con información de la cita creada

### ✅ `cancel_appointment(appointment_id, reason)`
Cancela una cita existente.

**Parámetros:**
- `appointment_id` (int): ID de la cita a cancelar
- `reason` (Optional[str]): Motivo de la cancelación

**Retorna:** Diccionario con resultado de la cancelación

### ✅ `reschedule_appointment(appointment_id, new_date, new_time, reason)`
Reagenda una cita existente a una nueva fecha y hora.

**Parámetros:**
- `appointment_id` (int): ID de la cita a reagendar
- `new_date` (str): Nueva fecha en formato YYYY-MM-DD
- `new_time` (str): Nueva hora en formato HH:MM
- `reason` (Optional[str]): Motivo del cambio

**Retorna:** Diccionario con resultado del reagendamiento

### ✅ `get_upcoming_appointments(patient_id)`
Obtiene las próximas citas de un paciente.

**Parámetros:**
- `patient_id` (int): ID del paciente

**Retorna:** Diccionario con las próximas citas del paciente

---

## 🔍 Query Tools (`tools/query_tools.py`)

Herramientas para consultas de información.

### ✅ `get_treatments_from_db()`
Obtiene todos los tratamientos disponibles desde la base de datos.

**Retorna:** Diccionario con tratamientos y precios

### ✅ `search_treatment(query)`
Busca un tratamiento específico en la base de datos.

**Parámetros:**
- `query` (str): Término de búsqueda

**Retorna:** Información del tratamiento encontrado

### ✅ `get_treatment_info(treatment_name)`
Obtiene información detallada de un tratamiento específico.

**Parámetros:**
- `treatment_name` (str): Nombre del tratamiento

**Retorna:** Información completa del tratamiento

### ✅ `get_business_hours()`
Obtiene los horarios de atención de la clínica.

**Retorna:** Diccionario con horarios de atención

### ✅ `get_location_info()`
Obtiene la ubicación y datos de contacto de la clínica.

**Retorna:** Diccionario con ubicación y contacto

### ✅ `get_clinic_info(info_type)`
Obtiene información de la clínica (wrapper unificado).

**Parámetros:**
- `info_type` (Optional[str]): Tipo de info ('horarios', 'ubicacion', 'contacto', o None para todo)

**Retorna:** Información solicitada de la clínica

### ✅ `get_prices(service_name)`
Obtiene los precios de servicios/tratamientos.

**Parámetros:**
- `service_name` (Optional[str]): Nombre del servicio (opcional)

**Retorna:** Precios de servicios

### ✅ `search_faq(query)`
Busca en las preguntas frecuentes (FAQ) / base de conocimiento.

**Parámetros:**
- `query` (str): Pregunta o término de búsqueda

**Retorna:** Respuesta encontrada o mensaje de no encontrado

---

## 🧠 RAG Tools (`tools/rag_tools.py`) ✨ NUEVO

Herramientas de Retrieval-Augmented Generation para contexto conversacional.

### ✅ `retrieve_context(query, conversation_id, k, threshold)`
Recupera contexto relevante usando búsqueda semántica.

Busca en conversaciones previas, FAQs y knowledge base para encontrar
información relevante.

**Parámetros:**
- `query` (str): Consulta o pregunta del usuario
- `conversation_id` (Optional[int]): ID de la conversación actual
- `k` (int): Número máximo de resultados (default: 5)
- `threshold` (float): Umbral mínimo de similitud (default: 0.75)

**Retorna:** Diccionario con contexto relevante encontrado

### ✅ `index_conversation(conversation_id, pregunta, respuesta, metadata)`
Indexa una conversación en la base de conocimiento.

Guarda una pregunta-respuesta validada para futuras búsquedas.

**Parámetros:**
- `conversation_id` (int): ID de la conversación
- `pregunta` (str): Pregunta del usuario
- `respuesta` (str): Respuesta proporcionada
- `metadata` (Optional[Dict]): Metadatos adicionales

**Retorna:** Diccionario con resultado de la indexación

### ✅ `search_similar_conversations(conversation_id, k, threshold)`
Busca conversaciones similares a una conversación dada.

Útil para encontrar patrones y aprender de interacciones previas.

**Parámetros:**
- `conversation_id` (int): ID de la conversación de referencia
- `k` (int): Número máximo de similares (default: 5)
- `threshold` (float): Umbral de similitud (default: 0.80)

**Retorna:** Diccionario con conversaciones similares

---

## 🗄️ Vector Store (`utils/vector_store.py`) ✨ NUEVO

Gestión de pgvector para almacenamiento y búsqueda de embeddings.

### ✅ Clase `VectorStore`

Proporciona una interfaz de alto nivel para:
- Agregar documentos con embeddings automáticos
- Búsqueda por similitud semántica
- Filtrado por metadatos y validación
- Gestión de embeddings persistentes en PostgreSQL

#### Métodos:

##### `add_document(text, metadata, embedding, doc_id)`
Agrega un documento al vector store.

**Parámetros:**
- `text` (str): Texto del documento
- `metadata` (Optional[Dict]): Metadatos asociados
- `embedding` (Optional[List[float]]): Embedding pre-calculado
- `doc_id` (Optional[int]): ID del documento

**Retorna:** ID del documento creado/actualizado

##### `add_documents(documents)`
Agrega múltiples documentos al vector store.

**Parámetros:**
- `documents` (List[Dict]): Lista de documentos

**Retorna:** Lista de IDs de documentos creados

##### `similarity_search(query_text, k, threshold, filter_validated, filter_category)`
Realiza búsqueda por similitud semántica.

**Parámetros:**
- `query_text` (str): Texto de consulta
- `k` (int): Número máximo de resultados (default: 5)
- `threshold` (float): Umbral mínimo de similitud (default: 0.75)
- `filter_validated` (Optional[bool]): Filtrar solo validados
- `filter_category` (Optional[str]): Filtrar por categoría

**Retorna:** Lista de documentos similares con scores

##### `get_by_id(doc_id)`
Obtiene un documento por su ID.

**Parámetros:**
- `doc_id` (int): ID del documento

**Retorna:** Diccionario con información del documento

##### `update_validation(doc_id, validated, validated_by)`
Actualiza el estado de validación de un documento.

**Parámetros:**
- `doc_id` (int): ID del documento
- `validated` (bool): Nuevo estado de validación
- `validated_by` (Optional[str]): Usuario que validó

**Retorna:** True si se actualizó correctamente

##### `delete_document(doc_id)`
Elimina un documento del vector store.

**Parámetros:**
- `doc_id` (int): ID del documento

**Retorna:** True si se eliminó

##### `get_statistics()`
Obtiene estadísticas del vector store.

**Retorna:** Diccionario con estadísticas

### ✅ Función `get_vector_store()`
Obtiene la instancia global del vector store (singleton).

---

## 📊 Estadísticas

- **Total de herramientas**: 20+ tools implementados
- **Líneas de código agregadas**: ~1,948 líneas
- **Archivos nuevos**: 2 (rag_tools.py, vector_store.py)
- **Archivos actualizados**: 5 (patient_tools.py, appointment_tools.py, query_tools.py, tools/__init__.py, utils/__init__.py)

---

## 🎯 Patrones Implementados

Todas las herramientas siguen los patrones obligatorios:

✅ **Decorator @tool** de LangChain  
✅ **Funciones async** donde corresponde  
✅ **Estructura de respuesta consistente** con `{"success": True/False, "data": {...}}`  
✅ **Manejo de excepciones** con try/except  
✅ **Integración con utils** (execute_query, get_embeddings_service)  
✅ **Docstrings completos** con Args y Returns  

---

## 🚀 Próximos Pasos

1. ✅ FASE 3: Herramientas - **COMPLETADA**
2. ✅ FASE 4: Utilidades Avanzadas - **COMPLETADA**
3. ⏳ FASE 5: Testing - Pendiente
   - Tests unitarios de cada tool
   - Tests de integración con BD
   - Tests end-to-end de flujos completos

---

## 📝 Notas de Implementación

- Todas las herramientas están listas para usar en los nodos del grafo LangGraph
- El VectorStore usa pgvector para búsqueda semántica real
- Los embeddings se generan con all-MiniLM-L6-v2 (384 dimensiones)
- La búsqueda semántica usa similitud coseno con threshold configurable
- Los documentos pueden ser validados por admins para mejorar la calidad

---

**Fecha de completación**: 2025-12-29  
**Estado**: ✅ FASE 3 Y 4 COMPLETADAS - LISTO PARA TESTING
