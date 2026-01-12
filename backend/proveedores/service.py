"""
Servicio de Proveedores
========================
Lógica de negocio para gestión de proveedores.
"""

from typing import List, Optional, Dict, Any
from db import fetch_all, fetch_one, execute_returning


class ProveedoresService:
    """Servicio para operaciones CRUD de proveedores."""

    async def get_all(self, activo: bool = None) -> List[Dict[str, Any]]:
        query = """
            SELECT id, nombre_comercial, razon_social, rfc, tipo_proveedor,
                   telefono, email, direccion, ciudad, estado, codigo_postal,
                   contacto_principal, dias_credito, activo, notas, fecha_registro
            FROM proveedores
        """
        if activo is not None:
            query += f" WHERE activo = {activo}"
        query += " ORDER BY nombre_comercial"
        return await fetch_all(query)

    async def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        query = """
            SELECT id, nombre_comercial, razon_social, rfc, tipo_proveedor,
                   telefono, email, direccion, ciudad, estado, codigo_postal,
                   contacto_principal, dias_credito, activo, notas, fecha_registro
            FROM proveedores WHERE id = $1
        """
        return await fetch_one(query, id)

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = """
            INSERT INTO proveedores (
                nombre_comercial, razon_social, rfc, tipo_proveedor,
                telefono, email, direccion, ciudad, estado, codigo_postal,
                contacto_principal, dias_credito, activo, notas
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, true, $13)
            RETURNING id, nombre_comercial, razon_social, rfc, tipo_proveedor,
                      telefono, email, direccion, ciudad, estado, codigo_postal,
                      contacto_principal, dias_credito, activo, notas, fecha_registro
        """
        return await execute_returning(
            query,
            data.get("nombre_comercial"),
            data.get("razon_social"),
            data.get("rfc"),
            data.get("tipo_proveedor"),
            data.get("telefono"),
            data.get("email"),
            data.get("direccion"),
            data.get("ciudad"),
            data.get("estado"),
            data.get("codigo_postal"),
            data.get("contacto_principal"),
            data.get("dias_credito", 0),
            data.get("notas"),
        )

    async def update(self, id: int, data: Dict[str, Any]) -> Optional[Dict]:
        updates = []
        params = []
        idx = 1
        for key, value in data.items():
            if value is not None:
                updates.append(f"{key} = ${idx}")
                params.append(value)
                idx += 1
        if not updates:
            return await self.get_by_id(id)
        params.append(id)
        query = f"""
            UPDATE proveedores SET {', '.join(updates)} 
            WHERE id = ${idx}
            RETURNING id, nombre_comercial, razon_social, rfc, tipo_proveedor,
                      telefono, email, direccion, ciudad, estado, codigo_postal,
                      contacto_principal, dias_credito, activo, notas, fecha_registro
        """
        return await execute_returning(query, *params)

    async def delete(self, id: int) -> bool:
        query = "UPDATE proveedores SET activo = false WHERE id = $1 RETURNING id"
        result = await execute_returning(query, id)
        return result is not None


proveedores_service = ProveedoresService()
