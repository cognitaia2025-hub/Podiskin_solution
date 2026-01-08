/**
 * Servicio para generación y descarga de reportes ejecutivos
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ReporteGastosMensuales {
  periodo: string;
  fecha_inicio: string;
  fecha_fin: string;
  total_gastos: number;
  total_gastos_mes_anterior: number;
  variacion_porcentual: number;
  gastos_por_categoria: Array<{
    categoria: string;
    total: number;
    cantidad: number;
    porcentaje: number;
    variacion_mes_anterior: number;
  }>;
  top_10_gastos: Array<{
    concepto: string;
    monto: number;
    fecha: string;
    metodo_pago: string;
    categoria: string;
  }>;
  tendencia_6_meses: Array<{
    periodo: string;
    total: number;
  }>;
  productos_comprados: Array<{
    producto: string;
    cantidad: number;
    precio_unitario: number;
    subtotal: number;
    concepto_gasto: string;
    fecha: string;
  }>;
}

export interface ReporteInventario {
  fecha_generacion: string;
  valor_total_inventario: number;
  numero_productos: number;
  productos_criticos: Array<{
    producto_id: number;
    codigo: string;
    nombre: string;
    categoria: string;
    stock_actual: number;
    stock_minimo: number;
    stock_maximo: number;
    unidad_medida: string;
    deficit: number;
    valor_stock: number;
  }>;
  productos_exceso: Array<{
    producto_id: number;
    codigo: string;
    nombre: string;
    stock_actual: number;
    stock_maximo: number;
    exceso: number;
    unidad_medida: string;
  }>;
  productos_sin_movimiento: Array<{
    producto_id: number;
    codigo: string;
    nombre: string;
    stock_actual: number;
    unidad_medida: string;
    ultimo_movimiento: string;
  }>;
  rotacion_promedio_dias: number;
  num_criticos: number;
  num_exceso: number;
  num_sin_movimiento: number;
}

export type FormatoReporte = 'json' | 'csv' | 'excel' | 'pdf';
export type TipoReporte = 'gastos-mensuales' | 'inventario-estado';

/**
 * Descarga un reporte de gastos mensuales
 */
export async function descargarReporteGastos(
  mes: number,
  anio: number,
  formato: FormatoReporte,
  token: string
): Promise<ReporteGastosMensuales | Blob> {
  const params = new URLSearchParams({
    mes: mes.toString(),
    anio: anio.toString(),
    formato,
  });

  const response = await fetch(
    `${API_URL}/api/reportes/gastos-mensuales?${params}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al generar reporte de gastos');
  }

  if (formato === 'json') {
    return await response.json();
  } else {
    return await response.blob();
  }
}

/**
 * Descarga un reporte de estado del inventario
 */
export async function descargarReporteInventario(
  formato: FormatoReporte,
  incluirCriticos: boolean,
  incluirObsoletos: boolean,
  token: string
): Promise<ReporteInventario | Blob> {
  const params = new URLSearchParams({
    formato,
    incluir_criticos: incluirCriticos.toString(),
    incluir_obsoletos: incluirObsoletos.toString(),
  });

  const response = await fetch(
    `${API_URL}/api/reportes/inventario-estado?${params}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al generar reporte de inventario');
  }

  if (formato === 'json') {
    return await response.json();
  } else {
    return await response.blob();
  }
}

/**
 * Helper para trigger automático de descarga de archivos
 */
export function triggerFileDownload(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

/**
 * Genera el nombre del archivo según tipo y formato
 */
export function generarNombreArchivo(
  tipo: TipoReporte,
  formato: FormatoReporte,
  mes?: number,
  anio?: number
): string {
  const fecha = new Date();
  const fechaStr = fecha.toISOString().split('T')[0];
  
  if (tipo === 'gastos-mensuales' && mes && anio) {
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    const periodo = `${meses[mes - 1]}_${anio}`;
    const extension = formato === 'excel' ? 'xlsx' : formato === 'pdf' ? 'pdf' : formato;
    return `reporte_gastos_${periodo}.${extension}`;
  }
  
  const extension = formato === 'excel' ? 'xlsx' : formato === 'pdf' ? 'pdf' : formato;
  return `reporte_inventario_${fechaStr}.${extension}`;
}
