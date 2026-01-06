import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { startOfWeek, endOfWeek } from 'date-fns';
import Layout from './components/Layout';
import AppLayout from './layouts/AppLayout';
import { GlobalProvider } from './context/GlobalContext';
import { AuthProvider, useAuth } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';
import LoginPage from './auth/LoginPage';
import RecoverPasswordPage from './auth/RecoverPasswordPage';
import ResetPasswordPage from './auth/ResetPasswordPage';
import CalendarGrid from './components/CalendarGrid';
import DayView from './components/DayView';
import MonthView from './components/MonthView';
import AgendaView from './components/AgendaView';
import StaffAvailability from './components/StaffAvailability';
import MedicalAttention from './pages/MedicalAttention';
import RecordsPage from './pages/RecordsPage';
import BillingPage from './pages/BillingPage';
import FinancesPage from './pages/FinancesPage';
import PatientsPage from './pages/PatientsPage';
import DashboardPage from './pages/DashboardPage';
import AjustesPage from './pages/AjustesPage';
import AdminPage from './pages/AdminPage';
import PerfilPage from './pages/PerfilPage';
import StaffManagement from './pages/admin/StaffManagement';
import InventoryPage from './pages/admin/InventoryPage';
import AuditPage from './pages/admin/AuditPage';
import type { ViewType } from './components/ViewSelector';
import { useAppointments } from './hooks/useAppointments';
import type { Doctor, Patient, Appointment } from './types/appointments';
import { getDoctors } from './services/doctorService';

const ServicesPage = React.lazy(() => import('./pages/admin/ServicesPage'));
const MedicalAttentionPage = React.lazy(() => import('./pages/medical/MedicalAttentionPage'));
const MedicalRecordsPage = React.lazy(() => import('./pages/medical/MedicalRecordsPage'));

