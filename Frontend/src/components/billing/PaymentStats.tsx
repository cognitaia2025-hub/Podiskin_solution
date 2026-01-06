/**
 * Componente PaymentStats
 * ========================
 * Muestra tarjetas con estadísticas de pagos
 */

import React from 'react';
import { DollarSign, AlertCircle, TrendingUp, FileText } from 'lucide-react';
import type { PaymentStats } from '../../types/billing';
import { formatCurrency } from '../../services/billingService';

interface PaymentStatsProps {
  stats: PaymentStats | null;
  loading?: boolean;
}

export const PaymentStats: React.FC<PaymentStatsProps> = ({ stats, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const cards = [
    {
      title: 'Total Cobrado',
      value: formatCurrency(stats.total_cobrado),
      icon: DollarSign,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      borderColor: 'border-green-500',
      subtitle: `${stats.pagos_completos} pagos completos`,
    },
    {
      title: 'Pendientes',
      value: formatCurrency(stats.total_pendiente),
      icon: AlertCircle,
      bgColor: 'bg-red-50',
      iconColor: 'text-red-600',
      borderColor: 'border-red-500',
      subtitle: `${stats.pagos_pendientes} sin pagar`,
    },
    {
      title: 'Promedio por Pago',
      value: formatCurrency(stats.promedio_por_pago),
      icon: TrendingUp,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-500',
      subtitle: `${stats.total_pagos} pagos totales`,
    },
    {
      title: 'Facturas',
      value: `${stats.facturas_emitidas}/${stats.facturas_solicitadas}`,
      icon: FileText,
      bgColor: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
      borderColor: 'border-yellow-500',
      subtitle: 'Emitidas/Solicitadas',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div
            key={index}
            className={`${card.bgColor} rounded-lg shadow p-6 border-l-4 ${card.borderColor} transition-transform hover:scale-105`}
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-700">{card.title}</h3>
              <Icon className={`w-5 h-5 ${card.iconColor}`} />
            </div>
            <p className="text-2xl font-bold text-gray-900 mb-1">{card.value}</p>
            <p className="text-xs text-gray-600">{card.subtitle}</p>
          </div>
        );
      })}
    </div>
  );
};
