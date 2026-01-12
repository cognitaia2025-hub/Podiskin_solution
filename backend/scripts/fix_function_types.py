"""
Script para corregir el tipo de retorno de la función get_pacientes_podologo.
"""

import asyncio
import os
import psycopg
from psycopg.rows import dict_row


async def fix_function():
    """Ejecuta la corrección de tipos en la función de base de datos."""
    print("Conectando a la base de datos...")
    conn = await psycopg.AsyncConnection.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "podoskin_db"),
        user=os.getenv("DB_USER", "podoskin_user"),
        password=os.getenv("DB_PASSWORD"),  # Requerido en .env
        row_factory=dict_row,
        autocommit=True,
    )

    print("Ejecutando corrección de función...")
    try:
        async with conn.cursor() as cur:
            # Eliminar función anterior por si acaso cambia signatura de tipos
            # (CREATE OR REPLACE funciona bien si solo cambias tipos de retorno
            # TABLE en PG moderno, pero a veces es delicado si cambia la
            # estructura de retorno. Como es TABLE(...), CREATE OR REPLACE
            # debería reescribirla si los parámetros de ENTRADA son iguales.)

            # En este caso, solo cambio el tipo de una columna de salida.
            # A veces postgres se queja: "cannot change return type...".
            # Es mas seguro hacer DROP y luego CREATE.

            await cur.execute(
                "DROP FUNCTION IF EXISTS get_pacientes_podologo(INTEGER);"
            )

            # Usamos SQL raw multilínea
            sql = """
            CREATE OR REPLACE FUNCTION get_pacientes_podologo(
                p_podologo_id INTEGER
            )
            RETURNS TABLE (
                paciente_id BIGINT,  -- CAMBIADO DE INTEGER A BIGINT
                nombre_completo VARCHAR,
                telefono VARCHAR,
                ultimo_tratamiento TEXT,
                fecha_ultimo_tratamiento DATE,
                tiene_interino BOOLEAN,
                podologo_interino_id INTEGER,
                podologo_interino_nombre VARCHAR
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT
                    v.paciente_id,
                    v.paciente_nombre,
                    v.telefono,
                    v.ultimo_tratamiento,
                    v.fecha_ultimo_tratamiento,
                    (v.podologo_interino_id IS NOT NULL) as tiene_interino,
                    v.podologo_interino_id,
                    v.podologo_interino_nombre
                FROM v_pacientes_con_podologos v
                WHERE v.podologo_oficial_id = p_podologo_id
                ORDER BY v.paciente_nombre;
            END;
            $$ LANGUAGE plpgsql;
            """
            await cur.execute(sql)
            print("Función get_pacientes_podologo corregida exitosamente.")

    # pylint: disable=broad-exception-caught
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    if os.name == "nt":
        # pylint: disable=no-member, deprecated-method
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_function())
