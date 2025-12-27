# 🗄️ Base de Datos Podoskin Solution - COMPLETA

Sistema integral de gestión clínica para podología con asistente de voz IA, CRM, inventario y cumplimiento COFEPRIS.

## 📋 Archivos SQL (Orden de Ejecución)

| # | Archivo | Descripción | Tablas/Vistas |
|---|---------|-------------|---------------|
| 0 | `00_inicializacion.sql` | Extensión pgvector | 0 |
| 1 | `01_funciones.sql` | Funciones del sistema | 5 funciones |
| 2 | `02_usuarios.sql` | Usuarios y podólogos | 2 tablas |
| 3 | `03_pacientes.sql` | Expediente clínico | 6 tablas |
| 4 | `04_citas_tratamientos.sql` | Agenda y pagos | 8 tablas |
| 5 | `05_chatbot_crm.sql` | Mensajería y CRM | 10 tablas |
| 6 | `06_vistas.sql` | Vistas de consulta | 2 vistas |
| 7 | `07_asistente_voz_consulta.sql` | **Asistente de voz Gemini Live** | 7 tablas + 2 vistas |
| 8 | `08_recordatorios_automatizacion.sql` | **Recordatorios y análisis** | 2 tablas + 3 vistas |
| 9 | `09_inventario_materiales.sql` | **Control de inventario** | 3 tablas + 4 vistas |
| 10 | `10_dashboard_kpis.sql` | **Dashboard y KPIs** | 0 tablas + 9 vistas |
| 11 | `11_horarios_personal.sql` | **Gestión de horarios** | 2 tablas + 2 vistas |
| 12 | `12_documentos_impresion.sql` | **Documentos médicos e impresión** | 2 tablas + 2 vistas |

**Total**: 42 tablas + 24 vistas + 15+ funciones

---

## 🎯 Características Principales

### 1. 🎙️ Asistente de Voz con Gemini Live

- ✅ Transcripción en tiempo real de consultas
- ✅ Llenado automático de formularios por voz
- ✅ Consultas al historial del paciente
- ✅ Generación de resúmenes automáticos
- ✅ Auditoría completa de acciones de IA
- ✅ 8 Function Declarations predefinidas

### 2. 📅 Gestión Clínica Completa

- ✅ Expediente médico digital (alergias, antecedentes, signos vitales)
- ✅ Notas clínicas estructuradas
- ✅ Evolución de tratamientos por fases
- ✅ Archivos multimedia (fotos clínicas, estudios)
- ✅ Consentimientos informados con firma digital

### 3. 🗓️ Sistema de Citas Inteligente

- ✅ Agenda con validación de disponibilidad
- ✅ Horarios de trabajo configurables
- ✅ Bloqueos de agenda (vacaciones, días festivos)
- ✅ Recordatorios automáticos (24h y 2h antes)
- ✅ Seguimiento post-cancelación
- ✅ Análisis de patrones de cancelación

### 4. 💬 CRM y Chatbot

- ✅ Gestión de contactos multicanal (WhatsApp, Telegram, Facebook)
- ✅ Conversaciones con categorización automática
- ✅ Plantillas de mensajes personalizables
- ✅ Respuestas automáticas configurables
- ✅ Métricas en tiempo real
- ✅ Análisis de conversiones

### 5. 📦 Control de Inventario

- ✅ Catálogo de productos y materiales
- ✅ Movimientos de entrada/salida automáticos
- ✅ Alertas de stock bajo
- ✅ Control de caducidad
- ✅ Relación tratamiento-materiales
- ✅ Descuento automático al completar cita
- ✅ Valor del inventario en tiempo real

### 6. 📊 Dashboard y KPIs

- ✅ Dashboard ejecutivo en tiempo real
- ✅ KPIs mensuales automáticos
- ✅ Análisis de tratamientos más solicitados
- ✅ Top pacientes por valor
- ✅ Reporte de ingresos detallado
- ✅ Análisis de conversiones CRM
- ✅ Alertas del sistema

### 7. 📄 Documentos e Impresión

- ✅ Generación de notas de cobro
- ✅ Historial médico completo imprimible
- ✅ Evoluciones de tratamiento
- ✅ Consentimientos informados
- ✅ Firmas digitales con trazabilidad
- ✅ Control de archivo físico (COFEPRIS)
- ✅ Plantillas HTML personalizables

### 8. 📈 Análisis y Reportes

- ✅ Scoring de pacientes (adherencia, valor, riesgo)
- ✅ Identificación de pacientes que requieren seguimiento
- ✅ Análisis de cancelaciones por período
- ✅ Productos más usados
- ✅ Capacidad mensual de agenda

---

## 🐳 Instalación con Docker

### 1. Estructura del Proyecto

```
podoskin-project/
├── data/                    <-- Esta carpeta
│   ├── 00_inicializacion.sql
│   ├── 01_funciones.sql
│   ├── ...
│   └── 12_documentos_impresion.sql
├── backend/
│   └── .env
└── docker-compose.yml
```

