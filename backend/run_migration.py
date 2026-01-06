"""
Script para ejecutar la migración de expedientes médicos
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener credenciales de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/podoskin_db")

def run_migration():
    try:
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        conn = psycopg.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        print("Leyendo archivo de migración...")
        with open("../data/06_expedientes_medicos.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Ejecutar el SQL
        print("Ejecutando migración...")
        cursor.execute(sql_content)
        conn.commit()
        print("✅ Migración ejecutada exitosamente")
        
        # Refrescar vista materializada
        print("\nRefrescando vista materializada...")
        cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY expedientes_medicos_resumen")
        conn.commit()
        print("✅ Vista materializada refrescada")
        
        # Verificar tablas creadas
        print("\nVerificando tablas creadas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('consultas', 'diagnosticos', 'historial_cambios_expediente')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print("\nTablas creadas:")
            for table in tables:
                print(f"  ✓ {table[0]}")
        
        # Verificar vista materializada
        cursor.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE matviewname = 'expedientes_medicos_resumen'
        """)
        view = cursor.fetchone()
        
        if view:
            print(f"\nVista materializada creada:")
            print(f"  ✓ {view[0]}")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\n📌 Próximos pasos:")
        print("1. Reiniciar el backend (Ctrl+C y luego python -m uvicorn main:app --reload)")
        print("2. Refrescar el frontend en el navegador (F5)")
        print("3. Probar la funcionalidad de expedientes médicos")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    run_migration()
