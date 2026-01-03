/**
 * AvailabilityIndicator Component
 * 
 * Shows real-time availability status with visual feedback
 */

import React from 'react';
import { CheckCircle2, XCircle, Loader2, AlertCircle } from 'lucide-react';
import type { Appointment } from '../../types/appointments';

type AvailabilityStatus = 'idle' | 'checking' | 'available' | 'unavailable';

interface AvailabilityIndicatorProps {
  status: AvailabilityStatus;
  conflictingAppointments?: Appointment[];
}

const AvailabilityIndicator: React.FC<AvailabilityIndicatorProps> = ({
  status,
  conflictingAppointments = []
}) => {
  if (status === 'idle') {
    return null;
  }

  if (status === 'checking') {
    return (
      <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
        <span className="text-sm font-medium text-blue-700">
          Verificando disponibilidad...
        </span>
      </div>
    );
  }

  if (status === 'available') {
    return (
      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
        <CheckCircle2 className="w-5 h-5 text-green-600" />
        <span className="text-sm font-medium text-green-700">
          ✓ Horario disponible
        </span>
      </div>
    );
  }

  if (status === 'unavailable') {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <XCircle className="w-5 h-5 text-red-600" />
          <span className="text-sm font-medium text-red-700">
            ✗ Horario no disponible
          </span>
        </div>

        {/* Show conflicting appointments */}
        {conflictingAppointments.length > 0 && (
          <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="flex items-start gap-2 mb-2">
              <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-orange-900 mb-1">
                  Conflictos encontrados:
                </p>
                <ul className="text-sm text-orange-800 space-y-1">
                  {conflictingAppointments.map((appt, index) => {
                    const startTime = new Date(appt.fecha_hora_inicio).toLocaleTimeString('es-MX', {
                      hour: '2-digit',
                      minute: '2-digit'
                    });
                    const endTime = new Date(appt.fecha_hora_fin).toLocaleTimeString('es-MX', {
                      hour: '2-digit',
                      minute: '2-digit'
                    });
                    
                    return (
                      <li key={index} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-orange-600 rounded-full" />
                        <span>
                          Cita existente: {startTime} - {endTime}
                          {appt.tipo_cita && ` (${appt.tipo_cita})`}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
};

export default AvailabilityIndicator;
