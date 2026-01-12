"""
Servicio de Roles
==================
Lógica de negocio para gestión de roles.
"""

from typing import List, Optional, Dict, Any
from db import fetch_all, fetch_one, execute_returning
import json


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

    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un rol por ID."""
        query = """
            SELECT id, nombre_rol, descripcion, permisos, activo, fecha_creacion
            FROM roles WHERE id = $1
        """
        return await fetch_one(query, id)

    async def create(
        self, nombre_rol: str, descripcion: str = None, permisos: dict = None
    ) -> Dict[str, Any]:
        """Crea un nuevo rol."""
        permisos_json = json.dumps(permisos) if permisos else "{}"
        query = """
            INSERT INTO roles (nombre_rol, descripcion, permisos, activo)
            VALUES ($1, $2, $3::jsonb, true)
            RETURNING id, nombre_rol, descripcion, permisos, activo, fecha_creacion
        """
        return await execute_returning(query, nombre_rol, descripcion, permisos_json)

    async def update(
        self,
        id: int,
        nombre_rol: str = None,
        descripcion: str = None,
        permisos: dict = None,
        activo: bool = None,
    ) -> Optional[Dict[str, Any]]:
        """Actualiza un rol existente."""
        updates = []
        params = []
        idx = 1
        if nombre_rol is not None:
            updates.append(f"nombre_rol = ${idx}")
            params.append(nombre_rol)
            idx += 1
        if descripcion is not None:
            updates.append(f"descripcion = ${idx}")
            params.append(descripcion)
            idx += 1
        if permisos is not None:
            updates.append(f"permisos = ${idx}::jsonb")
            params.append(json.dumps(permisos))
            idx += 1
        if activo is not None:
            updates.append(f"activo = ${idx}")
            params.append(activo)
            idx += 1

        if not updates:
            return await self.get_by_id(id)

        params.append(id)
        query = f"UPDATE roles SET {', '.join(updates)} WHERE id = ${idx} RETURNING id, nombre_rol, descripcion, permisos, activo, fecha_creacion"
        return await execute_returning(query, *params)

    async def delete(self, id: int) -> bool:
        """Elimina un rol (soft delete - pone activo=false)."""
        query = "UPDATE roles SET activo = false WHERE id = $1 RETURNING id"
        result = await execute_returning(query, id)
        return result is not None


# Singleton
roles_service = RolesService()
