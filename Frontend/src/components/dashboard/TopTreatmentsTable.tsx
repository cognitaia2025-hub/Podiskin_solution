/**
 * Top Treatments Table Component
 * 
 * Table showing the most common treatments.
 */

import React from 'react';

interface TopTreatmentsTableProps {
  data?: Array<{
    nombre: string;
    cantidad: number;
  }>;
}

const TopTreatmentsTable: React.FC<TopTreatmentsTableProps> = ({ data }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        🩺 Tratamientos Más Comunes
      </h3>
      {!data || data.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-gray-500">
          No hay datos disponibles
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tratamiento
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cantidad
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Porcentaje
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.map((treatment, index) => {
                const total = data.reduce((sum, t) => sum + t.cantidad, 0);
                const percentage = ((treatment.cantidad / total) * 100).toFixed(1);
                
                return (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <div className="flex items-center">
                        <span className="mr-2 text-gray-400">#{index + 1}</span>
                        {treatment.nombre}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right font-medium">
                      {treatment.cantidad}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 text-right">
                      {percentage}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TopTreatmentsTable;
