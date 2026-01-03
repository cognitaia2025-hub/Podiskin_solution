"""
Actualizar contraseñas de Ibeth e Ivette
"""
import asyncio
import asyncpg
import bcrypt

async def update_passwords():
    try:
        # Generar hash para Ibeth.Martinez.123
        password = "Ibeth.Martinez.123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = await asyncpg.connect(
            host="127.0.0.1",
            port=5432,
            database="podoskin_db",
            user="podoskin_user",
            password="podoskin123"
        )
        
        print("\n🔐 Actualizando contraseñas...")
        
        # Actualizar ivette.martinez
        await conn.execute(
            """
            UPDATE usuarios 
            SET password_hash = $1 
            WHERE nombre_usuario = 'ivette.martinez'
            """,
            password_hash
        )
        print("✅ ivette.martinez → Ibeth.Martinez.123")
        
        # Actualizar ibeth.martinez
        await conn.execute(
            """
            UPDATE usuarios 
            SET password_hash = $1 
            WHERE nombre_usuario = 'ibeth.martinez'
            """,
            password_hash
        )
        print("✅ ibeth.martinez → Ibeth.Martinez.123")
        
        print("\n✅ Contraseñas actualizadas\n")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_passwords())
