/**
 * Servicio para gestión de horarios de trabajo.
 * Conecta con el backend /api/horarios
 */

import { API_BASE_URL } from './api';

export interface Horario {
  id: number;
  id_podologo: number;
  nombre_podologo: string;
  dia_semana: number;
  dia_semana_nombre: string;
  hora_inicio: string;
  hora_fin: string;
  duracion_cita_minutos: number;
  tiempo_buffer_minutos: number;
  max_citas_simultaneas: number;
  activo: boolean;
  fecha_inicio_vigencia?: string;
  fecha_fin_vigencia?: string;
}

export interface HorarioCreate {
  id_podologo: number;
  dia_semana: number;
  hora_inicio: string; // "HH:MM:SS"
  hora_fin: string;
  duracion_cita_minutos?: number;
  tiempo_buffer_minutos?: number;
  max_citas_simultaneas?: number;
  fecha_inicio_vigencia?: string;
  fecha_fin_vigencia?: string;
  activo?: boolean;
}

export interface HorarioUpdate {
  hora_inicio?: string;
  hora_fin?: string;
  duracion_cita_minutos?: number;
  tiempo_buffer_minutos?: number;
  max_citas_simultaneas?: number;
  fecha_fin_vigencia?: string;
  activo?: boolean;
}

/**
 * Obtiene todos los horarios (con filtros opcionales).
 */
export async function getHorarios(
  idPodologo?: number,
  activo?: boolean
): Promise<Horario[]> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const params = new URLSearchParams();
  if (idPodologo !== undefined) params.append('id_podologo', idPodologo.toString());
  if (activo !== undefined) params.append('activo', activo.toString());

  const url = `${API_BASE_URL}/horarios${params.toString() ? '?' + params.toString() : ''}`;

  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Error al obtener horarios: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Obtiene un horario específico por ID.
 */
export async function getHorarioById(id: number): Promise<Horario> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/horarios/${id}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Error al obtener horario: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Crea un nuevo horario de trabajo.
 */
export async function createHorario(data: HorarioCreate): Promise<Horario> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/horarios`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al crear horario');
  }

  return response.json();
}

/**
 * Actualiza un horario existente.
 */
export async function updateHorario(id: number, data: HorarioUpdate): Promise<Horario> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/horarios/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al actualizar horario');
  }

  return response.json();
}

/**
 * Desactiva un horario (soft delete).
 */
export async function deleteHorario(id: number): Promise<void> {
  const token = localStorage.getItem('access_token');
  if (!token) throw new Error('No hay token de autenticación');

  const response = await fetch(`${API_BASE_URL}/horarios/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al eliminar horario');
  }
}
