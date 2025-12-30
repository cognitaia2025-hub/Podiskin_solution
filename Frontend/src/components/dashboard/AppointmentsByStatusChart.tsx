/**
 * Appointments By Status Chart Component
 * 
 * Pie chart showing distribution of appointments by status.
 */

import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface AppointmentsByStatusChartProps {
  data?: {
    pendiente: number;
    confirmada: number;
    completada: number;
    cancelada: number;
    no_asistio: number;
  };
}

const COLORS: Record<string, string> = {
  pendiente: '#fbbf24',
  confirmada: '#3b82f6',
  completada: '#10b981',
  cancelada: '#ef4444',
  no_asistio: '#f97316',
};

const LABELS: Record<string, string> = {
  pendiente: 'Pendiente',
  confirmada: 'Confirmada',
  completada: 'Completada',
  cancelada: 'Cancelada',
  no_asistio: 'No asistió',
};

const AppointmentsByStatusChart: React.FC<AppointmentsByStatusChartProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📊 Citas por Estado
        </h3>
        <div className="h-[300px] flex items-center justify-center text-gray-500">
          No hay datos disponibles
        </div>
      </div>
    );
  }

  const chartData = Object.entries(data).map(([key, value]) => ({
    name: LABELS[key] || key,
    value,
    key,
  }));

  // Filter out zero values
  const filteredData = chartData.filter(item => item.value > 0);

  const renderLabel = (entry: any) => {
    const percent = ((entry.value / chartData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(0);
    return `${percent}%`;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        📊 Citas por Estado
      </h3>
      {filteredData.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-gray-500">
          No hay citas registradas
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={filteredData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {filteredData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.key]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '0.375rem',
              }}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              formatter={(value) => <span className="text-sm">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default AppointmentsByStatusChart;
