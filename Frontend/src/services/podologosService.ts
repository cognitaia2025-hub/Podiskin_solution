/**
 * Servicio de API para Gestión de Podólogos
 * ==========================================
 * Maneja llamadas a endpoints de pacientes por podólogo
 */

import axios from 'axios';
import { API_BASE_URL } from '../config/api';

const API_URL = API_BASE_URL;

export interface PatientWithInterino {
  paciente_id: number;
  nombre_completo: string;
  telefono: string | null;
  ultimo_tratamiento: string | null;
  fecha_ultimo_tratamiento: string | null;
  tiene_interino: boolean;
  podologo_interino_id: number | null;
  podologo_interino_nombre: string | null;
}

export interface AvailablePodologo {
  id: number;
  nombre_completo: string;
  rol: string;
}

export interface AssignInterinoRequest {
  paciente_id: number;
  podologo_interino_id: number | null;
  fecha_fin?: string;
  motivo?: string;
}

/**
 * Obtiene los pacientes asignados a un podólogo
 */
export const getPodologoPatients = async (
  podologoId: number
): Promise<PatientWithInterino[]> => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(
      `${API_URL}/podologos/${podologoId}/patients`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error obteniendo pacientes del podólogo:', error);
    throw error;
  }
};

/**
 * Obtiene lista de podólogos disponibles para asignación
 */
export const getAvailablePodologos = async (
  excludePodologoId?: number
): Promise<AvailablePodologo[]> => {
  try {
    const token = localStorage.getItem('token');
    const params = excludePodologoId
      ? { exclude_podologo_id: excludePodologoId }
      : {};
    
    const response = await axios.get(
      `${API_URL}/podologos/available`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params,
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error obteniendo podólogos disponibles:', error);
    throw error;
  }
};

/**
 * Asigna un podólogo interino a un paciente
 */
export const assignInterinoToPaciente = async (
  podologoId: number,
  assignment: AssignInterinoRequest
): Promise<void> => {
  try {
    const token = localStorage.getItem('token');
    await axios.post(
      `${API_URL}/podologos/${podologoId}/assign-interino`,
      assignment,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (error) {
    console.error('Error asignando podólogo interino:', error);
    throw error;
  }
};
