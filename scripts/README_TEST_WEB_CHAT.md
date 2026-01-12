# Simuladores de Chat Web

Scripts de prueba para simular el flujo completo del chat web con el agente Maya.

## 📁 Scripts Disponibles

### 1. `test_web_chat_simple.py` ⭐ RECOMENDADO

Versión simple con `requests` (síncrono). Más fácil de usar y debuggear.

**Uso:**
```bash
cd /workspaces/Podiskin_solution
python scripts/test_web_chat_simple.py
```

**Requisitos:**
```bash
pip install requests
```

### 2. `test_web_chat.py`

Versión avanzada con `aiohttp` (asíncrono) y colores en terminal.

**Uso:**
```bash
cd /workspaces/Podiskin_solution
python scripts/test_web_chat.py
```

**Requisitos:**
```bash
pip install aiohttp colorama
```

## 🔍 ¿Qué prueban estos scripts?

Simulan el flujo completo de un usuario en el chat web:

### Fase 1: Health Check
- Verifica que el backend esté corriendo
- Valida que el endpoint `/api/chatbot/health` responda

### Fase 2: Conversación sin Registro
- Envía mensajes como usuario anónimo
- Verifica respuestas del agente Maya
- Sin `patient_id` todavía

**Ejemplo:**
```
👤 Usuario: Hola, ¿cuáles son sus horarios de atención?
🤖 Maya: ¡Hola! 😊 Nuestros horarios son...
```

### Fase 3: Búsqueda de Paciente
- Llama a `POST /api/patient/lookup`
- Busca si el paciente ya existe
- Datos de prueba: **Amelia Vargas** (04/05/1995)

**Request:**
```json
{
  "first_name": "Amelia",
  "first_last_name": "Vargas",
  "birth_date": "1995-05-04"
}
```

**Response (no existe):**
```json
{
  "found": false,
  "patient_id": null
}
```

### Fase 4: Registro de Paciente
- Si no existe, llama a `POST /api/patient/register`
- Backend inserta en tabla `pacientes`
- **Trigger genera automáticamente el `patient_id`**

**Request:**
```json
{
  "first_name": "Amelia",
  "second_name": "Sofia",
  "first_last_name": "Vargas",
  "second_last_name": "Mendoza",
  "birth_date": "1995-05-04"
}
```

**Response (éxito):**
```json
{
  "success": true,
  "patient_id": "VA-AM-0504-0009",
  "message": "Paciente registrado exitosamente"
}
```

**Formato del ID:**
```
VA-AM-0504-0009
│  │  │    │
│  │  │    └─ Contador: 0009 (9º paciente con ese partial_id)
│  │  └────── Fecha nacimiento: 0504 (04 de mayo, MMDD)
│  └───────── Últimas 2 letras nombre: AM (Amelia)
└──────────── Últimas 2 letras apellido: VA (Vargas)
```

### Fase 5: Conversación con Registro
- Envía mensajes incluyendo `patient_info`
- Backend vincula conversación con paciente
- Maya tiene contexto completo del paciente

**Request:**
```json
{
  "message": "Quiero agendar una cita",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-12T10:30:00Z",
  "patient_info": {
    "patient_id": "VA-AM-0504-0009",
    "first_name": "Amelia",
    "first_last_name": "Vargas",
    "is_registered": true
  }
}
```

### Fase 6: Verificación en BD
- Muestra comandos SQL para verificar datos
- Consulta `web_chat_sessions` y `web_chat_messages`

## 🚀 Ejecución Rápida

### Opción 1: Simple (recomendado)

```bash
# Asegúrate de que el backend esté corriendo
cd /workspaces/Podiskin_solution/backend
python main.py &

# Ejecuta el simulador
cd /workspaces/Podiskin_solution
python scripts/test_web_chat_simple.py
```

### Opción 2: Con colores

```bash
# Instalar dependencias
pip install aiohttp colorama

# Ejecutar
python scripts/test_web_chat.py
```

## 📊 Salida Esperada

```
╔════════════════════════════════════════════════════════════════╗
║   SIMULADOR SIMPLE DE CHAT WEB - PODOSKIN SOLUTION            ║
║   Prueba de integración Web Chat + Agente Maya                ║
╚════════════════════════════════════════════════════════════════╝

Session ID: 550e8400-e29b-41d4-a716-446655440000

====================================================================
>>> 1. VERIFICANDO BACKEND
====================================================================
✅ Backend conectado: Web Chat API funcionando correctamente
   Agente: whatsapp_medico (Maya)
   Canal: web

====================================================================
>>> 2. CONVERSACIÓN SIN REGISTRO
====================================================================

👤 Usuario: Hola, ¿cuáles son sus horarios de atención?
🤖 Maya: ¡Hola! 😊 Nuestros horarios son de lunes a viernes...
   💡 Sugerencias: Agendar una cita, Ver servicios, Hablar con un asesor

====================================================================
>>> 3. BÚSQUEDA DE PACIENTE
====================================================================
Buscando: Amelia Vargas
Fecha de nacimiento: 1995-05-04

📄 Resultado de búsqueda:
{
  "found": false,
  "patient_id": null,
  "first_name": null,
  "first_last_name": null,
  "registration_date": null
}

====================================================================
>>> 4. REGISTRO DE NUEVO PACIENTE
====================================================================
Paciente no encontrado. Procediendo con el registro...

🎉 PACIENTE REGISTRADO EXITOSAMENTE
📄 Respuesta del servidor:
{
  "success": true,
  "patient_id": "VA-AM-0504-0009",
  "message": "Paciente registrado exitosamente"
}

✅ 🆔 ID COMPLETO GENERADO: VA-AM-0504-0009
   📌 Últimas 2 letras apellido: VA
   📌 Últimas 2 letras nombre: AM
   📌 Fecha nacimiento (MMDD): 0504
   📌 Contador: 0009

   ✅ FORMATO CORRECTO: [AP]-[NO]-[MMDD]-[####]

====================================================================
>>> 5. CONVERSACIÓN CON PACIENTE REGISTRADO
====================================================================

👤 Usuario: Quiero agendar una cita
   (Enviando con patient_id: VA-AM-0504-0009)
🤖 Maya: ¡Perfecto Amelia! Para agendar tu cita...

====================================================================
>>> 6. RESUMEN DE LA SESIÓN
====================================================================
✅ Session ID: 550e8400-e29b-41d4-a716-446655440000
✅ Patient ID: VA-AM-0504-0009
✅ Paciente: Amelia Vargas
✅ Fecha de nacimiento: 1995-05-04
====================================================================
```

