# Errores y Problemas - Frontend Podoskin

==========================================

## Errores Identificados en Frontend [04/01/26] [17:47]

==========================================

### 1. CRÍTICO: Fragmentación de Layouts

**Ubicación:** Arquitectura general de la aplicación

**Problema:**
El proyecto usa múltiples layouts que no están unificados:

- `components/Layout.tsx` - Solo para sección de Calendario
- `components/medical/Header.tsx` + estructura propia - Solo para Atención Médica
- `components/AppShell.tsx` - Shell global

**Impacto:**

- La navegación global (GlobalNavigation) se ve "duplicada" o "perdida" al cambiar de sección
- No hay una jerarquía de componentes clara
- La aplicación no se siente como una sola plataforma unificada

**Archivos afectados:**

- `src/components/Layout.tsx`
- `src/components/medical/Header.tsx`
- `src/components/AppShell.tsx`
- `src/pages/MedicalAttention.tsx` (L1-302)

**Solución recomendada:**
Extraer el Sidebar y la Navegación a un nivel superior en `App.tsx` que envuelva a todas las rutas, usando AppShell como único layout global.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "01. Estructura y Navegación"

---

### 2. ERROR: Inconsistencia de Componentes Globales

**Problema:**
Existen dos "Headers" y dos "Navigations":

- `GlobalNavigation` (componente global)
- `TopNavigation` (componente del módulo médico - no usado actualmente)
- Header en `AppShell`
- Header en `components/medical/Header.tsx`

**Impacto:**
Confusión en la arquitectura y experiencia de usuario inconsistente entre módulos.

**Archivos afectados:**

- `src/components/GlobalNavigation.tsx`
- `src/components/medical/TopNavigation.tsx`
- `src/components/AppShell.tsx`
- `src/components/medical/Header.tsx`

**Solución recomendada:**
Mantener solo GlobalNavigation y el Header de AppShell. Eliminar o refactorizar los componentes del módulo médico.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "01. Estructura y Navegación"

---

### 3. ERROR: Rutas Fragmentadas

**Ubicación:** `src/App.tsx`

**Problema:**
Las rutas en `App.tsx` no comparten un ancestro común de UI, lo que rompe la persistencia de la barra de navegación al cambiar entre secciones.

**Impacto:**

- Al navegar de Calendario a Atención Médica, la interfaz cambia completamente
- La navegación global no persiste correctamente
- Experiencia de usuario fragmentada

**Archivos afectados:**

- `src/App.tsx` (L1-449)
- `src/pages/MedicalAttention.tsx`

**Solución recomendada:**
Envolver todas las rutas autenticadas en un layout común (AppShell) que mantenga la navegación persistente.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "01. Estructura y Navegación"

---

### 4. ERROR: Aislamiento del Módulo Médico

**Ubicación:** `src/components/medical/` y `src/pages/MedicalAttention.tsx`

**Problema:**
El módulo médico (`src/components/medical`) funciona como un "repo dentro de un repo":

- Tiene su propia estructura de Header/Sidebar
- Sus estilos y lógica no están integrados con los componentes globales
- Usa su propio sistema de navegación

**Impacto:**

- Inconsistencia visual entre módulos
- Dificultad para mantener un diseño coherente
- Código duplicado

**Archivos afectados:**

- `src/components/medical/Header.tsx`
- `src/components/medical/TopNavigation.tsx`
- `src/pages/MedicalAttention.tsx`
- Todo el directorio `src/components/medical/`

**Solución recomendada:**
Integrar el módulo médico con el sistema de layout global, eliminando su Header/Sidebar propios y usando los componentes globales.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "02. Componentes (Interfase de Usuario)"

---

### 5. ERROR: Divergencia de Estilos

**Problema:**
Se usan utilidades de `clsx` y `tailwind` en ambos módulos (calendario y médico), pero con paletas de colores y espaciados que no siempre coinciden.

**Impacto:**

- Inconsistencia visual
- Dificultad para mantener un sistema de diseño coherente

**Archivos afectados:**

- Componentes en `src/components/` (calendario)
- Componentes en `src/components/medical/` (módulo médico)

**Solución recomendada:**
Crear un sistema de diseño unificado con variables CSS o configuración de Tailwind centralizada.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "02. Componentes"

---

### 6. ERROR: Duplicidad de Modelos de Datos

**Ubicación:** `src/types/medical.ts` y `src/services/mockData.ts`

**Problema:**
Tanto `types/medical.ts` como `services/mockData.ts` manejan "pacientes", pero con estructuras de datos que no están completamente alineadas.

