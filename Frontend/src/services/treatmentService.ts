/**
 * Treatment Service
 * 
 * HTTP service for medical treatments, vital signs, and diagnostics
 */

import api from './api';

export interface VitalSigns {
  id?: string;
  id_paciente: string;
  id_expediente?: string;
  fecha_registro: string;
  presion_arterial_sistolica?: number;
  presion_arterial_diastolica?: number;
  frecuencia_cardiaca?: number;
  frecuencia_respiratoria?: number;
  temperatura?: number;
  saturacion_oxigeno?: number;
  peso?: number;
  talla?: number;
  imc?: number;
  glucosa?: number;
}

export interface Diagnosis {
  id?: string;
  id_expediente: string;
  codigo_cie10: string;
  descripcion: string;
  tipo: 'Principal' | 'Secundario' | 'Presuntivo';
  fecha_diagnostico: string;
  notas?: string;
}

export interface Treatment {
  id?: string;
  id_expediente: string;
  id_diagnostico?: string;
  tipo_tratamiento: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_fin?: string;
  frecuencia?: string;
  dosis?: string;
  via_administracion?: string;
  indicaciones?: string;
  observaciones?: string;
  estado: 'Activo' | 'Completado' | 'Suspendido';
}

export interface MedicalProcedure {
  id?: string;
  id_expediente: string;
  nombre_procedimiento: string;
  descripcion?: string;
  fecha_realizacion: string;
  duracion_minutos?: number;
  personal_responsable?: string;
  observaciones?: string;
  complicaciones?: string;
}

/**
 * Vital Signs
 */
export const getVitalSigns = async (patientId: string): Promise<VitalSigns[]> => {
  try {
    const response = await api.get(`/patients/${patientId}/vital-signs`);
    return response.data;
  } catch (error) {
    console.error('Error fetching vital signs:', error);
    throw error;
  }
};

export const createVitalSigns = async (vitalSigns: VitalSigns): Promise<VitalSigns> => {
  try {
    const response = await api.post('/vital-signs', vitalSigns);
    return response.data;
  } catch (error) {
    console.error('Error creating vital signs:', error);
    throw error;
  }
};

/**
 * Diagnoses
 */
export const getDiagnoses = async (expedienteId: string): Promise<Diagnosis[]> => {
  try {
    const response = await api.get(`/medical-records/${expedienteId}/diagnoses`);
    return response.data;
  } catch (error) {
    console.error('Error fetching diagnoses:', error);
    throw error;
  }
};

export const createDiagnosis = async (diagnosis: Diagnosis): Promise<Diagnosis> => {
  try {
    const response = await api.post('/diagnoses', diagnosis);
    return response.data;
  } catch (error) {
    console.error('Error creating diagnosis:', error);
    throw error;
  }
};

/**
 * Treatments
 */
export const getTreatments = async (expedienteId: string): Promise<Treatment[]> => {
  try {
    const response = await api.get(`/medical-records/${expedienteId}/treatments`);
    return response.data;
  } catch (error) {
    console.error('Error fetching treatments:', error);
    throw error;
  }
};

export const createTreatment = async (treatment: Treatment): Promise<Treatment> => {
  try {
    const response = await api.post('/treatments', treatment);
    return response.data;
  } catch (error) {
    console.error('Error creating treatment:', error);
    throw error;
  }
};

export const updateTreatment = async (
  id: string,
  treatment: Partial<Treatment>
): Promise<Treatment> => {
  try {
    const response = await api.put(`/treatments/${id}`, treatment);
    return response.data;
  } catch (error) {
    console.error(`Error updating treatment ${id}:`, error);
    throw error;
  }
};

/**
 * Medical Procedures
 */
export const getMedicalProcedures = async (
  expedienteId: string
): Promise<MedicalProcedure[]> => {
  try {
    const response = await api.get(`/medical-records/${expedienteId}/procedures`);
    return response.data;
  } catch (error) {
    console.error('Error fetching procedures:', error);
    throw error;
  }
};

export const createMedicalProcedure = async (
  procedure: MedicalProcedure
): Promise<MedicalProcedure> => {
  try {
    const response = await api.post('/procedures', procedure);
    return response.data;
  } catch (error) {
    console.error('Error creating procedure:', error);
    throw error;
  }
};

/**
 * Search CIE-10 codes
 */
export const searchCIE10 = async (query: string): Promise<{ codigo: string; descripcion: string }[]> => {
  try {
    const response = await api.get('/cie10/search', {
      params: { q: query },
    });
    return response.data;
  } catch (error) {
    console.error('Error searching CIE-10:', error);
    throw error;
  }
};
