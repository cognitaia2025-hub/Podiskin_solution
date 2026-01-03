/**
 * AppointmentFormModal Component
 * 
 * Enhanced modal for creating and editing appointments with validation
 */

import React, { useState, useEffect } from 'react';
import { X, Calendar, Clock, User, FileText, AlertCircle } from 'lucide-react';
import { format, addMinutes, setHours, setMinutes, isBefore, startOfDay } from 'date-fns';
import { es } from 'date-fns/locale';
import PatientAutocomplete from './PatientAutocomplete';
import AvailabilityIndicator from './AvailabilityIndicator';
import { checkDoctorAvailability } from '../../services/appointmentService';
import { getServices, Service } from '../../services/catalogService';
import type { Appointment, Doctor, AppointmentType } from '../../types/appointments';
import type { Patient } from '../../services/patientService';

interface AppointmentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: AppointmentFormData) => Promise<void>;
  initialData?: Partial<Appointment>;
  doctors: Doctor[];
  initialDate?: Date;
  initialTime?: string;
}

export interface AppointmentFormData {
  id?: string;
  id_paciente: string;
  id_podologo: string;
  fecha_hora_inicio: string;
  fecha_hora_fin: string;
  tipo_cita: AppointmentType;
  motivo_consulta?: string;
  notas_recepcion?: string;
  es_primera_vez?: boolean;
}

type AvailabilityStatus = 'idle' | 'checking' | 'available' | 'unavailable';

const APPOINTMENT_TYPES: AppointmentType[] = ['Consulta', 'Seguimiento', 'Urgencia'];
const DURATIONS = [
  { label: '30 minutos', value: 30 },
  { label: '60 minutos', value: 60 },
  { label: '90 minutos', value: 90 },
  { label: '120 minutos', value: 120 },
];

