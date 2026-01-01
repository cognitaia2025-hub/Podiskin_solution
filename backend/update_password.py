import pg8000

# Conectar a la base de datos
conn = pg8000.connect(
    host="127.0.0.1",
    port=5432,
    database="podoskin_db",
    user="podoskin_user",
    password="podoskin_password_123",
)

# Hash bcrypt valido para 'password123'
import bcrypt

password_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
print(f"Hash generado: {password_hash}")

# Actualizar el usuario
cur = conn.cursor()
cur.execute(
    "UPDATE usuarios SET password_hash = %s WHERE nombre_usuario = %s",
    (password_hash, "dr.santiago"),
)
conn.commit()

# Verificar
cur.execute(
    "SELECT nombre_usuario, password_hash FROM usuarios WHERE nombre_usuario = 'dr.santiago'"
)
result = cur.fetchone()
print(f"Usuario: {result[0]}")
print(f"Hash en DB: {result[1]}")

conn.close()
print("Hash actualizado correctamente!")
