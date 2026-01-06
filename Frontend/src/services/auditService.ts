/**
 * Servicio API para Auditoría
 * ============================
 */

import api from './api';
import type {
  AuditLog,
  AuditLogsListResponse,
  AuditFilters,
  UserActivity,
} from '../types/billing';

const BASE_URL = '/api/audit';

// ============================================================================
// FUNCIONES DE AUDITORÍA
// ============================================================================

/**
 * Obtiene logs de auditoría con filtros
 */
export const getAuditLogs = async (filters?: AuditFilters): Promise<AuditLogsListResponse> => {
  try {
    const response = await api.get<AuditLogsListResponse>(`${BASE_URL}/logs`, {
      params: filters,
    });
    return response.data;
  } catch (error) {
    console.error('Error obteniendo logs de auditoría:', error);
    throw error;
  }
};

/**
 * Obtiene resumen de actividad de un usuario
 */
export const getUserActivity = async (
  userId: number,
  days: number = 30
): Promise<UserActivity[]> => {
  try {
    const response = await api.get<UserActivity[]>(`${BASE_URL}/user-activity/${userId}`, {
      params: { days },
    });
    return response.data;
  } catch (error) {
    console.error(`Error obteniendo actividad de usuario ${userId}:`, error);
    throw error;
  }
};

/**
 * Obtiene lista de módulos disponibles para filtrar
 */
export const getAuditModules = async (): Promise<string[]> => {
  try {
    const response = await api.get<string[]>(`${BASE_URL}/modules`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo módulos de auditoría:', error);
    throw error;
  }
};

/**
 * Obtiene lista de acciones disponibles para filtrar
 */
export const getAuditActions = async (): Promise<string[]> => {
  try {
    const response = await api.get<string[]>(`${BASE_URL}/actions`);
    return response.data;
  } catch (error) {
    console.error('Error obteniendo acciones de auditoría:', error);
    throw error;
  }
};

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Obtiene color según el tipo de acción
 */
export const getAccionColor = (accion: string): string => {
  switch (accion.toLowerCase()) {
    case 'crear':
      return 'text-green-600';
    case 'actualizar':
      return 'text-blue-600';
    case 'eliminar':
    case 'cancelar':
      return 'text-red-600';
    case 'aprobar':
      return 'text-green-600';
    case 'rechazar':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

/**
 * Obtiene icono según el módulo
 */
export const getModuloIcon = (modulo: string): string => {
  const iconMap: Record<string, string> = {
    pagos: '💰',
    facturas: '🧾',
    gastos: '📉',
    cortes_caja: '🧮',
    pacientes: '👤',
    citas: '📅',
    usuarios: '👥',
    inventario: '📦',
    expedientes: '📋',
  };
  return iconMap[modulo.toLowerCase()] || '📄';
};

/**
 * Formatea fecha para auditoría
 */
export const formatAuditDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

/**
 * Exporta logs a CSV
 */
export const exportLogsToCSV = (logs: AuditLog[]): void => {
  const headers = ['ID', 'Usuario', 'Acción', 'Módulo', 'Descripción', 'Fecha/Hora', 'IP'];
  const rows = logs.map((log) => [
    log.id,
    log.usuario_nombre || log.usuario_id,
    log.accion,
    log.modulo,
    log.descripcion,
    formatAuditDate(log.fecha_hora),
    log.ip_address || '',
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `auditoria_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
};
