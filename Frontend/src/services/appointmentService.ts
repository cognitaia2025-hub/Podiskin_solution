/**
 * Appointment Service
 * 
 * HTTP service for appointment CRUD operations
 */

import api from './api';
import type { Appointment, AppointmentStatus, AppointmentType } from '../types/appointments';

export interface AppointmentCreateRequest {
  id_paciente: string;
  id_podologo: string;
  fecha_hora_inicio: string; // ISO string
  fecha_hora_fin: string; // ISO string
  tipo_cita: AppointmentType;
  es_primera_vez?: boolean;
  notas_recepcion?: string;
  color?: string;
}

export interface AppointmentUpdateRequest extends Partial<AppointmentCreateRequest> {
  estado?: AppointmentStatus;
}

export interface AppointmentListResponse {
  appointments: Appointment[];
  total: number;
}

/**
 * Get all appointments with optional filters
 */
export const getAppointments = async (params?: {
  start_date?: string;
  end_date?: string;
  doctor_id?: string;
  patient_id?: string;
  status?: AppointmentStatus;
}): Promise<Appointment[]> => {
  try {
    const response = await api.get('/appointments', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching appointments:', error);
    throw error;
  }
};

/**
 * Get a single appointment by ID
 */
export const getAppointmentById = async (id: string): Promise<Appointment> => {
  try {
    const response = await api.get(`/appointments/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching appointment ${id}:`, error);
    throw error;
  }
};

/**
 * Create a new appointment
 */
export const createAppointment = async (
  appointment: AppointmentCreateRequest
): Promise<Appointment> => {
  try {
    const response = await api.post('/appointments', appointment);
    return response.data;
  } catch (error) {
    console.error('Error creating appointment:', error);
    throw error;
  }
};

/**
 * Update an existing appointment
 */
export const updateAppointment = async (
  id: string,
  appointment: AppointmentUpdateRequest
): Promise<Appointment> => {
  try {
    const response = await api.put(`/appointments/${id}`, appointment);
    return response.data;
  } catch (error) {
    console.error(`Error updating appointment ${id}:`, error);
    throw error;
  }
};

/**
 * Delete an appointment
 */
export const deleteAppointment = async (id: string): Promise<void> => {
  try {
    await api.delete(`/appointments/${id}`);
  } catch (error) {
    console.error(`Error deleting appointment ${id}:`, error);
    throw error;
  }
};

/**
 * Update appointment status
 */
export const updateAppointmentStatus = async (
  id: string,
  status: AppointmentStatus
): Promise<Appointment> => {
  try {
    const response = await api.patch(`/appointments/${id}/status`, { estado: status });
    return response.data;
  } catch (error) {
    console.error(`Error updating appointment status ${id}:`, error);
    throw error;
  }
};

/**
 * Check doctor availability for a time slot
 */
export const checkDoctorAvailability = async (params: {
  doctor_id: string;
  start_time: string;
  end_time: string;
  exclude_appointment_id?: string;
}): Promise<{ available: boolean; conflicting_appointments?: Appointment[] }> => {
  try {
    const response = await api.post('/appointments/check-availability', params);
    return response.data;
  } catch (error) {
    console.error('Error checking availability:', error);
    throw error;
  }
};
