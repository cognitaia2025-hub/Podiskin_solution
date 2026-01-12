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
  motivo_consulta?: string;
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
    const response = await api.get('/citas', { params });
    // Backend devuelve { citas: [], total: number }
    return response.data.citas || response.data;
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
    const response = await api.get(`/citas/${id}`);
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
    const response = await api.post('/citas', appointment);
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
    const response = await api.put(`/citas/${id}`, appointment);
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
    await api.delete(`/citas/${id}`);
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
    const response = await api.patch(`/citas/${id}/status`, { estado: status });
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
    // Backend usa GET /citas/disponibilidad?id_podologo=X&fecha=YYYY-MM-DD
    const response = await api.get('/citas/disponibilidad', {
      params: {
        id_podologo: params.doctor_id,
        fecha: params.start_time.split('T')[0] // Extraer solo la fecha
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error checking availability:', error);
    throw error;
  }
};

// ============================================================================
// RECORDATORIOS
// ============================================================================

export interface ReminderCreate {
  tiempo: number;
  unidad: 'minutos' | 'horas' | 'días';
  metodo_envio?: 'whatsapp' | 'email' | 'sms';
}

export interface Reminder {
  id: number;
  id_cita: number;
  tiempo: number;
  unidad: string;
  enviado: boolean;
  fecha_envio?: string;
  metodo_envio: string;
  error_envio?: string;
  fecha_creacion: string;
}

/**
 * Create a reminder for an appointment
 */
export const createReminder = async (
  citaId: string,
  reminder: ReminderCreate
): Promise<Reminder> => {
  try {
    const response = await api.post(`/citas/${citaId}/recordatorios`, reminder);
    return response.data;
  } catch (error) {
    console.error('Error creating reminder:', error);
    throw error;
  }
};

/**
 * Get all reminders for an appointment
 */
export const getReminders = async (citaId: string): Promise<Reminder[]> => {
  try {
    const response = await api.get(`/citas/${citaId}/recordatorios`);
    return response.data.recordatorios || response.data;
  } catch (error) {
    console.error('Error fetching reminders:', error);
    throw error;
  }
};

/**
 * Delete a specific reminder
 */
export const deleteReminder = async (
  citaId: string,
  reminderId: number
): Promise<void> => {
  try {
    await api.delete(`/citas/${citaId}/recordatorios/${reminderId}`);
  } catch (error) {
    console.error('Error deleting reminder:', error);
    throw error;
  }
};

// ============================================================================
// SERIES / RECURRENCIA
// ============================================================================

export type RecurrenceFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY';

export interface RecurrenceRule {
  frequency: RecurrenceFrequency;
  interval: number;
  count?: number;
  until?: string;
  byweekday?: number[];
}

export interface SeriesCreate {
  regla_recurrencia: RecurrenceRule;
  fecha_inicio: string;
  fecha_fin?: string;
  id_paciente: string;
  id_podologo: string;
  tipo_cita: 'Consulta' | 'Seguimiento' | 'Urgencia';
  duracion_minutos: number;
  hora_inicio: string;
  notas_serie?: string;
}

export interface Series {
  id: number;
  regla_recurrencia: Record<string, any>;
  fecha_inicio: string;
  fecha_fin?: string;
  id_paciente: number;
  id_podologo: number;
  tipo_cita: string;
  duracion_minutos: number;
  hora_inicio: string;
  notas_serie?: string;
  activa: boolean;
  fecha_creacion: string;
  citas_generadas: number;
}

/**
 * Create a recurring appointment series
 */
export const createSeries = async (series: SeriesCreate): Promise<Series> => {
  try {
    const response = await api.post('/citas/series', series);
    return response.data;
  } catch (error) {
    console.error('Error creating series:', error);
    throw error;
  }
};

/**
 * Get all recurring series with optional filters
 */
export const getSeries = async (params?: {
  id_paciente?: string;
  id_podologo?: string;
  activa?: boolean;
  limit?: number;
  offset?: number;
}): Promise<{ series: Series[]; total: number }> => {
  try {
    const response = await api.get('/citas/series', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching series:', error);
    throw error;
  }
};

/**
 * Get a specific series by ID
 */
export const getSeriesById = async (id: number): Promise<Series> => {
  try {
    const response = await api.get(`/citas/series/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching series ${id}:`, error);
    throw error;
  }
};

/**
 * Deactivate a recurring series
 */
export const deactivateSeries = async (
  id: number,
  cancelFutureAppointments: boolean = false
): Promise<void> => {
  try {
    await api.post(`/citas/series/${id}/desactivar`, null, {
      params: { cancelar_futuras: cancelFutureAppointments }
    });
  } catch (error) {
    console.error(`Error deactivating series ${id}:`, error);
    throw error;
  }
};
