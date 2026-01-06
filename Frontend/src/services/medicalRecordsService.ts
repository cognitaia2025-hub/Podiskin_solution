/**
 * Medical Records Service
 * 
 * Service for managing patient medical records and appointments
 */

import api from './api';

// ============================================================================
// TYPES
// ============================================================================

export interface Patient {
  id: number;
  nombre_completo: string;
  primer_nombre: string;
  segundo_nombre?: string;
  primer_apellido: string;
  segundo_apellido?: string;
  telefono: string;
  email?: string;
  fecha_nacimiento: string;
  edad: number;
  ultima_visita?: string;
  total_consultas: number;
  tiene_alergias: boolean;
  diagnostico_reciente?: string;
  activo: boolean;
}

export interface UpcomingAppointment {
  id: number;
  paciente_id: number;
  paciente_nombre: string;
  telefono: string;
  fecha_hora: string;
  motivo_consulta?: string;
  alergias_importantes?: string[];
  ultima_visita?: string;
  tipo_cita: string;
}

export interface MedicalRecord {
  // Identificación
  id: number;
  paciente_id: number;
  paciente: Patient;
  
  // Alergias
  alergias: Allergy[];
  
  // Antecedentes
  antecedentes_medicos?: string;
  antecedentes_familiares?: string;
  
  // Estilo de vida
  ocupacion?: string;
  actividad_fisica?: string;
  tabaquismo?: boolean;
  alcoholismo?: boolean;
  tipo_calzado?: string;
  
  // Historia ginecológica (solo mujeres)
  historia_ginecologica?: {
    menarca?: number;
    menopausia?: boolean;
    embarazos?: number;
    partos?: number;
    cesareas?: number;
  };
  
  // Consultas
  consultas: Consultation[];
  
  // Metadata
  creado_por: number;
  fecha_registro: string;
  ultima_actualizacion?: string;
}

export interface Allergy {
  id: number;
  nombre: string;
  tipo: string;
  gravedad: 'leve' | 'moderada' | 'grave';
  reaccion?: string;
}

export interface Consultation {
  id: number;
  fecha_hora: string;
  motivo_consulta: string;
  signos_vitales: VitalSigns;
  exploracion_fisica?: string;
  diagnosticos: Diagnosis[];
  tratamientos: Treatment[];
  plan_tratamiento?: string;
  notas_medicas?: string;
  atendido_por: number;
  atendido_por_nombre: string;
}

export interface VitalSigns {
  peso?: number;
  altura?: number;
  presion_arterial?: string;
  frecuencia_cardiaca?: number;
  temperatura?: number;
  saturacion_oxigeno?: number;
}

export interface Diagnosis {
  id: number;
  codigo_cie10: string;
  descripcion: string;
  tipo: 'principal' | 'secundario';
  fecha_diagnostico: string;
}

export interface Treatment {
  id: number;
  servicio_nombre: string;
  descripcion?: string;
  medicamentos?: string;
  indicaciones?: string;
  duracion_estimada?: string;
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Buscar pacientes (fuzzy search)
 * Busca por ID, teléfono, o nombre (tolerante a errores de tipeo)
 */
export const searchPatients = async (query: string): Promise<Patient[]> => {
  try {
    const response = await api.get('/api/medical-records/search', {
      params: { q: query }
    });
    return response.data;
  } catch (error) {
    console.error('Error searching patients:', error);
    return [];
  }
};

/**
 * Obtener pacientes con citas próximas (hoy y próximos días)
 */
export const getUpcomingAppointments = async (limit: number = 3): Promise<UpcomingAppointment[]> => {
  try {
    const response = await api.get('/api/medical-records/upcoming-appointments', {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching upcoming appointments:', error);
    return [];
  }
};

/**
 * Obtener todos los pacientes (para grid)
 */
export const getAllPatients = async (): Promise<Patient[]> => {
  try {
    const response = await api.get('/api/medical-records/patients');
    return response.data;
  } catch (error) {
    console.error('Error fetching patients:', error);
    return [];
  }
};

/**
 * Obtener expediente médico completo de un paciente
 */
export const getMedicalRecord = async (patientId: number): Promise<MedicalRecord | null> => {
  try {
    const response = await api.get(`/api/medical-records/patients/${patientId}/record`);
    return response.data;
  } catch (error) {
    console.error('Error fetching medical record:', error);
    return null;
  }
};

/**
 * Actualizar sección del expediente médico
 */
export const updateMedicalRecordSection = async (
  patientId: number,
  section: string,
  data: any
): Promise<boolean> => {
  try {
    await api.patch(`/api/medical-records/patients/${patientId}/record/${section}`, data);
    return true;
  } catch (error) {
    console.error('Error updating medical record section:', error);
    return false;
  }
};

/**
 * Crear nueva consulta
 */
export const createConsultation = async (
  patientId: number,
  consultation: Partial<Consultation>
): Promise<Consultation | null> => {
  try {
    const response = await api.post(`/api/medical-records/patients/${patientId}/consultations`, consultation);
    return response.data;
  } catch (error) {
    console.error('Error creating consultation:', error);
    return null;
  }
};

/**
 * Finalizar consulta
 */
export const finalizeConsultation = async (
  consultationId: number
): Promise<boolean> => {
  try {
    await api.post(`/api/medical-records/consultations/${consultationId}/finalize`);
    return true;
  } catch (error) {
    console.error('Error finalizing consultation:', error);
    return false;
  }
};