## 🔍 Verificación en Base de Datos

Después de ejecutar el script, verifica los datos en PostgreSQL:

```sql
-- Ver sesión creada
SELECT * FROM web_chat_sessions 
WHERE session_id = '550e8400-e29b-41d4-a716-446655440000';

-- Ver mensajes de la conversación
SELECT message_type, content, timestamp 
FROM web_chat_messages 
WHERE session_id = '550e8400-e29b-41d4-a716-446655440000' 
ORDER BY timestamp;

-- Ver paciente registrado
SELECT id, patient_id, primer_nombre, primer_apellido, fecha_nacimiento
FROM pacientes
WHERE patient_id = 'VA-AM-0504-0009';

-- Ver contacto creado
SELECT * FROM contactos WHERE id_paciente IN (
    SELECT id FROM pacientes WHERE patient_id = 'VA-AM-0504-0009'
);

-- Ver conversación creada
SELECT * FROM conversaciones WHERE id_contacto IN (
    SELECT id FROM contactos WHERE id_paciente IN (
        SELECT id FROM pacientes WHERE patient_id = 'VA-AM-0504-0009'
    )
) AND canal = 'web';
```

## 🧪 Casos de Prueba

### Caso 1: Usuario Nuevo
```bash
python scripts/test_web_chat_simple.py
```
- ✅ Debe generar nuevo `patient_id`
- ✅ Formato: `VA-AM-0504-0001` (primer paciente)

### Caso 2: Usuario Existente
```bash
# Ejecutar el script por segunda vez
python scripts/test_web_chat_simple.py
```
- ✅ Debe encontrar paciente existente
- ✅ Reutilizar `patient_id: VA-AM-0504-0001`

### Caso 3: Múltiples Pacientes con Mismo Partial ID
```bash
# Modificar TEST_PATIENT en el script:
# - Cambiar first_name a "Alejandra" (mantener last_name="Vargas", birth_date="1995-05-04")
# - Ejecutar script
```
- ✅ Debe generar: `VA-RA-0504-0002` (contador incrementado)

## 🐛 Troubleshooting

### Error: "No se pudo conectar al backend"
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/api/chatbot/health

# Si no responde, iniciar el backend:
cd /workspaces/Podiskin_solution/backend
python main.py
```

### Error: "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
```

### Error: "Table 'pacientes' does not exist"
```bash
# Aplicar migración SQL
cd /workspaces/Podiskin_solution
psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql
```

### Error: "Trigger 'generate_patient_id' does not exist"
```bash
# Verificar que la migración se aplicó correctamente
psql -U postgres -d podoskin_db -c "\d pacientes"
psql -U postgres -d podoskin_db -c "SELECT trigger_name FROM information_schema.triggers WHERE trigger_name = 'trigger_generate_patient_id';"
```

## 📝 Personalización

Para probar con otros datos, modifica las variables en el script:

```python
# En test_web_chat_simple.py o test_web_chat.py

TEST_PATIENT = {
    "first_name": "Carlos",        # Cambiar nombre
    "second_name": "Eduardo",
    "first_last_name": "Ramírez",  # Cambiar apellido
    "second_last_name": "López",
    "birth_date": "1988-03-15"     # Cambiar fecha (YYYY-MM-DD)
}
```

**ID esperado para este ejemplo:**
```
EZ-OS-0315-0001
│  │  │    │
│  │  │    └─ Contador: 0001
│  │  └────── Fecha: 0315 (15 de marzo)
│  └───────── Últimas 2 letras nombre: OS (Carlos)
└──────────── Últimas 2 letras apellido: EZ (Ramírez)
```

## ✅ Checklist de Pruebas

- [ ] Backend responde en `/api/chatbot/health`
- [ ] Endpoint `/api/patient/lookup` busca pacientes
- [ ] Endpoint `/api/patient/register` registra nuevos pacientes
- [ ] Trigger genera `patient_id` con formato correcto
- [ ] Endpoint `/api/chatbot/message` procesa mensajes
- [ ] Maya responde coherentemente
- [ ] Datos se guardan correctamente en BD
- [ ] Sesiones y mensajes se registran en tablas correctas
- [ ] `patient_id` es único por paciente
- [ ] Contador incrementa correctamente para mismo `partial_id`

## 📚 Referencias

- Documentación completa: [INTEGRACION_WEB_CHAT_WHATSAPP.md](../INTEGRACION_WEB_CHAT_WHATSAPP.md)
- API Web Chat: [backend/api/web_chat_api.py](../backend/api/web_chat_api.py)
- Migración SQL: [data/migrations/20_web_chat_integration.sql](../data/migrations/20_web_chat_integration.sql)
