import api from './api';

// Tipos disponibles
export type TipoServicio = 'servicio' | 'tratamiento';
export type CategoriaServicio = 'general' | 'podologia' | 'estetica' | 'cirugia' | 'diagnostico';

export const TIPOS_SERVICIO: { value: TipoServicio; label: string }[] = [
  { value: 'servicio', label: 'Servicio' },
  { value: 'tratamiento', label: 'Tratamiento' },
];

export const CATEGORIAS_SERVICIO: { value: CategoriaServicio; label: string }[] = [
  { value: 'general', label: 'General' },
  { value: 'podologia', label: 'Podología' },
  { value: 'estetica', label: 'Estética' },
  { value: 'cirugia', label: 'Cirugía' },
  { value: 'diagnostico', label: 'Diagnóstico' },
];

export interface Service {
  id: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  duracion_minutos: number;
  tipo: TipoServicio;
  categoria: CategoriaServicio;
  activo: boolean;
}

export interface ServiceCreate {
  nombre: string;
  descripcion?: string;
  precio: number;
  duracion_minutos: number;
  tipo?: TipoServicio;
  categoria?: CategoriaServicio;
  activo?: boolean;
}

export interface ServiceFilters {
  tipo?: TipoServicio;
  categoria?: CategoriaServicio;
  activo?: boolean;
  orden?: 'id' | 'nombre' | 'precio' | 'duracion_minutos';
  direccion?: 'asc' | 'desc';
}

const API_URL = '/api/services';

export const getServices = async (filters?: ServiceFilters): Promise<Service[]> => {
  const params = new URLSearchParams();
  if (filters?.tipo) params.append('tipo', filters.tipo);
  if (filters?.categoria) params.append('categoria', filters.categoria);
  if (filters?.activo !== undefined) params.append('activo', String(filters.activo));
  if (filters?.orden) params.append('orden', filters.orden);
  if (filters?.direccion) params.append('direccion', filters.direccion);
  
  const queryString = params.toString();
  const { data } = await api.get(`${API_URL}${queryString ? `?${queryString}` : ''}`);
  return data;
};

export const createService = async (service: ServiceCreate): Promise<Service> => {
  const { data } = await api.post(API_URL, service);
  return data;
};

export const updateService = async (id: number, service: ServiceCreate): Promise<Service> => {
  const { data } = await api.put(`${API_URL}/${id}`, service);
  return data;
};

export const deleteService = async (id: number): Promise<void> => {
  await api.delete(`${API_URL}/${id}`);
};
