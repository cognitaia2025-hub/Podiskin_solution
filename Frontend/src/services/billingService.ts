/**
 * Servicio API para Pagos y Cobros
 * =================================
 */

import api from './api';
import type {
  Payment,
  PaymentCreate,
  PaymentUpdate,
  PaymentListResponse,
  PaymentStats,
  PaymentFilters,
  EstadoPago,
  MetodoPago,
} from '../types/billing';

const BASE_URL = '/api/pagos';

// ============================================================================
// FUNCIONES DE PAGOS
// ============================================================================

/**
 * Obtiene lista de pagos con filtros
 */
export const getPayments = async (filters?: PaymentFilters): Promise<PaymentListResponse> => {
  try {
    const response = await api.get<PaymentListResponse>(BASE_URL, {
      params: filters,
    });
    return response.data;
  } catch (error) {
    console.error('Error obteniendo pagos:', error);
    throw error;
  }
};

/**
 * Obtiene un pago por ID
 */
export const getPaymentById = async (id: number): Promise<Payment> => {
  try {
    const response = await api.get<Payment>(`${BASE_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error obteniendo pago ${id}:`, error);
    throw error;
  }
};

/**
 * Crea un nuevo pago
 */
export const createPayment = async (payment: PaymentCreate): Promise<Payment> => {
  try {
    const response = await api.post<Payment>(BASE_URL, payment);
    return response.data;
  } catch (error) {
    console.error('Error creando pago:', error);
    throw error;
  }
};

/**
 * Actualiza un pago existente
 */
export const updatePayment = async (id: number, payment: PaymentUpdate): Promise<Payment> => {
  try {
    const response = await api.put<Payment>(`${BASE_URL}/${id}`, payment);
    return response.data;
  } catch (error) {
    console.error(`Error actualizando pago ${id}:`, error);
    throw error;
  }
};

/**
 * Obtiene todos los pagos de una cita
 */
export const getPaymentsByCita = async (citaId: number): Promise<Payment[]> => {
  try {
    const response = await api.get<Payment[]>(`${BASE_URL}/cita/${citaId}`);
    return response.data;
  } catch (error) {
    console.error(`Error obteniendo pagos de cita ${citaId}:`, error);
    throw error;
  }
};

/**
 * Obtiene lista de pagos pendientes o parciales
 */
export const getPendingPayments = async (): Promise<Payment[]> => {
  try {
    const response = await api.get<Payment[]>(`${BASE_URL}/pendientes/lista`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo pagos pendientes:', error);
    throw error;
  }
};

/**
 * Obtiene estadísticas de pagos
 */
export const getPaymentStats = async (
  fecha_desde?: string,
  fecha_hasta?: string
): Promise<PaymentStats> => {
  try {
    const response = await api.get<PaymentStats>(`${BASE_URL}/stats/resumen`, {
      params: { fecha_desde, fecha_hasta },
    });
    return response.data;
  } catch (error) {
    console.error('Error obteniendo estadísticas de pagos:', error);
    throw error;
  }
};

/**
 * Obtiene lista de estados de pago disponibles
 */
export const getEstadosPago = async (): Promise<EstadoPago[]> => {
  try {
    const response = await api.get<EstadoPago[]>(`${BASE_URL}/estados/lista`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo estados de pago:', error);
    throw error;
  }
};

/**
 * Obtiene lista de métodos de pago disponibles
 */
export const getMetodosPago = async (): Promise<MetodoPago[]> => {
  try {
    const response = await api.get<MetodoPago[]>(`${BASE_URL}/metodos/lista`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo métodos de pago:', error);
    throw error;
  }
};

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Obtiene color de badge según estado del pago
 */
export const getEstadoColor = (estado: EstadoPago): string => {
  switch (estado) {
    case 'Pagado':
      return 'bg-green-100 text-green-800';
    case 'Parcial':
      return 'bg-yellow-100 text-yellow-800';
    case 'Pendiente':
      return 'bg-red-100 text-red-800';
    case 'Cancelado':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Formatea monto como moneda MXN
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
  }).format(amount);
};

/**
 * Formatea fecha para mostrar
 */
export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Formatea fecha y hora
 */
export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};
