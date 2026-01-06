"""
Script para verificar los usuarios en la base de datos
"""
import asyncio
import asyncpg

async def check_users():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            database="podoskin_db",
            user="podoskin_user",
            password="podoskin123"
        )
        
        print("\n" + "="*80)
        print("VERIFICACIÓN DE USUARIOS")
        print("="*80)
        
        # Primero verificar el schema de la tabla usuarios
        schema_query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' 
            ORDER BY ordinal_position
        """
        schema = await conn.fetch(schema_query)
        print("\nSCHEMA DE LA TABLA 'usuarios':")
        print("-" * 40)
        for col in schema:
            print(f"{col['column_name']}: {col['data_type']}")
        
        # Verificar usuarios principales (usando rol como texto)
        query = """
            SELECT 
                u.id, 
                u.nombre_usuario, 
                u.email, 
                u.rol,
                u.activo
            FROM usuarios u
            WHERE u.nombre_usuario IN ('dr.santiago.ornelas', 'adm.santiago.ornelas', 'ivette.martinez')
            ORDER BY u.id
        """
        
        users = await conn.fetch(query)
        
        if not users:
            print("\n❌ NO SE ENCONTRARON USUARIOS")
        else:
            print(f"\n✅ ENCONTRADOS {len(users)} USUARIOS:\n")
            for user in users:
                print(f"ID: {user['id']}")
                print(f"Username: {user['nombre_usuario']}")
                print(f"Email: {user['email']}")
                print(f"Rol: {user['rol']}")
                print(f"Activo: {user['activo']}")
                print("-" * 40)
        
        # Verificar tabla roles
        print("\nROLES DISPONIBLES EN LA BD:")
        print("-" * 40)
        roles = await conn.fetch("SELECT id, nombre_rol FROM roles ORDER BY id")
        for role in roles:
            print(f"ID: {role['id']} - {role['nombre_rol']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_users())
