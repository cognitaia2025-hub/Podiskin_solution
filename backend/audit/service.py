"""
Servicio de Auditoría - Registro de acciones del sistema
========================================================
Registra todas las acciones sensibles para trazabilidad.
"""

import psycopg
from psycopg.rows import dict_row
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
import logging
import json

logger = logging.getLogger(__name__)


class AuditService:
    """Servicio para gestión de auditoría."""
    
    def __init__(self):
        self.conn = None
    
    def _get_connection(self):
        """Obtiene conexión a la base de datos."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("DB_PORT", "5432")),
                dbname=os.getenv("DB_NAME", "podoskin_db"),
                user=os.getenv("DB_USER", "podoskin_user"),
                password=os.getenv("DB_PASSWORD", "podoskin_password_123"),
                row_factory=dict_row
            )
        return self.conn
    
    def log_action(
        self,
        usuario_id: int,
        accion: str,
        modulo: str,
        descripcion: str,
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> dict:
        """
        Registra una acción en el log de auditoría.
        
        Args:
            usuario_id: ID del usuario que realiza la acción
            accion: Tipo de acción (crear, actualizar, eliminar, etc.)
            modulo: Módulo del sistema (pagos, pacientes, usuarios, etc.)
            descripcion: Descripción legible de la acción
            datos_anteriores: Estado anterior del registro (opcional)
            datos_nuevos: Estado nuevo del registro (opcional)
            ip_address: Dirección IP del usuario (opcional)
            
        Returns:
            dict: Registro de auditoría creado
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Convertir datos a JSON si son dicts
                datos_ant_json = json.dumps(datos_anteriores) if datos_anteriores else None
                datos_new_json = json.dumps(datos_nuevos) if datos_nuevos else None
                
                cur.execute("""
                    INSERT INTO auditoria 
                    (usuario_id, accion, modulo, descripcion, datos_anteriores, datos_nuevos, ip_address)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
                    RETURNING id, usuario_id, accion, modulo, descripcion, fecha_hora
                """, (
                    usuario_id,
                    accion,
                    modulo,
                    descripcion,
                    datos_ant_json,
                    datos_new_json,
                    ip_address
                ))
                
                result = cur.fetchone()
                conn.commit()
                
                logger.info(
                    f"Auditoría registrada: {accion} en {modulo} por usuario {usuario_id}"
                )
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def get_logs(
        self,
        usuario_id: Optional[int] = None,
        modulo: Optional[str] = None,
        accion: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """
        Obtiene logs de auditoría con filtros.
        
        Args:
            usuario_id: Filtrar por ID de usuario
            modulo: Filtrar por módulo
            accion: Filtrar por tipo de acción
            fecha_desde: Filtrar desde fecha
            fecha_hasta: Filtrar hasta fecha
            limit: Número máximo de resultados
            offset: Offset para paginación
            
        Returns:
            dict: Lista de logs y total de registros
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                # Construir query dinámicamente
                conditions = []
                params = []
                
                if usuario_id:
                    conditions.append("a.usuario_id = %s")
                    params.append(usuario_id)
                
                if modulo:
                    conditions.append("a.modulo = %s")
                    params.append(modulo)
                
                if accion:
                    conditions.append("a.accion = %s")
                    params.append(accion)
                
                if fecha_desde:
                    conditions.append("a.fecha_hora >= %s")
                    params.append(fecha_desde)
                
                if fecha_hasta:
                    conditions.append("a.fecha_hora <= %s")
                    params.append(fecha_hasta)
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                # Query principal con JOIN a usuarios para obtener nombre
                query = f"""
                    SELECT 
                        a.id,
                        a.usuario_id,
                        u.nombre as usuario_nombre,
                        a.accion,
                        a.modulo,
                        a.descripcion,
                        a.datos_anteriores,
                        a.datos_nuevos,
                        a.ip_address,
                        a.fecha_hora
                    FROM auditoria a
                    LEFT JOIN usuarios u ON a.usuario_id = u.id
                    WHERE {where_clause}
                    ORDER BY a.fecha_hora DESC
                    LIMIT %s OFFSET %s
                """
                
                params.extend([limit, offset])
                cur.execute(query, params)
                logs = cur.fetchall()
                
                # Contar total
                count_query = f"""
                    SELECT COUNT(*) as total
                    FROM auditoria a
                    WHERE {where_clause}
                """
                cur.execute(count_query, params[:-2])  # Sin limit y offset
                total = cur.fetchone()['total']
                
                return {
                    "logs": [dict(log) for log in logs],
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo logs de auditoría: {e}")
            raise
    
    def get_user_activity(self, usuario_id: int, days: int = 30) -> list:
        """
        Obtiene resumen de actividad de un usuario.
        
        Args:
            usuario_id: ID del usuario
            days: Número de días hacia atrás
            
        Returns:
            list: Resumen de actividad por módulo
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cur:
                fecha_desde = datetime.now() - timedelta(days=days)
                
                cur.execute("""
                    SELECT 
                        modulo,
                        accion,
                        COUNT(*) as cantidad
                    FROM auditoria
                    WHERE usuario_id = %s AND fecha_hora >= %s
                    GROUP BY modulo, accion
                    ORDER BY cantidad DESC
                """, (usuario_id, fecha_desde))
                
                return [dict(row) for row in cur.fetchall()]
                
        except Exception as e:
            logger.error(f"Error obteniendo actividad de usuario: {e}")
            raise


# Instancia global del servicio
_audit_service = AuditService()


def log_action(
    usuario_id: int,
    accion: str,
    modulo: str,
    descripcion: str,
    datos_anteriores: Optional[Dict[str, Any]] = None,
    datos_nuevos: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> dict:
    """
    Función helper para registrar acciones en auditoría.
    
    Simplifica el uso del servicio de auditoría.
    """
    return _audit_service.log_action(
        usuario_id,
        accion,
        modulo,
        descripcion,
        datos_anteriores,
        datos_nuevos,
        ip_address
    )
