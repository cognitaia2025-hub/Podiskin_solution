"""
Verificar cantidad de datos en la BD
"""
import asyncio
import asyncpg

async def check_data():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            database="podoskin_db",
            user="podoskin_user",
            password="podoskin123"
        )
        
        print("\n" + "="*80)
        print("DATOS EN LA BASE DE DATOS")
        print("="*80 + "\n")
        
        # Contar registros en cada tabla
        tables = [
            ('usuarios', 'Usuarios del sistema'),
            ('pacientes', 'Pacientes registrados'),
            ('citas', 'Citas programadas'),
            ('roles', 'Roles del sistema'),
            ('podologos', 'Podólogos registrados'),
        ]
        
        for table, description in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"📊 {description:30} → {count:4} registros")
            except Exception as e:
                print(f"❌ {description:30} → Error: {e}")
        
        print("\n" + "="*80)
        print("RECOMENDACIÓN PARA PRODUCCIÓN:")
        print("="*80)
        print("\n✓ MANTENER: usuarios (4) y roles (4)")
        print("❌ LIMPIAR: Si hay pacientes/citas de prueba, eliminarlos")
        print("\nUna app NUEVA debería tener SOLO usuarios reales y cero pacientes/citas.\n")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check_data())
