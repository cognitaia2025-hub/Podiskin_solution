/**
 * PatientBadge - Badge reutilizable para mostrar estado de paciente
 * ================================================================
 */

import React from 'react';
import { UserPlus, User } from 'lucide-react';
import { clsx } from 'clsx';

interface PatientBadgeProps {
    esNuevo: boolean;
    idPaciente?: number;
    size?: 'sm' | 'md' | 'lg';
    showIcon?: boolean;
}

export const PatientBadge: React.FC<PatientBadgeProps> = ({
    esNuevo,
    idPaciente,
    size = 'md',
    showIcon = true
}) => {
    const sizeClasses = {
        sm: 'text-xs px-2 py-0.5',
        md: 'text-sm px-2.5 py-1',
        lg: 'text-base px-3 py-1.5'
    };

    const iconSizes = {
        sm: 'w-3 h-3',
        md: 'w-4 h-4',
        lg: 'w-5 h-5'
    };

    return (
        <div className="flex items-center gap-2">
            {esNuevo ? (
                <span
                    className={clsx(
                        'inline-flex items-center gap-1.5 rounded-full font-medium',
                        'bg-blue-100 text-blue-700 border border-blue-200',
                        sizeClasses[size]
                    )}
                >
                    {showIcon && <UserPlus className={iconSizes[size]} />}
                    <span>Nuevo Paciente</span>
                </span>
            ) : (
                <span
                    className={clsx(
                        'inline-flex items-center gap-1.5 rounded-full font-medium',
                        'bg-green-100 text-green-700 border border-green-200',
                        sizeClasses[size]
                    )}
                >
                    {showIcon && <User className={iconSizes[size]} />}
                    <span>Paciente</span>
                    {idPaciente && (
                        <span className="ml-1 text-xs opacity-75">#{idPaciente}</span>
                    )}
                </span>
            )}
        </div>
    );
};
