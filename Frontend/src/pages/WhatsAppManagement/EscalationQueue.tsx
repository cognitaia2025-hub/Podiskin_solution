/**
 * EscalationQueue - Cola de escalamientos
 */

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { AlertCircle, Send } from 'lucide-react';
import { PatientBadge } from '../../components/whatsapp/PatientBadge';
import { ToneSelector } from '../../components/whatsapp/ToneSelector';
import { formatearFechaRelativa } from '../../services/whatsappService';
import type { DudaPendienteItem, TonoCl, TonoRespuesta } from '../../types/whatsapp';

interface EscalationQueueProps {
    dudas: DudaPendienteItem[];
    onResponder: (dudaId: number, respuesta: string, tono?: TonoCl, tonoResp?: TonoRespuesta) => void;
}

export const EscalationQueue: React.FC<EscalationQueueProps> = ({
    dudas = [],
    onResponder
}) => {
    // Garantizar que dudas sea un array
    const items = Array.isArray(dudas) ? dudas : [];

    const [selectedDuda, setSelectedDuda] = useState<number | null>(null);
    const [respuesta, setRespuesta] = useState('');
    const [tonoCliente, setTonoCliente] = useState<TonoCl | null>(null);
    const [tonoRespuesta, setTonoRespuesta] = useState<TonoRespuesta | null>(null);

    const handleSubmit = () => {
        if (!selectedDuda || !respuesta.trim()) return;

        onResponder(selectedDuda, respuesta, tonoCliente || undefined, tonoRespuesta || undefined);
        setSelectedDuda(null);
        setRespuesta('');
        setTonoCliente(null);
        setTonoRespuesta(null);
    };

    const dudaSeleccionada = items.find(d => d.id === selectedDuda);

    return (
        <div className="space-y-4">
            {/* Lista de dudas */}
            <div className="space-y-2">
                {items.map((duda) => (
                    <div
                        key={duda.id}
                        className={clsx(
                            'p-4 rounded-lg border-2 cursor-pointer transition-all',
                            selectedDuda === duda.id
                                ? 'border-orange-500 bg-orange-50'
                                : 'border-gray-200 bg-white hover:border-gray-300'
                        )}
                        onClick={() => setSelectedDuda(duda.id)}
                    >
                        <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="font-medium text-gray-900">{duda.paciente_nombre}</h4>
                                    <span className="text-xs text-gray-500">
                                        {formatearFechaRelativa(duda.fecha_creacion)}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-700 mb-2">{duda.duda}</p>
                                <PatientBadge
                                    esNuevo={!duda.id_paciente}
                                    idPaciente={duda.id_paciente}
                                    size="sm"
                                />
                            </div>
                        </div>
                    </div>
                ))}

                {items.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No hay dudas pendientes</p>
                    </div>
                )}
            </div>

            {/* Editor de respuesta */}
            {dudaSeleccionada && (
                <div className="bg-white rounded-lg border-2 border-orange-500 p-6 space-y-4">
                    <h3 className="text-lg font-semibold text-gray-900">Responder Duda</h3>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Pregunta del paciente
                        </label>
                        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                            <p className="text-sm text-gray-700">{dudaSeleccionada.duda}</p>
                        </div>
                    </div>

                    <ToneSelector
                        value={tonoCliente}
                        onChange={setTonoCliente}
                        type="cliente"
                        label="Tono del cliente"
                    />

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tu respuesta <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            value={respuesta}
                            onChange={(e) => setRespuesta(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            rows={4}
                            placeholder="Escribe tu respuesta aquí..."
                        />
                    </div>

                    <ToneSelector
                        value={tonoRespuesta}
                        onChange={setTonoRespuesta}
                        type="respuesta"
                        label="Tono de respuesta"
                    />

                    <div className="flex gap-3">
                        <button
                            onClick={() => setSelectedDuda(null)}
                            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                        >
                            Cancelar
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={!respuesta.trim()}
                            className={clsx(
                                'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium',
                                'bg-primary-600 text-white hover:bg-primary-700',
                                'disabled:opacity-50 disabled:cursor-not-allowed'
                            )}
                        >
                            <Send className="w-4 h-4" />
                            Enviar Respuesta
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
