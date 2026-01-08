import { useState } from 'react';
import {
  descargarReporteGastos,
  descargarReporteInventario,
  triggerFileDownload,
  generarNombreArchivo,
} from '../../services/reportesService';
import type { FormatoReporte, TipoReporte } from '../../services/reportesService';

interface ReportGeneratorComponentProps {
  className?: string;
}

export default function ReportGeneratorComponent({
  className = '',
}: ReportGeneratorComponentProps) {
  const [tipoReporte, setTipoReporte] = useState<TipoReporte>('gastos-mensuales');
  const [formato, setFormato] = useState<FormatoReporte>('excel');
  const [mes, setMes] = useState<number>(new Date().getMonth() + 1);
  const [anio, setAnio] = useState<number>(new Date().getFullYear());
  const [incluirCriticos, setIncluirCriticos] = useState<boolean>(true);
  const [incluirObsoletos, setIncluirObsoletos] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const meses = [
    { value: 1, label: 'Enero' },
    { value: 2, label: 'Febrero' },
    { value: 3, label: 'Marzo' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Mayo' },
    { value: 6, label: 'Junio' },
    { value: 7, label: 'Julio' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Septiembre' },
    { value: 10, label: 'Octubre' },
    { value: 11, label: 'Noviembre' },
    { value: 12, label: 'Diciembre' },
  ];

  const aniosDisponibles = Array.from(
    { length: 10 },
    (_, i) => new Date().getFullYear() - i
  );

  const handleGenerarReporte = async () => {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    
    if (!token) {
      setError('No hay sesión activa');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let resultado: any;
      let filename: string;

      if (tipoReporte === 'gastos-mensuales') {
        resultado = await descargarReporteGastos(mes, anio, formato, token);
        filename = generarNombreArchivo(tipoReporte, formato, mes, anio);
      } else {
        resultado = await descargarReporteInventario(
          formato,
          incluirCriticos,
          incluirObsoletos,
          token
        );
        filename = generarNombreArchivo(tipoReporte, formato);
      }

      // Si el resultado es un Blob (CSV o Excel), descargarlo automáticamente
      if (resultado instanceof Blob) {
        triggerFileDownload(resultado, filename);
        setSuccess(`Reporte descargado: ${filename}`);
      } else {
        // Si es JSON, mostrarlo o descargarlo
        const jsonBlob = new Blob([JSON.stringify(resultado, null, 2)], {
          type: 'application/json',
        });
        triggerFileDownload(jsonBlob, filename);
        setSuccess('Reporte generado en JSON');
      }
    } catch (err: any) {
      setError(err.message || 'Error al generar el reporte');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        <svg
          className="w-6 h-6 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        Generador de Reportes
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tipo de Reporte */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Reporte
          </label>
          <select
            value={tipoReporte}
            onChange={(e) => setTipoReporte(e.target.value as TipoReporte)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="gastos-mensuales">Gastos Mensuales</option>
            <option value="inventario-estado">Estado del Inventario</option>
          </select>
        </div>

        {/* Formato */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Formato de Exportación
          </label>
          <select
            value={formato}
            onChange={(e) => setFormato(e.target.value as FormatoReporte)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="excel">Excel (.xlsx)</option>
            <option value="pdf">PDF (.pdf)</option>
            <option value="csv">CSV (.csv)</option>
            <option value="json">JSON (.json)</option>
          </select>
        </div>

        {/* Parámetros específicos para Gastos Mensuales */}
        {tipoReporte === 'gastos-mensuales' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mes
              </label>
              <select
                value={mes}
                onChange={(e) => setMes(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {meses.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Año
              </label>
              <select
                value={anio}
                onChange={(e) => setAnio(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {aniosDisponibles.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}

        {/* Parámetros específicos para Inventario */}
        {tipoReporte === 'inventario-estado' && (
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="incluir-criticos"
                checked={incluirCriticos}
                onChange={(e) => setIncluirCriticos(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label
                htmlFor="incluir-criticos"
                className="text-sm font-medium text-gray-700"
              >
                Incluir productos críticos (stock bajo)
              </label>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="incluir-obsoletos"
                checked={incluirObsoletos}
                onChange={(e) => setIncluirObsoletos(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label
                htmlFor="incluir-obsoletos"
                className="text-sm font-medium text-gray-700"
              >
                Incluir productos sin movimiento (&gt;90 días)
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Botón de Generar */}
      <div className="mt-6">
        <button
          onClick={handleGenerarReporte}
          disabled={loading}
          className="w-full md:w-auto px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Generando...
            </>
          ) : (
            <>
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Generar y Descargar Reporte
            </>
          )}
        </button>
      </div>

      {/* Mensajes de éxito/error */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <svg
            className="w-5 h-5 text-red-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-red-800">Error</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
          <svg
            className="w-5 h-5 text-green-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-green-800">¡Éxito!</p>
            <p className="text-sm text-green-700">{success}</p>
          </div>
        </div>
      )}

      {/* Información adicional */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-sm font-semibold text-blue-800 mb-2">
          📊 Información del Reporte
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          {tipoReporte === 'gastos-mensuales' ? (
            <>
              <li>• Resumen de gastos por categoría</li>
              <li>• Comparativa con mes anterior</li>
              <li>• Top 10 gastos mayores</li>
              <li>• Tendencia de últimos 6 meses</li>
              <li>• Productos comprados vinculados a gastos</li>
            </>
          ) : (
            <>
              <li>• Valor total del inventario</li>
              <li>• Productos con stock crítico</li>
              <li>• Productos con exceso de stock</li>
              <li>• Rotación promedio de inventario</li>
              <li>• Análisis de productos sin movimiento</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
}
