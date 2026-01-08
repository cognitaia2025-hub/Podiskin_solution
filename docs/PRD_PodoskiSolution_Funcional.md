# Documento de Requisitos del Producto (PRD) - Podoskin Solution

**Versión:** 1.1 (Completa)  
**Fecha:** 08/01/2026  
**Idioma:** Español  

---

## 📋 Introducción

El presente documento describe las funcionalidades y requisitos de **todos los módulos** de la aplicación **Podoskin Solution**, incluyendo aquellos de gestión financiera y de pacientes, tras verificar la corrección de incidencias previas. Este PRD constituye la especificación "Estado del Arte" de la plataforma.

---

## 📱 Estructura de Navegación y Módulos

La aplicación se organiza en pestañas principales accesibles desde la barra de navegación global (`GlobalNavigation`).

### 1. Dashboard (Panel Principal)

**Ruta:** `/dashboard`  
**Objetivo:** Proveer una visión general inmediata del estado de la clínica mediante indicadores clave de rendimiento (KPIs) y gráficos de tendencias.

#### Requisitos Funcionales

- **KPIs en Tiempo Real:** Visualización de tarjetas con métricas críticas:
  - Total de Pacientes activos.
  - Citas programadas para el día actual.
  - Ingresos estimados del mes actual.
  - Porcentaje de ocupación de la agenda.
- **Gráficos de Tendencias:**
  - *Curva de Citas:* Gráfico lineal que muestra la evolución del volumen de citas.
  - *Estado de Citas (Pie Chart):* Distribución porcentual (Completadas, Canceladas, Pendientes, No Asistió).
  - *Ingresos:* Gráfico de barras comparativo de ingresos.
- **Tratamientos Top:** Tabla resumen con los tratamientos más solicitados.

### 2. Calendario (Agenda Inteligente)

**Ruta:** `/calendar`  
**Objetivo:** Gestión centralizada de la disponibilidad y programación de citas.

#### Requisitos Funcionales

- **Vistas Múltiples:** Mensual, Semanal, Diaria, Agenda (Lista) y por Equipo (Staff).
- **Gestión de Citas:**
  - Creación rápida (clic en bloque) y arrastrar para reprogramar.
  - Filtrado dinámico por Doctor y Búsqueda de Paciente.
  - Códigos de color por estado.
- **Indicadores Visuales:** Alertas para citas de "Primera Vez" y notas.

### 3. Gestión de Pacientes

**Ruta:** `/patients`
**Objetivo:** Administración completa del directorio de pacientes y sus datos demográficos.

#### Requisitos Funcionales

- **Directorio Centralizado:** Listado paginado de todos los pacientes registrados.
- **Búsqueda Inteligente:** Filtrado en tiempo real por nombre, teléfono o correo electrónico.
- **Gestión de Perfiles:**
  - Alta de nuevos pacientes con validación de campos obligatorios (nombre, contacto).
  - Edición de información existente.
  - Desactivación ("Soft Delete") de pacientes inactivos.
- **Accesibilidad:** Acceso directo al expediente médico desde la tarjeta del paciente.

### 4. Gestión Médica

**Ruta:** `/medical` (Submenú)
**Objetivo:** Documentación clínica integral y seguimiento.

#### 4.1 Atención Médica

**Ruta:** `/medical/attention`

- **Flujo Clínico:** Interfaz paso a paso para la consulta activa.
- **Historia Clínica (SOAP):** Registros estructurados.
- **Evoluciones:** Historial de cambios y progreso.

#### 4.2 Expedientes Médicos

**Ruta:** `/medical/records`

- **Repositorio Digital:** Historial completo del paciente.
- **Búsqueda Avanzada:** Localización por ID o datos personales.

### 5. Gestión de Cobros (Billing)

**Ruta:** `/billing`
**Objetivo:** Control financiero, registro de pagos y emisión de comprobantes.

#### Requisitos Funcionales

- **Tablero Financiero:**
  - Estadísticas de ingresos (Total cobrado, Pendiente, Promedio).
  - Filtrado por rango de fechas, método de pago y estado.
- **Registro de Transacciones:**
  - Creación de nuevos pagos asociados a citas o pacientes.
  - Edición de detalles y anulación de pagos.
- **Comprobantes:** Visualización y previsualización de recibos de pago.

### 6. Administración

**Ruta:** `/admin` (Roles Admin/Manager)
**Objetivo:** Configuración de recursos de la clínica.

#### 6.1 Equipo (Staff)

**Ruta:** `/admin/staff`

- **Gestión de Usuarios:** Alta/Baja de empleados y control de roles.
- **Disponibilidad:** Configuración de horarios por doctor.

#### 6.2 Inventario

**Ruta:** `/admin/inventory`

- **Catálogo:** Gestión de productos e insumos.
- **Stock:** Ajustes de inventario.

#### 6.3 Servicios

**Ruta:** `/admin/services`

- **Catálogo de Tratamientos:** Definición de precios y duración de servicios.

### 7. Configuración y Usuario

**Rutas:** `/ajustes`, `/perfil`
**Objetivo:** Personalización y seguridad de cuenta.

#### Requisitos Funcionales

- **Perfil:** Actualización de datos y contraseña.

---

## 🔒 Requisitos No Funcionales

- **Seguridad:** Autenticación JWT y Guardias de Roles (`RoleGuard`) en todas las rutas sensibles.
- **Manejo de Errores Robust:** El sistema debe manejar respuestas vacías o fallos de red sin colapsar la interfaz ("Graceful Degradation"), mostrando mensajes amigables al usuario.
- **Diseño Responsivo:** Adaptabilidad total a móviles y escritorio.
