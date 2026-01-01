import traceback
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="podoskin_db",
        user="podoskin_user",
        password="podoskin_password_123",
    )
    print("Conexion exitosa!")
    conn.close()
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    traceback.print_exc()
