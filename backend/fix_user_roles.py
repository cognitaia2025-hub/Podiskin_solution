"""
Script para corregir los roles de los usuarios
"""
import asyncio
import asyncpg

async def fix_roles():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            database="podoskin_db",
            user="podoskin_user",
            password="podoskin123"
        )
        
        print("\n" + "="*80)
        print("CORRIGIENDO ROLES Y CREANDO USUARIO PODÓLOGA")
        print("="*80)
        
        # 1. Corregir adm.santiago.ornelas a Admin (no Podologo)
        await conn.execute(
            """
            UPDATE usuarios 
            SET rol = 'Admin' 
            WHERE nombre_usuario = 'adm.santiago.ornelas'
            """
        )
        print(f"✅ adm.santiago.ornelas corregido a Admin")
        
        # 2. Verificar si ya existe ibeth.martinez
        existing_ibeth = await conn.fetchval(
            "SELECT COUNT(*) FROM usuarios WHERE nombre_usuario = 'ibeth.martinez'"
        )
        
        if existing_ibeth == 0:
            # Crear nuevo usuario Ibeth como Podóloga
            await conn.execute(
                """
                INSERT INTO usuarios (
                    nombre_usuario, 
                    password_hash,
                    nombre_completo, 
                    email, 
                    rol,
                    activo,
                    fecha_registro
                )
                VALUES ($1, $2, $3, $4, $5, true, NOW())
                """,
                'ibeth.martinez',
                # Password: Santiago.Ornelas.123 (mismo hash que los otros)
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyE8FqjKOW8m',
                'Ibeth Martínez García',
                'ibeth@podoskin.com',
                'Podologo'
            )
            print(f"✅ Usuario ibeth.martinez creado como Podóloga")
        else:
            # Actualizar rol si ya existe
            await conn.execute(
                """
                UPDATE usuarios 
                SET rol = 'Podologo',
                    nombre_completo = 'Ibeth Martínez García',
                    email = 'ibeth@podoskin.com'
                WHERE nombre_usuario = 'ibeth.martinez'
                """
            )
            print(f"✅ Usuario ibeth.martinez actualizado a Podóloga")
        
        # Verificar los cambios
        print("\n" + "-"*80)
        print("VERIFICACIÓN FINAL DE USUARIOS:")
        print("-"*80)
        
        users = await conn.fetch(
            """
            SELECT id, nombre_usuario, nombre_completo, rol, activo 
            FROM usuarios 
            WHERE nombre_usuario IN ('dr.santiago.ornelas', 'adm.santiago.ornelas', 'ivette.martinez', 'ibeth.martinez')
            ORDER BY id
            """
        )
        
        for user in users:
            print(f"\n{user['nombre_completo']}")
            print(f"  Username: {user['nombre_usuario']}")
            print(f"  Rol: {user['rol']}")
            print(f"  Activo: {user['activo']}")
        
        print("\n" + "="*80)
        print("✅ ROLES CORREGIDOS EXITOSAMENTE")
        print("="*80 + "\n")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_roles())
