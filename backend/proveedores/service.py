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
            "direccion",
            "ciudad",
            "estado",
            "codigo_postal",
            "contacto_principal",
            "dias_credito",
            "activo",
            "notas",
            "fecha_registro",
        ]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nombre_comercial, razon_social, rfc, tipo_proveedor,
                   telefono, email, direccion, ciudad, estado, codigo_postal,
                   contacto_principal, dias_credito, activo, notas, fecha_registro
            FROM proveedores WHERE id = %s
        """,
            (id,),
        )
        row = cur.fetchone()
        if row:
            columns = [
                "id",
                "nombre_comercial",
                "razon_social",
                "rfc",
                "tipo_proveedor",
                "telefono",
                "email",
                "direccion",
                "ciudad",
                "estado",
                "codigo_postal",
                "contacto_principal",
                "dias_credito",
                "activo",
                "notas",
                "fecha_registro",
            ]
            return dict(zip(columns, row))
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO proveedores (
                nombre_comercial, razon_social, rfc, tipo_proveedor,
                telefono, email, direccion, ciudad, estado, codigo_postal,
                contacto_principal, dias_credito, activo, notas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, %s)
            RETURNING id
        """,
            (
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
            ),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        return self.get_by_id(new_id)

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Dict]:
        conn = self._get_connection()
        cur = conn.cursor()
        updates = []
        params = []
        for key, value in data.items():
            if value is not None:
                updates.append(f"{key} = %s")
                params.append(value)
        if not updates:
            return self.get_by_id(id)
        params.append(id)
        query = f"UPDATE proveedores SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, params)
        conn.commit()
        return self.get_by_id(id)

    def delete(self, id: int) -> bool:
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE proveedores SET activo = false WHERE id = %s", (id,))
        conn.commit()
        return cur.rowcount > 0


proveedores_service = ProveedoresService()
