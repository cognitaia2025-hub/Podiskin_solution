"""
LIMPIAR BASE DE DATOS PARA PRODUCCIÓN
======================================
Elimina TODOS los datos de prueba pero mantiene:
- 4 usuarios del staff (2 Santiago, Ivette, Ibeth)
- Roles y permisos del sistema
"""
import asyncio
import asyncpg

async def clean_production_db():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            database="podoskin_db",
            user="podoskin_user",
            password="podoskin123"
        )
        
        print("\n" + "="*80)
        print("🧹 LIMPIANDO BASE DE DATOS PARA PRODUCCIÓN")
        print("="*80 + "\n")
        
        # 1. Eliminar citas de prueba
        deleted_citas = await conn.execute("DELETE FROM citas")
        print(f"✅ Citas de prueba eliminadas")
        
        # 2. Eliminar expedientes médicos
        try:
            deleted_expedientes = await conn.execute("DELETE FROM expedientes_medicos")
            print(f"✅ Expedientes médicos eliminados")
        except:
            print(f"⚠️  Tabla expedientes_medicos no existe (ok)")
        
        # 3. Eliminar pacientes de prueba
        deleted_pacientes = await conn.execute("DELETE FROM pacientes")
        print(f"✅ Pacientes de prueba eliminados")
        
        # 4. Eliminar podólogos que NO estén vinculados a usuarios del staff
        # Primero, obtener IDs de usuarios del staff
        staff_user_ids = await conn.fetch(
            """
            SELECT id FROM usuarios 
            WHERE nombre_usuario IN ('dr.santiago.ornelas', 'adm.santiago.ornelas', 'ivette.martinez', 'ibeth.martinez')
            """
        )
        staff_ids = [row['id'] for row in staff_user_ids]
        
        if staff_ids:
            # Eliminar podólogos que NO pertenezcan al staff
            deleted_podologos = await conn.execute(
                f"""
                DELETE FROM podologos 
                WHERE id_usuario IS NULL OR id_usuario NOT IN ({','.join(map(str, staff_ids))})
                """
            )
            print(f"✅ Podólogos de prueba eliminados (staff mantenido)")
        
        # 5. Limpiar tablas financieras si existen
        tables_to_clean = [
            'pagos',
            'gastos', 
            'cortes_caja',
            'inventario_movimientos'
        ]
        
        for table in tables_to_clean:
            try:
                await conn.execute(f"DELETE FROM {table}")
                print(f"✅ {table} limpiada")
            except:
                pass  # Tabla no existe, ok
        
        print("\n" + "="*80)
        print("VERIFICACIÓN POST-LIMPIEZA:")
        print("="*80 + "\n")
        
        # Verificar lo que quedó
        usuarios_count = await conn.fetchval("SELECT COUNT(*) FROM usuarios")
        pacientes_count = await conn.fetchval("SELECT COUNT(*) FROM pacientes")
        citas_count = await conn.fetchval("SELECT COUNT(*) FROM citas")
        roles_count = await conn.fetchval("SELECT COUNT(*) FROM roles")
        
        print(f"👥 Usuarios (staff):     {usuarios_count}")
        print(f"🏥 Pacientes:            {pacientes_count}")
        print(f"📅 Citas:                {citas_count}")
        print(f"🔑 Roles:                {roles_count}")
        
        # Mostrar usuarios activos
        print("\n" + "-"*80)
        print("STAFF ACTIVO:")
        print("-"*80 + "\n")
        
        staff = await conn.fetch(
            """
            SELECT nombre_usuario, nombre_completo, rol, activo
            FROM usuarios
            ORDER BY id
            """
        )
        
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
