/**
 * Servicio API para Facturas
 * ===========================
 * NOTA: Funcionalidad de timbrado SAT pendiente de implementación
 */

import api from './api';
import type {
  Invoice,
  InvoiceCreate,
  InvoiceCancel,
  InvoiceListResponse,
  EstadoFactura,
} from '../types/billing';

const BASE_URL = '/api/facturas';

// ============================================================================
// FUNCIONES DE FACTURAS
// ============================================================================

/**
 * Obtiene lista de facturas con filtros
 */
export const getInvoices = async (filters?: {
  id_pago?: number;
  rfc_receptor?: string;
  estado?: EstadoFactura;
  fecha_desde?: string;
  fecha_hasta?: string;
  limit?: number;
  offset?: number;
}): Promise<InvoiceListResponse> => {
  try {
    const response = await api.get<InvoiceListResponse>(BASE_URL, {
      params: filters,
    });
    return response.data;
  } catch (error) {
    console.error('Error obteniendo facturas:', error);
    throw error;
  }
};

/**
 * Obtiene una factura por ID
 */
export const getInvoiceById = async (id: number): Promise<Invoice> => {
  try {
    const response = await api.get<Invoice>(`${BASE_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error obteniendo factura ${id}:`, error);
    throw error;
  }
};

/**
 * Solicita generación de factura para un pago
 * NOTA: Por ahora solo registra la solicitud sin timbrado SAT
 */
export const generateInvoice = async (invoice: InvoiceCreate): Promise<Invoice> => {
  try {
    const response = await api.post<Invoice>(BASE_URL, invoice);
    return response.data;
  } catch (error) {
    console.error('Error generando factura:', error);
    throw error;
  }
};

/**
 * Cancela una factura
 */
export const cancelInvoice = async (id: number, motivo: string): Promise<Invoice> => {
  try {
    const cancelData: InvoiceCancel = { motivo };
    const response = await api.put<Invoice>(`${BASE_URL}/${id}/cancelar`, cancelData);
    return response.data;
  } catch (error) {
    console.error(`Error cancelando factura ${id}:`, error);
    throw error;
  }
};

/**
 * Obtiene estado de la integración con el SAT
 */
export const getSATStatus = async (): Promise<{
  estado: string;
  mensaje: string;
  funcionalidades_pendientes: string[];
  nota: string;
}> => {
  try {
    const response = await api.get(`${BASE_URL}/sat/status`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo estado SAT:', error);
    throw error;
  }
};

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Obtiene color de badge según estado de la factura
 */
export const getEstadoFacturaColor = (estado: EstadoFactura): string => {
  switch (estado) {
    case 'Vigente':
      return 'bg-green-100 text-green-800';
    case 'Cancelada':
      return 'bg-red-100 text-red-800';
    case 'Pendiente_Timbrado':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Obtiene texto legible del estado
 */
export const getEstadoFacturaLabel = (estado: EstadoFactura): string => {
  switch (estado) {
    case 'Vigente':
      return 'Vigente';
    case 'Cancelada':
      return 'Cancelada';
    case 'Pendiente_Timbrado':
      return 'Pendiente Timbrado SAT';
    default:
      return estado;
  }
};
