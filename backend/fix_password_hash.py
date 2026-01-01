"""
Script para regenerar hash de password del usuario de prueba con PBKDF2
"""

import pg8000
from passlib.context import CryptContext

# Configurar PBKDF2 (igual que en auth/utils.py)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Conectar a la base de datos
conn = pg8000.connect(
    host="127.0.0.1",
    port=5432,
    database="podoskin_db",
    user="podoskin_user",
    password="podoskin_password_123",
)
cursor = conn.cursor()

# Password de prueba
plain_password = "password123"
username = "dr.santiago"

# Generar nuevo hash
new_hash = pwd_context.hash(plain_password)

# Actualizar en base de datos
cursor.execute(
    "UPDATE usuarios SET password_hash = %s WHERE nombre_usuario = %s",
    (new_hash, username),
)

# Verificar
cursor.execute(
    "SELECT nombre_usuario, password_hash FROM usuarios WHERE nombre_usuario = %s",
    (username,),
)
result = cursor.fetchone()

print(f"✅ Password actualizado para usuario: {result[0]}")
print(f"   Nuevo hash: {result[1][:50]}...")

conn.commit()
conn.close()
