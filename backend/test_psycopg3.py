import psycopg

try:
    # Con password
    conn = psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="podoskin_db",
        user="podoskin_user",
        password="podoskin_password_123",
    )
    print("CONEXION psycopg3 OK!")

    # Probar una consulta simple
    cur = conn.cursor()
    cur.execute("SELECT 1 as test")
    result = cur.fetchone()
    print(f"Query result: {result}")

    conn.close()
    print("Conexion cerrada correctamente")
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error: {e}")
