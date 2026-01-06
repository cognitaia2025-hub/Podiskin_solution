/**
 * Tipos TypeScript para el módulo de Cobros y Facturación
 * ========================================================
 */

// ============================================================================
// PAGOS
// ============================================================================

export type EstadoPago = 'Pagado' | 'Parcial' | 'Pendiente' | 'Cancelado';

export type MetodoPago =
  | 'Efectivo'
  | 'Tarjeta_Debito'
  | 'Tarjeta_Credito'
  | 'Transferencia'
  | 'Cheque'
  | 'Otro';

export interface Payment {
  id: number;
  id_cita: number;
  fecha_pago: string;
  monto_total: number;
  monto_pagado: number;
  saldo_pendiente: number;
  metodo_pago: MetodoPago;
  referencia_pago?: string;
  factura_solicitada: boolean;
  factura_emitida: boolean;
  rfc_factura?: string;
  folio_factura?: string;
  estado_pago: EstadoPago;
  recibo_por?: number;
  recibo_por_nombre?: string;
  notas?: string;
  fecha_registro: string;

  // Información adicional de la cita
  paciente_id?: number;
  paciente_nombre?: string;
  podologo_id?: number;
  podologo_nombre?: string;
  fecha_cita?: string;
}

export interface PaymentCreate {
  id_cita: number;
  fecha_pago?: string;
  monto_total: number;
  monto_pagado: number;
  metodo_pago: MetodoPago;
  referencia_pago?: string;
  factura_solicitada?: boolean;
  rfc_factura?: string;
  estado_pago?: EstadoPago;
  recibo_por?: number;
  notas?: string;
}

export interface PaymentUpdate {
  monto_pagado?: number;
  metodo_pago?: MetodoPago;
  referencia_pago?: string;
  factura_solicitada?: boolean;
  factura_emitida?: boolean;
  rfc_factura?: string;
  folio_factura?: string;
  estado_pago?: EstadoPago;
  notas?: string;
}

export interface PaymentListResponse {
  pagos: Payment[];
  total: number;
  limit: number;
  offset: number;
}

export interface PaymentStats {
  total_cobrado: number;
  total_pendiente: number;
  total_parcial: number;
  promedio_por_pago: number;
  total_pagos: number;
  pagos_completos: number;
  pagos_parciales: number;
  pagos_pendientes: number;

  // Por método de pago
  efectivo: number;
  tarjeta_debito: number;
  tarjeta_credito: number;
  transferencia: number;
  otros: number;

  // Facturas
  facturas_solicitadas: number;
  facturas_emitidas: number;
}

export interface PaymentFilters {
  id_cita?: number;
  id_paciente?: number;
  estado_pago?: EstadoPago;
  metodo_pago?: MetodoPago;
  fecha_desde?: string;
  fecha_hasta?: string;
  factura_solicitada?: boolean;
  factura_emitida?: boolean;
  limit?: number;
  offset?: number;
}

// ============================================================================
// FACTURAS
// ============================================================================

export type EstadoFactura = 'Vigente' | 'Cancelada' | 'Pendiente_Timbrado';

export interface Invoice {
  id: number;
  id_pago: number;
  folio_fiscal: string;
  serie?: string;
  folio?: number;
  rfc_emisor: string;
  rfc_receptor: string;
  nombre_receptor?: string;
  uso_cfdi: string;
  metodo_pago: string;
  forma_pago: string;
  subtotal: number;
  iva: number;
  total: number;
  fecha_emision: string;
  fecha_timbrado?: string;
  uuid_sat?: string;
  estado_factura: EstadoFactura;
  xml_url?: string;
  pdf_url?: string;
  generado_por?: number;
  generado_por_nombre?: string;
  notas?: string;
  fecha_registro: string;

  // Información del pago asociado
  monto_pagado?: number;
  metodo_pago_original?: string;
}

export interface InvoiceCreate {
  id_pago: number;
  rfc_receptor: string;
  nombre_receptor: string;
  uso_cfdi?: string;
}

export interface InvoiceCancel {
  motivo: string;
}

export interface InvoiceListResponse {
  facturas: Invoice[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// AUDITORÍA
// ============================================================================

export interface AuditLog {
  id: number;
  usuario_id: number;
  usuario_nombre?: string;
  accion: string;
  modulo: string;
  descripcion: string;
  datos_anteriores?: Record<string, any>;
  datos_nuevos?: Record<string, any>;
  ip_address?: string;
  fecha_hora: string;
}

export interface AuditLogsListResponse {
  logs: AuditLog[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditFilters {
  usuario_id?: number;
  modulo?: string;
  accion?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  limit?: number;
  offset?: number;
}

export interface UserActivity {
  modulo: string;
  accion: string;
  cantidad: number;
}

// ============================================================================
// PERMISOS
// ============================================================================

export interface Permission {
  read: boolean;
  write: boolean;
}

export interface UserPermissions {
  calendario?: Permission;
  pacientes?: Permission;
  cobros?: Permission;
  expedientes?: Permission;
  inventario?: Permission;
  gastos?: Permission;
  cortes_caja?: Permission;
  administracion?: Permission;
}

export interface PermissionTemplate {
  name: string;
  label: string;
  permissions: UserPermissions;
}

export const PERMISSION_TEMPLATES: PermissionTemplate[] = [
  {
    name: 'admin',
    label: 'Administrador',
    permissions: {
      calendario: { read: true, write: true },
      pacientes: { read: true, write: true },
      cobros: { read: true, write: true },
      expedientes: { read: true, write: true },
      inventario: { read: true, write: true },
      gastos: { read: true, write: true },
      cortes_caja: { read: true, write: true },
      administracion: { read: true, write: true },
    },
  },
  {
    name: 'podologo',
    label: 'Podólogo',
    permissions: {
      calendario: { read: true, write: false },
      pacientes: { read: true, write: true },
      cobros: { read: true, write: false },
      expedientes: { read: true, write: true },
      inventario: { read: true, write: false },
      gastos: { read: false, write: false },
      cortes_caja: { read: false, write: false },
      administracion: { read: false, write: false },
    },
  },
  {
    name: 'recepcionista',
    label: 'Recepcionista',
    permissions: {
      calendario: { read: true, write: true },
      pacientes: { read: true, write: true },
      cobros: { read: true, write: true },
      expedientes: { read: true, write: false },
      inventario: { read: true, write: false },
      gastos: { read: false, write: false },
      cortes_caja: { read: true, write: true },
      administracion: { read: false, write: false },
    },
  },
];

export const PERMISSION_MODULES = [
  { key: 'calendario', label: 'Calendario' },
  { key: 'pacientes', label: 'Pacientes' },
  { key: 'cobros', label: 'Cobros' },
  { key: 'expedientes', label: 'Expedientes Médicos' },
  { key: 'inventario', label: 'Inventario' },
  { key: 'gastos', label: 'Gastos' },
  { key: 'cortes_caja', label: 'Cortes de Caja' },
  { key: 'administracion', label: 'Administración' },
];
