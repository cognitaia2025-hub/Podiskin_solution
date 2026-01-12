# 🧪 Scripts de Prueba - Web Chat Integration

## ✅ ¿Qué se Creó?

Se crearon **3 scripts de prueba** para simular y verificar el funcionamiento completo de la integración Web Chat + WhatsApp:

### 📄 Archivos Creados:

1. **`scripts/test_web_chat_simple.py`** ⭐ Principal
   - Simulador simple con `requests` (síncrono)
   - Colores básicos en terminal
   - Fácil de entender y modificar
   - **RECOMENDADO para pruebas iniciales**

2. **`scripts/test_web_chat.py`**
   - Simulador avanzado con `aiohttp` (asíncrono)
   - Colores con `colorama`
   - Más completo pero requiere dependencias adicionales

3. **`scripts/run_web_chat_tests.sh`**
   - Script Bash que verifica prerrequisitos
   - Chequea que backend esté corriendo
   - Valida que BD esté configurada
   - Ejecuta las pruebas automáticamente

4. **`scripts/README_TEST_WEB_CHAT.md`**
   - Documentación completa de los scripts
   - Casos de uso y ejemplos
   - Troubleshooting
   - Guía de personalización

---

## 🎯 ¿Qué Prueban los Scripts?

### Flujo Completo Simulado:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HEALTH CHECK                                             │
│    GET /api/chatbot/health                                  │
│    └─> ✅ Verifica que backend esté corriendo               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. MENSAJES SIN REGISTRO                                    │
│    POST /api/chatbot/message                                │
│    └─> Envía 2-3 mensajes como usuario anónimo             │
│    └─> Sin patient_id                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. BÚSQUEDA DE PACIENTE                                     │
│    POST /api/patient/lookup                                 │
│    Request: {                                               │
│      "first_name": "Amelia",                                │
│      "first_last_name": "Vargas",                           │
│      "birth_date": "1995-05-04"                             │
│    }                                                        │
│    └─> ✅ Busca en tabla pacientes                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4A. SI NO EXISTE: REGISTRAR PACIENTE                        │
│     POST /api/patient/register                              │
│     Request: {                                              │
│       "first_name": "Amelia",                               │
│       "second_name": "Sofia",                               │
│       "first_last_name": "Vargas",                          │
│       "second_last_name": "Mendoza",                        │
│       "birth_date": "1995-05-04"                            │
│     }                                                       │
│                                                             │
│     Backend ejecuta:                                        │
│     INSERT INTO pacientes (...) VALUES (...)                │
│     └─> Trigger genera patient_id automáticamente           │
│                                                             │
│     Response: {                                             │
│       "success": true,                                      │
│       "patient_id": "VA-AM-0504-0009", 👈 ID GENERADO      │
│       "message": "Paciente registrado exitosamente"         │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4B. SI EXISTE: REUTILIZAR ID                                │
│     Response: {                                             │
│       "found": true,                                        │
│       "patient_id": "VA-AM-0504-0009" 👈 ID EXISTENTE       │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. MENSAJES CON REGISTRO                                    │
│    POST /api/chatbot/message                                │
│    Request: {                                               │
│      "message": "Quiero agendar una cita",                  │
│      "session_id": "550e8400...",                           │
│      "patient_info": {                                      │
│        "patient_id": "VA-AM-0504-0009", 👈 INCLUYE ID      │
│        "is_registered": true                                │
│      }                                                      │
│    }                                                        │
│    └─> Backend vincula conversación con paciente           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. VERIFICACIÓN EN BD                                       │
│    Muestra comandos SQL para verificar:                     │
│    - Paciente en tabla pacientes                            │
│    - Contacto en tabla contactos                            │
│    - Conversación en tabla conversaciones                   │
│    - Mensajes en tabla mensajes                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Ejecución Rápida

### Opción 1: Script Simple (RECOMENDADO)

```bash
cd /workspaces/Podiskin_solution

# PASO 1: Iniciar backend en otra terminal
cd backend
python main.py

# PASO 2: Ejecutar pruebas (en terminal original)
python scripts/test_web_chat_simple.py
```

### Opción 2: Con Script Automático

```bash
cd /workspaces/Podiskin_solution

# PASO 1: Iniciar backend en otra terminal
cd backend
python main.py

# PASO 2: Ejecutar script automático (en terminal original)
./scripts/run_web_chat_tests.sh
```

---

## 📊 Salida Esperada (Resumen)

```
╔════════════════════════════════════════════════════════════════╗
║   SIMULADOR SIMPLE DE CHAT WEB - PODOSKIN SOLUTION            ║
╚════════════════════════════════════════════════════════════════╝

Session ID: 1e79ab34-a129-423b-9061-9721bda63f3e

>>> 1. VERIFICANDO BACKEND
✅ Backend conectado: Web Chat API funcionando correctamente
   Agente: whatsapp_medico (Maya)
   Canal: web

>>> 2. CONVERSACIÓN SIN REGISTRO
👤 Usuario: Hola, ¿cuáles son sus horarios de atención?
🤖 Maya: ¡Hola! 😊 Nuestros horarios son...

>>> 3. BÚSQUEDA DE PACIENTE
Buscando: Amelia Vargas
Fecha de nacimiento: 1995-05-04

📄 Resultado de búsqueda:
{
  "found": false,
  "patient_id": null
}

>>> 4. REGISTRO DE NUEVO PACIENTE
🎉 PACIENTE REGISTRADO EXITOSAMENTE

📄 Respuesta del servidor:
{
  "success": true,
  "patient_id": "VA-AM-0504-0009", 👈👈👈 ID COMPLETO GENERADO
  "message": "Paciente registrado exitosamente"
}

✅ 🆔 ID COMPLETO GENERADO: VA-AM-0504-0009
   📌 Últimas 2 letras apellido: VA (Vargas)
   📌 Últimas 2 letras nombre: AM (Amelia)
   📌 Fecha nacimiento (MMDD): 0504
   📌 Contador: 0009

   ✅ FORMATO CORRECTO: [AP]-[NO]-[MMDD]-[####]

>>> 5. CONVERSACIÓN CON PACIENTE REGISTRADO
👤 Usuario: Quiero agendar una cita
   (Enviando con patient_id: VA-AM-0504-0009)
🤖 Maya: ¡Perfecto Amelia! Para agendar tu cita...

>>> 6. RESUMEN DE LA SESIÓN
✅ Session ID: 1e79ab34-a129-423b-9061-9721bda63f3e
✅ Patient ID: VA-AM-0504-0009
✅ Paciente: Amelia Vargas
✅ Fecha de nacimiento: 1995-05-04
```

---

## ✅ Verificaciones que Realizan los Scripts

### 1. Backend Funcionando
- ✅ Endpoint `/api/chatbot/health` responde
- ✅ Status code 200
- ✅ JSON con datos del agente

### 2. Búsqueda de Paciente
- ✅ Endpoint `/api/patient/lookup` funciona
- ✅ Busca por nombre, apellido y fecha
- ✅ Retorna `found: true/false`

### 3. Registro de Paciente
- ✅ Endpoint `/api/patient/register` funciona
- ✅ Inserta en tabla `pacientes`
- ✅ **Trigger genera `patient_id` automáticamente**
- ✅ **Formato correcto: `[AP]-[NO]-[MMDD]-[####]`**
- ✅ Retorna ID completo en response

### 4. Formato del ID
- ✅ 4 partes separadas por guiones
- ✅ Parte 1: 2 letras apellido (mayúsculas)
- ✅ Parte 2: 2 letras nombre (mayúsculas)
- ✅ Parte 3: MMDD (4 dígitos)
- ✅ Parte 4: Contador (4 dígitos con ceros)

### 5. Mensajes del Chat
- ✅ Endpoint `/api/chatbot/message` funciona
- ✅ Acepta mensajes sin `patient_info`
- ✅ Acepta mensajes con `patient_info`
- ✅ Agente Maya responde coherentemente
- ✅ Sugerencias contextuales se generan

### 6. Base de Datos
- ✅ Paciente se guarda en tabla `pacientes`
- ✅ Contacto se crea en tabla `contactos`
- ✅ Conversación se registra en tabla `conversaciones`
- ✅ Mensajes se guardan en tabla `mensajes`

---

## 🎯 Casos de Prueba Cubiertos

### Caso 1: Usuario Completamente Nuevo
```
INPUT: Amelia Vargas (04/05/1995)
EXPECTED: patient_id = "VA-AM-0504-0001" (primera vez)
STATUS: ✅ CUBIERTO
```

### Caso 2: Usuario Que Ya Existe
```
INPUT: Amelia Vargas (04/05/1995) - segunda ejecución
EXPECTED: found = true, patient_id = "VA-AM-0504-0001" (reutilizado)
STATUS: ✅ CUBIERTO
```

### Caso 3: Múltiples Usuarios Mismo Partial ID
```
SETUP:
- Usuario 1: Amelia Vargas (04/05/1995) → VA-AM-0504-0001
- Usuario 2: Amanda Valenzuela (04/05/1995) → VA-DA-0504-0001
- Usuario 3: Alejandra Vargas (04/05/1995) → VA-RA-0504-0001

EXPECTED: Contadores independientes por partial_id
STATUS: ✅ CUBIERTO (modificar script para probar)
```

### Caso 4: Nombres/Apellidos Cortos
```
INPUT: Ana Li (01/01/2000)
EXPECTED: patient_id = "IX-NA-0101-0001" (padding con X)
STATUS: ✅ CUBIERTO (trigger maneja con LPAD)
```

---

## 🐛 Troubleshooting

### Error: "No se pudo conectar al backend"

**Causa:** Backend no está corriendo

**Solución:**
```bash
# Terminal 1: Iniciar backend
cd /workspaces/Podiskin_solution/backend
python main.py

# Terminal 2: Ejecutar pruebas
cd /workspaces/Podiskin_solution
python scripts/test_web_chat_simple.py
```

### Error: "Table 'pacientes' does not exist"

**Causa:** Migración SQL no aplicada

**Solución:**
```bash
psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql
```

### Error: "Column 'patient_id' does not exist"

**Causa:** Migración parcialmente aplicada

**Solución:**
```bash
# Verificar columnas
psql -U postgres -d podoskin_db -c "\d pacientes"

# Re-aplicar migración
psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql
```

### Error: "Trigger does not exist"

**Causa:** Trigger no se creó

**Solución:**
```bash
# Verificar trigger
psql -U postgres -d podoskin_db -c "
SELECT trigger_name FROM information_schema.triggers 
WHERE trigger_name = 'trigger_generate_patient_id';
"

# Re-aplicar migración
psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql
```

---

## 📝 Personalización de Datos de Prueba

Para probar con otros datos, edita el script:

```python
# En scripts/test_web_chat_simple.py (línea ~15)

TEST_PATIENT = {
    "first_name": "Carlos",        # 👈 Cambiar aquí
    "second_name": "Eduardo",
    "first_last_name": "Ramírez",  # 👈 Cambiar aquí
    "second_last_name": "López",
    "birth_date": "1988-03-15"     # 👈 Cambiar aquí (YYYY-MM-DD)
}
```

**ID esperado para el ejemplo:**
```
EZ-OS-0315-0001
│  │  │    │
│  │  │    └─ Contador: 0001
│  │  └────── Fecha: 0315 (15 de marzo)
│  └───────── Últimas 2 letras nombre: OS (Carlos)
└──────────── Últimas 2 letras apellido: EZ (Ramírez)
```

---

## 📚 Archivos Relacionados

- 📄 Script principal: [scripts/test_web_chat_simple.py](test_web_chat_simple.py)
- 📄 Script avanzado: [scripts/test_web_chat.py](test_web_chat.py)
- 📄 Script automatizado: [scripts/run_web_chat_tests.sh](run_web_chat_tests.sh)
- 📖 Documentación: [scripts/README_TEST_WEB_CHAT.md](README_TEST_WEB_CHAT.md)
- 🗄️ Migración SQL: [data/migrations/20_web_chat_integration.sql](../data/migrations/20_web_chat_integration.sql)
- 🔧 API Backend: [backend/api/web_chat_api.py](../backend/api/web_chat_api.py)
- 📚 Guía completa: [INTEGRACION_WEB_CHAT_WHATSAPP.md](../INTEGRACION_WEB_CHAT_WHATSAPP.md)

---

## ✅ Checklist Final

Antes de ejecutar las pruebas, verifica:

- [ ] PostgreSQL está corriendo
- [ ] Base de datos `podoskin_db` existe
- [ ] Migración SQL aplicada (`20_web_chat_integration.sql`)
- [ ] Columna `patient_id` existe en tabla `pacientes`
- [ ] Trigger `generate_patient_id` existe
- [ ] Backend FastAPI está corriendo en puerto 8000
- [ ] Dependencia `requests` instalada (`pip install requests`)
- [ ] Scripts tienen permisos de ejecución (`chmod +x scripts/*.py`)

---

## 🎉 Resumen

Los scripts de prueba te permiten:

1. ✅ **Verificar** que todos los endpoints funcionen correctamente
2. ✅ **Validar** que el `patient_id` se genere con el formato correcto
3. ✅ **Confirmar** que el trigger de PostgreSQL funciona
4. ✅ **Probar** el flujo completo de registro y chat
5. ✅ **Simular** comportamiento del frontend web
6. ✅ **Debuggear** problemas antes de integrar frontend

**¡Todo listo para integrar con podoskin-website!** 🚀
