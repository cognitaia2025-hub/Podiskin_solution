/**
 * ConversationPanel - Panel de conversación individual
 */

import React, { useEffect, useRef } from 'react';
import { MessageBubble } from '../../components/whatsapp/MessageBubble';
import { PatientBadge } from '../../components/whatsapp/PatientBadge';
import { Loader2 } from 'lucide-react';
import type { ConversacionDetalle } from '../../types/whatsapp';

interface ConversationPanelProps {
    conversacion: ConversacionDetalle | null;
    loading?: boolean;
}

export const ConversationPanel: React.FC<ConversationPanelProps> = ({
    conversacion,
    loading
}) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversacion?.mensajes]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
            </div>
        );
    }

    if (!conversacion) {
        return (
            <div className="flex items-center justify-center h-full text-gray-500">
                <p>Selecciona una conversación para ver los mensajes</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 bg-white">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                            {conversacion.contacto.nombre}
                        </h3>
                        {conversacion.contacto.telefono && (
                            <p className="text-sm text-gray-600">{conversacion.contacto.telefono}</p>
                        )}
                    </div>
                    <PatientBadge
                        esNuevo={conversacion.contacto.es_nuevo_paciente}
                        idPaciente={conversacion.contacto.id_paciente}
                    />
                </div>
            </div>

            {/* Mensajes */}
            <div className="flex-1 overflow-y-auto px-6 py-4 bg-gray-50">
                {conversacion.mensajes.map((mensaje) => (
                    <MessageBubble key={mensaje.id} mensaje={mensaje} showSentiment />
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Notas internas */}
            {conversacion.notas_internas && (
                <div className="px-6 py-3 bg-yellow-50 border-t border-yellow-200">
                    <p className="text-sm text-yellow-800">
                        <span className="font-medium">Notas:</span> {conversacion.notas_internas}
                    </p>
                </div>
            )}
        </div>
    );
};
