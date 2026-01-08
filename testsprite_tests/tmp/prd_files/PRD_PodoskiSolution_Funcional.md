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

---

## 🧪 Estrategia de Pruebas y Matriz de Casos (TestSprite)

Para asegurar la calidad y cobertura de la plataforma, se definen criterios de aceptación, historias de usuario y ejemplos de casos de prueba para cada módulo. Esta información servirá como base para la configuración de suites y escenarios en TestSprite.

### Convenciones
- **ID Caso:** Identificador único para cada caso de prueba.
- **Historia de Usuario:** Descripción funcional desde la perspectiva del usuario.
- **Criterios de Aceptación:** Condiciones mínimas para considerar la funcionalidad como "aprobada".
- **Pasos de Prueba:** Secuencia detallada para ejecutar la validación.
- **Resultado Esperado:** Comportamiento esperado del sistema.

---

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

##### Historias de Usuario y Criterios de Aceptación

**HU-001:** Como usuario, quiero ver los KPIs actualizados al ingresar al dashboard para conocer el estado de la clínica.
- **Criterios de aceptación:**
  - Los KPIs se muestran en tarjetas separadas.
  - Los valores reflejan datos reales y actualizados.
  - Si no hay datos, se muestra mensaje informativo.

**HU-002:** Como usuario, quiero visualizar gráficos de tendencias para analizar el comportamiento de citas e ingresos.
- **Criterios de aceptación:**
  - Los gráficos se cargan correctamente y muestran leyendas.
  - Permiten filtrar por rango de fechas.
  - El sistema maneja correctamente la ausencia de datos.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-001  | HU-001             | Acceder a /dashboard | Se muestran 4 tarjetas KPI con datos actualizados |
| TC-002  | HU-001             | Simular ausencia de datos | Se muestra mensaje "No hay datos disponibles" |
| TC-003  | HU-002             | Cambiar rango de fechas en gráfico | Los gráficos se actualizan correctamente |
| TC-004  | HU-002             | Forzar error de red | Se muestra mensaje de error amigable |
| TC-005  | HU-002             | Validar leyendas y colores | Leyendas y colores corresponden a cada estado |

---

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

##### Historias de Usuario y Criterios de Aceptación

**HU-010:** Como usuario, quiero crear y reprogramar citas fácilmente desde el calendario.
- **Criterios de aceptación:**
  - Se puede crear una cita haciendo clic en un bloque horario.
  - Se puede arrastrar una cita para cambiar su horario.
  - El sistema valida solapamientos y muestra alertas.

**HU-011:** Como usuario, quiero filtrar y buscar citas por doctor o paciente.
- **Criterios de aceptación:**
  - El filtro es reactivo y muestra resultados en tiempo real.
  - La búsqueda es insensible a mayúsculas/minúsculas.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-010  | HU-010             | Crear cita en bloque libre | Cita se crea y aparece en calendario |
| TC-011  | HU-010             | Arrastrar cita a nuevo horario | Cita se reprograma correctamente |
| TC-012  | HU-010             | Intentar solapar dos citas | Se muestra alerta de conflicto |
| TC-013  | HU-011             | Filtrar por doctor | Solo se muestran citas del doctor seleccionado |
| TC-014  | HU-011             | Buscar paciente por nombre parcial | Resultados coinciden con búsqueda |

---

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

##### Historias de Usuario y Criterios de Aceptación

**HU-020:** Como usuario, quiero registrar nuevos pacientes validando los campos obligatorios.
- **Criterios de aceptación:**
  - El sistema impide guardar si falta nombre o contacto.
  - Se muestra mensaje de validación clara.

**HU-021:** Como usuario, quiero buscar y filtrar pacientes rápidamente.
- **Criterios de aceptación:**
  - El filtro es instantáneo y preciso.
  - Permite buscar por cualquier campo visible.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-020  | HU-020             | Intentar guardar paciente sin nombre | Se muestra error de validación |
| TC-021  | HU-020             | Registrar paciente con todos los campos | Paciente aparece en el listado |
| TC-022  | HU-021             | Buscar por teléfono | Resultados coinciden con el teléfono ingresado |
| TC-023  | HU-021             | Buscar por correo | Resultados coinciden con el correo ingresado |
| TC-024  | HU-021             | Desactivar paciente | Paciente ya no aparece en listado activo |

---

### 4. Gestión Médica

**Ruta:** `/medical` (Submenú)
**Objetivo:** Documentación clínica integral y seguimiento.

#### 4.1 Atención Médica

**Ruta:** `/medical/attention`

- **Flujo Clínico:** Interfaz paso a paso para la consulta activa.
- **Historia Clínica (SOAP):** Registros estructurados.
- **Evoluciones:** Historial de cambios y progreso.

##### Historias de Usuario y Criterios de Aceptación

**HU-030:** Como médico, quiero registrar la atención clínica siguiendo un flujo guiado.
- **Criterios de aceptación:**
  - El sistema guía paso a paso el llenado de la consulta.
  - No permite avanzar si faltan datos obligatorios.

**HU-031:** Como médico, quiero consultar el historial clínico y evoluciones del paciente.
- **Criterios de aceptación:**
  - El historial muestra todas las consultas previas.
  - Permite filtrar por fecha o tipo de evolución.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-030  | HU-030             | Completar flujo clínico sin omitir pasos | Consulta se guarda correctamente |
| TC-031  | HU-030             | Omitir campo obligatorio | Se muestra error y no permite avanzar |
| TC-032  | HU-031             | Consultar historial de un paciente | Se listan todas las consultas previas |
| TC-033  | HU-031             | Filtrar evoluciones por fecha | Solo aparecen evoluciones del rango seleccionado |

---

#### 4.2 Expedientes Médicos

**Ruta:** `/medical/records`

