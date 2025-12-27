# Diagnóstico Integral del Frontend - Caso Podoskin

Este documento detalla los hallazgos, errores e incongruencias encontrados durante la inspección profunda de la plataforma.

## Bitácora de Errores e Incongruencias

### 01. Estructura y Navegación

- **Fragmentación de Layouts (CRÍTICO)**:
  - El proyecto usa `src/components/Layout.tsx` para la sección de Calendario.
  - La sección de `MedicalAttention.tsx` redefine su propia estructura completa (Header, Sidebar, Main Content) sin usar el Layout global.
  - Esto genera que la pestaña de navegación que agregamos se vea "duplicada" o "perdida" porque no hay una jerarquía de componentes clara.
- **Inconsistencia de Componentes Globales**: Existen dos "Headers" y dos "Navigations" (GlobalNavigation vs TopNavigation médica).
- **Rutas Fragmentadas**: `App.tsx` sirve rutas que no comparten un ancestro común de UI, lo que rompe la persistencia de la barra de navegación.

### 02. Componentes (Interfase de Usuario)

- **Aislamiento del módulo médico**: El módulo en `src/components/medical` parece ser un "repo dentro de un repo". Sus estilos y lógica no están integrados con los componentes globales.
- **Divergencia de estilos**: Se usan utilidades de `clsx` y `tailwind` en ambos lados, pero con paletas de colores y espaciados que no siempre coinciden.

### 03. Lógica de Negocio y Datos

- **Duplicidad de Modelos**: Tanto `types/medical.ts` como `services/mockData.ts` manejan "pacientes", pero con estructuras de datos que no están completamente alineadas, lo que dificultará la integración real con una base de datos única.
- **Validaciones no Estandarizadas**: El módulo médico usa `zod` y `react-hook-form`, mientras que el calendario usa validaciones manuales/propias en los modales.

### 04. Estado Global y Contextos

- **Aislamiento de Estado**: No existe un "GlobalState" que comparta información entre la agenda y la atención médica. Por ejemplo, al seleccionar un paciente en la agenda, esa información no se pasa automáticamente de forma limpia al contexto médico sin recargar o manejar props complejas.
- **Conflictos de Contexto**: Se encontró que `MedicalFormProvider` no envolvía a sus hijos con el `FormProvider` de `react-hook-form`, rompiendo componentes internos como `SectionAccordion`.

## Análisis por Carpeta

- `src/pages`: Contiene las "vistas" de alto nivel, pero actualmente cargan sus propios layouts en lugar de inyectarse en uno común. Esto rompe la navegación al cambiar de tab.
- `src/components/medical`: Es el corazón de la atención médica. Funciona de forma aislada y tiene su propia jerarquía de Header/Sidebar.
- `src/components`: Contiene componentes de la agenda que están muy acoplados al `Layout.tsx` original.
- `src/services` / `src/utils`: El archivo `utils/formSections.ts` es crítico y muy extenso (31KB), define toda la estructura del formulario. `services/mockData.ts` solo sirve a la agenda.
- `src/context`: Solo existe contexto para el formulario médico. La app carece de un contexto de navegación o usuario global.

## Conclusión del Diagnóstico

La aplicación no se siente como una sola porque **no comparte un Layout Shell**. El Calendario vive en un marco y la Atención Médica en otro. Para solucionar esto, debemos extraer el Sidebar y la Navegación a un nivel superior en `App.tsx` que envuelva a todas las rutas.
