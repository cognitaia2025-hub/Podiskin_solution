"""Servicio de Horarios - Lógica de negocio."""

from typing import List, Optional
from db import fetch_all, fetch_one, execute_returning

DIAS_SEMANA = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

class HorariosService:
    """Servicio para gestión de horarios de trabajo."""
    
    async def get_all(self, id_podologo: Optional[int] = None, activo: Optional[bool] = None) -> List[dict]:
        """Obtiene todos los horarios, con filtros opcionales."""
        query = """
            SELECT 
                h.id, h.id_podologo, h.dia_semana,
                h.hora_inicio, h.hora_fin,
                h.duracion_cita_minutos, h.tiempo_buffer_minutos,
                h.max_citas_simultaneas, h.activo,
                h.fecha_inicio_vigencia, h.fecha_fin_vigencia,
                p.nombre_completo as nombre_podologo
            FROM horarios_trabajo h
            INNER JOIN podologos p ON h.id_podologo = p.id
            WHERE 1=1
        """
        params = []
        
        if id_podologo is not None:
            query += " AND h.id_podologo = $" + str(len(params) + 1)
            params.append(id_podologo)
        
        if activo is not None:
            query += " AND h.activo = $" + str(len(params) + 1)
            params.append(activo)
        
        query += " ORDER BY h.id_podologo, h.dia_semana, h.hora_inicio"
        horarios = await fetch_all(query, *params)
        
        # Agregar nombre del día
        for h in horarios:
            h['dia_semana_nombre'] = DIAS_SEMANA[h['dia_semana']]
            h['hora_inicio'] = str(h['hora_inicio'])
            h['hora_fin'] = str(h['hora_fin'])
        
        return horarios

    
    def get_by_id(self, horario_id: int) -> Optional[dict]:
        """Obtiene un horario por ID."""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        h.id, h.id_podologo, h.dia_semana,
                        h.hora_inicio, h.hora_fin,
                        h.duracion_cita_minutos, h.tiempo_buffer_minutos,
                        h.max_citas_simultaneas, h.activo,
                        h.fecha_inicio_vigencia, h.fecha_fin_vigencia,
                        p.nombre_completo as nombre_podologo
                    FROM horarios_trabajo h
                    INNER JOIN podologos p ON h.id_podologo = p.id
                    WHERE h.id = %s
                """, (horario_id,))
                
                horario = cur.fetchone()
                if horario:
                    horario['dia_semana_nombre'] = DIAS_SEMANA[horario['dia_semana']]
                    horario['hora_inicio'] = str(horario['hora_inicio'])
                    horario['hora_fin'] = str(horario['hora_fin'])
                
                return horario
        finally:
            conn.close()
    
    def create(self, horario_data: dict, creado_por: int) -> dict:
        """Crea un nuevo horario de trabajo."""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar que el podólogo existe y está activo
                cur.execute("""
                    SELECT id FROM podologos 
                    WHERE id = %s AND activo = true
                """, (horario_data['id_podologo'],))
                
                if not cur.fetchone():
                    raise ValueError(f"Podólogo con ID {horario_data['id_podologo']} no existe o está inactivo")
                
                # Validar que hora_fin > hora_inicio
                if horario_data['hora_fin'] <= horario_data['hora_inicio']:
                    raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
                
                # Crear el horario
                cur.execute("""
                    INSERT INTO horarios_trabajo (
                        id_podologo, dia_semana, hora_inicio, hora_fin,
                        duracion_cita_minutos, tiempo_buffer_minutos,
                        max_citas_simultaneas, activo,
                        fecha_inicio_vigencia, fecha_fin_vigencia, creado_por
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    horario_data['id_podologo'],
                    horario_data['dia_semana'],
                    horario_data['hora_inicio'],
                    horario_data['hora_fin'],
                    horario_data.get('duracion_cita_minutos', 30),
                    horario_data.get('tiempo_buffer_minutos', 5),
                    horario_data.get('max_citas_simultaneas', 1),
                    horario_data.get('activo', True),
                    horario_data.get('fecha_inicio_vigencia'),
                    horario_data.get('fecha_fin_vigencia'),
                    creado_por
                ))
                
                horario_id = cur.fetchone()['id']
                conn.commit()
                
                return self.get_by_id(horario_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update(self, horario_id: int, updates: dict) -> dict:
        """Actualiza un horario existente."""
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Verificar que el horario existe
                cur.execute("SELECT id FROM horarios_trabajo WHERE id = %s", (horario_id,))
                if not cur.fetchone():
                    raise ValueError(f"Horario con ID {horario_id} no encontrado")
                
                # Construir query de actualización
                set_clauses = []
                params = []
                
                for field, value in updates.items():
                    if value is not None:
                        set_clauses.append(f"{field} = %s")
                        params.append(value)
                
                if not set_clauses:
                    raise ValueError("No hay campos para actualizar")
                
                params.append(horario_id)
                query = f"""
                    UPDATE horarios_trabajo 
                    SET {', '.join(set_clauses)}
                    WHERE id = %s
                """
                
                cur.execute(query, params)
                conn.commit()
                
                return self.get_by_id(horario_id)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete(self, horario_id: int) -> bool:
        """Desactiva un horario (soft delete)."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE horarios_trabajo 
                    SET activo = false 
                    WHERE id = %s
                    RETURNING id
                """, (horario_id,))
                
                result = cur.fetchone()
                conn.commit()
                
                return result is not None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

horarios_service = HorariosService()