const AppointmentFormModal: React.FC<AppointmentFormModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialData,
  doctors,
  initialDate,
  initialTime,
}) => {
  const [formData, setFormData] = useState<Partial<AppointmentFormData>>({
    tipo_cita: 'Consulta',
    es_primera_vez: false,
  });
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [duration, setDuration] = useState(30);
  const [availabilityStatus, setAvailabilityStatus] = useState<AvailabilityStatus>('idle');
  const [conflictingAppointments, setConflictingAppointments] = useState<Appointment[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedServiceId, setSelectedServiceId] = useState<number | null>(null);
  const [servicePrice, setServicePrice] = useState<number | null>(null);

  // Initialize form data
  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setFormData({
          id: initialData.id,
          id_paciente: initialData.id_paciente,
          id_podologo: initialData.id_podologo,
          fecha_hora_inicio: initialData.fecha_hora_inicio 
            ? format(new Date(initialData.fecha_hora_inicio), "yyyy-MM-dd'T'HH:mm")
            : '',
          fecha_hora_fin: initialData.fecha_hora_fin
            ? format(new Date(initialData.fecha_hora_fin), "yyyy-MM-dd'T'HH:mm")
            : '',
          tipo_cita: initialData.tipo_cita || 'Consulta',
          motivo_consulta: initialData.motivo_consulta || '',
          notas_recepcion: initialData.notas_recepcion || '',
          es_primera_vez: initialData.es_primera_vez || false,
        });
      } else {
        // New appointment - set defaults
        const now = new Date();
        const defaultDate = initialDate || now;
        const defaultTime = initialTime || format(setMinutes(setHours(now, 9), 0), 'HH:mm');
        const [hours, minutes] = defaultTime.split(':').map(Number);
        const startDateTime = setMinutes(setHours(defaultDate, hours), minutes);
        
        setFormData({
          fecha_hora_inicio: format(startDateTime, "yyyy-MM-dd'T'HH:mm"),
          fecha_hora_fin: format(addMinutes(startDateTime, 30), "yyyy-MM-dd'T'HH:mm"),
          tipo_cita: 'Consulta',
          es_primera_vez: false,
        });
        setDuration(30);
      }
      setErrors({});
      setAvailabilityStatus('idle');
      setConflictingAppointments([]);
    }
  }, [isOpen, initialData, initialDate, initialTime]);

  // Auto-calculate end time when start time or duration changes
  useEffect(() => {
    if (formData.fecha_hora_inicio && duration) {
      const startDate = new Date(formData.fecha_hora_inicio);
      const endDate = addMinutes(startDate, duration);
      setFormData(prev => ({
        ...prev,
        fecha_hora_fin: format(endDate, "yyyy-MM-dd'T'HH:mm"),
      }));
    }
  }, [formData.fecha_hora_inicio, duration]);

  // Check availability when relevant fields change
  useEffect(() => {
    const checkAvailability = async () => {
      if (
        formData.id_podologo &&
        formData.fecha_hora_inicio &&
        formData.fecha_hora_fin
      ) {
        setAvailabilityStatus('checking');
        setConflictingAppointments([]);

        try {
          const result = await checkDoctorAvailability({
            doctor_id: formData.id_podologo,
            start_time: new Date(formData.fecha_hora_inicio).toISOString(),
            end_time: new Date(formData.fecha_hora_fin).toISOString(),
            exclude_appointment_id: formData.id,
          });

          if (result.available) {
            setAvailabilityStatus('available');
          } else {
            setAvailabilityStatus('unavailable');
            setConflictingAppointments(result.conflicting_appointments || []);
          }
        } catch (error) {
          console.error('Error checking availability:', error);
          setAvailabilityStatus('idle');
        }
      } else {
        setAvailabilityStatus('idle');
      }
    };

    // Debounce availability check
    const timer = setTimeout(checkAvailability, 500);
    return () => clearTimeout(timer);
  }, [formData.id_podologo, formData.fecha_hora_inicio, formData.fecha_hora_fin, formData.id]);

  useEffect(() => {
    if (isOpen) {
      getServices().then(setServices);
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedServiceId !== null) {
      const found = services.find(s => s.id === selectedServiceId);
      setServicePrice(found ? found.precio : null);
    } else {
      setServicePrice(null);
    }
  }, [selectedServiceId, services]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.id_paciente) {
      newErrors.id_paciente = 'Selecciona un paciente';
    }
    if (!formData.id_podologo) {
      newErrors.id_podologo = 'Selecciona un podólogo';
    }
    if (!formData.fecha_hora_inicio) {
      newErrors.fecha_hora_inicio = 'Selecciona fecha y hora';
    } else {
      // Check if date is in the past
      const startDate = new Date(formData.fecha_hora_inicio);
      if (isBefore(startDate, new Date()) && !formData.id) {
        newErrors.fecha_hora_inicio = 'No se pueden crear citas en el pasado';
      }
    }
    if (!formData.tipo_cita) {
      newErrors.tipo_cita = 'Selecciona el tipo de cita';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    if (availabilityStatus === 'unavailable') {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSave(formData as AppointmentFormData);
      onClose();
    } catch (error) {
      console.error('Error saving appointment:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden transform transition-all scale-100 animate-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <Calendar className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                {formData.id ? 'Editar Cita' : 'Nueva Cita Médica'}
              </h3>
              <p className="text-primary-100 text-sm">
                Completa los datos de la cita
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            type="button"
            className="text-white/80 hover:text-white p-2 hover:bg-white/10 rounded-full transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto max-h-[calc(90vh-180px)]">
          {/* Patient Search */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <User className="w-4 h-4 text-primary-600" />
              Paciente <span className="text-red-500">*</span>
            </label>
            <PatientAutocomplete
              value={formData.id_paciente || null}
              onChange={(patientId, patient) => {
                setFormData(prev => ({ ...prev, id_paciente: patientId }));
                setSelectedPatient(patient);
                if (errors.id_paciente) {
                  setErrors(prev => ({ ...prev, id_paciente: '' }));
                }
              }}
              error={errors.id_paciente}
            />
          </div>

          {/* Doctor Selection */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <User className="w-4 h-4 text-primary-600" />
              Podólogo <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.id_podologo || ''}
              onChange={(e) => {
                setFormData(prev => ({ ...prev, id_podologo: e.target.value }));
                if (errors.id_podologo) {
                  setErrors(prev => ({ ...prev, id_podologo: '' }));
                }
              }}
              className={`
                w-full px-4 py-3 border-2 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-primary-500/20
                ${errors.id_podologo ? 'border-red-300 bg-red-50' : 'border-gray-200'}
              `}
            >
              <option value="">Selecciona un podólogo...</option>
              {doctors.map((doctor) => (
                <option key={doctor.id} value={doctor.id}>
                  {doctor.name}
                </option>
              ))}
            </select>
            {errors.id_podologo && (
              <p className="text-sm text-red-600">{errors.id_podologo}</p>
            )}
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <Calendar className="w-4 h-4 text-primary-600" />
                Fecha y Hora <span className="text-red-500">*</span>
              </label>
              <input
                type="datetime-local"
                value={formData.fecha_hora_inicio || ''}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, fecha_hora_inicio: e.target.value }));
                  if (errors.fecha_hora_inicio) {
                    setErrors(prev => ({ ...prev, fecha_hora_inicio: '' }));
                  }
                }}
                className={`
                  w-full px-4 py-3 border-2 rounded-lg
                  focus:outline-none focus:ring-2 focus:ring-primary-500/20
                  ${errors.fecha_hora_inicio ? 'border-red-300 bg-red-50' : 'border-gray-200'}
                `}
              />
              {errors.fecha_hora_inicio && (
                <p className="text-sm text-red-600">{errors.fecha_hora_inicio}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                <Clock className="w-4 h-4 text-primary-600" />
                Duración
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              >
                {DURATIONS.map((dur) => (
                  <option key={dur.value} value={dur.value}>
                    {dur.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Appointment Type */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <FileText className="w-4 h-4 text-primary-600" />
              Tipo de Cita <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.tipo_cita || ''}
              onChange={(e) => {
                setFormData(prev => ({ ...prev, tipo_cita: e.target.value as AppointmentType }));
                if (errors.tipo_cita) {
                  setErrors(prev => ({ ...prev, tipo_cita: '' }));
                }
              }}
              className={`
                w-full px-4 py-3 border-2 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-primary-500/20
                ${errors.tipo_cita ? 'border-red-300 bg-red-50' : 'border-gray-200'}
              `}
            >
              {APPOINTMENT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            {errors.tipo_cita && (
              <p className="text-sm text-red-600">{errors.tipo_cita}</p>
            )}
          </div>

          {/* First Time Visit */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <input
              type="checkbox"
              id="es_primera_vez"
              checked={formData.es_primera_vez || false}
              onChange={(e) => setFormData(prev => ({ ...prev, es_primera_vez: e.target.checked }))}
              className="w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500/20"
            />
            <label htmlFor="es_primera_vez" className="text-sm font-medium text-gray-700 cursor-pointer">
              Primera consulta del paciente
            </label>
          </div>

          {/* Reason for Visit */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <FileText className="w-4 h-4 text-primary-600" />
              Motivo de Consulta
            </label>
            <textarea
              value={formData.motivo_consulta || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, motivo_consulta: e.target.value }))}
              placeholder="Describe el motivo de la consulta..."
              rows={3}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 resize-none"
            />
          </div>

          {/* Reception Notes */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <FileText className="w-4 h-4 text-primary-600" />
              Notas de Recepción
            </label>
            <textarea
              value={formData.notas_recepcion || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, notas_recepcion: e.target.value }))}
              placeholder="Notas adicionales..."
              rows={2}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 resize-none"
            />
          </div>

          {/* Service Selector */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700">
              <FileText className="w-4 h-4 text-primary-600" />
              Servicio <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedServiceId ?? ''}
              onChange={e => setSelectedServiceId(Number(e.target.value))}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              required
            >
              <option value="">Selecciona un servicio...</option>
              {services.map(service => (
                <option key={service.id} value={service.id}>
                  {service.nombre} ({service.duracion_minutos} min)
                </option>
              ))}
            </select>
            {servicePrice !== null && (
              <div className="text-sm text-gray-600 mt-1">Precio: <b>${servicePrice.toFixed(2)}</b></div>
            )}
          </div>

          {/* Availability Indicator */}
          <AvailabilityIndicator
            status={availabilityStatus}
            conflictingAppointments={conflictingAppointments}
          />

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || availabilityStatus === 'unavailable' || availabilityStatus === 'checking'}
              className={`
                px-6 py-2.5 rounded-lg font-medium transition-colors
                ${isSubmitting || availabilityStatus === 'unavailable' || availabilityStatus === 'checking'
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 text-white'
                }
              `}
            >
              {isSubmitting ? 'Guardando...' : formData.id ? 'Actualizar Cita' : 'Crear Cita'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AppointmentFormModal;
