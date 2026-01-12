/**
 * Servicio API para WhatsApp Management
 * ======================================
 * 
 * Funciones para interactuar con los endpoints del backend.
 */

import api from './api';
import type {
    // QR
    QRSessionCreate,
    QRSessionInfo,
    QRSessionUpdate,
    // Conversaciones
    ConversacionesResponse,
    ConversacionDetalle,
    DudaPendienteItem,
    RespuestaAdminCreate,
    // Aprendizajes
    AprendizajeAvanzadoItem,
    AprendizajesResponse,
    AprendizajeAvanzadoCreate,
    AprendizajeAvanzadoUpdate,
    EstadisticasAprendizaje,
} from '../types/whatsapp';

// ============================================================================
// QR Y SESIÓN
// ============================================================================

/**
 * Obtiene el QR actual desde el servicio Node.js
 * 
 * Este es el ÚNICO método correcto para obtener el QR.
 * El QR se genera automáticamente cuando el servicio inicia.
 * 
 * @returns Promise con el QR en base64 o null si no está disponible
 * @throws Error si el servicio no está disponible (503)
 */
export const fetchQRCode = async (): Promise<{ qr: string; timestamp: string } | null> => {
    try {
        const response = await api.get('/api/whatsapp-bridge/qr');
        // Respuesta 200: QR disponible
        return response.data;
    } catch (error: any) {
        if (error.response?.status === 404) {
            // QR no disponible aún (servicio iniciando)
            return null;
        }
        // Otros errores (503, 500, etc.)
        throw new Error(error.response?.data?.detail || 'Servicio WhatsApp no disponible');
    }
};

// ============================================================================
// FUNCIONES DEPRECADAS - NO USAR
// ============================================================================
// Las siguientes funciones usan endpoints incorrectos o lógica obsoleta.
// Se mantienen temporalmente para compatibilidad pero serán eliminadas.

/** @deprecated Use fetchQRCode() instead */
export const generarQRSession = async (
    data: QRSessionCreate = {}
): Promise<QRSessionInfo> => {
    console.warn('generarQRSession() está deprecado. Use fetchQRCode() en su lugar.');
    const response = await api.post('/api/whatsapp-bridge/qr', data);
    return response.data;
};

/** @deprecated Use fetchQRCode() instead */
export const getQREstado = async (sessionId: number): Promise<QRSessionInfo> => {
    console.warn('getQREstado() está deprecado. Use fetchQRCode() en su lugar.');
    const response = await api.get(`/api/whatsapp-bridge/qr`);
    return response.data;
};

/** @deprecated Use fetchQRCode() instead */
export const getQRActiva = async (): Promise<QRSessionInfo | null> => {
    console.warn('getQRActiva() está deprecado. Use fetchQRCode() en su lugar.');
    const response = await api.get('/api/whatsapp-bridge/qr');
    return response.data;
};

/** @deprecated No longer needed - Node.js handles state internally */
export const actualizarEstadoQR = async (
    sessionId: number,
    data: QRSessionUpdate
): Promise<QRSessionInfo> => {
    console.warn('actualizarEstadoQR() está deprecado y será eliminado.');
    const response = await api.post(`/api/whatsapp-bridge/qr`, data);
    return response.data;
};

// ============================================================================
// CONVERSACIONES
// ============================================================================

export const getConversaciones = async (
    limit: number = 50,
    estado?: string
): Promise<ConversacionesResponse> => {
    const params: any = { limit };
    if (estado) params.estado = estado;

    const response = await api.get('/api/whatsapp-bridge/conversaciones', { params });
    return response.data;
};

export const getConversacionDetalle = async (
    conversacionId: number
): Promise<ConversacionDetalle> => {
    const response = await api.get(`/whatsapp/conversaciones/${conversacionId}`);
    return response.data;
};

export const marcarConversacionAtendida = async (
    conversacionId: number,
    notas?: string
): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(
        `/whatsapp/conversaciones/${conversacionId}/marcar-atendida`,
        { notas }
    );
    return response.data;
};

export const actualizarNotasConversacion = async (
    conversacionId: number,
    notas: string
): Promise<{ success: boolean; message: string }> => {
    const response = await api.put(
        `/whatsapp/conversaciones/${conversacionId}/notas`,
        { notas }
    );
    return response.data;
};

// ============================================================================
// DUDAS ESCALADAS
// ============================================================================

export const getDudasEscaladas = async (
    soloPendientes: boolean = true
): Promise<DudaPendienteItem[]> => {
    const response = await api.get('/whatsapp/dudas-escaladas', {
        params: { solo_pendientes: soloPendientes }
    });
    return response.data;
};

