/**
 * AppointmentFilters Component
 * 
 * Filter panel for appointments by status, type, and date range
 */

import React from 'react';
import { Filter } from 'lucide-react';
import type { AppointmentStatus, AppointmentType } from '../../services/mockData';

interface AppointmentFiltersProps {
  statusFilter: AppointmentStatus[];
  onStatusFilterChange: (statuses: AppointmentStatus[]) => void;
  typeFilter: AppointmentType[];
  onTypeFilterChange: (types: AppointmentType[]) => void;
}

const STATUS_OPTIONS: AppointmentStatus[] = [
  'Pendiente',
  'Confirmada',
  'En_Curso',
  'Completada',
  'Cancelada',
  'No_Asistio',
];

const TYPE_OPTIONS: AppointmentType[] = [
  'Consulta',
  'Seguimiento',
  'Urgencia',
];

const AppointmentFilters: React.FC<AppointmentFiltersProps> = ({
  statusFilter,
  onStatusFilterChange,
  typeFilter,
  onTypeFilterChange,
}) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const toggleStatus = (status: AppointmentStatus) => {
    if (statusFilter.includes(status)) {
      onStatusFilterChange(statusFilter.filter(s => s !== status));
    } else {
      onStatusFilterChange([...statusFilter, status]);
    }
  };

  const toggleType = (type: AppointmentType) => {
    if (typeFilter.includes(type)) {
      onTypeFilterChange(typeFilter.filter(t => t !== type));
    } else {
      onTypeFilterChange([...typeFilter, type]);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
      >
        <Filter className="w-4 h-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Filtros</span>
        {(statusFilter.length > 0 || typeFilter.length > 0) && (
          <span className="px-2 py-0.5 bg-primary-500 text-white text-xs rounded-full">
            {statusFilter.length + typeFilter.length}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-2 w-72 bg-white border-2 border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden">
            {/* Status Filters */}
            <div className="p-4 border-b border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">
                Estado de la Cita
              </h4>
              <div className="space-y-2">
                {STATUS_OPTIONS.map((status) => (
                  <label
                    key={status}
                    className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={statusFilter.includes(status)}
                      onChange={() => toggleStatus(status)}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500/20"
                    />
                    <span className="text-sm text-gray-700">{status.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Type Filters */}
            <div className="p-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">
                Tipo de Cita
              </h4>
              <div className="space-y-2">
                {TYPE_OPTIONS.map((type) => (
                  <label
                    key={type}
                    className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={typeFilter.includes(type)}
                      onChange={() => toggleType(type)}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500/20"
                    />
                    <span className="text-sm text-gray-700">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Clear Filters */}
            {(statusFilter.length > 0 || typeFilter.length > 0) && (
              <div className="p-3 bg-gray-50 border-t border-gray-200">
                <button
                  onClick={() => {
                    onStatusFilterChange([]);
                    onTypeFilterChange([]);
                  }}
                  className="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Limpiar filtros
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AppointmentFilters;
