import React, { useState, useRef, useEffect } from 'react';
import { useNotifications } from '../../hooks/useNotifications';
import { useAuth } from '../../auth/AuthContext';

/**
 * Panel de notificaciones en tiempo real
 * Muestra campana con badge y dropdown de notificaciones
 */
export const NotificationsPanel: React.FC = () => {
  const { token } = useAuth();
  const { notifications, unreadCount, isConnected, markAsRead, refreshNotifications } = 
    useNotifications(token);
  
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  /**
   * Cerrar dropdown al hacer clic fuera
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  /**
   * Manejar clic en notificación
   */
  const handleNotificationClick = (notificationId: number, leido: boolean) => {
    if (!leido) {
      markAsRead(notificationId);
    }
    // TODO: Navegar según referencia_tipo (cita, inventario, etc.)
  };

  /**
   * Formatear fecha relativa
   */
  const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Justo ahora';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours}h`;
    if (diffDays < 7) return `Hace ${diffDays}d`;
    
    return date.toLocaleDateString('es-MX', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  /**
   * Iconos según tipo de notificación
   */
  const getNotificationIcon = (tipo: string): string => {
    switch (tipo) {
      case 'recordatorio_cita_24h':
      case 'recordatorio_cita_2h':
        return '📅';
      case 'alerta_inventario':
        return '⚠️';
      case 'seguimiento_tratamiento':
        return '💊';
      default:
        return '🔔';
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Botón de campana */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
        aria-label="Notificaciones"
        aria-expanded={isOpen}
      >
        {/* Icono de campana */}
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Badge de contador */}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}

        {/* Indicador de conexión */}
        {!isConnected && (
          <span className="absolute bottom-0 right-0 block w-2 h-2 bg-yellow-400 border-2 border-white rounded-full"></span>
        )}
      </button>

      {/* Dropdown de notificaciones */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-[32rem] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50">
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-semibold text-gray-900">Notificaciones</h3>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
                  {unreadCount} nuevas
                </span>
              )}
            </div>
            
            <button
              onClick={refreshNotifications}
              className="text-gray-500 hover:text-gray-700 transition-colors"
              title="Actualizar"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>

          {/* Lista de notificaciones */}
          <div className="overflow-y-auto flex-1">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="text-sm">No hay notificaciones</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.map((notification: any) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification.id, notification.leido)}
                    className={`px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors ${
                      !notification.leido ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      {/* Icono */}
                      <div className="flex-shrink-0 text-2xl">
                        {getNotificationIcon(notification.tipo)}
                      </div>

                      {/* Contenido */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <p className={`text-sm font-medium truncate ${
                            !notification.leido ? 'text-gray-900' : 'text-gray-700'
                          }`}>
                            {notification.titulo}
                          </p>
                          <span className="ml-2 text-xs text-gray-500 flex-shrink-0">
                            {formatRelativeTime(notification.fecha_envio)}
                          </span>
                        </div>
                        
                        <p className="text-sm text-gray-600 whitespace-pre-wrap line-clamp-3">
                          {notification.mensaje}
                        </p>

                        {/* Indicador de no leída */}
                        {!notification.leido && (
                          <div className="mt-2">
                            <span className="inline-flex items-center text-xs text-blue-600 font-medium">
                              <span className="w-2 h-2 bg-blue-600 rounded-full mr-1.5"></span>
                              Sin leer
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => {
                  // TODO: Navegar a página de todas las notificaciones
                  setIsOpen(false);
                }}
                className="w-full text-center text-sm text-blue-600 hover:text-blue-700 font-medium py-1"
              >
                Ver todas las notificaciones
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
