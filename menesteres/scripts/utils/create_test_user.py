"""
Script para crear un usuario de prueba en la base de datos.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from auth.jwt_handler import get_password_hash
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/podoskin_db")

def create_test_user():
    """Crea un usuario de prueba si no existe."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Verificar si existe el usuario
        cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s", ("dr.santiago",))
        existing = cur.fetchone()
        
        if existing:
            print("✅ Usuario 'dr.santiago' ya existe")
            cur.close()
            conn.close()
            return
        
        # Crear usuario de prueba
        password_hash = get_password_hash("password123")
        
        # Obtener el ID del rol 'Podologo'
        cur.execute("SELECT id FROM roles WHERE nombre_rol = %s", ("Podologo",))
        rol_result = cur.fetchone()
        
        if not rol_result:
            print("❌ Error: Rol 'Podologo' no encontrado en la tabla roles")
            cur.close()
            conn.close()
            sys.exit(1)
        
        id_rol = rol_result[0]
        
        cur.execute("""
            INSERT INTO usuarios (
                nombre_usuario, 
                password_hash, 
                email, 
                id_rol, 
                nombre_completo,
                activo
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            "dr.santiago",
            password_hash,
            "santiago@podoskin.com",
            id_rol,
            "Dr. Santiago Ornelas",
            True
        ))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"✅ Usuario de prueba creado exitosamente (ID: {user_id})")
        print("   Username: dr.santiago")
        print("   Password: password123")
        print("   Rol: Podologo")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_test_user()
