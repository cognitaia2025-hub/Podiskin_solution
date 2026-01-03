// Types for appointments, doctors, and patients

export type AppointmentStatus = 'Pendiente' | 'Confirmada' | 'En_Curso' | 'Completada' | 'Cancelada' | 'No_Asistio';
export type AppointmentType = 'Consulta' | 'Seguimiento' | 'Urgencia';
export type ReminderUnit = 'minutos' | 'horas' | 'días';
export type RecurrenceFrequency = 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY';

export interface Reminder {
    tiempo: number;
    unidad: ReminderUnit;
}

export interface RecurrenceRule {
    frequency: RecurrenceFrequency;
    interval?: number;
    count?: number;
    until?: Date;
    byweekday?: number[];
}

export interface Patient {
    id: string;
    name: string;
    phone?: string;
    email?: string;
}

export interface Doctor {
    id: string;
    name: string;
    color: string;
    workingHours?: { start: number; end: number }; // hour 0-23
}

export interface Appointment {
    id: string;
    id_paciente: string;
    id_podologo: string;
    fecha_hora_inicio: Date;
    fecha_hora_fin: Date;
    estado: AppointmentStatus;
    es_primera_vez: boolean;
    tipo_cita: AppointmentType;
    notas_recepcion?: string;
    creado_por?: string;
    color?: string; // Hex color code
    recordatorios?: Reminder[];
    es_recurrente?: boolean;
    regla_recurrencia?: RecurrenceRule;
    fecha_fin_recurrencia?: Date;
    serie_id?: string; // ID for recurring series
    // Legacy/display fields
    title?: string;
    start: Date;
    end: Date;
    type?: string;
    patientId?: string;
    doctorId?: string;
    notes?: string;
    status?: string;
}
