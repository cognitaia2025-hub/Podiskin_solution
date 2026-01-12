/**
 * MessageBubble - Burbuja de mensaje reutilizable
 * ===============================================
 */

import React from 'react';
import { clsx } from 'clsx';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Bot, User, CheckCheck, Check } from 'lucide-react';
import type { MensajeItem } from '../../types/whatsapp';
import { getSentimientoColor, getTonoColor } from '../../services/whatsappService';

interface MessageBubbleProps {
    mensaje: MensajeItem;
    showSentiment?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
    mensaje,
    showSentiment = false
}) => {
    const isIncoming = mensaje.direccion === 'Entrante';
    const isBot = mensaje.enviado_por_tipo === 'Bot';

    return (
        <div
            className={clsx(
                'flex gap-3 mb-4 animate-in fade-in slide-in-from-bottom-2 duration-200',
                isIncoming ? 'justify-start' : 'justify-end'
            )}
        >
            {/* Avatar */}
            {isIncoming && (
                <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <User className="w-5 h-5 text-gray-600" />
                    </div>
                </div>
            )}

            {/* Mensaje */}
            <div className={clsx('flex flex-col max-w-[70%]', isIncoming ? 'items-start' : 'items-end')}>
                {/* Burbuja */}
                <div
                    className={clsx(
                        'rounded-2xl px-4 py-2.5 shadow-sm',
                        isIncoming
                            ? 'bg-white border border-gray-200 text-gray-900'
                            : isBot
                                ? 'bg-blue-500 text-white'
                                : 'bg-primary-600 text-white'
                    )}
                >
                    {/* Indicador de bot */}
                    {isBot && isIncoming && (
                        <div className="flex items-center gap-1.5 mb-1 text-xs text-gray-500">
                            <Bot className="w-3 h-3" />
                            <span>Maya (Bot)</span>
                        </div>
                    )}

                    {/* Contenido */}
                    <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                        {mensaje.contenido}
                    </p>

                    {/* Sentimiento (opcional) */}
                    {showSentiment && (mensaje.sentimiento || mensaje.tono) && (
                        <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-200/20">
                            {mensaje.sentimiento && (
                                <span
                                    className={clsx(
                                        'text-xs px-2 py-0.5 rounded-full',
                                        isIncoming ? 'bg-gray-100 text-gray-700' : 'bg-white/20 text-white'
                                    )}
                                >
                                    {mensaje.sentimiento}
                                </span>
                            )}
                            {mensaje.tono && (
                                <span
                                    className={clsx(
                                        'text-xs px-2 py-0.5 rounded-full',
                                        isIncoming ? 'bg-gray-100 text-gray-700' : 'bg-white/20 text-white'
                                    )}
                                >
                                    {mensaje.tono}
                                </span>
                            )}
                        </div>
                    )}
                </div>

                {/* Metadata */}
                <div className="flex items-center gap-2 mt-1 px-1">
                    <span className="text-xs text-gray-500">
                        {format(new Date(mensaje.fecha_envio), 'HH:mm', { locale: es })}
                    </span>

                    {/* Estado de entrega (solo para salientes) */}
                    {!isIncoming && (
                        <span className="text-gray-400">
                            {mensaje.estado_entrega === 'Leido' ? (
                                <CheckCheck className="w-3 h-3 text-blue-500" />
                            ) : mensaje.estado_entrega === 'Entregado' ? (
                                <CheckCheck className="w-3 h-3" />
                            ) : (
                                <Check className="w-3 h-3" />
                            )}
                        </span>
                    )}
                </div>
            </div>

            {/* Avatar bot/usuario */}
            {!isIncoming && (
                <div className="flex-shrink-0">
                    <div
                        className={clsx(
                            'w-8 h-8 rounded-full flex items-center justify-center',
                            isBot ? 'bg-blue-100' : 'bg-primary-100'
                        )}
                    >
                        {isBot ? (
                            <Bot className="w-5 h-5 text-blue-600" />
                        ) : (
                            <User className="w-5 h-5 text-primary-600" />
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
