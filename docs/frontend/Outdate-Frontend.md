# Componentes Obsoletos - Frontend Podoskin

==========================================

## Componentes y Código Obsoleto [04/01/26] [17:47]

==========================================

### 1. Layouts No Utilizados

**`layouts/AppLayout.tsx`** (L1-115)

- **Estado:** Potencialmente obsoleto
- **Razón:** No se encontraron importaciones de este componente en ningún archivo del proyecto
- **Descripción:** Layout unificado global que fue diseñado para envolver todas las rutas autenticadas con navegación persistente, header y sidebar consistentes
- **Reemplazo:** Actualmente se usa `AppShell.tsx` como el shell principal de la aplicación
- **Acción recomendada:** Verificar si este componente fue reemplazado completamente por AppShell o si está planeado para uso futuro. Si no se usa, considerar eliminarlo para evitar confusión.

---

### 2. Componentes de Navegación Duplicados

**`components/medical/TopNavigation.tsx`** (L1-57)

- **Estado:** No utilizado actualmente
- **Razón:** No se encontraron importaciones de este componente en ningún archivo
- **Descripción:** Navegación de pestañas para módulo médico (Clínico/Historial/Imágenes)
- **Problema:** Fue diseñado para navegación interna del módulo médico pero no está implementado
- **Acción recomendada:** Eliminar si no está en los planes de desarrollo, o implementar si es funcionalidad pendiente

---

### 3. Páginas Placeholder (Incompletas)

Las siguientes páginas existen pero solo contienen código mínimo placeholder:

**`pages/BillingPage.tsx`** (684 bytes)

- **Estado:** Placeholder
- **Contenido:** Solo muestra un mensaje "Página de Facturación - En desarrollo"
- **Funcionalidad:** No implementada

**`pages/FinancesPage.tsx`** (692 bytes)

- **Estado:** Placeholder
- **Contenido:** Solo muestra un mensaje "Página de Finanzas - En desarrollo"
- **Funcionalidad:** No implementada

**`pages/RecordsPage.tsx`** (686 bytes)

- **Estado:** Placeholder
- **Contenido:** Solo muestra un mensaje "Página de Expedientes - En desarrollo"
- **Funcionalidad:** No implementada

**Acción recomendada:** Estas páginas están marcadas como "en desarrollo". No son obsoletas, pero están incompletas. Mantener si están en el roadmap, o eliminar las rutas si no están planeadas.

---

### 4. Assets No Utilizados

**`assets/react.svg`**

- **Estado:** Obsoleto
- **Razón:** Logo default de Vite que no se usa en la aplicación
- **Acción recomendada:** Eliminar para limpiar assets

---

### 5. Código Duplicado / Fragmentado

**Problema de Fragmentación de Layouts** (Identificado en DIAGNOSTICO_FRONTEND.md)

Aunque no son componentes obsoletos per se, existe duplicación de funcionalidad:

- **`components/Layout.tsx`**: Layout específico para calendario
- **`components/medical/Header.tsx`**: Header específico del módulo médico
- **`components/AppShell.tsx`**: Shell global de la aplicación

**Problema:** Tres componentes diferentes manejan layout/header cuando debería haber uno solo unificado.

**Impacto:** Esto causa que la aplicación se sienta fragmentada, con diferentes estilos y comportamientos según la sección.

**Acción recomendada:** Unificar bajo un solo Layout global (AppShell) y deprecar los layouts específicos de módulos.

---

### 6. Servicios Mock

**`services/mockData.ts`** (Si existe)

- **Estado:** Verificar si aún se usa
- **Razón:** Según DIAGNOSTICO_FRONTEND.md, este archivo contiene datos mock que solo sirven a la agenda
- **Problema:** Duplicidad de modelos con `types/medical.ts`
- **Acción recomendada:** Si la aplicación ya usa datos reales del backend, eliminar datos mock

---

## Resumen de Componentes Obsoletos

| Componente | Ruta | Tamaño | Estado | Acción |
|------------|------|--------|--------|--------|
| AppLayout.tsx | layouts/ | 4.3KB | No usado | Verificar/Eliminar |
| TopNavigation.tsx | components/medical/ | 1.5KB | No usado | Verificar/Eliminar |
| BillingPage.tsx | pages/ | 684B | Placeholder | Completar/Eliminar |
| FinancesPage.tsx | pages/ | 692B | Placeholder | Completar/Eliminar |
| RecordsPage.tsx | pages/ | 686B | Placeholder | Completar/Eliminar |
| react.svg | assets/ | - | No usado | Eliminar |

---

## Notas Importantes

1. **No eliminar sin verificar:** Algunos componentes pueden estar planeados para uso futuro o en ramas de desarrollo
2. **Fragmentación ≠ Obsoleto:** Los componentes fragmentados (Layout, Header duplicados) no son obsoletos, pero necesitan refactorización
3. **Placeholders:** Las páginas placeholder no son obsoletas si están en el roadmap de desarrollo

---

**Última actualización:** 04/01/2026 - 17:47 hrs
