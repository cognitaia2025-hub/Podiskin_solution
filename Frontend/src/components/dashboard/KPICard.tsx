/**
 * KPI Card Component
 * 
 * Displays a single KPI metric with icon, value, and optional trend.
 */

import React from 'react';
import { clsx } from 'clsx';

export interface KPICardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number; // Porcentaje
    isPositive: boolean;
  };
  color: 'blue' | 'green' | 'purple' | 'orange';
}

const KPICard: React.FC<KPICardProps> = ({ title, value, icon, trend, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div className={clsx('p-3 rounded-lg', colorClasses[color])}>
          {icon}
        </div>
        {trend && (
          <div
            className={clsx(
              'flex items-center text-sm font-medium',
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            )}
          >
            <span className="mr-1">{trend.isPositive ? '↑' : '↓'}</span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-gray-500 text-sm">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      </div>
    </div>
  );
};

export default KPICard;
