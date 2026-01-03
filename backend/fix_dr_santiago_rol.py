"""
Cambiar SOLO dr.santiago.ornelas a Podologo
"""
import asyncio
import asyncpg

async def fix_dr_santiago():
    try:
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            database="podoskin_db",
            user="podoskin_user",
            password="podoskin123"
        )
        
        print("\n🔧 Cambiando dr.santiago.ornelas a Podologo...")
        
        await conn.execute(
            """
            UPDATE usuarios 
            SET rol = 'Podologo' 
            WHERE nombre_usuario = 'dr.santiago.ornelas'
            """
        )
        
        # Verificar solo este usuario
        user = await conn.fetchrow(
            """
            SELECT nombre_usuario, rol 
            FROM usuarios 
            WHERE nombre_usuario = 'dr.santiago.ornelas'
            """
        )
        
        print(f"✅ Listo: {user['nombre_usuario']} → {user['rol']}\n")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(fix_dr_santiago())