**Impacto:**

- Dificultad para integración real con base de datos única
- Posibles errores de tipo en TypeScript
- Confusión sobre cuál modelo usar

**Archivos afectados:**

- `src/types/medical.ts`
- `src/services/mockData.ts` (si existe)
- `src/types/appointments.ts`

**Solución recomendada:**
Unificar los modelos de datos bajo una sola fuente de verdad en `types/`, eliminando duplicaciones.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "03. Lógica de Negocio y Datos"

---

### 7. ERROR: Validaciones No Estandarizadas

**Problema:**

- El módulo médico usa `zod` y `react-hook-form` para validaciones
- El calendario usa validaciones manuales/propias en los modales

**Impacto:**

- Inconsistencia en manejo de errores
- Código duplicado
- Dificultad para mantener

**Archivos afectados:**

- `src/components/medical/MedicalRecordForm.tsx`
- `src/components/EventModal.tsx`
- `src/components/patients/PatientFormModal.tsx`

**Solución recomendada:**
Estandarizar todas las validaciones usando `zod` + `react-hook-form` en toda la aplicación.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "03. Lógica de Negocio y Datos"

---

### 8. ERROR: Aislamiento de Estado Global

**Ubicación:** Contextos de la aplicación

**Problema:**
No existe un "GlobalState" robusto que comparta información entre la agenda y la atención médica. Al seleccionar un paciente en la agenda, esa información no se pasa automáticamente al contexto médico sin recargar o manejar props complejas.

**Impacto:**

- Dificultad para comunicación entre módulos
- Props drilling
- Estado duplicado

**Archivos afectados:**

- `src/context/GlobalContext.tsx` (L1-82)
- `src/context/MedicalFormContext.tsx`
- `src/App.tsx`

**Solución recomendada:**
Fortalecer el `GlobalContext` para manejar toda la comunicación entre módulos, o considerar usar una librería de estado global como Zustand o Redux.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "04. Estado Global y Contextos"

---

### 9. ERROR: Conflicto de Contexto en Formulario Médico

**Ubicación:** `src/context/MedicalFormContext.tsx`

**Problema:**
Se encontró que `MedicalFormProvider` no envolvía a sus hijos con el `FormProvider` de `react-hook-form`, rompiendo componentes internos como `SectionAccordion`.

**Estado:** Posiblemente ya corregido, verificar implementación actual

**Archivos afectados:**

- `src/context/MedicalFormContext.tsx` (L1-523)
- `src/components/medical/SectionAccordion.tsx`

**Solución recomendada:**
Asegurar que `MedicalFormProvider` envuelva correctamente a sus hijos con `FormProvider`.

**Referencia:** DIAGNOSTICO_FRONTEND.md - Sección "04. Estado Global y Contextos"

---

## Resumen de Errores por Prioridad

### 🔴 Críticos (Afectan experiencia de usuario)

1. Fragmentación de Layouts
2. Rutas Fragmentadas
3. Aislamiento del Módulo Médico

### 🟡 Importantes (Afectan mantenibilidad)

4. Inconsistencia de Componentes Globales
2. Duplicidad de Modelos de Datos
3. Validaciones No Estandarizadas
4. Aislamiento de Estado Global

### 🟢 Menores (Mejoras de código)

8. Divergencia de Estilos
2. Conflicto de Contexto (posiblemente resuelto)

---

## Impacto en la Experiencia del Usuario (Para Santiago)

Los errores identificados hacen que la aplicación funcione, pero no se sienta como una sola plataforma profesional:

**Lo que notarás al usar la app:**

- Cuando cambias de "Calendario" a "Atención Médica", la pantalla se ve completamente diferente
- Los menús y botones no están siempre en el mismo lugar
- Algunos colores y estilos cambian entre secciones
- La navegación puede sentirse confusa porque no es consistente

**Lo que esto significa:**
La aplicación funciona correctamente para gestionar citas y pacientes, pero necesita trabajo de "pulido" para que toda la interfaz se vea y se sienta como una sola aplicación profesional y cohesiva, en lugar de varias aplicaciones pequeñas juntas.

**Prioridad de corrección:**
Los desarrolladores deben enfocarse primero en unificar el layout global para que toda la aplicación use el mismo diseño, menús y navegación. Esto mejorará significativamente tu experiencia al usar el sistema.

---

**Última actualización:** 04/01/2026 - 17:47 hrs
**Fuente:** Análisis basado en DIAGNOSTICO_FRONTEND.md y revisión de código
