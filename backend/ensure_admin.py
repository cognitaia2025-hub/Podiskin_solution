import os
import sys
from dotenv import load_dotenv
import psycopg
from passlib.context import CryptContext

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# MATCHING APP CONFIGURATION EXACTLY
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def create_admin_user():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://podoskin_user:podoskin_password_123@localhost:5432/podoskin_db",
    )

    conn = None
    try:
        conn = psycopg.connect(db_url)
        cur = conn.cursor()

        # 2. Check if admin exists
        cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = 'admin'")
        existing = cur.fetchone()

        pw_hash = get_password_hash("admin123")

        if existing:
            print("ℹ️ El usuario 'admin' ya existe. Actualizando contraseña y rol...")
            # Update password AND role to ensure it's Admin
            cur.execute(
                """
                UPDATE usuarios 
                SET password_hash = %s, rol = 'Admin', activo = true 
                WHERE nombre_usuario = 'admin'
            """,
                (pw_hash,),
            )
            conn.commit()
            print("✅ 'admin' actualizado correctamente (Pass: admin123, Rol: Admin)")
        else:
            # 3. Create admin user with text Role
            sql = """
                INSERT INTO usuarios (nombre_usuario, email, password_hash, rol, nombre_completo, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            try:
                cur.execute(
                    sql,
                    (
                        "admin",
                        "admin@podoskin.com",
                        pw_hash,
                        "Admin",
                        "Administrador",
                        True,
                    ),
                )
                conn.commit()
                print("✅ Usuario 'admin' creado exitosamente.")
            except Exception as insert_err:
                print(f"❌ Error insertando usuario: {insert_err}")
                print(f"SQL usada: {sql}")

        print("\n🔑 CREDENCIALES ACTUALIZADAS:")
        print("-------------------------------")
        print("👤 ADMIN:")
        print("   User: admin")
        print("   Pass: admin123")
        print("-------------------------------")

    except Exception as e:
        print(f"❌ Error General: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_admin_user()
