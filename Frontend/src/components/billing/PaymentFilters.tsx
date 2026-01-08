/**
 * Componente PaymentFilters
 * ==========================
 * Filtros para búsqueda y filtrado de pagos
 */

import React from 'react';
import { Search, Filter } from 'lucide-react';
import type { EstadoPago, MetodoPago } from '../../types/billing';

interface PaymentFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  estadoFilter: string;
  onEstadoChange: (estado: string) => void;
  metodoFilter: string;
  onMetodoChange: (metodo: string) => void;
}

export const PaymentFilters: React.FC<PaymentFiltersProps> = ({
  searchQuery,
  onSearchChange,
  estadoFilter,
  onEstadoChange,
  metodoFilter,
  onMetodoChange,
}) => {
  const estados: (EstadoPago | 'todos')[] = ['todos', 'Pagado', 'Parcial', 'Pendiente', 'Cancelado'];
  const metodos: (MetodoPago | 'todos')[] = [
    'todos',
    'Efectivo',
    'Tarjeta_Debito',
    'Tarjeta_Credito',
    'Transferencia',
    'Cheque',
    'Otro',
  ];

  const getEstadoLabel = (estado: string): string => {
    if (estado === 'todos') return 'Todos los estados';
    return estado;
  };

  const getMetodoLabel = (metodo: string): string => {
    if (metodo === 'todos') return 'Todos los métodos';
    return metodo.replace('_', ' ');
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Búsqueda */}
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar por paciente, folio..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Filtro por Estado */}
        <div className="w-full md:w-48">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              value={estadoFilter}
              onChange={(e) => onEstadoChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
            >
              {estados.map((estado) => (
                <option key={estado} value={estado}>
                  {getEstadoLabel(estado)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Filtro por Método */}
        <div className="w-full md:w-48">
          <select
            value={metodoFilter}
            onChange={(e) => onMetodoChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
          >
            {metodos.map((metodo) => (
              <option key={metodo} value={metodo}>
                {getMetodoLabel(metodo)}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