- **Repositorio Digital:** Historial completo del paciente.
- **Búsqueda Avanzada:** Localización por ID o datos personales.

##### Historias de Usuario y Criterios de Aceptación

**HU-040:** Como usuario, quiero buscar expedientes médicos por ID o datos personales.
- **Criterios de aceptación:**
  - El sistema permite búsqueda por múltiples campos.
  - Resultados son precisos y rápidos.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-040  | HU-040             | Buscar expediente por ID | Se muestra expediente correcto |
| TC-041  | HU-040             | Buscar expediente por nombre | Se muestran coincidencias |

---

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

##### Historias de Usuario y Criterios de Aceptación

**HU-050:** Como usuario, quiero registrar pagos y asociarlos a citas o pacientes.
- **Criterios de aceptación:**
  - El sistema permite seleccionar cita o paciente al registrar pago.
  - Se valida el monto y método de pago.

**HU-051:** Como usuario, quiero filtrar y visualizar estadísticas financieras.
- **Criterios de aceptación:**
  - El tablero se actualiza según los filtros aplicados.
  - Se muestran totales y promedios correctamente.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-050  | HU-050             | Registrar pago con datos válidos | Pago aparece en el registro |
| TC-051  | HU-050             | Registrar pago sin monto | Se muestra error de validación |
| TC-052  | HU-051             | Filtrar por método de pago | Estadísticas y lista se actualizan |
| TC-053  | HU-051             | Visualizar comprobante de pago | Se muestra previsualización correcta |

---

### 6. Administración

**Ruta:** `/admin` (Roles Admin/Manager)
**Objetivo:** Configuración de recursos de la clínica.

#### 6.1 Equipo (Staff)

**Ruta:** `/admin/staff`

- **Gestión de Usuarios:** Alta/Baja de empleados y control de roles.
- **Disponibilidad:** Configuración de horarios por doctor.

##### Historias de Usuario y Criterios de Aceptación

**HU-060:** Como administrador, quiero dar de alta o baja empleados y asignar roles.
- **Criterios de aceptación:**
  - El sistema permite crear, editar y desactivar usuarios.
  - Los roles determinan el acceso a módulos.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-060  | HU-060             | Crear nuevo usuario staff | Usuario aparece en listado |
| TC-061  | HU-060             | Asignar rol y validar acceso | Acceso restringido según rol |
| TC-062  | HU-060             | Desactivar usuario | Usuario ya no puede iniciar sesión |

---

#### 6.2 Inventario

**Ruta:** `/admin/inventory`

- **Catálogo:** Gestión de productos e insumos.
- **Stock:** Ajustes de inventario.

##### Historias de Usuario y Criterios de Aceptación

**HU-070:** Como usuario, quiero gestionar productos e insumos del inventario.
- **Criterios de aceptación:**
  - Se pueden agregar, editar y eliminar productos.
  - El stock se actualiza en tiempo real.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-070  | HU-070             | Agregar nuevo producto | Producto aparece en catálogo |
| TC-071  | HU-070             | Editar stock de producto | Stock se actualiza correctamente |
| TC-072  | HU-070             | Eliminar producto | Producto ya no aparece en catálogo |

---

#### 6.3 Servicios

**Ruta:** `/admin/services`

- **Catálogo de Tratamientos:** Definición de precios y duración de servicios.

##### Historias de Usuario y Criterios de Aceptación

**HU-080:** Como administrador, quiero definir y actualizar tratamientos y precios.
- **Criterios de aceptación:**
  - Se pueden crear, editar y eliminar tratamientos.
  - Los cambios se reflejan en la agenda y facturación.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-080  | HU-080             | Crear nuevo tratamiento | Tratamiento aparece en catálogo |
| TC-081  | HU-080             | Editar precio de tratamiento | Precio actualizado en agenda y cobros |
| TC-082  | HU-080             | Eliminar tratamiento | Tratamiento ya no está disponible |

---

### 7. Configuración y Usuario

**Rutas:** `/ajustes`, `/perfil`
**Objetivo:** Personalización y seguridad de cuenta.

#### Requisitos Funcionales

- **Perfil:** Actualización de datos y contraseña.

##### Historias de Usuario y Criterios de Aceptación

**HU-090:** Como usuario, quiero actualizar mis datos personales y contraseña.
- **Criterios de aceptación:**
  - El sistema valida la contraseña actual antes de permitir el cambio.
  - Se muestra confirmación de éxito o error.

##### Ejemplos de Casos de Prueba (TestSprite)

| ID Caso | Historia de Usuario | Paso de Prueba | Resultado Esperado |
|---------|--------------------|----------------|--------------------|
| TC-090  | HU-090             | Cambiar contraseña con datos correctos | Se muestra mensaje de éxito |
| TC-091  | HU-090             | Intentar cambiar contraseña con actual incorrecta | Se muestra error de validación |

---

---

## 🔒 Requisitos No Funcionales

- **Seguridad:** Autenticación JWT y Guardias de Roles (`RoleGuard`) en todas las rutas sensibles.
- **Manejo de Errores Robust:** El sistema debe manejar respuestas vacías o fallos de red sin colapsar la interfaz ("Graceful Degradation"), mostrando mensajes amigables al usuario.
- **Diseño Responsivo:** Adaptabilidad total a móviles y escritorio.

##### Casos de Prueba No Funcionales

- **NF-001:** Simular acceso a rutas protegidas sin autenticación → El sistema redirige a login.
- **NF-002:** Probar acceso con usuario de rol restringido → Acceso denegado y mensaje claro.
- **NF-003:** Simular caída de red en cualquier módulo → Se muestra mensaje de error sin romper la UI.
- **NF-004:** Probar visualización en dispositivos móviles y escritorio → La interfaz se adapta correctamente.