function AppContent() {
  const { user } = useAuth(); // Get authenticated user
  const [triggerCreateAppointment, setTriggerCreateAppointment] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedDoctors, setSelectedDoctors] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Doctors state
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loadingDoctors, setLoadingDoctors] = useState(false);
  const [doctorsError, setDoctorsError] = useState<string | null>(null);

  // Load doctors from API ONLY when user is authenticated
  useEffect(() => {
    if (!user) {
      // User not logged in - don't try to load doctors
      setDoctors([]);
      setLoadingDoctors(false);
      return;
    }

    async function loadDoctors() {
      try {
        setLoadingDoctors(true);
        setDoctorsError(null);
        const fetchedDoctors = await getDoctors();
        setDoctors(fetchedDoctors);
        
        // Auto-select all doctors by default
        setSelectedDoctors(fetchedDoctors.map(d => d.id));
        
        console.log('✅ Doctors loaded successfully:', fetchedDoctors.length);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Error al cargar podólogos';
        setDoctorsError(errorMessage);
        console.error('❌ Error loading doctors:', error);
        
        // Fallback: empty array, app won't break
        setDoctors([]);
        setSelectedDoctors([]);
      } finally {
        setLoadingDoctors(false);
      }
    }

    loadDoctors();
  }, [user]); // Re-run when user changes (login/logout)

  // Use real API through custom hook
  const {
    appointments,
    createAppointment,
    updateAppointment,
    fetchData
  } = useAppointments({
    startDate: startOfWeek(selectedDate),
    endDate: endOfWeek(selectedDate),
    doctorIds: selectedDoctors,
    autoFetch: true,
  });

  // Filter appointments based on selected doctors AND search query
  const filteredAppointments = appointments.filter(appt => {
    // 1. Doctor Filter
    if (!selectedDoctors.includes(appt.id_podologo)) return false;

    // 2. Search Query Filter
    if (!searchQuery) return true;

    const query = searchQuery.toLowerCase();
    const doctor = doctors.find(d => d.id === appt.id_podologo);

    const matchesDoctor = doctor?.name.toLowerCase().includes(query);
    const matchesNotes = appt.notas_recepcion?.toLowerCase().includes(query);

    return matchesDoctor || matchesNotes;
  });

  // Toggle doctor selection
  const handleDoctorFilterChange = (doctorId: string) => {
    setSelectedDoctors(prev =>
      prev.includes(doctorId)
        ? prev.filter(id => id !== doctorId)
        : [...prev, doctorId]
    );
  };

  // Refetch when filters change
  React.useEffect(() => {
    fetchData();
  }, [selectedDoctors, selectedDate, fetchData]);

  // Empty patients array - patients are loaded dynamically from API when needed
  const patients: Patient[] = [];

  const handleCreateClick = () => {
    setTriggerCreateAppointment(true);
    setTimeout(() => setTriggerCreateAppointment(false), 100);
  };

  const handleSearch = (query: string) => {
    // Check if it's a date (DD/MM/YYYY or YYYY-MM-DD)
    const dateRegex = /^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$/;
    const match = query.match(dateRegex);

    if (match) {
      const [_, day, month, year] = match;
      const targetDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

      if (!isNaN(targetDate.getTime())) {
        setSelectedDate(targetDate);
        setCurrentView('day');
        setSearchQuery('');
        return;
      }
    }

    setSearchQuery(query);
    if (query) {
      setCurrentView('agenda');
    }
  };

  const handleSaveAppointment = async (apptData: Partial<Appointment>) => {
    if (apptData.start && apptData.end) {
      if (apptData.id) {
        // Update existing appointment
        await updateAppointment(apptData.id, {
          id_paciente: apptData.id_paciente,
          id_podologo: apptData.id_podologo,
          fecha_hora_inicio: apptData.start.toISOString(),
          fecha_hora_fin: apptData.end.toISOString(),
          tipo_cita: apptData.tipo_cita,
          motivo_consulta: apptData.motivo_consulta,
          notas_recepcion: apptData.notas_recepcion,
        });
      } else {
        // Create new appointment
        await createAppointment({
          id_paciente: apptData.id_paciente!,
          id_podologo: apptData.id_podologo!,
          fecha_hora_inicio: apptData.start.toISOString(),
          fecha_hora_fin: apptData.end.toISOString(),
          tipo_cita: apptData.tipo_cita!,
          motivo_consulta: apptData.motivo_consulta,
          notas_recepcion: apptData.notas_recepcion,
          es_primera_vez: apptData.es_primera_vez,
        });
      }
    }
  };

  const renderCalendarView = () => {
    // Show loading state while doctors are being fetched
    if (loadingDoctors) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando podólogos...</p>
          </div>
        </div>
      );
    }

    // Show error state if doctors failed to load
    if (doctorsError) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center max-w-md">
            <div className="text-red-600 text-5xl mb-4">⚠️</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Error al cargar podólogos</h3>
            <p className="text-gray-600 mb-4">{doctorsError}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reintentar
            </button>
          </div>
        </div>
      );
    }

    // Show empty state if no doctors available
    if (doctors.length === 0) {
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center max-w-md">
            <div className="text-gray-400 text-5xl mb-4">👨‍⚕️</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No hay podólogos disponibles</h3>
            <p className="text-gray-600">Por favor contacta al administrador para agregar podólogos al sistema.</p>
          </div>
        </div>
      );
    }

    switch (currentView) {
      case 'day':
        return (
          <DayView
            selectedDate={selectedDate}
            appointments={filteredAppointments}
            doctors={doctors}
            patients={patients}
            onSave={handleSaveAppointment}
            triggerCreate={triggerCreateAppointment}
          />
        );
      case 'month':
        return (
          <MonthView
            selectedDate={selectedDate}
            appointments={filteredAppointments}
            doctors={doctors}
            patients={patients}
            onDayClick={(date) => {
              setSelectedDate(date);
              setCurrentView('day');
            }}
            onSave={handleSaveAppointment}
            triggerCreate={triggerCreateAppointment}
          />
        );
      case 'agenda':
        return (
          <AgendaView
            appointments={filteredAppointments}
            doctors={doctors}
            patients={patients}
            onSave={handleSaveAppointment}
            triggerCreate={triggerCreateAppointment}
          />
        );
      case 'staff':
        return (
          <StaffAvailability
            appointments={filteredAppointments}
            doctors={doctors}
            patients={patients}
            onSave={handleSaveAppointment}
            triggerCreate={triggerCreateAppointment}
          />
        );
      case 'week':
      default:
        return (
          <CalendarGrid
            triggerCreate={triggerCreateAppointment}
            appointments={filteredAppointments}
            doctors={doctors}
            onSave={handleSaveAppointment}
          />
        );
    }
  };

  return (
    <GlobalProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/auth/recover-password" element={<RecoverPasswordPage />} />
            <Route path="/auth/reset-password" element={<ResetPasswordPage />} />

            {/* Protected Routes */}
            <Route element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }>
              {/* Calendar Routes */}
              <Route
                path="/calendar"
                element={
                  <Layout
                    onCreateClick={handleCreateClick}
                    currentView={currentView}
                    onViewChange={setCurrentView}
                    selectedDoctors={selectedDoctors}
                    onDoctorFilterChange={handleDoctorFilterChange}
                    onSearch={handleSearch}
                  >
                    {renderCalendarView()}
                  </Layout>
                }
              />

              {/* Medical Attention Route */}
              <Route
                path="/medical"
                element={<MedicalAttention />}
              />

              {/* New Medical Management Routes */}
              <Route
                path="/medical/attention"
                element={
                  <React.Suspense fallback={<div>Loading...</div>}>
                    <MedicalAttentionPage />
                  </React.Suspense>
                }
              />
              <Route
                path="/medical/records"
                element={
                  <React.Suspense fallback={<div>Loading...</div>}>
                    <MedicalRecordsPage />
                  </React.Suspense>
                }
              />

              {/* Patients Route */}
              <Route
                path="/patients"
                element={<PatientsPage />}
              />

              {/* Dashboard Route */}
              <Route
                path="/dashboard"
                element={<DashboardPage />}
              />

              {/* Admin Menu Routes */}
              <Route
                path="/ajustes"
                element={<AjustesPage />}
              />
              <Route
                path="/admin"
                element={<AdminPage />}
              />
              <Route
                path="/admin/staff"
                element={<StaffManagement />}
              />
              <Route
                path="/admin/inventory"
                element={<InventoryPage />}
              />
              <Route
                path="/admin/audit"
                element={<AuditPage />}
              />
              <Route
                path="/admin/services"
                element={
                  <React.Suspense fallback={<div>Loading...</div>}>
                    <ServicesPage />
                  </React.Suspense>
                }
              />
              <Route
                path="/perfil"
                element={<PerfilPage />}
              />

              {/* Placeholder Routes */}
              <Route
                path="/records"
                element={<RecordsPage />}
              />

              <Route
                path="/billing"
                element={<BillingPage />}
              />

              <Route
                path="/finances"
                element={<FinancesPage />}
              />

              {/* Default Route */}
              <Route path="/" element={<Navigate to="/calendar" replace />} />
            </Route>
          </Routes>
        </Router>
      </GlobalProvider>
  );
}

// Main App wrapper
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
