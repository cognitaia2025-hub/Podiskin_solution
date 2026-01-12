/**
 * SentimentIndicator - Indicador de sentimiento
 * =============================================
 */

import React from 'react';
import { clsx } from 'clsx';
import { Smile, Meh, Frown, AlertTriangle } from 'lucide-react';
import { Sentimiento } from '../../types/whatsapp';

interface SentimentIndicatorProps {
    sentimiento: Sentimiento;
    confianza?: number;
    size?: 'sm' | 'md' | 'lg';
    showLabel?: boolean;
}

export const SentimentIndicator: React.FC<SentimentIndicatorProps> = ({
    sentimiento,
    confianza,
    size = 'md',
    showLabel = true
}) => {
    const config = {
        [Sentimiento.POSITIVO]: {
            icon: Smile,
            color: 'text-green-600',
            bg: 'bg-green-100',
            border: 'border-green-200',
            label: 'Positivo'
        },
        [Sentimiento.NEUTRAL]: {
            icon: Meh,
            color: 'text-gray-600',
            bg: 'bg-gray-100',
            border: 'border-gray-200',
            label: 'Neutral'
        },
        [Sentimiento.NEGATIVO]: {
            icon: Frown,
            color: 'text-red-600',
            bg: 'bg-red-100',
            border: 'border-red-200',
            label: 'Negativo'
        },
        [Sentimiento.URGENTE]: {
            icon: AlertTriangle,
            color: 'text-orange-600',
            bg: 'bg-orange-100',
            border: 'border-orange-200',
            label: 'Urgente'
        }
    };

    const { icon: Icon, color, bg, border, label } = config[sentimiento];

    const sizeClasses = {
        sm: { icon: 'w-3 h-3', text: 'text-xs', padding: 'px-2 py-0.5' },
        md: { icon: 'w-4 h-4', text: 'text-sm', padding: 'px-2.5 py-1' },
        lg: { icon: 'w-5 h-5', text: 'text-base', padding: 'px-3 py-1.5' }
    };

    return (
        <div
            className={clsx(
                'inline-flex items-center gap-1.5 rounded-full border font-medium',
                bg,
                border,
                color,
                sizeClasses[size].padding
            )}
        >
            <Icon className={sizeClasses[size].icon} />
            {showLabel && <span className={sizeClasses[size].text}>{label}</span>}
            {confianza !== undefined && (
                <span className={clsx(sizeClasses[size].text, 'opacity-75')}>
                    ({Math.round(confianza * 100)}%)
                </span>
            )}
        </div>
    );
};
