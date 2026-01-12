/**
 * WhatsApp Control Panel
 * Panel de control con botones Start/Stop y configuración
 */

import React, { useState, useEffect } from 'react';
import {
    Power,
    StopCircle,
    Settings,
    Activity,
    AlertTriangle,
    CheckCircle,
    Loader
} from 'lucide-react';
import api from '../../services/api';

interface ControlPanelProps {
    onStatusChange?: (status: string) => void;
    onStartClick?: () => void | Promise<void>;
    onSettingsClick?: () => void;
}

interface ServiceStatus {
    service: {
        status: string;
        hasQR: boolean;
    };
    config: {
        telefono_admin: string;
        estado: string;
        grupos_activos: boolean;
    };
}

export const WhatsAppControlPanel: React.FC<ControlPanelProps> = ({ onStatusChange, onStartClick, onSettingsClick }) => {
    const [status, setStatus] = useState<ServiceStatus | null>(null);
    const [loading, setLoading] = useState(false);
    const [serviceAvailable, setServiceAvailable] = useState(true);
    const [isStarting, setIsStarting] = useState(false);

    const mountedRef = React.useRef(true);
    const pollingRef = React.useRef<NodeJS.Timeout>();

    // Limpieza al desmontar
    useEffect(() => {
        mountedRef.current = true;
        return () => {
            mountedRef.current = false;
            if (pollingRef.current) clearTimeout(pollingRef.current);
        };
    }, []);

    // Función para obtener estado (una sola vez o durante inicio)
    const fetchStatus = React.useCallback(async () => {
        try {
            const response = await api.get('/api/whatsapp-bridge/control/status', {
                timeout: 5000
            });

            if (!mountedRef.current) return;

            const data = response.data;
            const currentStatus = data.service?.status || 'stopped';

            setStatus(data);
            setServiceAvailable(true);
            onStatusChange?.(currentStatus);

            // Si está "starting", seguir preguntando hasta que cambie
            // (único caso donde necesitamos polling temporal)
            if (currentStatus === 'starting' && isStarting) {
                pollingRef.current = setTimeout(fetchStatus, 3000);
            } else {
                setIsStarting(false);
            }
        } catch (error: any) {
            if (!mountedRef.current) return;
            setServiceAvailable(false);
            onStatusChange?.('stopped');
        }
    }, [onStatusChange, isStarting]);

    // Obtener estado UNA VEZ al cargar la página
    useEffect(() => {
        fetchStatus();
    }, []);

    // Polling temporal solo durante el proceso de inicio
    useEffect(() => {
        if (isStarting) {
            fetchStatus();
        }
        return () => {
            if (pollingRef.current) clearTimeout(pollingRef.current);
        };
    }, [isStarting, fetchStatus]);

    const handleStart = async () => {
        setLoading(true);

        try {
            if (onStartClick) await onStartClick();

            await api.post('/api/whatsapp-bridge/control/start');

            // Activar polling temporal hasta que termine de iniciar
            setIsStarting(true);
        } catch (error: any) {
            console.error('Error starting service:', error);
            const message = error.response?.data?.detail || 'No se pudo iniciar el servicio. Verifique que el contenedor esté activo.';
            alert(message);
        } finally {
            setLoading(false);
        }
    };

    const handleAction = async (endpoint: string, confirmMsg?: string) => {
        if (confirmMsg && !confirm(confirmMsg)) return;

        setLoading(true);

        try {
            await api.post(endpoint);

            // Esperar un momento y obtener estado actualizado
            await new Promise(r => setTimeout(r, 500));
            await fetchStatus();
        } catch (error: any) {
            console.error(`Error en acción ${endpoint}:`, error);
            alert('Hubo un error al ejecutar la acción. Verifique el estado.');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (serviceStatus: string) => {
        switch (serviceStatus) {
            case 'running': return 'text-green-600 bg-green-50';
            case 'starting': return 'text-yellow-600 bg-yellow-50';
            case 'stopped': return 'text-gray-600 bg-gray-50';
            case 'error': return 'text-red-600 bg-red-50';
            default: return 'text-gray-600 bg-gray-50';
        }
    };

    const getStatusIcon = (serviceStatus: string) => {
        switch (serviceStatus) {
            case 'running': return <CheckCircle className="w-5 h-5" />;
            case 'starting': return <Loader className="w-5 h-5 animate-spin" />;
            case 'stopped': return <StopCircle className="w-5 h-5" />;
            case 'error': return <AlertTriangle className="w-5 h-5" />;
            default: return <Activity className="w-5 h-5" />;
        }
    };

    const getStatusText = (serviceStatus: string) => {
        switch (serviceStatus) {
            case 'running': return 'Activo';
            case 'starting': return 'Iniciando...';
            case 'stopped': return 'Detenido';
            case 'error': return 'Error (Verifique Logs)';
            default: return 'Desconocido';
        }
    };

    const serviceStatus = status?.service.status || 'stopped';
    const isRunning = serviceStatus === 'running';
    const isStopped = serviceStatus === 'stopped';

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Control del Agente</h2>
                <div className="flex gap-2">
                    <div className={`text-xs px-2 py-1 rounded ${serviceAvailable ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {serviceAvailable ? 'Conectado' : 'Sin conexión'}
                    </div>
                    <button
                        onClick={onSettingsClick}
                        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                        title="Configuración"
                    >
                        <Settings className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Alerta si servicio Node.js no disponible */}
            {!serviceAvailable && (
                <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <div className="flex gap-2 text-sm text-orange-800">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <div>
                            <strong>Servicio WhatsApp no disponible.</strong> Verifica que el contenedor Docker esté corriendo.
                        </div>
                    </div>
                </div>
            )}

            {/* Estado */}
            <div className={`flex items-center gap-3 p-4 rounded-lg mb-6 ${getStatusColor(serviceStatus)}`}>
                {getStatusIcon(serviceStatus)}
                <div className="flex-1">
                    <div className="font-medium">Estado: {getStatusText(serviceStatus)}</div>
                    {status?.service?.hasQR && (
                        <div className="text-sm opacity-75">QR disponible para escanear</div>
                    )}
                </div>
            </div>

            {/* Botones de Control */}
            <div className="grid grid-cols-2 gap-4">
                {/* Botón Iniciar */}
                <button
                    onClick={handleStart}
                    disabled={loading || isRunning}
                    className={`
                        flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium
                        transition-all duration-200
                        ${isRunning
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-green-600 text-white hover:bg-green-700 active:scale-95'
                        }
                        ${loading ? 'opacity-50 cursor-wait' : ''}
                    `}
                >
                    {loading ? <Loader className="w-5 h-5 animate-spin" /> : <Power className="w-5 h-5" />}
                    <span>{isRunning ? 'Corriendo' : 'Iniciar Servicio'}</span>
                </button>

                {/* Botón Pausar (No destructivo) */}
                <button
                    onClick={() => handleAction('/api/whatsapp-bridge/control/stop')}
                    disabled={loading || isStopped}
                    className={`
                        flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium
                        transition-all duration-200
                        ${isStopped
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-yellow-500 text-white hover:bg-yellow-600 active:scale-95'
                        }
                    `}
                >
                    <StopCircle className="w-5 h-5" />
                    <span>Pausar</span>
                </button>

                {/* Botón Desvincular (Destructivo) */}
                <button
                    onClick={() => handleAction(
                        '/api/whatsapp-bridge/control/logout',
                        '⚠️ ¿Desvincular y cerrar sesión?\n\nSe borrarán los datos de conexión y tendrás que escanear el QR de nuevo.'
                    )}
                    className="col-span-2 flex items-center justify-center gap-2 px-4 py-2 mt-2 rounded-lg font-medium text-red-600 hover:bg-red-50 border border-transparent hover:border-red-200 transition-all"
                >
                    <AlertTriangle className="w-4 h-4" />
                    <span>Desvincular Dispositivo (Reset Total)</span>
                </button>
            </div>

            {/* Información adicional */}
            {status && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <div className="text-gray-500">Admin</div>
                            <div className="font-medium text-gray-900">
                                {status.config.telefono_admin || 'No configurado'}
                            </div>
                        </div>
                        <div>
                            <div className="text-gray-500">Grupos</div>
                            <div className="font-medium text-gray-900">
                                {status.config.grupos_activos ? 'Activos' : 'Desactivados'}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Advertencia */}
            {isRunning && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex gap-2 text-sm text-yellow-800">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                        <div>
                            <strong>Modo Activo:</strong> El bot está procesando mensajes automáticamente.
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
