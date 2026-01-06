/**
 * AuditPage - Página de Auditoría
 * =================================
 * Muestra logs de auditoría con filtros y exportación
 */

import React, { useState, useEffect } from 'react';
import { Shield, Download, Eye, AlertCircle } from 'lucide-react';
import { PermissionGuard } from '../../components/common/PermissionGuard';
import { getAuditLogs, exportLogsToCSV } from '../../services/auditService';
import type { AuditLog } from '../../types/billing';
import { usePermissions } from '../../hooks/usePermissions';

const AuditPage: React.FC = () => {
  const { canRead } = usePermissions();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  // Filters
  const [moduloFilter, setModuloFilter] = useState<string>('todos');
  const [accionFilter, setAccionFilter] = useState<string>('todas');

  useEffect(() => {
    if (canRead('administracion')) {
      loadLogs();
    }
  }, [canRead]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await getAuditLogs({
        modulo: moduloFilter !== 'todos' ? moduloFilter : undefined,
        accion: accionFilter !== 'todas' ? accionFilter : undefined,
      });
      setLogs(data.logs);
    } catch (error) {
      console.error('Error al cargar logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (canRead('administracion')) {
      loadLogs();
    }
  }, [moduloFilter, accionFilter]);

  const handleExport = () => {
    try {
      exportLogsToCSV(logs);
    } catch (error) {
      console.error('Error al exportar:', error);
    }
  };

  if (!canRead('administracion')) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            Acceso Denegado
          </h2>
          <p className="text-gray-500">
            Solo los administradores pueden ver los logs de auditoría
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-50 overflow-auto">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Auditoría</h1>
              <p className="text-gray-600">Registro de actividades del sistema</p>
            </div>
          </div>

          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-md"
          >
            <Download className="w-5 h-5" />
            Exportar CSV
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Módulo
              </label>
              <select
                value={moduloFilter}
                onChange={(e) => setModuloFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="todos">Todos los módulos</option>
                <option value="cobros">Cobros</option>
                <option value="pacientes">Pacientes</option>
                <option value="citas">Citas</option>
                <option value="expedientes">Expedientes</option>
                <option value="inventario">Inventario</option>
                <option value="usuarios">Usuarios</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Acción
              </label>
              <select
                value={accionFilter}
                onChange={(e) => setAccionFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="todas">Todas las acciones</option>
                <option value="crear">Crear</option>
                <option value="actualizar">Actualizar</option>
                <option value="eliminar">Eliminar</option>
                <option value="login">Login</option>
                <option value="export">Exportar</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha/Hora
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Módulo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acción
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Descripción
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Detalles
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="animate-pulse text-gray-500">Cargando logs...</div>
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                      No se encontraron registros
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(log.fecha_hora).toLocaleString('es-MX')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.usuario_nombre || `ID: ${log.usuario_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {log.modulo}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            log.accion === 'eliminar'
                              ? 'bg-red-100 text-red-800'
                              : log.accion === 'crear'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {log.accion}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {log.descripcion}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {log.ip_address || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <Eye className="w-4 h-4 inline" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail Modal */}
        {selectedLog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-bold text-gray-900">Detalles del Log</h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">ID Auditoría</p>
                    <p className="text-gray-900">{selectedLog.id}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Fecha/Hora</p>
                    <p className="text-gray-900">
                      {new Date(selectedLog.fecha_hora).toLocaleString('es-MX')}
                    </p>
                  </div>
                </div>

                {selectedLog.datos_anteriores && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">Datos Anteriores</p>
                    <pre className="bg-red-50 p-4 rounded-lg text-xs overflow-auto">
                      {JSON.stringify(selectedLog.datos_anteriores, null, 2)}
                    </pre>
                  </div>
                )}

                {selectedLog.datos_nuevos && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">Datos Nuevos</p>
                    <pre className="bg-green-50 p-4 rounded-lg text-xs overflow-auto">
                      {JSON.stringify(selectedLog.datos_nuevos, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditPage;
