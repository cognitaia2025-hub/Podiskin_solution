import axios from 'axios';

export interface Service {
  id: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  duracion_minutos: number;
  activo: boolean;
}

export interface ServiceCreate {
  nombre: string;
  descripcion?: string;
  precio: number;
  duracion_minutos: number;
  activo?: boolean;
}

const API_URL = '/api/services';

export const getServices = async (): Promise<Service[]> => {
  const { data } = await axios.get(API_URL);
  return data;
};

export const createService = async (service: ServiceCreate): Promise<Service> => {
  const { data } = await axios.post(API_URL, service);
  return data;
};

export const updateService = async (id: number, service: ServiceCreate): Promise<Service> => {
  const { data } = await axios.put(`${API_URL}/${id}`, service);
  return data;
};

export const deleteService = async (id: number): Promise<void> => {
  await axios.delete(`${API_URL}/${id}`);
};
