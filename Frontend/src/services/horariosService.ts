/**
 * Servicio para gestión de horarios de trabajo.
 * Conecta con el backend /api/horarios
 */

import api from './api';

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
  const params: Record<string, any> = {};
  if (idPodologo !== undefined) params.id_podologo = idPodologo;
  if (activo !== undefined) params.activo = activo;
  
  const { data } = await api.get('/api/horarios', { params });
  return data;
}

/**
 * Obtiene un horario específico por ID.
 */
export async function getHorarioById(id: number): Promise<Horario> {
  const { data } = await api.get(`/api/horarios/${id}`);
  return data;
}

/**
 * Crea un nuevo horario de trabajo.
 */
export async function createHorario(horarioData: HorarioCreate): Promise<Horario> {
  const { data } = await api.post('/api/horarios', horarioData);
  return data;
}

/**
 * Actualiza un horario existente.
 */
export async function updateHorario(id: number, horarioData: HorarioUpdate): Promise<Horario> {
  const { data } = await api.put(`/api/horarios/${id}`, horarioData);
  return data;
}

/**
 * Desactiva un horario (soft delete).
 */
export async function deleteHorario(id: number): Promise<void> {
  await api.delete(`/api/horarios/${id}`);
}
