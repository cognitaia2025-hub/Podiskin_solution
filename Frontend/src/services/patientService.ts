/**
 * Patient Service
 * 
 * HTTP service for patient CRUD operations
 */

import api from './api';

export interface Patient {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  fecha_nacimiento?: string;
  curp?: string;
  estado_civil?: string;
  ocupacion?: string;
  direccion?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PatientListResponse {
  patients: Patient[];
  total: number;
  page: number;
  per_page: number;
}

/**
 * Get all patients with pagination
 */
export const getPatients = async (
  page: number = 1,
  perPage: number = 50
): Promise<PatientListResponse> => {
  try {
    const response = await api.get('/patients', {
      params: { page, per_page: perPage },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching patients:', error);
    throw error;
  }
};

/**
 * Get a single patient by ID
 */
export const getPatientById = async (id: string): Promise<Patient> => {
  try {
    const response = await api.get(`/patients/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching patient ${id}:`, error);
    throw error;
  }
};

/**
 * Create a new patient
 */
export const createPatient = async (patient: Partial<Patient>): Promise<Patient> => {
  try {
    const response = await api.post('/patients', patient);
    return response.data;
  } catch (error) {
    console.error('Error creating patient:', error);
    throw error;
  }
};

/**
 * Update an existing patient
 */
export const updatePatient = async (
  id: string,
  patient: Partial<Patient>
): Promise<Patient> => {
  try {
    const response = await api.put(`/patients/${id}`, patient);
    return response.data;
  } catch (error) {
    console.error(`Error updating patient ${id}:`, error);
    throw error;
  }
};

/**
 * Delete a patient
 */
export const deletePatient = async (id: string): Promise<void> => {
  try {
    await api.delete(`/patients/${id}`);
  } catch (error) {
    console.error(`Error deleting patient ${id}:`, error);
    throw error;
  }
};

/**
 * Search patients by name, phone, or email
 */
export const searchPatients = async (query: string): Promise<Patient[]> => {
  try {
    const response = await api.get('/patients/search', {
      params: { q: query },
    });
    return response.data;
  } catch (error) {
    console.error('Error searching patients:', error);
    throw error;
  }
};
