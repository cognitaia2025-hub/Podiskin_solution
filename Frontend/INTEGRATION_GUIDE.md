# Integration Guide for Appointments Module

## Overview

This guide explains how to complete the integration of the new appointments module components into the existing calendar views. The core functionality has been implemented, and this guide shows how to wire everything together.

## Already Completed ✅

1. **useAppointments Hook** - Centralized API integration
2. **AppointmentFormModal** - New appointment form with validation
3. **PatientAutocomplete** - Patient search component
4. **AvailabilityIndicator** - Real-time availability checking
5. **AppointmentContextMenu** - Status change menu
6. **AppointmentFilters** - Filter by status/type
7. **Utility Functions** - Click handlers, color coding, formatting
8. **Toast Notifications** - Error and success messages
9. **App.tsx Integration** - Using useAppointments hook
10. **Documentation** - Comprehensive README

## Integration Steps

### 1. Replace EventModal with AppointmentFormModal

The calendar views (CalendarGrid, DayView, MonthView, AgendaView) currently use `EventModal`. To use the new `AppointmentFormModal`:

**Before:**
```tsx
import EventModal from './EventModal';

<EventModal
  isOpen={isModalOpen}
  onClose={() => setIsModalOpen(false)}
  onSave={handleSaveAppointment}
  initialData={selectedAppointment}
  doctors={doctors}
  patients={patients}
/>
```

**After:**
```tsx
import AppointmentFormModal from './appointments/AppointmentFormModal';
import type { AppointmentFormData } from './appointments/AppointmentFormModal';

<AppointmentFormModal
  isOpen={isModalOpen}
  onClose={() => setIsModalOpen(false)}
  onSave={async (data: AppointmentFormData) => {
    // The hook handles API calls and validation
    await onSave({
      ...data,
      start: new Date(data.fecha_hora_inicio),
      end: new Date(data.fecha_hora_fin),
      fecha_hora_inicio: new Date(data.fecha_hora_inicio),
      fecha_hora_fin: new Date(data.fecha_hora_fin),
    });
  }}
  initialData={selectedAppointment}
  doctors={doctors}
  initialDate={selectedDate}
  initialTime="09:00"
/>
```

### 2. Add Click-to-Navigate Functionality

To enable clicking an appointment to view the medical record:

**Import the hook:**
```tsx
import { useAppointmentClick } from '../utils/appointmentUtils';
```

**In component:**
```tsx
const navigateToMedical = useAppointmentClick();

const handleEventClick = async (appt: Appointment) => {
  // Open appointment details modal
  setSelectedAppointment(appt);
  setIsModalOpen(true);
  
  // OR navigate directly to medical record (Ctrl+Click or right-click)
  // await navigateToMedical(appt);
};

// Add to appointment render:
<div
  onClick={(e) => handleEventClick(appt)}
  onContextMenu={(e) => {
    e.preventDefault();
    navigateToMedical(appt);
  }}
  onClickCapture={(e) => {
    if (e.ctrlKey || e.metaKey) {
      e.stopPropagation();
      navigateToMedical(appt);
    }
  }}
>
  {/* Appointment content */}
</div>
```

### 3. Add Status-Based Color Coding

Update appointment styling to use status colors:

```tsx
import { getAppointmentStatusColor } from '../utils/appointmentUtils';

// In appointment render:
<div
  className={`
    rounded-md p-2 border-l-4
    ${getAppointmentStatusColor(appt.estado)}
  `}
>
  {/* Appointment content */}
</div>
```

### 4. Add Context Menu to Appointments

Add the context menu for status changes:

```tsx
import AppointmentContextMenu from './appointments/AppointmentContextMenu';
import { useAppointments } from '../hooks/useAppointments';

// Get the updateStatus function from hook
const { updateStatus, deleteAppointment } = useAppointments({ autoFetch: false });

// In appointment render:
<div className="relative">
  <div className="appointment-content">
    {/* Appointment details */}
  </div>
  
  <div className="absolute top-1 right-1">
    <AppointmentContextMenu
      appointment={appt}
      onStatusChange={(status) => updateStatus(appt.id, status)}
      onEdit={() => handleEditAppointment(appt)}
      onDelete={() => deleteAppointment(appt.id)}
      onViewDetails={() => handleViewDetails(appt)}
    />
  </div>
</div>
```

