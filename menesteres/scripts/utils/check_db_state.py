import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("=== ESTADO ACTUAL DE LA BASE DE DATOS ===\n")

# Verificar tablas
print("TABLAS:")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN (
        'consultas', 'diagnosticos', 'historial_cambios_expediente',
        'pacientes', 'alergias', 'signos_vitales', 'citas'
    )
    ORDER BY table_name
""")
for row in cur.fetchall():
    print(f"  ✅ {row[0]}")

# Verificar índices relacionados
print("\nÍNDICES RELACIONADOS CON DIAGNÓSTICOS:")
cur.execute("""
    SELECT indexname 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname LIKE '%diagnostico%'
    ORDER BY indexname
""")
for row in cur.fetchall():
    print(f"  - {row[0]}")

# Verificar vista materializada
print("\nVISTAS MATERIALIZADAS:")
cur.execute("""
    SELECT matviewname 
    FROM pg_matviews 
    WHERE schemaname = 'public'
""")
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f"  ✅ {row[0]}")
else:
    print("  ❌ Ninguna")

cur.close()
conn.close()
