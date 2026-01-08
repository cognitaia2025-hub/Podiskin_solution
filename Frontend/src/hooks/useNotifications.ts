import { useState, useEffect, useRef, useCallback } from 'react';

interface Notification {
  id: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  referencia_id: string | null;
  referencia_tipo: string | null;
  fecha_envio: string;
  leido: boolean;
}

interface WebSocketMessage {
  type: string;
  count?: number;
  data?: Notification;
  notifications?: Notification[];
  message?: string;
  timestamp?: string;
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  markAsRead: (notificationId: number) => void;
  refreshNotifications: () => void;
}

/**
 * Hook personalizado para gestionar notificaciones en tiempo real con WebSocket
 */
export const useNotifications = (token: string | null): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);

  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000; // 3 segundos

  /**
   * Conectar al WebSocket
   */
  const connect = useCallback(() => {
    if (!token) return;

    // Evitar múltiples conexiones
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = `ws://localhost:8000/ws/notifications?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('[WebSocket] Conectado al servidor de notificaciones');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;

        // Solicitar notificaciones recientes
        ws.send(JSON.stringify({ action: 'get_recent', limit: 20 }));
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'connected':
              console.log('[WebSocket] Bienvenida:', message.message);
              break;

            case 'count':
              // Actualizar contador de no leídas
              setUnreadCount(message.count || 0);
              break;

            case 'notification':
              // Nueva notificación recibida
              if (message.data) {
                setNotifications(prev => [message.data!, ...prev]);
                // Reproducir sonido o mostrar toast (opcional)
                console.log('[WebSocket] Nueva notificación:', message.data.titulo);
              }
              break;

            case 'recent_notifications':
              // Lista de notificaciones recientes
              if (message.notifications) {
                setNotifications(message.notifications);
              }
              break;

            case 'mark_read_success':
              // Confirmación de marcar como leída
              setNotifications(prev =>
                prev.map(n =>
                  n.id === message.data?.id ? { ...n, leido: true } : n
                )
              );
              if (message.count !== undefined) {
                setUnreadCount(message.count);
              }
              break;

            case 'error':
              console.error('[WebSocket] Error:', message.message);
              break;

            default:
              console.log('[WebSocket] Mensaje desconocido:', message);
          }
        } catch (error) {
          console.error('[WebSocket] Error parseando mensaje:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error de conexión:', error);
      };

      ws.onclose = () => {
        console.log('[WebSocket] Conexión cerrada');
        setIsConnected(false);
        wsRef.current = null;

        // Intentar reconectar
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          console.log(
            `[WebSocket] Reintento ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS} en ${RECONNECT_DELAY}ms`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_DELAY);
        } else {
          console.error('[WebSocket] Máximo de reintentos alcanzado');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('[WebSocket] Error creando conexión:', error);
    }
  }, [token]);

  /**
   * Desconectar WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  /**
   * Marcar notificación como leída
   */
  const markAsRead = useCallback((notificationId: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: 'mark_read',
          notification_id: notificationId
        })
      );
    }
  }, []);

  /**
   * Refrescar lista de notificaciones
   */
  const refreshNotifications = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: 'get_recent',
          limit: 20
        })
      );
    }
  }, []);

  /**
   * Efecto: Conectar/desconectar WebSocket
   */
  useEffect(() => {
    if (token) {
      // Pequeño delay para evitar race condition al hacer login
      // Esto da tiempo a que el token esté completamente disponible
      const initialConnectionTimeout = setTimeout(() => {
        connect();
      }, 150);

      return () => {
        clearTimeout(initialConnectionTimeout);
        disconnect();
      };
    }

    return () => {
      disconnect();
    };
  }, [token, connect, disconnect]);

  return {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    refreshNotifications
  };
};
