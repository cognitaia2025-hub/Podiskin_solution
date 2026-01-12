/**
 * QRViewer - Visualizador de código QR para WhatsApp
 * ==================================================
 * 
 * ARQUITECTURA CORRECTA:
 * 1. NO genera QR por sí mismo
 * 2. Recibe serviceStatus como prop desde WhatsAppControlPanel
 * 3. Cuando status = 'starting', inicia polling a GET /api/whatsapp-bridge/qr
 * 4. Cuando recibe QR, lo muestra
 * 5. Cuando status = 'running', muestra "Conectado"
 */

import React, { useState, useEffect, useRef } from 'react';
import { QrCode, CheckCircle, XCircle, Loader2, AlertTriangle } from 'lucide-react';
import { fetchQRCode } from '../../services/whatsappService';

interface QRViewerProps {
    serviceStatus: string;  // 'stopped' | 'starting' | 'running' | 'error'
    onConnected?: () => void;
}

export const QRViewer: React.FC<QRViewerProps> = ({ serviceStatus, onConnected }) => {
    const [qrImage, setQrImage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const timeoutRef = useRef<NodeJS.Timeout>();

    // Polling recursivo seguro (solo cuando serviceStatus = 'starting')
    const pollQR = React.useCallback(async () => {
        if (serviceStatus !== 'starting') {
            // Detener polling si el servicio ya no está iniciando
            return;
        }

        try {
            const result = await fetchQRCode();

            if (result?.qr) {
                // QR recibido exitosamente
                setQrImage(result.qr);
                setError(null);
            } else {
                // QR aún no disponible (404), continuar polling
                setError(null);
            }
        } catch (err: any) {
            console.error('Error fetching QR:', err);
            setError(err.message || 'Error al obtener código QR');
        } finally {
            // Programar siguiente poll SOLO si aún estamos en 'starting'
            if (serviceStatus === 'starting') {
                timeoutRef.current = setTimeout(pollQR, 2000);
            }
        }
    }, [serviceStatus]);

    // Iniciar/detener polling basado en serviceStatus
    useEffect(() => {
        if (serviceStatus === 'starting') {
            // Iniciar polling
            pollQR();
        } else if (serviceStatus === 'running') {
            // Servicio conectado, limpiar QR y notificar
            setQrImage(null);
            onConnected?.();
        } else if (serviceStatus === 'stopped') {
            // Servicio detenido, limpiar todo
            setQrImage(null);
            setError(null);
        }

        // Cleanup al desmontar o cambiar status
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [serviceStatus, pollQR, onConnected]);

    return (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <QrCode className="w-5 h-5 text-primary-600" />
                    <h3 className="text-lg font-semibold text-gray-900">
                        Sincronización de WhatsApp
                    </h3>
                </div>

                {serviceStatus === 'running' && (
                    <span className="flex items-center gap-2 text-green-600 text-sm font-medium">
                        <CheckCircle className="w-5 h-5" />
                        Conectado
                    </span>
                )}
            </div>

            {/* Contenido */}
            <div className="min-h-[400px] flex items-center justify-center">
                {/* Estado: Detenido */}
                {serviceStatus === 'stopped' && (
                    <div className="flex flex-col items-center gap-4 py-12 text-center">
                        <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                            <QrCode className="w-10 h-10 text-gray-400" />
                        </div>
                        <div>
                            <p className="text-gray-900 font-semibold text-xl mb-2">
                                Servicio Detenido
                            </p>
                            <p className="text-gray-600 text-sm">
                                Haz clic en "Iniciar Servicio" para vincular WhatsApp
                            </p>
                        </div>
                    </div>
                )}

                {/* Estado: Iniciando (sin QR aún) */}
                {serviceStatus === 'starting' && !qrImage && !error && (
                    <div className="flex flex-col items-center gap-4 py-12">
                        <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
                        <div className="text-center">
                            <p className="text-gray-900 font-semibold text-lg mb-1">
                                Generando código QR...
                            </p>
                            <p className="text-gray-600 text-sm">
                                Esto puede tardar unos segundos
                            </p>
                        </div>
                    </div>
                )}

                {/* Estado: Iniciando (con QR) */}
                {serviceStatus === 'starting' && qrImage && (
                    <div className="flex flex-col items-center gap-6 py-8">
                        <div className="bg-white p-4 rounded-lg border-4 border-primary-500 shadow-lg">
                            <img
                                src={qrImage}
                                alt="Código QR de WhatsApp"
                                className="w-64 h-64"
                            />
                        </div>
                        <div className="text-center max-w-md">
                            <p className="text-gray-900 font-semibold text-lg mb-2">
                                Escanea este código con WhatsApp
                            </p>
                            <ol className="text-left text-sm text-gray-600 space-y-1">
                                <li>1. Abre WhatsApp en tu teléfono</li>
                                <li>2. Ve a Menú → Dispositivos vinculados</li>
                                <li>3. Toca "Vincular un dispositivo"</li>
                                <li>4. Escanea este código QR</li>
                            </ol>
                            <div className="mt-4 flex items-center gap-2 justify-center text-yellow-600">
                                <AlertTriangle className="w-4 h-4" />
                                <p className="text-xs">El código expira en ~60 segundos</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Estado: Conectado */}
                {serviceStatus === 'running' && (
                    <div className="flex flex-col items-center gap-4 py-12">
                        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center">
                            <CheckCircle className="w-12 h-12 text-green-600" />
                        </div>
                        <div className="text-center">
                            <p className="text-gray-900 font-semibold text-xl mb-2">
                                ¡Conectado exitosamente!
                            </p>
                            <p className="text-gray-600 text-sm">
                                WhatsApp está vinculado y funcionando
                            </p>
                        </div>
                    </div>
                )}

                {/* Estado: Error */}
                {(serviceStatus === 'error' || error) && (
                    <div className="flex flex-col items-center gap-4 py-12 text-center">
                        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
                            <XCircle className="w-10 h-10 text-red-600" />
                        </div>
                        <div>
                            <p className="text-gray-900 font-semibold text-xl mb-2">
                                Error de Conexión
                            </p>
                            <p className="text-gray-600 text-sm mb-4">
                                {error || 'No se pudo conectar con el servicio de WhatsApp'}
                            </p>
                            <p className="text-gray-500 text-xs">
                                Verifica que el contenedor Docker esté activo
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