### 2. Docker Compose

```yaml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: podoskin_db
    environment:
      POSTGRES_DB: podoskin_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - ./data:/docker-entrypoint-initdb.d
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Levantar el Sistema

```bash
docker-compose up -d
docker logs -f podoskin_db  # Ver progreso
```

---

## 🔧 Configuración del Backend

### Variables de Entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/podoskin_db

# Gemini AI
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-2.0-flash-exp

# Almacenamiento
STORAGE_BUCKET=podoskin-recordings
STORAGE_REGION=us-central1
```

---

## 📊 Casos de Uso Principales

### Durante la Consulta (Asistente de Voz)

```
Doctor: "Peso 75 kilos, talla 170, presión 120/80"
IA: [Llama update_vital_signs()]
IA: "Registrado. IMC: 25.95"

Doctor: "¿Tiene alergias?"
IA: [Llama query_patient_data()]
IA: "Sí, alergia a penicilina desde 2020"
```

### Análisis de Cancelaciones

```sql
-- ¿Quién canceló este mes?
SELECT * FROM obtener_cancelaciones_periodo(
  DATE_TRUNC('month', CURRENT_DATE),
  CURRENT_DATE
);
```

### Control de Inventario

```sql
-- Productos con stock bajo
SELECT * FROM alertas_stock_bajo;

-- Registrar entrada de inventario
SELECT registrar_entrada_inventario(
  p_id_producto := 5,
  p_cantidad := 100,
  p_costo_unitario := 15.50,
  p_numero_factura := 'FAC-2024-001'
);
```

### Impresión de Documentos

```sql
-- Generar historial médico completo
SELECT generar_historial_medico_completo(123);

-- Generar nota de cobro
SELECT generar_nota_cobro(456);

-- Documentos pendientes de archivo
SELECT * FROM documentos_pendientes_archivo;
```

### Dashboard Ejecutivo

```sql
-- Ver dashboard en tiempo real
SELECT * FROM dashboard_ejecutivo;

-- KPIs del mes actual
SELECT * FROM kpis_mensuales 
WHERE mes = DATE_TRUNC('month', CURRENT_DATE);

-- Alertas del sistema
SELECT * FROM alertas_sistema;
```

---

## 🔐 Cumplimiento COFEPRIS

### Documentos Físicos Requeridos

El sistema permite generar e imprimir:

1. ✅ **Historial médico completo** con firmas
2. ✅ **Evoluciones de tratamiento** por separado
3. ✅ **Consentimientos informados** firmados
4. ✅ **Notas clínicas** de cada consulta

### Control de Archivo Físico

```sql
-- Marcar documento como archivado físicamente
UPDATE documentos_generados
SET archivado_fisicamente = true,
    ubicacion_archivo_fisico = 'Expediente 2024-001, Carpeta A',
    fecha_archivo = NOW()
WHERE id = 123;

-- Ver documentos pendientes de archivar
SELECT * FROM documentos_pendientes_archivo;
```

---

## 📚 Documentación Adicional

- **[GEMINI_LIVE_FUNCTIONS.md](./GEMINI_LIVE_FUNCTIONS.md)**: Function Declarations completas
- **[GUIA_PRO_SETUP.md](./GUIA_PRO_SETUP.md)**: Guía de instalación detallada
- **Ejemplo de integración**: Ver carpeta `gemini-live-voice-controller/`

---

## 🆘 Consultas Útiles

### Pacientes que Requieren Seguimiento

```sql
SELECT * FROM pacientes_requieren_seguimiento
WHERE prioridad_seguimiento IN ('Alta', 'Urgente');
```

### Tratamientos Más Rentables

```sql
SELECT * FROM tratamientos_mas_solicitados
ORDER BY ingresos_generados DESC
LIMIT 10;
```

### Horarios Disponibles

```sql
SELECT * FROM obtener_horarios_disponibles(
  p_id_podologo := 1,
  p_fecha := CURRENT_DATE + 1
);
```

### Capacidad de Agenda

```sql
SELECT * FROM calcular_capacidad_mensual(
  p_id_podologo := 1,
  p_mes := CURRENT_DATE
);
```

---

## 🚀 Próximos Pasos

1. ✅ Instalar base de datos con Docker
2. ✅ Configurar backend con Gemini API
3. ✅ Implementar Function Calling en frontend
4. ✅ Probar flujo de consulta con voz
5. ✅ Configurar worker para recordatorios
6. ✅ Diseñar plantillas de documentos HTML
7. ✅ Configurar impresora para documentos médicos

---

**Desarrollado para**: Podoskin Solution - Dr. Santiago de Jesús Ornelas Reynoso  
**Versión**: 3.0 (Sistema Completo)  
**Última actualización**: 2025-12-19  
**Tablas**: 42 | **Vistas**: 24 | **Funciones**: 15+
