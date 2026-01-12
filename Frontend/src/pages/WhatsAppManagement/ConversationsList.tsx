/**
 * ConversationsList - Lista de conversaciones
 */

import React from 'react';
import { clsx } from 'clsx';
import { formatearFechaRelativa } from '../../services/whatsappService';
import { PatientBadge } from '../../components/whatsapp/PatientBadge';
import type { ConversacionListItem } from '../../types/whatsapp';

interface ConversationsListProps {
    conversaciones: ConversacionListItem[];
    selectedId?: number;
    onSelect: (conversacion: ConversacionListItem) => void;
}

export const ConversationsList: React.FC<ConversationsListProps> = ({
    conversaciones = [],
    selectedId,
    onSelect
}) => {
    // Garantizar que conversaciones sea un array
    const items = Array.isArray(conversaciones) ? conversaciones : [];

    return (
        <div className="space-y-1">
            {items.map((conv) => {
                const isSelected = conv.id === selectedId;

                return (
                    <button
                        key={conv.id}
                        onClick={() => onSelect(conv)}
                        className={clsx(
                            'w-full text-left px-4 py-3 rounded-lg transition-all',
                            'hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500',
                            isSelected && 'bg-primary-50 border-l-4 border-primary-600'
                        )}
                    >
                        <div className="flex items-start justify-between gap-2 mb-1">
                            <h4 className="font-medium text-gray-900">{conv.contacto_nombre}</h4>
                            <span className="text-xs text-gray-500 flex-shrink-0">
                                {formatearFechaRelativa(conv.fecha_ultima_actividad)}
                            </span>
                        </div>

                        <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                            {conv.ultimo_mensaje}
                        </p>

                        <div className="flex items-center justify-between">
                            <PatientBadge
                                esNuevo={conv.es_nuevo_paciente}
                                idPaciente={conv.id_paciente}
                                size="sm"
                                showIcon={false}
                            />

                            {conv.numero_mensajes_sin_leer > 0 && (
                                <span className="bg-primary-600 text-white text-xs font-medium px-2 py-0.5 rounded-full">
                                    {conv.numero_mensajes_sin_leer}
                                </span>
                            )}
                        </div>
                    </button>
                );
            })}

            {items.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <p>No hay conversaciones</p>
                </div>
            )}
        </div>
    );
};
