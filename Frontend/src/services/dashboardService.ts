/**
 * Dashboard Service
 * 
 * Service for fetching dashboard statistics and metrics.
 * NOTE: Backend endpoints need to be implemented at /stats/*
 */

import api from './api';

export interface DashboardStats {
  // Métricas generales
  total_patients: number;
  active_patients: number;
  new_patients_this_month: number;
  
  // Citas
  total_appointments_today: number;
  total_appointments_week: number;
  total_appointments_month: number;
  appointments_by_status: {
    pendiente: number;
    confirmada: number;
    completada: number;
    cancelada: number;
    no_asistio: number;
  };
  
  // Ingresos
  revenue_today: number;
  revenue_week: number;
  revenue_month: number;
  revenue_year: number;
  
  // Tratamientos más comunes
  top_treatments: Array<{
    nombre: string;
    cantidad: number;
  }>;
  
  // Ocupación de agenda
  ocupacion_porcentaje: number;
  
  // Próximas citas
  upcoming_appointments: number;
}

export interface AppointmentTrend {
  fecha: string;
  cantidad: number;
  completadas: number;
  canceladas: number;
}

export interface RevenueTrend {
  mes: string;
  ingresos: number;
}

/**
 * Obtener estadísticas generales del dashboard
 */
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/api/stats/dashboard');
  return response.data;
};

/**
 * Obtener tendencia de citas (últimos N días)
 */
export const getAppointmentTrend = async (days: number = 30): Promise<AppointmentTrend[]> => {
  const response = await api.get(`/api/stats/appointments-trend?days=${days}`);
  return response.data;
};

/**
 * Obtener tendencia de ingresos (último año)
 */
export const getRevenueTrend = async (): Promise<RevenueTrend[]> => {
  const response = await api.get('/api/stats/revenue-trend');
  return response.data;
};

/**
 * Mock data generator for development (remove when backend is ready)
 */
export const getMockDashboardStats = (): DashboardStats => {
  return {
    total_patients: 248,
    active_patients: 186,
    new_patients_this_month: 23,
    total_appointments_today: 12,
    total_appointments_week: 67,
    total_appointments_month: 284,
    appointments_by_status: {
      pendiente: 45,
      confirmada: 38,
      completada: 156,
      cancelada: 32,
      no_asistio: 13,
    },
    revenue_today: 3250,
    revenue_week: 18400,
    revenue_month: 67500,
    revenue_year: 780000,
    top_treatments: [
      { nombre: 'Quiropedia Básica', cantidad: 89 },
      { nombre: 'Tratamiento de Uñas Encarnadas', cantidad: 67 },
      { nombre: 'Plantillas Ortopédicas', cantidad: 45 },
      { nombre: 'Callos y Durezas', cantidad: 38 },
      { nombre: 'Pie Diabético', cantidad: 28 },
    ],
    ocupacion_porcentaje: 87,
    upcoming_appointments: 156,
  };
};

export const getMockAppointmentTrend = (): AppointmentTrend[] => {
  const data: AppointmentTrend[] = [];
  const today = new Date();
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    const cantidad = Math.floor(Math.random() * 15) + 5;
    const completadas = Math.floor(cantidad * (0.7 + Math.random() * 0.2));
    const canceladas = Math.floor((cantidad - completadas) * 0.3);
    
    data.push({
      fecha: date.toISOString().split('T')[0],
      cantidad,
      completadas,
      canceladas,
    });
  }
  
  return data;
};

export const getMockRevenueTrend = (): RevenueTrend[] => {
  const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  const data: RevenueTrend[] = [];
  
  const currentMonth = new Date().getMonth();
  
  for (let i = 0; i <= currentMonth; i++) {
    data.push({
      mes: meses[i],
      ingresos: Math.floor(Math.random() * 30000) + 50000,
    });
  }
  
  return data;
};
