/**
 * Appointment Utilities
 * 
 * Shared utilities for appointment interactions across calendar views
 */

import { useNavigate } from 'react-router-dom';
import { useGlobalContext } from '../context/GlobalContext';
import { getPatientById } from '../services/patientService';
import { toast } from 'react-toastify';
import type { Appointment } from '../types/appointments';

/**
 * Custom hook for handling appointment clicks
 * Loads patient data and navigates to medical attention page
 */
export const useAppointmentClick = () => {
  const navigate = useNavigate();
  const { setSelectedPatient, setSelectedAppointment } = useGlobalContext();

  const handleAppointmentClick = async (appointment: Appointment) => {
    try {
      // Load full patient data
      const patient = await getPatientById(appointment.id_paciente);
      
      // Update global context
      setSelectedPatient(patient);
      setSelectedAppointment(appointment);
      
      // Navigate to medical attention
      navigate('/medical');
    } catch (error) {
      console.error('Error loading patient:', error);
      toast.error('Error al cargar datos del paciente');
    }
  };

  return handleAppointmentClick;
};

/**
 * Get color class based on appointment status
 */
export const getAppointmentStatusColor = (estado: string): string => {
  switch (estado) {
    case 'Pendiente':
      return 'bg-yellow-100 border-yellow-400 text-yellow-800';
    case 'Confirmada':
      return 'bg-blue-100 border-blue-400 text-blue-800';
    case 'En_Curso':
      return 'bg-green-100 border-green-400 text-green-800';
    case 'Completada':
      return 'bg-gray-100 border-gray-400 text-gray-600';
    case 'Cancelada':
      return 'bg-red-100 border-red-400 text-red-800';
    case 'No_Asistio':
      return 'bg-orange-100 border-orange-400 text-orange-800';
    default:
      return 'bg-gray-100 border-gray-400 text-gray-800';
  }
};

/**
 * Get upcoming appointments (within next 2 hours)
 */
export const getUpcomingAppointments = (appointments: Appointment[]): Appointment[] => {
  const now = new Date();
  const twoHoursFromNow = new Date(now.getTime() + 2 * 60 * 60 * 1000);
  
  return appointments.filter(apt => {
    const start = new Date(apt.fecha_hora_inicio);
    return start >= now && start <= twoHoursFromNow && apt.estado !== 'Cancelada';
  });
};

/**
 * Format appointment time range
 */
export const formatAppointmentTime = (appointment: Appointment): string => {
  const start = new Date(appointment.fecha_hora_inicio);
  const end = new Date(appointment.fecha_hora_fin);
  
  const startTime = start.toLocaleTimeString('es-MX', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
  const endTime = end.toLocaleTimeString('es-MX', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
  
  return `${startTime} - ${endTime}`;
};
