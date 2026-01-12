/**
 * ToneSelector - Selector de tono reutilizable
 * ============================================
 */

import React from 'react';
import { clsx } from 'clsx';
import { TonoCl, TonoRespuesta, TONO_LABELS, TONO_RESPUESTA_LABELS } from '../../types/whatsapp';

interface ToneSelectorProps {
    value: TonoCl | TonoRespuesta | null;
    onChange: (tono: TonoCl | TonoRespuesta) => void;
    type: 'cliente' | 'respuesta';
    label?: string;
    required?: boolean;
}

export const ToneSelector: React.FC<ToneSelectorProps> = ({
    value,
    onChange,
    type,
    label,
    required = false
}) => {
    const options = type === 'cliente' ? TONO_LABELS : TONO_RESPUESTA_LABELS;

    return (
        <div className="space-y-2">
            {label && (
                <label className="block text-sm font-medium text-gray-700">
                    {label}
                    {required && <span className="text-red-500 ml-1">*</span>}
                </label>
            )}

            <div className="grid grid-cols-2 gap-2">
                {Object.entries(options).map(([key, { label: optionLabel, emoji }]) => {
                    const isSelected = value === key;

                    return (
                        <button
                            key={key}
                            type="button"
                            onClick={() => onChange(key as any)}
                            className={clsx(
                                'flex items-center gap-2 px-4 py-3 rounded-lg border-2 transition-all',
                                'hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                                isSelected
                                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                                    : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                            )}
                        >
                            <span className="text-2xl">{emoji}</span>
                            <span className="text-sm font-medium">{optionLabel}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
