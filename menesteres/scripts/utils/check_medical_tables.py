import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar a la base de datos
conn = psycopg.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Verificar qué tablas existen
print("=== VERIFICANDO TABLAS EXISTENTES ===\n")

tablas_necesarias = [
    'consultas',
    'diagnosticos', 
    'historial_cambios_expediente'
]

print("Tablas que deberían existir:")
for tabla in tablas_necesarias:
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
    """, (tabla,))
    existe = cur.fetchone()[0]
    status = "✅ EXISTE" if existe else "❌ NO EXISTE"
    print(f"  - {tabla}: {status}")

print("\n=== VERIFICANDO VISTA MATERIALIZADA ===\n")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM pg_matviews 
        WHERE schemaname = 'public' 
        AND matviewname = 'expedientes_medicos_resumen'
    )
""")
existe_vista = cur.fetchone()[0]
status_vista = "✅ EXISTE" if existe_vista else "❌ NO EXISTE"
print(f"  - expedientes_medicos_resumen: {status_vista}")

print("\n=== VERIFICANDO EXTENSIÓN pg_trgm ===\n")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM pg_extension 
        WHERE extname = 'pg_trgm'
    )
""")
existe_ext = cur.fetchone()[0]
status_ext = "✅ INSTALADA" if existe_ext else "❌ NO INSTALADA"
print(f"  - pg_trgm: {status_ext}")

cur.close()
conn.close()
