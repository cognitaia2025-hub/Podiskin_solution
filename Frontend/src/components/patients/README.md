# Componentes de Pacientes

Esta carpeta contiene todos los componentes relacionados con la gestión de pacientes del sistema Podoskin.

## Componentes

### PatientAvatar.tsx
Avatar circular con las iniciales del paciente. Genera un color consistente basado en el nombre del paciente.

**Props:**
- `firstName: string` - Primer nombre del paciente
- `lastName: string` - Apellido del paciente
- `size?: 'sm' | 'md' | 'lg'` - Tamaño del avatar (default: 'md')
- `className?: string` - Clases CSS adicionales

**Uso:**
```tsx
<PatientAvatar 
  firstName="Juan" 
  lastName="Pérez" 
  size="md" 
/>
```

### AllergyForm.tsx
Formulario inline para agregar una nueva alergia al paciente.

**Props:**
- `onSave: (allergy: Omit<Allergy, 'id'>) => void` - Callback al guardar
- `onCancel: () => void` - Callback al cancelar
- `className?: string` - Clases CSS adicionales

**Campos:**
- Tipo de alérgeno (Medicamento, Alimento, Ambiental, Material, Otro)
- Nombre del alérgeno (requerido)
- Reacción
- Severidad (Leve, Moderada, Grave, Mortal)

**Uso:**
```tsx
<AllergyForm 
  onSave={(allergy) => console.log(allergy)}
  onCancel={() => setShowForm(false)}
/>
```

### AllergyList.tsx
Lista editable de alergias con opción de agregar/eliminar.

**Props:**
- `allergies: Allergy[]` - Lista de alergias
- `onChange: (allergies: Allergy[]) => void` - Callback cuando cambia la lista
- `className?: string` - Clases CSS adicionales

**Funcionalidades:**
- Muestra lista de alergias con iconos según tipo
- Código de colores según severidad
- Botón para agregar nueva alergia
- Botón para eliminar cada alergia
- Estado vacío cuando no hay alergias

**Uso:**
```tsx
<AllergyList 
  allergies={formData.alergias}
  onChange={(allergies) => setFormData({ ...formData, alergias: allergies })}
/>
```

### PatientCard.tsx
Tarjeta responsive para mostrar información del paciente (vista móvil).

**Props:**
- `patient: PatientCardData` - Datos del paciente
- `onClick?: () => void` - Callback al hacer clic en la tarjeta
- `onEdit?: () => void` - Callback al hacer clic en editar
- `onDelete?: () => void` - Callback al hacer clic en eliminar
- `className?: string` - Clases CSS adicionales

**Uso:**
```tsx
<PatientCard 
  patient={patient}
  onClick={() => navigate('/medical')}
  onEdit={() => setEditingId(patient.id)}
  onDelete={() => handleDelete(patient.id)}
/>
```

### PatientFormModal.tsx
Modal con formulario de 3 tabs para crear/editar pacientes.

**Props:**
- `isOpen: boolean` - Control de visibilidad del modal
- `onClose: () => void` - Callback al cerrar
- `patientId?: string` - ID del paciente (si es edición)
- `onSuccess: (patient: any) => void` - Callback al guardar exitosamente

**Tabs:**
1. **Datos Personales**: Nombre, apellidos, fecha de nacimiento, sexo, CURP, estado civil, ocupación
2. **Contacto**: Teléfonos, email, dirección completa
3. **Información Médica**: Tipo de sangre, alergias, referencia

**Validaciones:**
- Campos requeridos: Primer nombre, primer apellido, fecha de nacimiento, sexo, teléfono principal
- Fecha de nacimiento no puede ser futura
- Teléfono debe tener 10 dígitos
- Email debe tener formato válido
- CURP debe tener 18 caracteres (si se proporciona)

**Uso:**
```tsx
<PatientFormModal
  isOpen={isModalOpen}
  onClose={() => setIsModalOpen(false)}
  patientId={editingPatientId}
  onSuccess={(patient) => {
    console.log('Paciente guardado:', patient);
    loadPatients();
  }}
/>
```

## Página Principal

### PatientsPage.tsx
Página principal de gestión de pacientes con todas las funcionalidades.

**Funcionalidades:**
- ✅ Lista de pacientes con paginación
- ✅ Búsqueda en tiempo real (debounce 300ms)
- ✅ Filtros por estado (todos, activos, inactivos)
- ✅ Ordenamiento (nombre, fecha)
- ✅ Tabla responsive (desktop) y cards (mobile)
- ✅ CRUD completo de pacientes
- ✅ Soft delete (desactivación)
- ✅ Integración con GlobalContext
- ✅ Estados de loading y empty

