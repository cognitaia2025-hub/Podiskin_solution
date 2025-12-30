# Appointments Module

## Overview

This module handles the complete appointment management system, integrating the frontend calendar with the backend API. It includes real-time availability checking, patient autocomplete search, and seamless navigation to medical records.

## Components

### 1. AppointmentFormModal

Enhanced modal for creating and editing appointments with comprehensive validation.

**Features:**
- Patient autocomplete with debounced search
- Doctor selection
- Date and time picker (with past date validation)
- Duration selector (30, 60, 90, 120 minutes)
- Appointment type selection
- Real-time availability checking
- Conflict detection and display
- First-time visit checkbox
- Reason for visit and reception notes

**Usage:**
```tsx
<AppointmentFormModal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  onSave={handleSave}
  initialData={appointment}
  doctors={doctors}
  initialDate={new Date()}
  initialTime="09:00"
/>
```

**Validation:**
- ✅ Patient selected
- ✅ Doctor selected
- ✅ Date not in the past
- ✅ Time within working hours
- ✅ Doctor availability verified
- ✅ No conflicting appointments

### 2. PatientAutocomplete

Searchable dropdown for patient selection with debounced API calls.

**Features:**
- Real-time search (300ms debounce)
- Displays patient name and phone
- Shows selected patient info
- "Create new patient" button
- Error state handling

**Usage:**
```tsx
<PatientAutocomplete
  value={patientId}
  onChange={(id, patient) => handlePatientSelect(id, patient)}
  onCreateNew={() => openPatientForm()}
  error={errors.patient}
/>
```

### 3. AvailabilityIndicator

Visual feedback for doctor availability checking.

**States:**
- `idle` - No check performed
- `checking` - Verification in progress
- `available` - Time slot available ✅
- `unavailable` - Conflicting appointments ❌

**Features:**
- Shows conflicting appointment times
- Clear visual feedback with icons
- Prevents form submission when unavailable

### 4. AppointmentContextMenu

Right-click/options menu for appointment actions.

**Actions:**
- 📝 View details
- ✏️ Edit appointment
- ✅ Mark as Confirmed
- 🩺 Mark as In Progress
- ✓ Mark as Completed
- ❌ Cancel appointment
- ⚠️ Mark as No-Show
- 🗑️ Delete appointment

**Usage:**
```tsx
<AppointmentContextMenu
  appointment={appointment}
  onStatusChange={handleStatusChange}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onViewDetails={handleView}
/>
```

### 5. AppointmentFilters

Filter panel for appointments by status and type.

**Filters:**
- **Status:** Pendiente, Confirmada, En Proceso, Completada, Cancelada, No Asistió
- **Type:** Consulta, Seguimiento, Urgencia

**Features:**
- Multiple selection
- Active filter count badge
- Clear all filters button

## Hooks

### useAppointments

Centralized hook for appointment state management and API integration.

**Features:**
- Automatic data fetching with filters
- Create appointment (with availability check)
- Update appointment
- Update status
- Delete appointment
- Loading and error states
- Toast notifications

**Usage:**
```tsx
const {
  appointments,
  loading,
  error,
  createAppointment,
  updateAppointment,
  updateStatus,
  deleteAppointment,
  checkAvailability,
  fetchData,
} = useAppointments({
  startDate: new Date(),
  endDate: addDays(new Date(), 7),
  doctorIds: ['1', '2', '3'],
  status: 'Confirmada',
  autoFetch: true,
});
```

**API Integration:**
- `GET /appointments` - List appointments with filters
- `POST /appointments` - Create new appointment
- `PUT /appointments/:id` - Update appointment
- `PATCH /appointments/:id/status` - Update status
- `DELETE /appointments/:id` - Delete appointment
- `POST /appointments/check-availability` - Check doctor availability

## Utilities

### appointmentUtils.ts

**useAppointmentClick()**
Hook to handle appointment clicks and navigate to medical records:
```tsx
const handleClick = useAppointmentClick();
// Loads patient data, updates GlobalContext, navigates to /medical
await handleClick(appointment);
```

**getAppointmentStatusColor(status)**
Returns Tailwind CSS classes for appointment status:
```tsx
const colorClass = getAppointmentStatusColor('Confirmada');
// Returns: 'bg-blue-100 border-blue-400 text-blue-800'
```

**getUpcomingAppointments(appointments)**
Filters appointments within next 2 hours:
```tsx
const upcoming = getUpcomingAppointments(allAppointments);
// Shows badge: upcoming.length
```