### 5. Add Filters to Header/Layout

To add appointment filters to the calendar header:

**In App.tsx or Layout:**
```tsx
import AppointmentFilters from './components/appointments/AppointmentFilters';
import type { AppointmentStatus, AppointmentType } from './services/mockData';

const [statusFilter, setStatusFilter] = useState<AppointmentStatus[]>([
  'Pendiente', 'Confirmada', 'En_Curso'
]);
const [typeFilter, setTypeFilter] = useState<AppointmentType[]>([
  'Consulta', 'Seguimiento', 'Urgencia'
]);

// Use in useAppointments hook:
const { appointments } = useAppointments({
  startDate,
  endDate,
  doctorIds: selectedDoctors,
  // Note: Current backend may not support these filters yet
  // status: statusFilter.join(','),
  autoFetch: true,
});

// Client-side filtering if backend doesn't support:
const filteredAppointments = appointments.filter(appt => {
  if (statusFilter.length > 0 && !statusFilter.includes(appt.estado)) {
    return false;
  }
  if (typeFilter.length > 0 && !typeFilter.includes(appt.tipo_cita)) {
    return false;
  }
  return true;
});

// In Layout header:
<div className="flex items-center gap-4">
  <AppointmentFilters
    statusFilter={statusFilter}
    onStatusFilterChange={setStatusFilter}
    typeFilter={typeFilter}
    onTypeFilterChange={setTypeFilter}
  />
  {/* Other header items */}
</div>
```

### 6. Add Upcoming Appointments Badge

Show a notification badge for upcoming appointments:

**In Layout or Header component:**
```tsx
import { getUpcomingAppointments } from '../utils/appointmentUtils';

const upcomingCount = getUpcomingAppointments(appointments).length;

{upcomingCount > 0 && (
  <div className="relative">
    <Bell className="w-5 h-5 text-gray-600" />
    <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
      {upcomingCount}
    </span>
  </div>
)}
```

### 7. Wire Up "Today" Button

The "Today" button already exists in Layout. Wire it up in App.tsx:

```tsx
const handleTodayClick = () => {
  setSelectedDate(new Date());
  setCurrentView('day');
};

<Layout
  onTodayClick={handleTodayClick}
  // ... other props
/>
```

## Complete Example: DayView Integration

Here's a complete example showing how to integrate everything in DayView:

```tsx
import React, { useState, useEffect } from 'react';
import { format, setHours, setMinutes } from 'date-fns';
import { es } from 'date-fns/locale';
import AppointmentFormModal from './appointments/AppointmentFormModal';
import AppointmentContextMenu from './appointments/AppointmentContextMenu';
import { useAppointmentClick, getAppointmentStatusColor } from '../utils/appointmentUtils';
import { useAppointments } from '../hooks/useAppointments';
import type { Appointment, Doctor } from '../services/mockData';
import type { AppointmentFormData } from './appointments/AppointmentFormModal';

interface DayViewProps {
  selectedDate: Date;
  appointments: Appointment[];
  doctors: Doctor[];
  onSave: (appt: Partial<Appointment>) => void;
  triggerCreate?: boolean;
}

const DayView: React.FC<DayViewProps> = ({ 
  selectedDate, 
  appointments, 
  doctors, 
  onSave, 
  triggerCreate 
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<Partial<Appointment> | undefined>();
  
  const navigateToMedical = useAppointmentClick();
  const { updateStatus, deleteAppointment } = useAppointments({ autoFetch: false });

  // ... existing logic ...

  const handleEventClick = (appt: Appointment) => {
    setSelectedAppointment(appt);
    setIsModalOpen(true);
  };

  const handleSaveAppointment = async (data: AppointmentFormData) => {
    await onSave({
      ...data,
      start: new Date(data.fecha_hora_inicio),
      end: new Date(data.fecha_hora_fin),
      fecha_hora_inicio: new Date(data.fecha_hora_inicio),
      fecha_hora_fin: new Date(data.fecha_hora_fin),
    });
    setIsModalOpen(false);
  };

  return (
    <div className="day-view">
      {/* Time grid */}
      {/* ... */}
      
      {/* Appointments */}
      {dayAppointments.map(appt => (
        <div
          key={appt.id}
          className={`
            relative rounded-md p-2 border-l-4 cursor-pointer
            hover:shadow-lg transition-shadow
            ${getAppointmentStatusColor(appt.estado)}
          `}
          onClick={() => handleEventClick(appt)}
          onContextMenu={(e) => {
            e.preventDefault();
            navigateToMedical(appt);
          }}
        >
          <div className="font-medium">{appt.tipo_cita}</div>
          <div className="text-xs opacity-75">
            {format(new Date(appt.fecha_hora_inicio), 'HH:mm')}
          </div>
          
          <div className="absolute top-1 right-1">
            <AppointmentContextMenu
              appointment={appt}
              onStatusChange={(status) => updateStatus(appt.id, status)}
              onEdit={() => handleEventClick(appt)}
              onDelete={() => deleteAppointment(appt.id)}
              onViewDetails={() => navigateToMedical(appt)}
            />
          </div>
        </div>
      ))}
      
      <AppointmentFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveAppointment}
        initialData={selectedAppointment}
        doctors={doctors}
        initialDate={selectedDate}
        initialTime="09:00"
      />
    </div>
  );
};

export default DayView;
```

