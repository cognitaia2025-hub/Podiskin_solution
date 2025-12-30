/**
 * Appointment Trend Chart Component
 * 
 * Line chart showing appointments over the last 30 days.
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { AppointmentTrend } from '../../services/dashboardService';

interface AppointmentTrendChartProps {
  data: AppointmentTrend[];
}

const AppointmentTrendChart: React.FC<AppointmentTrendChartProps> = ({ data }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        📈 Citas de los últimos 30 días
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="fecha"
            tickFormatter={(value) =>
              new Date(value).toLocaleDateString('es-MX', {
                month: 'short',
                day: 'numeric',
              })
            }
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
          <Tooltip
            labelFormatter={(value) =>
              new Date(value).toLocaleDateString('es-MX', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })
            }
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.375rem',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="cantidad"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Total"
            dot={{ fill: '#3b82f6', r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="completadas"
            stroke="#10b981"
            strokeWidth={2}
            name="Completadas"
            dot={{ fill: '#10b981', r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="canceladas"
            stroke="#ef4444"
            strokeWidth={2}
            name="Canceladas"
            dot={{ fill: '#ef4444', r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AppointmentTrendChart;