**formatAppointmentTime(appointment)**
Formats appointment time range:
```tsx
const timeRange = formatAppointmentTime(appointment);
// Returns: "09:00 - 09:30"
```

## Flows

### 1. Creating an Appointment

```
User clicks "Nueva Cita"
  ↓
AppointmentFormModal opens
  ↓
User searches and selects patient (PatientAutocomplete)
  ↓
User selects doctor, date, time, duration
  ↓
AvailabilityIndicator checks availability (real-time)
  ↓
If available: User fills remaining fields
  ↓
User clicks "Crear Cita"
  ↓
useAppointments.createAppointment() called
  ↓
Backend validates and creates appointment
  ↓
Toast notification: "Cita creada exitosamente" ✅
  ↓
Calendar refreshes with new appointment
```

### 2. Availability Validation

```
User changes doctor, date, or time
  ↓
Debounce 500ms
  ↓
AvailabilityIndicator status → 'checking'
  ↓
API call: checkDoctorAvailability()
  ↓
Backend checks for conflicts
  ↓
If available:
  AvailabilityIndicator → 'available' ✅
  Form can be submitted
  ↓
If unavailable:
  AvailabilityIndicator → 'unavailable' ❌
  Display conflicting appointments
  Form submission disabled
```

### 3. Click on Appointment → Medical Record

```
User clicks appointment in calendar
  ↓
useAppointmentClick() hook triggered
  ↓
API call: getPatientById(appointment.id_paciente)
  ↓
Patient data loaded
  ↓
GlobalContext updated:
  - setSelectedPatient(patient)
  - setSelectedAppointment(appointment)
  ↓
Navigate to /medical route
  ↓
MedicalAttention page loads with patient context
```

### 4. Changing Appointment Status

```
User clicks ⋮ on appointment
  ↓
AppointmentContextMenu opens
  ↓
User selects new status (e.g., "Confirmar")
  ↓
useAppointments.updateStatus(id, 'Confirmada')
  ↓
Backend updates appointment status
  ↓
Local state updated immediately
  ↓
UI color changes to reflect new status
  ↓
Toast notification: "Cita marcada como confirmada" ✅
```

## Status Color Coding

| Status | Color | Border | Background |
|--------|-------|--------|------------|
| Pendiente | Yellow | `border-yellow-400` | `bg-yellow-100` |
| Confirmada | Blue | `border-blue-400` | `bg-blue-100` |
| En_Curso | Green | `border-green-400` | `bg-green-100` |
| Completada | Gray | `border-gray-400` | `bg-gray-100` |
| Cancelada | Red | `border-red-400` | `bg-red-100` |
| No_Asistio | Orange | `border-orange-400` | `bg-orange-100` |

## Integration with GlobalContext

The module integrates with `GlobalContext` for cross-module communication:

```tsx
// Setting selected entities
setSelectedPatient(patient);
setSelectedAppointment(appointment);

// Accessing in MedicalAttention page
const { selectedPatient, selectedAppointment } = useGlobalContext();
```

This enables:
- Click on appointment → View patient medical record
- Context preservation across navigation
- Shared state between Calendar and MedicalAttention modules

## Error Handling

All API calls include proper error handling:

```tsx
try {
  await createAppointment(data);
  toast.success('Cita creada exitosamente');
} catch (err) {
  toast.error(err.response?.data?.detail || 'Error al crear la cita');
  console.error('Error creating appointment:', err);
}
```

Common errors:
- **400 Bad Request** - Validation error (past date, missing fields)
- **409 Conflict** - Time slot unavailable
- **404 Not Found** - Patient/Doctor not found
- **500 Internal Server Error** - Backend error

## Testing

### Manual Testing Checklist

- [ ] Create appointment with all fields
- [ ] Search and select patient
- [ ] Verify availability checking works
- [ ] Try creating appointment in past (should fail)
- [ ] Try creating appointment with conflict (should fail)
- [ ] Edit existing appointment
- [ ] Change appointment status
- [ ] Click appointment → Navigate to medical record
- [ ] Filter appointments by status
- [ ] Filter appointments by type
- [ ] Delete appointment
- [ ] Check toast notifications appear
- [ ] Verify loading states

### TypeScript Compilation

```bash
cd Frontend
npm run build
```

Should compile without errors.

## Future Enhancements

- [ ] Recurrence/recurring appointments
- [ ] Email/SMS reminders integration
- [ ] Calendar export (iCal)
- [ ] Bulk operations (cancel multiple)
- [ ] Appointment templates
- [ ] Wait list management
- [ ] Patient no-show tracking
