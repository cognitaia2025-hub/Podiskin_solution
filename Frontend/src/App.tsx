import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { startOfWeek, endOfWeek } from 'date-fns';
import Layout from './components/Layout';
import AppLayout from './layouts/AppLayout';
import { GlobalProvider } from './context/GlobalContext';
import { AuthProvider } from './auth/AuthContext';
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
import StaffManagement from './pages/StaffManagement';
import type { ViewType } from './components/ViewSelector';
import { useAppointments } from './hooks/useAppointments';
import { getDoctors, getPatients } from './services/mockData';
import type { Appointment } from './services/mockData';

function App() {
  const [triggerCreateAppointment, setTriggerCreateAppointment] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedDoctors, setSelectedDoctors] = useState<string[]>(['1', '2', '3']);
  const [searchQuery, setSearchQuery] = useState('');

  // Use real API through custom hook
  const {
    appointments,
    loading,
    createAppointment,
    updateAppointment,
    updateStatus,
    fetchData
  } = useAppointments({
    startDate: startOfWeek(selectedDate),
    endDate: endOfWeek(selectedDate),
    doctorIds: selectedDoctors,
    autoFetch: true,
  });

  const doctors = getDoctors();
  const patients = getPatients();

  // Filter appointments based on selected doctors AND search query
  const filteredAppointments = appointments.filter(appt => {
    // 1. Doctor Filter
    if (!selectedDoctors.includes(appt.id_podologo)) return false;

    // 2. Search Query Filter
    if (!searchQuery) return true;

    const query = searchQuery.toLowerCase();
    const patient = patients.find(p => p.id === appt.id_paciente);
    const doctor = doctors.find(d => d.id === appt.id_podologo);

    const matchesPatient = patient?.name.toLowerCase().includes(query);
    const matchesDoctor = doctor?.name.toLowerCase().includes(query);

    return matchesPatient || matchesDoctor;
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
    <AuthProvider>
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
                path="/perfil"
                element={<PerfilPage />}
              />

              {/* Placeholder Routes */}
              <Route
                path="/records"
                element={
                  <Layout
                    selectedDoctors={selectedDoctors}
                    onDoctorFilterChange={handleDoctorFilterChange}
                  >
                    <RecordsPage />
                  </Layout>
                }
              />

              <Route
                path="/billing"
                element={
                  <Layout
                    selectedDoctors={selectedDoctors}
                    onDoctorFilterChange={handleDoctorFilterChange}
                  >
                    <BillingPage />
                  </Layout>
                }
              />

              <Route
                path="/finances"
                element={
                  <Layout
                    selectedDoctors={selectedDoctors}
                    onDoctorFilterChange={handleDoctorFilterChange}
                  >
                    <FinancesPage />
                  </Layout>
                }
              />

              {/* Default Route */}
              <Route path="/" element={<Navigate to="/calendar" replace />} />
            </Route>
          </Routes>
        </Router>
      </GlobalProvider>
    </AuthProvider>
  );
}

export default App;
