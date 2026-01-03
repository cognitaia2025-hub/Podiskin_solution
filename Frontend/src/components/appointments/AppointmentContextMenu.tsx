/**
 * AppointmentContextMenu Component
 * 
 * Context menu for appointment actions (status changes, edit, delete)
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  MoreVertical, 
  Eye, 
  Edit, 
  CheckCircle, 
  XCircle, 
  Clock,
  Trash2,
  Calendar
} from 'lucide-react';
import type { Appointment, AppointmentStatus } from '../../types/appointments';

interface AppointmentContextMenuProps {
  appointment: Appointment;
  onStatusChange: (status: AppointmentStatus) => void;
  onEdit: () => void;
  onDelete: () => void;
  onViewDetails: () => void;
}

const STATUS_OPTIONS: { value: AppointmentStatus; label: string; icon: any; color: string }[] = [
  { value: 'Confirmada', label: 'Confirmar', icon: CheckCircle, color: 'text-blue-600' },
  { value: 'En_Curso', label: 'En Proceso', icon: Clock, color: 'text-green-600' },
  { value: 'Completada', label: 'Completada', icon: CheckCircle, color: 'text-gray-600' },
  { value: 'Cancelada', label: 'Cancelar', icon: XCircle, color: 'text-red-600' },
  { value: 'No_Asistio', label: 'No Asistió', icon: XCircle, color: 'text-orange-600' },
];

const AppointmentContextMenu: React.FC<AppointmentContextMenuProps> = ({
  appointment,
  onStatusChange,
  onEdit,
  onDelete,
  onViewDetails,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        buttonRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleStatusClick = (status: AppointmentStatus) => {
    onStatusChange(status);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className="p-1 hover:bg-gray-100 rounded-full transition-colors"
        aria-label="Opciones"
      >
        <MoreVertical className="w-4 h-4 text-gray-600" />
      </button>

      {isOpen && (
        <div
          ref={menuRef}
          className="absolute right-0 top-full mt-1 w-56 bg-white border border-gray-200 rounded-lg shadow-xl z-50 overflow-hidden"
        >
          {/* View Details */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails();
              setIsOpen(false);
            }}
            className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left border-b border-gray-100"
          >
            <Eye className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Ver detalles</span>
          </button>

          {/* Edit */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit();
              setIsOpen(false);
            }}
            className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-gray-50 transition-colors text-left border-b border-gray-100"
          >
            <Edit className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Editar cita</span>
          </button>

          {/* Status Changes */}
          <div className="border-b border-gray-100">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
              Cambiar Estado
            </div>
            {STATUS_OPTIONS.map((option) => {
              const Icon = option.icon;
              const isCurrentStatus = appointment.estado === option.value;
              
              return (
                <button
                  key={option.value}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleStatusClick(option.value);
                  }}
                  disabled={isCurrentStatus}
                  className={`
                    w-full px-4 py-2 flex items-center gap-3 transition-colors text-left
                    ${isCurrentStatus 
                      ? 'bg-gray-50 cursor-not-allowed opacity-50' 
                      : 'hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon className={`w-4 h-4 ${option.color}`} />
                  <span className="text-sm text-gray-700">
                    {option.label}
                    {isCurrentStatus && ' (actual)'}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Delete */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (confirm('¿Estás seguro de que deseas eliminar esta cita?')) {
                onDelete();
                setIsOpen(false);
              }
            }}
            className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-red-50 transition-colors text-left"
          >
            <Trash2 className="w-4 h-4 text-red-600" />
            <span className="text-sm font-medium text-red-600">Eliminar cita</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default AppointmentContextMenu;