**Uso:**
```tsx
// En App.tsx
<Route path="/patients" element={<PatientsPage />} />
```

## Flujos de Usuario

### Flujo de Creación de Paciente
1. Usuario hace clic en "Nuevo Paciente"
2. Se abre el modal PatientFormModal
3. Usuario llena los 3 tabs del formulario
4. Se validan los campos requeridos
5. Al hacer clic en "Guardar":
   - Se llama a `createPatient()` del service
   - Se cierra el modal
   - Se recarga la lista de pacientes
   - Se muestra mensaje de éxito

### Flujo de Edición de Paciente
1. Usuario hace clic en "Editar" en la fila del paciente
2. Se abre el modal PatientFormModal con los datos del paciente
3. Usuario modifica los campos necesarios
4. Al hacer clic en "Guardar":
   - Se llama a `updatePatient()` del service
   - Se cierra el modal
   - Se recarga la lista de pacientes

### Flujo de Búsqueda
1. Usuario escribe en el campo de búsqueda
2. Después de 300ms sin escribir (debounce):
   - Si el query tiene menos de 2 caracteres: Carga lista completa
   - Si el query tiene 2+ caracteres: Llama a `searchPatients()`
3. Se actualiza la lista con los resultados

### Flujo de Selección y Navegación
1. Usuario hace clic en una fila/card de paciente
2. Se llama a `setSelectedPatient()` del GlobalContext
3. Se guarda el paciente en el contexto global
4. Se navega a `/medical`
5. El componente MedicalAttention usa `useGlobalContext()` para obtener el paciente
6. PatientSidebar también usa el contexto y muestra la información

### Flujo de Eliminación (Soft Delete)
1. Usuario hace clic en "Desactivar"
2. Se muestra confirmación: "¿Estás seguro de desactivar al paciente {nombre}?"
3. Si confirma:
   - Se llama a `updatePatient(id, { activo: false })`
   - Se recarga la lista de pacientes
   - El paciente aparece como "Inactivo" en la lista

## Integración con Backend

Los componentes utilizan el servicio `patientService.ts` que hace llamadas HTTP a:

- `GET /patients` - Lista paginada de pacientes
- `GET /patients/search?q={query}` - Búsqueda de pacientes
- `GET /patients/{id}` - Obtener un paciente
- `POST /patients` - Crear paciente
- `PUT /patients/{id}` - Actualizar paciente
- `DELETE /patients/{id}` - Eliminar paciente (soft delete en backend)

## Integración con GlobalContext

El módulo de pacientes utiliza el GlobalContext para:

1. **Compartir el paciente seleccionado** entre módulos (Calendar → Medical Attention)
2. **Permitir navegación fluida** desde lista de pacientes al expediente médico
3. **Mantener estado consistente** del paciente en toda la aplicación

```tsx
// En PatientsPage.tsx
const { setSelectedPatient } = useGlobalContext();

const handlePatientClick = (patient: Patient) => {
  setSelectedPatient(patient);
  navigate('/medical');
};

// En PatientSidebar.tsx
const { selectedPatient } = useGlobalContext();
```

## Estilos y Diseño

- **Framework**: Tailwind CSS
- **Iconos**: Lucide React
- **Colores principales**: Teal 600 (botones primarios), Gray 50-900 (texto y fondos)
- **Responsive**: Mobile-first, breakpoints en `md:` (768px)
- **Animaciones**: Transiciones suaves con `transition-colors`, spinners con `animate-spin`

## Testing Manual

Para probar el módulo completo:

1. Navegar a `/patients`
2. Verificar que la lista carga correctamente
3. Probar búsqueda escribiendo nombre de paciente
4. Crear un nuevo paciente con todos los campos
5. Editar el paciente creado
6. Agregar alergias al paciente
7. Hacer clic en el paciente para navegar a `/medical`
8. Verificar que PatientSidebar muestra la información correcta
9. Volver a `/patients` y desactivar el paciente
10. Verificar que aparece como "Inactivo"

## Mejoras Futuras

- [ ] Exportar lista de pacientes a CSV/Excel
- [ ] Importar pacientes desde archivo
- [ ] Historial de cambios del paciente
- [ ] Notas rápidas del paciente
- [ ] Fotos del paciente
- [ ] Documentos adjuntos (PDF, imágenes)
- [ ] Recordatorios de seguimiento
- [ ] Integración con WhatsApp
