"""
LIMPIAR BASE DE DATOS PARA PRODUCCIÓN
======================================
Elimina TODOS los datos de prueba pero mantiene:
- 4 usuarios del staff (2 Santiago, Ivette, Ibeth)
- Roles y permisos del sistema
"""
import asyncio
import psycopg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "podoskin_db")
DB_USER = os.getenv("DB_USER", "podoskin_user")
# IMPORTANTE: Cambiar la contraseña en producción
DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is required. Please set it in your .env file.")

async def clean_production_db():
    try:
        # Construir connection string para psycopg
        conninfo = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
        conn = await psycopg.AsyncConnection.connect(conninfo)
        
        print("\n" + "="*80)
        print("🧹 LIMPIANDO BASE DE DATOS PARA PRODUCCIÓN")
        print("="*80 + "\n")
        
        # 1. Eliminar citas de prueba
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM citas")
            print(f"✅ Citas de prueba eliminadas")
        await conn.commit()
        
        # 2. Eliminar expedientes médicos
        try:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM expedientes_medicos")
                print(f"✅ Expedientes médicos eliminados")
            await conn.commit()
        except Exception as e:
            print(f"⚠️  Tabla expedientes_medicos no existe o error: {e}")
            await conn.rollback()
        
        # 3. Eliminar pacientes de prueba
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM pacientes")
            print(f"✅ Pacientes de prueba eliminados")
        await conn.commit()
        
        # 4. Eliminar podólogos que NO estén vinculados a usuarios del staff
        # Primero, obtener IDs de usuarios del staff
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT id FROM usuarios 
                WHERE nombre_usuario IN ('dr.santiago.ornelas', 'adm.santiago.ornelas', 'ivette.martinez', 'ibeth.martinez')
                """
            )
            staff_user_ids = await cur.fetchall()
        
        staff_ids = [row[0] for row in staff_user_ids]
        
        if staff_ids:
            # Eliminar podólogos que NO pertenezcan al staff
            async with conn.cursor() as cur:
                placeholders = ','.join(['%s'] * len(staff_ids))
                await cur.execute(
                    f"""
                    DELETE FROM podologos 
                    WHERE id_usuario IS NULL OR id_usuario NOT IN ({placeholders})
                    """,
                    staff_ids
                )
                print(f"✅ Podólogos de prueba eliminados (staff mantenido)")
            await conn.commit()
        
        # 5. Limpiar tablas financieras si existen
        # Nota: Usamos nombres de tabla de una lista controlada (no de entrada de usuario)
        # por lo que no hay riesgo de SQL injection aquí
        tables_to_clean = [
            'pagos',
            'gastos', 
            'cortes_caja',
            'inventario_movimientos'
        ]
        
        for table in tables_to_clean:
            try:
                async with conn.cursor() as cur:
                    # Tabla viene de lista controlada, no de entrada de usuario
                    query = f"DELETE FROM {table}"
                    await cur.execute(query)
                    print(f"✅ {table} limpiada")
                await conn.commit()
            except Exception as e:
                print(f"⚠️  Tabla {table} no existe o error: {e}")
                await conn.rollback()
        
        print("\n" + "="*80)
        print("VERIFICACIÓN POST-LIMPIEZA:")
        print("="*80 + "\n")
        
        # Verificar lo que quedó
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM usuarios")
            usuarios_count = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COUNT(*) FROM pacientes")
            pacientes_count = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COUNT(*) FROM citas")
            citas_count = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COUNT(*) FROM roles")
            roles_count = (await cur.fetchone())[0]
        
        print(f"👥 Usuarios (staff):     {usuarios_count}")
        print(f"🏥 Pacientes:            {pacientes_count}")
        print(f"📅 Citas:                {citas_count}")
        print(f"🔑 Roles:                {roles_count}")
        
        # Mostrar usuarios activos
        print("\n" + "-"*80)
        print("STAFF ACTIVO:")
        print("-"*80 + "\n")
        
        from psycopg.rows import dict_row
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """
                SELECT nombre_usuario, nombre_completo, rol, activo
                FROM usuarios
                ORDER BY id
                """
            )
            staff = await cur.fetchall()
        
        for user in staff:
            status = "✅" if user['activo'] else "❌"
            print(f"{status} {user['nombre_completo']:30} → {user['rol']:15} ({user['nombre_usuario']})")
        
        print("\n" + "="*80)
        print("✅ BASE DE DATOS LISTA PARA PRODUCCIÓN")
        print("="*80)
        print("\nLa clínica puede empezar a trabajar con la app limpia.\n")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de prueba")
    print("Mantendrá SOLO al staff (4 usuarios) y roles del sistema")
    print("\nPresiona ENTER para continuar o Ctrl+C para cancelar...")
    input()
    
    asyncio.run(clean_production_db())