## Backend Integration Notes

The frontend is now integrated with the backend API through the `useAppointments` hook. Ensure the backend is running and accessible:

### API Endpoints Used

- `GET /appointments` - List appointments with filters
- `POST /appointments` - Create appointment
- `PUT /appointments/:id` - Update appointment
- `PATCH /appointments/:id/status` - Update status
- `DELETE /appointments/:id` - Delete appointment
- `POST /appointments/check-availability` - Check doctor availability
- `GET /patients/search?q={query}` - Search patients

### Environment Setup

Ensure `.env` file has the correct backend URL:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

## Testing Checklist

- [ ] Create new appointment
  - [ ] Patient autocomplete works
  - [ ] Availability checking shows correct status
  - [ ] Cannot create appointment in past
  - [ ] Cannot create appointment with conflict
  - [ ] Toast notification appears on success
- [ ] Edit existing appointment
  - [ ] Form pre-fills with existing data
  - [ ] Availability checking works for edit
  - [ ] Changes are saved
- [ ] Status changes
  - [ ] Context menu appears
  - [ ] Status updates immediately in UI
  - [ ] Colors change based on status
- [ ] Click to medical record
  - [ ] Ctrl+Click navigates to medical record
  - [ ] Right-click navigates to medical record
  - [ ] Patient data is loaded
- [ ] Filters
  - [ ] Status filter works
  - [ ] Type filter works
  - [ ] Clear filters works
- [ ] "Today" button
  - [ ] Jumps to today's date
  - [ ] Switches to day view
- [ ] Loading states
  - [ ] Loading indicator appears during API calls
  - [ ] Disabled states prevent double-submission
- [ ] Error handling
  - [ ] API errors show toast notification
  - [ ] Validation errors prevent submission

## Common Issues and Solutions

### Issue: Toast notifications not appearing
**Solution:** Ensure `<ToastContainer />` is added to `main.tsx`

### Issue: TypeScript errors in calendar views
**Solution:** Update import statements to use new components and types

### Issue: Appointments not loading
**Solution:** Check browser console for API errors, verify backend is running

### Issue: Availability check always shows unavailable
**Solution:** Verify `check-availability` endpoint is working in backend

### Issue: Patient search not working
**Solution:** Verify `/patients/search` endpoint exists in backend

## Next Steps

1. Apply the integration to all calendar views (CalendarGrid, DayView, MonthView, AgendaView)
2. Test with real backend data
3. Add loading skeletons for better UX
4. Implement date range picker for custom filtering
5. Add appointment reminders/notifications
6. Implement recurring appointments (if needed)

## Support

For questions or issues:
- Review the component README in `Frontend/src/components/appointments/README.md`
- Check the API documentation in backend
- Review TypeScript types in components for proper usage
