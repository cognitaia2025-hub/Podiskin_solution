/**
 * useAppointments Hook
 * 
 * Centralized hook for managing appointment state and API calls
 */

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import { useAuth } from '../auth/AuthContext';
import {
  getAppointments as fetchAppointments,
  createAppointment as apiCreateAppointment,
  updateAppointment as apiUpdateAppointment,
  updateAppointmentStatus as apiUpdateAppointmentStatus,
  deleteAppointment as apiDeleteAppointment,
  checkDoctorAvailability as apiCheckDoctorAvailability,
} from '../services/appointmentService';
import type { Appointment, AppointmentStatus } from '../types/appointments';
import type { AppointmentCreateRequest, AppointmentUpdateRequest } from '../services/appointmentService';

interface UseAppointmentsOptions {
  startDate?: Date;
  endDate?: Date;
  doctorIds?: string[];
  patientId?: string;
  status?: AppointmentStatus;
  autoFetch?: boolean;
}

export const useAppointments = (options: UseAppointmentsOptions = {}) => {
  const { user, isAuthenticated } = useAuth();
  const {
    startDate,
    endDate,
    doctorIds = [],
    patientId,
    status,
    autoFetch = true
  } = options;

  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch appointments from API with current filters
   */
  // Convert arrays to strings for stable dependency comparison
  const doctorIdsKey = doctorIds.join(',');

  const fetchData = useCallback(async () => {
    // Don't fetch if not authenticated
    if (!isAuthenticated || !user) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);

      const params: any = {};

      if (startDate) {
        params.start_date = startDate.toISOString();
      }
      if (endDate) {
        params.end_date = endDate.toISOString();
      }
      if (doctorIdsKey) {
        params.doctor_id = doctorIdsKey;
      }
      if (patientId) {
        params.patient_id = patientId;
      }
      if (status) {
        params.status = status;
      }

      const data = await fetchAppointments(params);

      // Handle both array response and {total, citas} response format
      const appointmentsArray = Array.isArray(data) ? data : (data.citas || []);

      // Map backend response to frontend format
      const mappedData = appointmentsArray.map((appt: any) => ({
        ...appt,
        start: new Date(appt.fecha_hora_inicio),
        end: new Date(appt.fecha_hora_fin),
        fecha_hora_inicio: new Date(appt.fecha_hora_inicio),
        fecha_hora_fin: new Date(appt.fecha_hora_fin),
        patientId: appt.id_paciente,
        doctorId: appt.id_podologo,
        title: `${appt.tipo_cita} - ${appt.paciente?.nombre_completo || 'Paciente'}`,
        type: appt.tipo_cita?.toLowerCase(),
        status: appt.estado?.toLowerCase(),
        notes: appt.notas_recepcion,
      }));

      setAppointments(mappedData);
    } catch (err) {
      const errorMsg = 'Error al cargar citas';
      setError(errorMsg);
      toast.error(errorMsg);
      console.error('Error fetching appointments:', err);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, user, startDate?.getTime(), endDate?.getTime(), doctorIdsKey, patientId, status]);

  /**
   * Create a new appointment
   */
  const createAppointment = async (appointmentData: AppointmentCreateRequest): Promise<Appointment | null> => {
    try {
      setLoading(true);

      // Check availability first
      const availability = await apiCheckDoctorAvailability({
        doctor_id: appointmentData.id_podologo,
        start_time: appointmentData.fecha_hora_inicio,
        end_time: appointmentData.fecha_hora_fin,
      });

      if (!availability.available) {
        toast.error('El doctor no está disponible en ese horario');
        if (availability.conflicting_appointments && availability.conflicting_appointments.length > 0) {
          const conflict = availability.conflicting_appointments[0];
          toast.warning(`Conflicto con cita existente: ${new Date(conflict.fecha_hora_inicio).toLocaleTimeString()}`);
        }
        return null;
      }

      const newAppointment = await apiCreateAppointment(appointmentData);

      // Map to frontend format
      const mappedAppointment = {
        ...newAppointment,
        start: new Date(newAppointment.fecha_hora_inicio),
        end: new Date(newAppointment.fecha_hora_fin),
        fecha_hora_inicio: new Date(newAppointment.fecha_hora_inicio),
        fecha_hora_fin: new Date(newAppointment.fecha_hora_fin),
        patientId: newAppointment.id_paciente,
        doctorId: newAppointment.id_podologo,
        title: `${newAppointment.tipo_cita}`,
        type: newAppointment.tipo_cita?.toLowerCase(),
        status: newAppointment.estado?.toLowerCase(),
        notes: newAppointment.notas_recepcion,
      };

      setAppointments(prev => [...prev, mappedAppointment]);
      toast.success('Cita creada exitosamente');
      return mappedAppointment;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al crear la cita';
      toast.error(errorMsg);
      console.error('Error creating appointment:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update an existing appointment
   */
  const updateAppointment = async (
    id: string,
    updateData: AppointmentUpdateRequest
  ): Promise<Appointment | null> => {
    try {
      setLoading(true);

      // Check availability if time is being changed
      if (updateData.fecha_hora_inicio && updateData.fecha_hora_fin && updateData.id_podologo) {
        const availability = await apiCheckDoctorAvailability({
          doctor_id: updateData.id_podologo,
          start_time: updateData.fecha_hora_inicio,
          end_time: updateData.fecha_hora_fin,
          exclude_appointment_id: id,
        });

        if (!availability.available) {
          toast.error('El doctor no está disponible en ese horario');
          return null;
        }
      }

      const updated = await apiUpdateAppointment(id, updateData);

      // Map to frontend format
      const mappedAppointment = {
        ...updated,
        start: new Date(updated.fecha_hora_inicio),
        end: new Date(updated.fecha_hora_fin),
        fecha_hora_inicio: new Date(updated.fecha_hora_inicio),
        fecha_hora_fin: new Date(updated.fecha_hora_fin),
        patientId: updated.id_paciente,
        doctorId: updated.id_podologo,
        title: `${updated.tipo_cita}`,
        type: updated.tipo_cita?.toLowerCase(),
        status: updated.estado?.toLowerCase(),
        notes: updated.notas_recepcion,
      };

      setAppointments(prev =>
        prev.map(appt => appt.id === id ? mappedAppointment : appt)
      );
      toast.success('Cita actualizada exitosamente');
      return mappedAppointment;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al actualizar la cita';
      toast.error(errorMsg);
      console.error('Error updating appointment:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update appointment status
   */
  const updateStatus = async (
    id: string,
    newStatus: AppointmentStatus
  ): Promise<boolean> => {
    try {
      setLoading(true);
      const updated = await apiUpdateAppointmentStatus(id, newStatus);

      // Map to frontend format
      const mappedAppointment = {
        ...updated,
        start: new Date(updated.fecha_hora_inicio),
        end: new Date(updated.fecha_hora_fin),
        fecha_hora_inicio: new Date(updated.fecha_hora_inicio),
        fecha_hora_fin: new Date(updated.fecha_hora_fin),
        patientId: updated.id_paciente,
        doctorId: updated.id_podologo,
        title: `${updated.tipo_cita}`,
        type: updated.tipo_cita?.toLowerCase(),
        status: updated.estado?.toLowerCase(),
        notes: updated.notas_recepcion,
      };

      setAppointments(prev =>
        prev.map(appt => appt.id === id ? mappedAppointment : appt)
      );

      const statusLabels: Record<AppointmentStatus, string> = {
        'Pendiente': 'pendiente',
        'Confirmada': 'confirmada',
        'En_Curso': 'en curso',
        'Completada': 'completada',
        'Cancelada': 'cancelada',
        'No_Asistio': 'no asistió',
      };

      toast.success(`Cita marcada como ${statusLabels[newStatus]}`);
      return true;
    } catch (err) {
      toast.error('Error al actualizar estado de la cita');
      console.error('Error updating appointment status:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Delete an appointment
   */
  const deleteAppointmentById = async (id: string): Promise<boolean> => {
    try {
      setLoading(true);
      await apiDeleteAppointment(id);
      setAppointments(prev => prev.filter(appt => appt.id !== id));
      toast.success('Cita eliminada exitosamente');
      return true;
    } catch (err) {
      toast.error('Error al eliminar la cita');
      console.error('Error deleting appointment:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Check doctor availability
   */
  const checkAvailability = async (params: {
    doctor_id: string;
    start_time: string;
    end_time: string;
    exclude_appointment_id?: string;
  }) => {
    try {
      return await apiCheckDoctorAvailability(params);
    } catch (err) {
      console.error('Error checking availability:', err);
      return { available: false };
    }
  };

  /**
   * Auto-fetch on mount and when filters change
   */
  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, [autoFetch, fetchData]);

  return {
    appointments,
    loading,
    error,
    fetchData,
    createAppointment,
    updateAppointment,
    updateStatus,
    deleteAppointment: deleteAppointmentById,
    checkAvailability,
  };
};