export const responderDuda = async (
    dudaId: number,
    data: RespuestaAdminCreate
): Promise<{ success: boolean; message: string; aprendizaje_id?: number }> => {
    const response = await api.post(
        `/whatsapp/dudas-escaladas/${dudaId}/responder`,
        data
    );
    return response.data;
};

// ============================================================================
// APRENDIZAJES
// ============================================================================

export const getAprendizajes = async (
    page: number = 1,
    perPage: number = 20,
    categoria?: string,
    soloValidados: boolean = false
): Promise<AprendizajesResponse> => {
    const response = await api.get('/whatsapp/aprendizajes', {
        params: {
            page,
            per_page: perPage,
            categoria,
            solo_validados: soloValidados
        }
    });
    return response.data;
};

export const getAprendizaje = async (
    aprendizajeId: number
): Promise<AprendizajeAvanzadoItem> => {
    const response = await api.get(`/whatsapp/aprendizajes/${aprendizajeId}`);
    return response.data;
};

export const createAprendizaje = async (
    data: AprendizajeAvanzadoCreate
): Promise<AprendizajeAvanzadoItem> => {
    const response = await api.post('/whatsapp/aprendizajes', data);
    return response.data;
};

export const updateAprendizaje = async (
    aprendizajeId: number,
    data: AprendizajeAvanzadoUpdate
): Promise<AprendizajeAvanzadoItem> => {
    const response = await api.put(`/whatsapp/aprendizajes/${aprendizajeId}`, data);
    return response.data;
};

export const deleteAprendizaje = async (
    aprendizajeId: number
): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/whatsapp/aprendizajes/${aprendizajeId}`);
    return response.data;
};

export const getEstadisticasAprendizaje = async (): Promise<EstadisticasAprendizaje> => {
    const response = await api.get('/whatsapp/aprendizajes/estadisticas/general');
    return response.data;
};

export const registrarUsoAprendizaje = async (
    aprendizajeId: number,
    fueUtil: boolean = true
): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(
        `/whatsapp/aprendizajes/${aprendizajeId}/registrar-uso`,
        { fue_util: fueUtil }
    );
    return response.data;
};

// ============================================================================
// HELPERS Y UTILIDADES
// ============================================================================

/**
 * Hook personalizado para polling de estado de QR
 */
export const useQRPolling = (
    sessionId: number | null,
    interval: number = 2000,
    onConnected?: () => void
) => {
    const [estado, setEstado] = React.useState<QRSessionInfo | null>(null);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        if (!sessionId) return;

        const poll = async () => {
            try {
                const session = await getQREstado(sessionId);
                setEstado(session);

                if (session.estado === 'conectado') {
                    onConnected?.();
                }
            } catch (err: any) {
                setError(err.message);
            }
        };

        poll(); // Primera llamada inmediata
        const intervalId = setInterval(poll, interval);

        return () => clearInterval(intervalId);
    }, [sessionId, interval, onConnected]);

    return { estado, error };
};

/**
 * Formatea una fecha relativa (ej: "hace 5 minutos")
 */
export const formatearFechaRelativa = (fecha: string): string => {
    const ahora = new Date();
    const fechaObj = new Date(fecha);
    const diff = ahora.getTime() - fechaObj.getTime();

    const segundos = Math.floor(diff / 1000);
    const minutos = Math.floor(segundos / 60);
    const horas = Math.floor(minutos / 60);
    const dias = Math.floor(horas / 24);

    if (dias > 0) return `hace ${dias} día${dias > 1 ? 's' : ''}`;
    if (horas > 0) return `hace ${horas} hora${horas > 1 ? 's' : ''}`;
    if (minutos > 0) return `hace ${minutos} minuto${minutos > 1 ? 's' : ''}`;
    return 'hace un momento';
};

/**
 * Obtiene el color de badge según el sentimiento
 */
export const getSentimientoColor = (sentimiento?: string): string => {
    switch (sentimiento) {
        case 'positivo':
            return 'green';
        case 'negativo':
            return 'red';
        case 'urgente':
            return 'orange';
        default:
            return 'gray';
    }
};

/**
 * Obtiene el color de badge según el tono
 */
export const getTonoColor = (tono?: string): string => {
    switch (tono) {
        case 'molesto':
            return 'red';
        case 'contento':
            return 'green';
        case 'urgente':
            return 'orange';
        case 'confundido':
            return 'yellow';
        case 'agradecido':
            return 'blue';
        case 'impaciente':
            return 'purple';
        default:
            return 'gray';
    }
};

// Importar React para el hook
import React from 'react';
