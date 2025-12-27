import { v4 as uuidv4 } from 'uuid';
import { addHours, startOfToday, setHours, setMinutes } from 'date-fns';

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

const DOCTORS: Doctor[] = [
    { id: '1', name: 'Dr. Alejandro Martínez', color: 'bg-blue-100 text-blue-700 border-blue-200', workingHours: { start: 9, end: 17 } },
    { id: '2', name: 'Dra. María González', color: 'bg-emerald-100 text-emerald-700 border-emerald-200', workingHours: { start: 10, end: 19 } },
    { id: '3', name: 'Dr. Carlos Rodríguez', color: 'bg-purple-100 text-purple-700 border-purple-200', workingHours: { start: 8, end: 16 } },
];

const PATIENTS: Patient[] = [
    { id: 'p1', name: 'Juan Pérez', phone: '555-0101', email: 'juan@example.com' },
    { id: 'p2', name: 'María López', phone: '555-0102', email: 'maria@example.com' },
    { id: 'p3', name: 'Carlos Sánchez', phone: '555-0103', email: 'carlos@example.com' },
    { id: 'p4', name: 'Ana Martínez', phone: '555-0104', email: 'ana@example.com' },
    { id: 'p5', name: 'Luis García', phone: '555-0105', email: 'luis@example.com' },
];

const today = startOfToday();

const MOCK_APPOINTMENTS: Appointment[] = [
    {
        id: uuidv4(),
        id_paciente: 'p1',
        id_podologo: '1',
        fecha_hora_inicio: setMinutes(setHours(today, 9), 0),
        fecha_hora_fin: setMinutes(setHours(today, 9), 30),
        estado: 'Confirmada',
        es_primera_vez: false,
        tipo_cita: 'Consulta',
        notas_recepcion: 'Paciente regular',
        color: '#3B82F6',
        title: 'Consulta General - Juan Pérez',
        start: setMinutes(setHours(today, 9), 0),
        end: setMinutes(setHours(today, 9), 30),
        type: 'consulta',
        patientId: 'p1',
        doctorId: '1',
        status: 'programada',
    },
    {
        id: uuidv4(),
        id_paciente: 'p2',
        id_podologo: '2',
        fecha_hora_inicio: setMinutes(setHours(today, 10), 0),
        fecha_hora_fin: setMinutes(setHours(today, 11), 0),
        estado: 'Pendiente',
        es_primera_vez: true,
        tipo_cita: 'Consulta',
        color: '#10B981',
        title: 'Primera Consulta - María López',
        start: setMinutes(setHours(today, 10), 0),
        end: setMinutes(setHours(today, 11), 0),
        type: 'quiropodia',
        patientId: 'p2',
        doctorId: '2',
        status: 'programada',
    },
    {
        id: uuidv4(),
        id_paciente: 'p3',
        id_podologo: '1',
        fecha_hora_inicio: setMinutes(setHours(today, 14), 0),
        fecha_hora_fin: addHours(setMinutes(setHours(today, 14), 0), 1),
        estado: 'Confirmada',
        es_primera_vez: false,
        tipo_cita: 'Urgencia',
        notas_recepcion: 'Dolor agudo en pie derecho',
        color: '#EF4444',
        title: 'Urgencia - Carlos Sánchez',
        start: setMinutes(setHours(today, 14), 0),
        end: addHours(setMinutes(setHours(today, 14), 0), 1),
        type: 'cirugia',
        patientId: 'p3',
        doctorId: '1',
        status: 'programada',
    },
];

export const getAppointments = (): Promise<Appointment[]> => {
    return new Promise((resolve) => {
        setTimeout(() => resolve([...MOCK_APPOINTMENTS]), 500);
    });
};

export const createAppointment = (appt: Omit<Appointment, 'id'>): Promise<Appointment> => {
    return new Promise((resolve) => {
        const newAppt = { ...appt, id: uuidv4() };
        MOCK_APPOINTMENTS.push(newAppt);
        setTimeout(() => resolve(newAppt), 500);
    });
};

export const getDoctors = () => DOCTORS;
export const getPatients = () => PATIENTS;
