import React from 'react';
import { Phone, Mail, Calendar, Edit, Trash2 } from 'lucide-react';
import { clsx } from 'clsx';
import PatientAvatar from './PatientAvatar';

export interface PatientCardData {
  id: string;
  primer_nombre?: string;
  segundo_nombre?: string;
  primer_apellido?: string;
  segundo_apellido?: string;
  telefono_principal?: string;
  correo_electronico?: string;
  fecha_nacimiento?: string;
  activo?: boolean;
}

interface PatientCardProps {
  patient: PatientCardData;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  className?: string;
}

/**
 * PatientCard Component
 * 
 * Displays patient information in a card format (for mobile)
 */
const PatientCard: React.FC<PatientCardProps> = ({
  patient,
  onClick,
  onEdit,
  onDelete,
  className,
}) => {
  const fullName = [
    patient.primer_nombre,
    patient.segundo_nombre,
    patient.primer_apellido,
    patient.segundo_apellido,
  ]
    .filter(Boolean)
    .join(' ');

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'No especificada';
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div
      className={clsx(
        'bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <PatientAvatar
          firstName={patient.primer_nombre || ''}
          lastName={patient.primer_apellido || ''}
          size="md"
        />

        <div className="flex-1 min-w-0">
          {/* Name */}
          <h3 className="font-semibold text-gray-900 truncate">
            {fullName || 'Sin nombre'}
          </h3>

          {/* Contact Info */}
          <div className="mt-2 space-y-1">
            {patient.telefono_principal && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Phone className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <span className="truncate">{patient.telefono_principal}</span>
              </div>
            )}

            {patient.correo_electronico && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <span className="truncate">{patient.correo_electronico}</span>
              </div>
            )}

            {patient.fecha_nacimiento && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Calendar className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <span>{formatDate(patient.fecha_nacimiento)}</span>
              </div>
            )}
          </div>

          {/* Status Badge */}
          {patient.activo !== undefined && (
            <div className="mt-2">
              <span
                className={clsx(
                  'inline-flex items-center px-2 py-1 text-xs font-medium rounded-full',
                  patient.activo
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                )}
              >
                {patient.activo ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          )}
        </div>

        {/* Actions */}
        {(onEdit || onDelete) && (
          <div className="flex items-center gap-2">
            {onEdit && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit();
                }}
                className="p-2 text-gray-600 hover:text-teal-600 hover:bg-teal-50 rounded-lg transition-colors"
                title="Editar paciente"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}

            {onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                }}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Desactivar paciente"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientCard;
