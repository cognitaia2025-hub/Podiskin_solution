"""
Script para actualizar contraseñas de usuarios Ornelas
"""
import psycopg
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar passlib igual que en la app
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Configuración de DB
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "podoskin_db")
DB_USER = os.getenv("DB_USER", "podoskin_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")

# Generar hash de la contraseña
password = "Santiago.Ornelas.123"
password_hash = pwd_context.hash(password)

print(f"Hash generado: {password_hash}")
print(f"Longitud del hash: {len(password_hash)}")

# Conectar a la base de datos
conn = psycopg.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

try:
    with conn.cursor() as cur:
        # Actualizar ambos usuarios
        cur.execute(
            """
            UPDATE usuarios 
            SET password_hash = %s
            WHERE nombre_usuario IN ('adm.santiago.ornelas', 'dr.santiago.ornelas')
            """,
            (password_hash,)
        )
        
        conn.commit()
        print(f"✅ Contraseñas actualizadas para ambos usuarios Ornelas")
        
        # Verificar
        cur.execute(
            """
            SELECT nombre_usuario, LEFT(password_hash, 30) as hash_preview
            FROM usuarios 
            WHERE nombre_usuario IN ('adm.santiago.ornelas', 'dr.santiago.ornelas')
            """
        )
        
        print("\n📋 Usuarios actualizados:")
        for row in cur.fetchall():
            print(f"  - {row[0]}: {row[1]}...")
            
finally:
    conn.close()

print("\n✅ Script completado")
print(f"\n🔑 Credenciales de prueba:")
print(f"   Usuario: adm.santiago.ornelas")
print(f"   Email: santiago.ornelas@podoskin.com")
print(f"   Teléfono: +52 686 189 2910")
print(f"   Contraseña: {password}")
