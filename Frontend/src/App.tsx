import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import AppLayout from './layouts/AppLayout';
import { GlobalProvider } from './context/GlobalContext';
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';
import LoginPage from './auth/LoginPage';
import CalendarGrid from './components/CalendarGrid';
import DayView from './components/DayView';
import MonthView from './components/MonthView';
import AgendaView from './components/AgendaView';
import StaffAvailability from './components/StaffAvailability';
import MedicalAttention from './pages/MedicalAttention';
import RecordsPage from './pages/RecordsPage';
import BillingPage from './pages/BillingPage';
import FinancesPage from './pages/FinancesPage';
import type { ViewType } from './components/ViewSelector';
import { getAppointments, createAppointment, getDoctors, getPatients } from './services/mockData';
import type { Appointment } from './services/mockData';

function App() {
  const [triggerCreateAppointment, setTriggerCreateAppointment] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedDoctors, setSelectedDoctors] = useState<string[]>(['1', '2', '3']);
  const [searchQuery, setSearchQuery] = useState('');

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

  React.useEffect(() => {
    getAppointments().then(setAppointments);
  }, []);

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
        setAppointments(prev => prev.map(p => p.id === apptData.id ? { ...p, ...apptData } as Appointment : p));
      } else {
        const newAppt = await createAppointment(apptData as any);
        setAppointments(prev => [...prev, newAppt]);
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
            {/* Public Route */}
            <Route path="/login" element={<LoginPage />} />

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
