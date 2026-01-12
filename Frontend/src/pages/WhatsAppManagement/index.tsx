import React, { useState, useEffect } from 'react';
import { MessageSquare } from 'lucide-react';
import { QRViewer } from './QRViewer';
import { ConversationsList } from './ConversationsList';
import { ConversationPanel } from './ConversationPanel';
import { EscalationQueue } from './EscalationQueue';
import { WhatsAppControlPanel } from './WhatsAppControlPanel';
import { WhatsAppConfigModal } from './WhatsAppConfigModal';
import {
    getConversaciones,
    getConversacionDetalle,
    responderDuda
} from '../../services/whatsappService';
import type { ConversacionListItem, ConversacionDetalle } from '../../types/whatsapp';

export const WhatsAppManagement: React.FC = () => {
    const [showQRModal, setShowQRModal] = useState(false);
    const [showConfigModal, setShowConfigModal] = useState(false);
    const [serviceStatus, setServiceStatus] = useState('stopped');
    const [conversaciones, setConversaciones] = useState<ConversacionListItem[]>([]);
    const [escaladas, setEscaladas] = useState<any[]>([]);
    const [selectedConv, setSelectedConv] = useState<ConversacionDetalle | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadConversaciones();
    }, []);

    const loadConversaciones = async () => {
        try {
            const data = await getConversaciones();
            // Manejar ambos formatos: array directo o objeto con {atendidas, escaladas}
            if (Array.isArray(data)) {
                // El endpoint retorna array directo
                setConversaciones(data);
                setEscaladas([]);
            } else if (data && typeof data === 'object') {
                // El endpoint retorna objeto estructurado
                setConversaciones(data.atendidas || []);
                setEscaladas(data.escaladas || []);
            } else {
                setConversaciones([]);
                setEscaladas([]);
            }
        } catch (error) {
            console.error('Error cargando conversaciones:', error);
            setConversaciones([]);
            setEscaladas([]);
        }
    };

    const handleSelectConversacion = async (conv: ConversacionListItem) => {
        setLoading(true);
        try {
            const detalle = await getConversacionDetalle(conv.id);
            setSelectedConv(detalle);
        } catch (error) {
            console.error('Error cargando conversación:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleResponderDuda = async (dudaId: number, respuesta: string, tono?: any, tonoResp?: any) => {
        try {
            await responderDuda(dudaId, {
                respuesta,
                generar_aprendizaje: true,
                tono_cliente: tono,
                tono_respuesta: tonoResp
            });
            loadConversaciones();
        } catch (error) {
            console.error('Error respondiendo duda:', error);
        }
    };

    const handleStartClick = async () => {
        // Solo mostrar el modal - el QR se generará automáticamente
        // cuando el serviceStatus cambie a 'starting'
        setShowQRModal(true);
    };

    return (
        <div className="h-full flex flex-col bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <div className="flex items-center gap-3">
                    <MessageSquare className="w-6 h-6 text-primary-600" />
                    <h1 className="text-2xl font-bold text-gray-900">Gestión de WhatsApp</h1>
                </div>
            </div>

            {/* Control Panel */}
            <div className="p-6">
                <WhatsAppControlPanel
                    onStartClick={handleStartClick}
                    onStatusChange={(status) => setServiceStatus(status)}
                    onSettingsClick={() => setShowConfigModal(true)}
                />
            </div>

            {/* Contenido principal */}
            <div className="flex-1 grid grid-cols-12 gap-6 px-6 pb-6 overflow-hidden">
                {/* Conversaciones */}
                <div className="col-span-3 bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col">
                    <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
                        <h2 className="font-semibold text-gray-900">Conversaciones</h2>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4">
                        <ConversationsList
                            conversaciones={conversaciones}
                            selectedId={selectedConv?.id}
                            onSelect={handleSelectConversacion}
                        />
                    </div>
                </div>

                {/* Panel de conversación */}
                <div className="col-span-6 bg-white rounded-lg border border-gray-200 overflow-hidden">
                    <ConversationPanel conversacion={selectedConv} loading={loading} />
                </div>

                {/* Escalamientos */}
                <div className="col-span-3 bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col">
                    <div className="px-4 py-3 border-b border-gray-200 bg-orange-50">
                        <h2 className="font-semibold text-gray-900">Dudas Escaladas</h2>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4">
                        <EscalationQueue dudas={escaladas} onResponder={handleResponderDuda} />
                    </div>
                </div>
            </div>

            {/* Modal de QR */}
            {showQRModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
                        <QRViewer
                            serviceStatus={serviceStatus}
                            onConnected={() => {
                                setShowQRModal(false);
                                setServiceStatus('running');
                            }}
                        />
                        <div className="px-6 pb-6">
                            <button
                                onClick={() => setShowQRModal(false)}
                                className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal de Configuración */}
            <WhatsAppConfigModal
                isOpen={showConfigModal}
                onClose={() => setShowConfigModal(false)}
                onSave={async (config) => {
                    console.log('Config saved:', config);
                }}
            />
        </div>
    );
};
