# Prompt Detallado: Pestaña "Atención Médica" (Expediente Médico)

## 🎯 Objetivo Principal

Desarrollar una pestaña de **Atención Médica** para la aplicación Podoskin (clínica de podología) que permita capturar un **expediente clínico completo** de un paciente. La interfaz debe ser:

1. **Dual**: Ofrecer dos modos de llenado (Guiado y Libre).
2. **Asistida por IA**: Incluir un asistente inteligente ("Maya") que sugiera diagnósticos y autocomplete campos.
3. **Profesional y estética**: Seguir un diseño moderno con tema oscuro.

---

## 🏗️ Arquitectura de Componentes

El sistema se compone de una página principal y múltiples componentes anidados.

### Página Principal: [MedicalAttention.tsx](file:/Frontend/src/pages/MedicalAttention.tsx)

**Intención**: Orquestar el layout de 3 columnas y proveer el contexto de datos a todos los hijos.

**Estructura del Layout**:

- **Header fijo**: Información del paciente actual y navegación de pestañas.
- **3 Columnas**:
    1. **Izquierda ([PatientSidebar](file:/Frontend/src/components/medical/PatientSidebar.tsx#4-68))**: Datos básicos del paciente (nombre, fecha nacimiento, teléfono, motivo de consulta) y resumen generado por IA.
    2. **Central ([MedicalRecordForm](file:/Frontend/src/components/medical/MedicalRecordForm.tsx#6-77))**: El formulario principal del expediente, con secciones acordeón.
    3. **Derecha ([MayaAssistant](file:/Frontend/src/components/medical/MayaAssistant.tsx#15-134) / [EvolutionSidebar](file:/Frontend/src/components/medical/EvolutionSidebar.tsx#3-108))**: Chat con la IA y/o historial de evolución del tratamiento.

**Comportamiento**:

- Cada columna tiene su propio scroll independiente (`overflow-y-auto`).
- El layout ocupa `100vh - altura del header global`.

---

### Componentes de Layout y Header

| Componente | Intención |
|---|---|
| [Header.tsx](file:/Frontend/src/components/medical/Header.tsx) | Muestra nombre del paciente, botones de acción (guardar, cerrar), y estado del guardado automático. |
| [TopNavigation.tsx](file:/Frontend/src/components/medical/TopNavigation.tsx) | Pestañas secundarias dentro de la sección médica (ej. "Clínico", "Historial", "Imágenes"). |
| [PatientSidebar.tsx](file:/Frontend/src/components/medical/PatientSidebar.tsx) | **Columna Izquierda**. Muestra datos clave del paciente (conectados al Context). Incluye un área para el resumen de IA. |
| [MayaAssistant.tsx](file:/Frontend/src/components/medical/MayaAssistant.tsx) | **Columna Derecha (Chat)**. Interfaz de chat para interactuar con la IA. Incluye mensajes, input de texto, y botones de acciones rápidas. |
| [MayaHeader.tsx](file:/Frontend/src/components/medical/MayaHeader.tsx) | Header interno del panel de Maya (o sidebar). Puede mostrar estado de la IA. |
| [EvolutionSidebar.tsx](file:/Frontend/src/components/medical/EvolutionSidebar.tsx) | **Columna Derecha (Alternativa)**. Muestra el historial de evolución del tratamiento, métricas, y "pensamiento" de la IA. Útil para seguimiento. |

---

### Componentes del Formulario Central

| Componente | Intención |
|---|---|
| [MedicalRecordForm.tsx](file:/Frontend/src/components/medical/MedicalRecordForm.tsx) | **Componente principal del formulario**. Contiene el header del expediente, selector de modo, barra de progreso, y las secciones del formulario. Soporta ambos modos (Guiado y Libre) directamente sin ventanas modales. |
| [FormModeToggle.tsx](file:/Frontend/src/components/medical/FormModeToggle.tsx) | Botón/Switch para alternar entre modo "Guiado" y modo "Libre". |
| [ProgressIndicator.tsx](file:/Frontend/src/components/medical/ProgressIndicator.tsx) | Barra de progreso visual que muestra el porcentaje de secciones completadas. |
| [SectionAccordion.tsx](file:/Frontend/src/components/medical/SectionAccordion.tsx) | Contenedor desplegable para cada sección del formulario. Incluye animación de expansión/colapso e indicador de completitud. |
| [FreeFormSections.tsx](file:/Frontend/src/components/medical/FreeFormSections.tsx) | **Contenedor para modo libre**. Renderiza todas las secciones como acordeones que el usuario puede llenar en cualquier orden. |

---

### Componentes de Campos

Ubicados en `src/components/medical/fields/`.

| Componente | Intención |
|---|---|
| [FormField.tsx](file:/Frontend/src/components/medical/fields/FormField.tsx) | **Componente base polimórfico**. Renderiza el tipo de input correcto (text, number, date, select, textarea, radio, checkbox, boolean) basado en la configuración del campo. Incluye: label, indicador de requerido (`*`), tooltip de ayuda (`?`), placeholder ("Opcional"), y mensajes de error. |
| [HelpTooltip.tsx](file:/Frontend/src/components/medical/HelpTooltip.tsx) | Icono `?` con tooltip que muestra texto de ayuda al pasar el cursor. |

---

## 📦 Estado y Contexto: [MedicalFormContext.tsx](file:/Frontend/src/context/MedicalFormContext.tsx)

**Intención**: Proveer un estado global para todo el formulario del expediente médico.

**Datos que maneja**:

1. `formData: MedicalRecord` - El objeto principal con todos los datos del expediente.
2. `formState: FormState` - Estado del UI (sección actual, secciones completadas, errores, si está guardando, etc.).
3. `formMode: FormMode` - Modo actual ('guided' | 'free') y progreso en modo guiado.

**Funciones Clave**:

- `updateFormData(path: string, value: any)`: Actualiza un campo específico del expediente usando notación de punto (ej. `'personalInfo.firstName'`).
- `setFormMode(mode: FormMode)`: Cambia el modo de llenado.
- `saveForm()`: Guarda el expediente actual (simula llamada a API).
- `submitForm()`: Finaliza y envía el expediente.
- `validateField(fieldName: string, value: any)`: Valida un campo individual.

**Auto-Guardado**:

- Implementado con `useEffect` y `setInterval` cada 30 segundos cuando `formState.isDirty` es `true`.

---

## 🔧 Tipos de Datos: [src/types/medical.ts](file:/Frontend/src/types/medical.ts)

Define las interfaces TypeScript para el expediente médico completo.

### Interfaces Principales

| Interface | Descripción |
|---|---|
| [MedicalRecord](file:/Frontend/src/types/medical.ts#244-271) | **Raíz del expediente**. Contiene: `personalInfo`, `allergies`, `medicalHistory`, `lifestyle`, `gynecologicalHistory?`, `consultationReason`, `vitalSigns`, `physicalExam`, `diagnoses`, `treatmentPlan`, `indications`, `evolution`. |
| [PersonalInfo](file:/Frontend/src/types/medical.ts#9-25) | Datos personales: nombres, fecha nacimiento, sexo, CURP, estado civil, dirección, contacto. |
| [Allergy](file:/Frontend/src/types/medical.ts#42-52) | Alergia: tipo, nombre, reacción, severidad. |
| [MedicalHistory](file:/Frontend/src/types/medical.ts#53-60) | Antecedentes: heredofamiliares, patológicos, quirúrgicos, traumáticos, transfusionales. |
| [Lifestyle](file:/Frontend/src/types/medical.ts#100-131) | Estilo de vida: dieta, ejercicio, tabaquismo, alcoholismo, drogas, esquema de vacunación. |
| [GynecologicalHistory](file:/Frontend/src/types/medical.ts#132-145) | Historia ginecológica (solo mujeres). |
| [ConsultationReason](file:/Frontend/src/types/medical.ts#146-152) | Motivo de consulta: síntoma principal, fecha de inicio, evolución. |
| [VitalSigns](file:/Frontend/src/types/medical.ts#157-172) | Signos vitales: peso, talla, IMC, TA, FC, FR, temperatura, SpO2, glucosa. |
| [PhysicalExam](file:/Frontend/src/types/medical.ts#173-185) | Exploración física: inspección de pie, palpación, movilidad, sensibilidad, circulación, lesiones. |
| [Diagnosis](file:/Frontend/src/types/medical.ts#186-197) | Diagnóstico: tipo (Presuntivo/Definitivo/Diferencial), descripción, código CIE-10. |
| [TreatmentPlan](file:/Frontend/src/types/medical.ts#207-211) | Plan de tratamiento: lista de servicios/procedimientos. |
| [Indications](file:/Frontend/src/types/medical.ts#222-228) | Indicaciones: instrucciones al paciente, pronóstico, próxima cita. |
| [Evolution](file:/Frontend/src/types/medical.ts#229-239) | Evolución: fase, fecha de evaluación, descripción, resultado, indicaciones. |
| [FormFieldConfig](file:/Frontend/src/types/medical.ts#286-298) | Configuración de un campo de formulario (nombre, label, tipo, requerido, opciones, validación). |
| [FormSection](file:/Frontend/src/types/medical.ts#299-308) | Sección del formulario (id, título, icono, campos). |
| [FormState](file:/Frontend/src/types/medical.ts#313-322) | Estado del UI del formulario (sección actual, completadas, errores, isDirty, isSubmitting). |
| [FormMode](file:/Frontend/src/types/medical.ts#323-328) | Modo de llenado ('guided' | 'free'). |

---

## 🛠️ Utilidades

### [formSections.ts](file:/Frontend/src/utils/formSections.ts)

**Intención**: Definir la estructura de las secciones del formulario y sus campos.

Exporta un array de [FormSection](file:/Frontend/src/types/medical.ts#299-308) con la configuración de cada sección (ej. "Ficha de Identificación", "Alergias", "Antecedentes Médicos", etc.), incluyendo los campos de cada una y sus propiedades.

### [formQuestions.ts](file:/Frontend/src/utils/formQuestions.ts)

**Intención**: Definir las preguntas para el **modo guiado**.

Exporta un array de objetos que representan cada pregunta/campo a mostrar secuencialmente en el modal guiado, con su texto, tipo de input, validación, y mapeo al `formData`.

---

## 🎨 Layout y Posicionamiento

**Framework CSS**: Tailwind CSS.

**Estructura de Layout**:

- **Header**: Fijo en la parte superior, altura fija.
- **Contenido**: Ocupa el resto de la altura disponible (`100vh - altura header`).
- **3 Columnas**:
  - Izquierda (fija): ~320px de ancho.
  - Central (flexible): Ocupa el espacio restante.
  - Derecha (fija): ~384px de ancho.
- Cada columna tiene scroll independiente (`overflow-y-auto`).
- Layout responsive: Columnas laterales se ocultan en móvil.

---

## ⚙️ Intenciones de la IA (Maya)

1. **Sugerencia de Diagnóstico**: Basado en síntomas, historial y exploración física.
2. **Autocompletado de Campos**: Al dictar o escribir en formato libre, la IA extrae datos estructurados.
3. **Resumen del Paciente**: Genera un resumen ejecutivo del caso.
4. **Consulta de CIE-10**: Busca códigos CIE-10 relevantes.
5. **Recomendaciones de Tratamiento**: Sugiere servicios o procedimientos.

---

## 📋 Secciones del Expediente Médico

### Parte 1: Datos del Paciente

1. **Ficha de Identificación**: Nombres, fecha de nacimiento, sexo, CURP, estado civil, escolaridad, ocupación, religión, dirección, contacto.
2. **Alergias**: Lista dinámica (tipo, nombre, reacción, severidad).
3. **Antecedentes Médicos**: Heredofamiliares, patológicos, quirúrgicos, traumáticos, transfusionales.
4. **Estilo de Vida**: Dieta, ejercicio, tabaquismo, alcoholismo, drogas, vacunas, exposición tóxica.
5. **Historia Ginecológica** (Condicional): Menarca, ciclo menstrual, embarazos, método anticonceptivo, menopausia.
6. **Motivo de Consulta**: Síntoma principal, fecha de inicio, evolución, automedicación.

### Parte 2: Datos del Médico

1. **Signos Vitales**: Peso, talla, IMC (auto-calculado), TA, FC, FR, temperatura, SpO2, glucosa.
2. **Exploración Física**: Inspección de pie, palpación, movilidad, sensibilidad, circulación, lesiones, deformidades, uñas, piel.
3. **Diagnósticos**: Presuntivo, Definitivo, Diferencial (con código CIE-10).
4. **Plan de Tratamiento**: Lista de servicios/procedimientos a realizar.
5. **Indicaciones y Pronóstico**: Plan de tratamiento para el paciente, instrucciones, pronóstico, próxima cita.
6. **Evolución del Tratamiento**: Historial de fases del tratamiento con fechas, descripciones y resultados.

---

# EXPEDIENTE MÉDICO COMPLETO - ORGANIZADO POR FUENTE DE DATOS

---

## 🗣️ PARTE 1: DATOS QUE SE OBTIENEN PREGUNTANDO AL PACIENTE

> Información que proporciona el paciente o se obtiene mediante entrevista directa

---

### 1️⃣ FICHA DE IDENTIFICACIÓN

#### Datos Personales Básicos

- **Primer nombre**: [Texto obligatorio]
- **Segundo nombre**: [Texto opcional]
- **Primer apellido**: [Texto obligatorio]
- **Segundo apellido**: [Texto opcional]
- **Fecha de nacimiento**: [Fecha obligatoria]
- **Sexo**: [Opción múltiple obligatoria]
  - [ ] M (Masculino)
  - [ ] F (Femenino)
  - [ ] O (Otro)
- **CURP**: [Texto opcional]
- **Estado civil**: [Texto opcional]
  - Soltero/a, Casado/a, Divorciado/a, Viudo/a, Unión libre
- **Escolaridad**: [Texto opcional]
  - Sin estudios, Primaria, Secundaria, Preparatoria, Licenciatura, Posgrado
- **Ocupación**: [Texto opcional]
- **Religión**: [Texto opcional]

#### Domicilio Completo

- **Calle**: [Texto opcional]
- **Número exterior**: [Texto opcional]
- **Número interior**: [Texto opcional]
- **Colonia**: [Texto opcional]
- **Ciudad**: [Texto opcional]
- **Estado**: [Texto opcional]
- **Código postal**: [Texto opcional]

#### Datos de Contacto

- **Teléfono principal**: [Texto obligatorio]
- **Teléfono secundario**: [Texto opcional]
- **Correo electrónico**: [Texto opcional]

#### Referencia

- **¿Cómo supo de nosotros?**: [Texto opcional]

---

### 2️⃣ ALERGIAS (Reportadas por el paciente)

Por cada alergia conocida:

- **Tipo de alérgeno**: [Opción múltiple]
  - [ ] Medicamento
  - [ ] Alimento
  - [ ] Ambiental
  - [ ] Material
  - [ ] Otro
- **Nombre del alérgeno**: [Texto obligatorio]
- **Reacción que ha experimentado**: [Texto opcional]
- **Severidad percibida**: [Opción múltiple]
  - [ ] Leve
  - [ ] Moderada
  - [ ] Grave
  - [ ] Mortal
- **¿Cuándo se lo diagnosticaron?**: [Fecha opcional]
- **Notas adicionales**: [Texto opcional]

---

### 3️⃣ ANTECEDENTES MÉDICOS (Reportados por el paciente)

> **Nota importante**: Estos son diagnósticos previos realizados por otros médicos, el paciente solo reporta lo que ya le han diagnosticado

#### Antecedentes Heredofamiliares

Por cada enfermedad en la familia:

- **Nombre de enfermedad**: [Texto obligatorio]
  - Ejemplos: Hipertensión, Diabetes mellitus, Cáncer, Enfermedades tiroideas, Enfermedades cardíacas
- **Parentesco**: [Texto obligatorio]
  - Ejemplos: Padre, Madre, Hermano/a, Abuelo/a
- **¿Cuándo le diagnosticaron?**: [Fecha opcional]
- **¿Qué tratamiento tiene?**: [Texto opcional]
- **¿Está controlado?**: [Sí/No]

#### Antecedentes Patológicos (Enfermedades que ha tenido)

Por cada enfermedad:

- **Nombre de enfermedad**: [Texto obligatorio]
  - Ejemplos: Tuberculosis, VIH, Hepatitis, Diabetes, Hipertensión
- **¿Cuándo se lo diagnosticaron?**: [Fecha opcional]
- **¿Qué tratamiento tiene actualmente?**: [Texto opcional]
- **¿Está controlado?**: [Sí/No]

#### Antecedentes Quirúrgicos (Cirugías previas)

Por cada cirugía:

- **Tipo de cirugía**: [Texto obligatorio]
- **¿Cuándo fue?**: [Fecha opcional]
- **Descripción**: [Texto opcional]

#### Antecedentes Traumáticos

Por cada traumatismo:

- **Tipo de traumatismo**: [Texto obligatorio]
  - Ejemplos: Fracturas, golpes, caídas
- **¿Cuándo ocurrió?**: [Fecha opcional]
- **Descripción**: [Texto opcional]

#### Antecedentes Transfusionales

- **¿Ha recibido transfusiones sanguíneas?**: [Sí/No]
- **¿Cuándo?**: [Fecha opcional]
- **Descripción**: [Texto opcional]

---

### 4️⃣ ESTILO DE VIDA Y HÁBITOS

#### Alimentación

- **Tipo de dieta**: [Opción múltiple]
  - [ ] Normal
  - [ ] Vegetariana
  - [ ] Vegana
  - [ ] Keto
  - [ ] Diabética
  - [ ] Otro
- **Descripción de su dieta**: [Texto opcional]
- **¿Toma suplementos o vitaminas?**: [Texto opcional]

#### Actividad Física

- **¿Con qué frecuencia hace ejercicio?**: [Texto opcional]
- **¿Qué tipo de ejercicio hace?**: [Texto opcional]

#### Tabaquismo

- **¿Fuma?**: [Sí/No]
- **¿Cuántos cigarros al día?**: [Entero opcional]
- **¿Cuántos años ha fumado?**: [Entero opcional]

#### Consumo de Alcohol

- **¿Consume alcohol?**: [Sí/No]
- **¿Con qué frecuencia?**: [Texto opcional]

#### Drogas

- **¿Consume drogas?**: [Sí/No]
- **¿Qué tipo?**: [Texto opcional]

#### Otros Hábitos

- **¿Tiene sus vacunas completas?**: [Sí/No]
- **Esquema de vacunación**: [Texto opcional]
- **¿Cuántas horas duerme?**: [Decimal]
- **¿Está expuesto a tóxicos?**: [Texto opcional]
- **Notas adicionales**: [Texto opcional]

---

### 5️⃣ HISTORIA GINECOLÓGICA (Solo mujeres)

- **¿A qué edad tuvo su primera menstruación?**: [Entero opcional]
- **¿Cada cuántos días menstrúa?**: [Texto opcional]
- **Fecha de su última menstruación**: [Fecha opcional]
- **¿Cuántos embarazos ha tenido?**: [Entero]
- **¿Cuántos partos?**: [Entero]
- **¿Cuántas cesáreas?**: [Entero]
- **¿Cuántos abortos?**: [Entero]
- **¿Qué método anticonceptivo usa?**: [Texto opcional]
- **¿Ya tiene menopausia?**: [Sí/No]
- **¿Cuándo inició la menopausia?**: [Fecha opcional]
- **Notas adicionales**: [Texto opcional]

---

### 6️⃣ MOTIVO DE CONSULTA (Lo que el paciente reporta)

- **¿Por qué viene hoy?**: [Texto obligatorio]
- **¿Cuándo empezaron los síntomas?**: [Fecha/descripción]
- **¿Cómo han evolucionado los síntomas?**: [Texto]
- **¿Qué ha hecho para aliviarlos?**: [Texto]

---

### 7️⃣ INFORMACIÓN DE PAGO (Proporcionada por el paciente)

- **Método de pago preferido**: [Opción múltiple]
  - [ ] Efectivo
  - [ ] Tarjeta de Débito
  - [ ] Tarjeta de Crédito
  - [ ] Transferencia
  - [ ] Cheque
  - [ ] Otro
- **¿Requiere factura?**: [Sí/No]
- **RFC para factura**: [Texto opcional]

---

### 8️⃣ CONSENTIMIENTOS (Firmados por el paciente)

- **Tipo de consentimiento**: [Texto]
- **Fecha de firma**: [Fecha]
- **¿Firmado digitalmente?**: [Sí/No]
- **Nombre de testigo 1**: [Texto opcional]
- **Nombre de testigo 2**: [Texto opcional]

---

## 👨‍⚕️ PARTE 2: DATOS QUE DETERMINA EL MÉDICO/PODÓLOGO

> Información que el profesional de salud determina mediante evaluación, exploración y criterio médico

---

### 1️⃣ SIGNOS VITALES (Medidos por el personal médico)

- **Fecha y hora de medición**: [Timestamp]
- **Peso (kg)**: [Decimal]
- **Talla (cm)**: [Decimal]
- **IMC**: [Auto-calculado]
- **Presión arterial sistólica**: [Entero]
- **Presión arterial diastólica**: [Entero]
- **Frecuencia cardíaca**: [Entero]
- **Frecuencia respiratoria**: [Entero]
- **Temperatura (°C)**: [Decimal]
- **Saturación de O2**: [Entero]
- **Glucosa capilar**: [Entero]
- **Medido por**: [ID usuario]

---

### 2️⃣ CITAS (Programadas por recepción/médico)

- **Fecha y hora de inicio**: [Timestamp]
- **Fecha y hora de fin**: [Timestamp]
- **Podólogo asignado**: [ID podólogo]
- **Estado de la cita**: [Opción múltiple]
  - [ ] Pendiente
  - [ ] Confirmada
  - [ ] En_Curso
  - [ ] Completada
  - [ ] Cancelada
  - [ ] No_Asistio
- **¿Es primera vez?**: [Sí/No]
- **Tipo de cita**: [Opción múltiple]
  - [ ] Consulta
  - [ ] Seguimiento
  - [ ] Urgencia
- **Notas de recepción**: [Texto opcional]
- **Motivo de cancelación** (si aplica): [Texto]

---

### 3️⃣ EXPLORACIÓN FÍSICA (Realizada por el podólogo)

- **Descripción de la exploración física**: [Texto]
  - Estado general
  - Inspección de pies
  - Palpación
  - Movilidad
  - Sensibilidad
  - Circulación
  - Lesiones observadas
  - Deformidades
  - Estado de uñas
  - Estado de piel

---

### 4️⃣ DIAGNÓSTICOS (IDX) - Determinados por el podólogo

#### A. Diagnóstico en Nota Clínica

**Diagnóstico Presuntivo** (primera impresión):

- **Descripción del diagnóstico presuntivo**: [Texto]
- **Código CIE-10 presuntivo** (del catálogo): [Selección]
- **Código CIE-10 presuntivo** (manual): [Texto]

**Diagnóstico Definitivo** (confirmado):

- **Descripción del diagnóstico definitivo**: [Texto]
- **Código CIE-10 definitivo** (del catálogo): [Selección]
- **Código CIE-10 definitivo** (manual): [Texto]

#### B. Diagnósticos por Tratamiento Específico

Por cada tratamiento, el podólogo puede registrar:

**Tipo de diagnóstico**: [Opción múltiple]

- [ ] **Presuntivo** - Diagnóstico inicial antes de confirmar
- [ ] **Definitivo** - Diagnóstico confirmado
- [ ] **Diferencial** - Lista de posibles diagnósticos a descartar

**Detalles del diagnóstico**:

- **Descripción del diagnóstico**: [Texto obligatorio]
- **Código CIE-10** (del catálogo): [Selección opcional]
- **Código CIE-10** (manual): [Texto opcional]
- **Fecha del diagnóstico**: [Timestamp]
- **Diagnosticado por**: [ID podólogo]
- **Notas del diagnóstico**: [Texto opcional]

#### C. Catálogo CIE-10 Disponible

El podólogo puede seleccionar de 30+ códigos:

- Diabetes (E10, E11.x)
- Hongos - Onicomicosis (B35.1)
- Pie de atleta (B35.3)
- Juanete - Hallux valgus (M20.1)
- Fascitis plantar (M72.2)
- Espolón calcáneo (M77.3)
- Uña encarnada (L60.0)
- Callos (L84)
- Verrugas (B07)
- Úlceras (L97, L89)
- Y más...

---

### 5️⃣ PLAN DE TRATAMIENTO (Determinado por el podólogo)

#### Tratamientos/Servicios Aplicados

Por cada tratamiento:

- **Servicio/Tratamiento**: [Selección del catálogo]
- **Precio aplicado**: [Decimal]
- **Descuento (%)**: [Decimal]
- **Precio final**: [Auto-calculado]
- **Notas del tratamiento**: [Texto]

**Catálogo de tratamientos disponibles**:

- Código de servicio
- Nombre del servicio
- Descripción
- Precio base
- Duración estimada
- ¿Requiere consentimiento?

---

### 6️⃣ INDICACIONES Y PRONÓSTICO (Determinado por el podólogo)

- **Plan de tratamiento general**: [Texto]
- **Indicaciones al paciente**: [Texto]
  - Cuidados en casa
  - Medicamentos recetados
  - Restricciones
  - Recomendaciones
- **Pronóstico**: [Texto]
  - Bueno / Reservado / Malo
- **Fecha sugerida para próxima cita**: [Fecha]

---

### 7️⃣ EVOLUCIÓN DEL TRATAMIENTO (Evaluada por el podólogo)

Por cada fase de evolución:

- **Número de fase**: [Entero]
- **Fecha de evaluación**: [Fecha]
- **Descripción de la evolución**: [Texto obligatorio]
- **Resultado observado**: [Opción múltiple]
  - [ ] Mejoría
  - [ ] Sin cambios
  - [ ] Empeoramiento
- **Indicaciones para siguiente fase**: [Texto]
- **Fecha de próxima revisión**: [Fecha]
- **Evaluado por**: [ID podólogo]

---

### 8️⃣ NOTA CLÍNICA COMPLETA (Elaborada por el podólogo)

**Resumen de la consulta**:

- **Motivo de consulta**: [Del paciente]
- **Padecimiento actual**: [Evaluación del podólogo]
- **Exploración física**: [Hallazgos del podólogo]
- **Diagnóstico presuntivo**: [Determinado por podólogo]
- **Diagnóstico definitivo**: [Determinado por podólogo]
- **Plan de tratamiento**: [Determinado por podólogo]
- **Indicaciones al paciente**: [Determinado por podólogo]
- **Pronóstico**: [Determinado por podólogo]
- **Próxima cita sugerida**: [Determinado por podólogo]
- **Fecha de elaboración**: [Timestamp]
- **Elaborado por**: [ID podólogo]

---

### 9️⃣ ARCHIVOS MULTIMEDIA (Capturados/Subidos por el personal)

Por cada archivo:

- **Tipo de archivo**: [Opción múltiple]
  - [ ] Foto Clínica
  - [ ] Radiografía
  - [ ] Laboratorio
  - [ ] Consentimiento
  - [ ] Estudio
  - [ ] Receta
  - [ ] Otro
- **Nombre del archivo**: [Texto]
- **URL de almacenamiento**: [Texto]
- **Descripción**: [Texto]
- **Fecha de subida**: [Timestamp]
- **Subido por**: [ID usuario]

---

### 🔟 GESTIÓN DE PAGOS (Procesado por recepción/administración)

- **Fecha de pago**: [Timestamp]
- **Monto total**: [Decimal]
- **Monto pagado**: [Decimal]
- **Saldo pendiente**: [Auto-calculado]
- **Método de pago usado**: [Opción múltiple]
- **Referencia de pago**: [Texto]
- **Estado del pago**: [Opción múltiple]
  - [ ] Pagado
  - [ ] Parcial
  - [ ] Pendiente
  - [ ] Cancelado
- **Factura emitida**: [Sí/No]
- **Folio de factura**: [Texto]
- **Procesado por**: [ID usuario]

---

## 📊 RESUMEN ESTADÍSTICO

### Datos que Proporciona el Paciente: ~80 campos

- Información personal y demográfica
- Antecedentes médicos reportados
- Hábitos y estilo de vida
- Historia ginecológica
- Motivo de consulta
- Información de pago

### Datos que Determina el Médico/Podólogo: ~70 campos

- Signos vitales medidos
- Exploración física
- Diagnósticos (presuntivo, definitivo, diferencial)
- Códigos CIE-10
- Plan de tratamiento
- Indicaciones y pronóstico
- Evolución del tratamiento
- Notas clínicas

### Total de Campos: 150+

---

## ✅ FLUJO DE TRABAJO RECOMENDADO

### 1. **Registro Inicial** (Recepción)

- Datos personales del paciente
- Datos de contacto
- Información de pago

### 2. **Entrevista Clínica** (Asistente/Podólogo)

- Motivo de consulta
- Antecedentes médicos
- Alergias
- Estilo de vida
- Historia ginecológica

### 3. **Exploración Física** (Podólogo)

- Toma de signos vitales
- Exploración física completa

### 4. **Diagnóstico y Tratamiento** (Podólogo)

- Diagnóstico presuntivo
- Diagnóstico definitivo
- Códigos CIE-10
- Plan de tratamiento
- Indicaciones

### 5. **Seguimiento** (Podólogo)

- Evolución del tratamiento
- Ajustes al plan
- Próxima cita

### 6. **Cierre** (Recepción)

- Procesamiento de pago
- Facturación
- Programación de siguiente cita
