"""
Servicio de Roles
==================
Lógica de negocio para gestión de roles.
"""

from typing import List, Optional, Dict, Any
from db import fetch_all, fetch_one, execute_returning


class RolesService:
    """Servicio para operaciones CRUD de roles."""

    async def get_all(self) -> List[Dict[str, Any]]:
        """Obtiene todos los roles."""
        query = """
            SELECT id, nombre_rol, descripcion, permisos, activo, fecha_creacion
            FROM roles
            ORDER BY id
        """
        return await fetch_all(query)

    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un rol por ID."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nombre_rol, descripcion, permisos, activo, fecha_creacion
            FROM roles WHERE id = %s
        """,
            (id,),
        )
        row = cur.fetchone()
        if row:
            columns = [
                "id",
                "nombre_rol",
                "descripcion",
                "permisos",
                "activo",
                "fecha_creacion",
            ]
            return dict(zip(columns, row))
        return None

    def create(
        self, nombre_rol: str, descripcion: str = None, permisos: dict = None
    ) -> Dict[str, Any]:
        """Crea un nuevo rol."""
        conn = self._get_connection()
        cur = conn.cursor()
        import json

        permisos_json = json.dumps(permisos) if permisos else "{}"
        cur.execute(
            """
            INSERT INTO roles (nombre_rol, descripcion, permisos, activo)
            VALUES (%s, %s, %s::jsonb, true)
            RETURNING id, nombre_rol, descripcion, permisos, activo, fecha_creacion
        """,
            (nombre_rol, descripcion, permisos_json),
        )
        row = cur.fetchone()
        conn.commit()
        columns = [
            "id",
            "nombre_rol",
            "descripcion",
            "permisos",
            "activo",
            "fecha_creacion",
        ]
        return dict(zip(columns, row))

    def update(
        self,
        id: int,
        nombre_rol: str = None,
        descripcion: str = None,
        permisos: dict = None,
        activo: bool = None,
    ) -> Optional[Dict[str, Any]]:
        """Actualiza un rol existente."""
        conn = self._get_connection()
        cur = conn.cursor()

        # Construir query dinámico
        updates = []
        params = []
        if nombre_rol is not None:
            updates.append("nombre_rol = %s")
            params.append(nombre_rol)
        if descripcion is not None:
            updates.append("descripcion = %s")
            params.append(descripcion)
        if permisos is not None:
            import json

            updates.append("permisos = %s::jsonb")
            params.append(json.dumps(permisos))
        if activo is not None:
            updates.append("activo = %s")
            params.append(activo)

        if not updates:
            return self.get_by_id(id)

        params.append(id)
        query = f"UPDATE roles SET {', '.join(updates)} WHERE id = %s RETURNING id, nombre_rol, descripcion, permisos, activo, fecha_creacion"
        cur.execute(query, params)
        row = cur.fetchone()
        conn.commit()
        if row:
            columns = [
                "id",
                "nombre_rol",
                "descripcion",
                "permisos",
                "activo",
                "fecha_creacion",
            ]
            return dict(zip(columns, row))
        return None

    def delete(self, id: int) -> bool:
        """Elimina un rol (soft delete - pone activo=false)."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE roles SET activo = false WHERE id = %s", (id,))
        conn.commit()
        return cur.rowcount > 0


# Singleton
roles_service = RolesService()
