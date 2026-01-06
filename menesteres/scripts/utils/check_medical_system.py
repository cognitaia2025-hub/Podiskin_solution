"""
Script para verificar y refrescar expedientes médicos
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

# Obtener credenciales de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/podoskin_db")

def check_and_refresh():
    try:
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        conn = psycopg.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        print("\nVerificando tablas de expedientes médicos...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('consultas', 'diagnosticos', 'historial_cambios_expediente')
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print("\n✅ Tablas encontradas:")
            for table in tables:
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  ✓ {table[0]} ({count} registros)")
        else:
            print("⚠️  No se encontraron las tablas de expedientes médicos")
        
        # Verificar vista materializada
        print("\nVerificando vista materializada...")
        cursor.execute("""
            SELECT matviewname 
            FROM pg_matviews 
            WHERE matviewname = 'expedientes_medicos_resumen'
        """)
        view = cursor.fetchone()
        
        if view:
            print(f"✅ Vista materializada encontrada: {view[0]}")
            
            # Refrescar vista materializada
            print("\nRefrescando vista materializada...")
            try:
                cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY expedientes_medicos_resumen")
                conn.commit()
                print("✅ Vista materializada refrescada exitosamente")
            except Exception as e:
                # Si falla CONCURRENTLY, intentar sin él
                print(f"⚠️  Error con CONCURRENTLY: {e}")
                print("Intentando refrescar sin CONCURRENTLY...")
                cursor.execute("REFRESH MATERIALIZED VIEW expedientes_medicos_resumen")
                conn.commit()
                print("✅ Vista materializada refrescada")
            
            # Contar pacientes en la vista
            cursor.execute("SELECT COUNT(*) FROM expedientes_medicos_resumen")
            count = cursor.fetchone()[0]
            print(f"📊 Total de pacientes en resumen: {count}")
            
        else:
            print("⚠️  Vista materializada no encontrada")
            print("Intentando crear la vista...")
            cursor.execute("""
                CREATE MATERIALIZED VIEW expedientes_medicos_resumen AS
                SELECT 
                    p.id as paciente_id,
                    p.primer_nombre || ' ' || p.primer_apellido || COALESCE(' ' || p.segundo_apellido, '') as paciente_nombre,
                    p.fecha_nacimiento,
                    p.sexo,
                    p.telefono_principal as telefono,
                    p.email,
                    p.fecha_registro,
                    (SELECT MAX(fecha_consulta) FROM consultas WHERE id_paciente = p.id) as ultima_visita,
                    (SELECT COUNT(*) FROM consultas WHERE id_paciente = p.id AND finalizada = true) as total_consultas,
                    (SELECT COUNT(*) > 0 FROM alergias WHERE id_paciente = p.id AND activo = true) as tiene_alergias,
                    (SELECT nombre_diagnostico 
                     FROM diagnosticos 
                     WHERE id_paciente = p.id AND activo = true 
                     ORDER BY fecha_diagnostico DESC 
                     LIMIT 1) as diagnostico_reciente,
                    GREATEST(
                        p.fecha_modificacion,
                        (SELECT MAX(fecha_registro) FROM consultas WHERE id_paciente = p.id),
                        (SELECT MAX(fecha_registro) FROM alergias WHERE id_paciente = p.id),
                        (SELECT MAX(fecha_actualizacion) FROM estilo_vida WHERE id_paciente = p.id)
                    ) as fecha_ultima_actualizacion
                FROM pacientes p
                WHERE p.activo = true
            """)
            cursor.execute("CREATE UNIQUE INDEX expedientes_medicos_resumen_paciente_id_idx ON expedientes_medicos_resumen (paciente_id)")
            conn.commit()
            print("✅ Vista materializada creada")
        
        # Verificar función de refresco
        print("\nVerificando función de refresco...")
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_name = 'refrescar_expedientes_resumen'
        """)
        func = cursor.fetchone()
        
        if func:
            print(f"✅ Función encontrada: {func[0]}")
        else:
            print("⚠️  Función no encontrada, creando...")
            cursor.execute("""
                CREATE OR REPLACE FUNCTION refrescar_expedientes_resumen()
                RETURNS void AS $$
                BEGIN
                    REFRESH MATERIALIZED VIEW CONCURRENTLY expedientes_medicos_resumen;
                EXCEPTION
                    WHEN OTHERS THEN
                        REFRESH MATERIALIZED VIEW expedientes_medicos_resumen;
                END;
                $$ LANGUAGE plpgsql;
            """)
            conn.commit()
            print("✅ Función creada")
        
        # Verificar extensión pg_trgm
        print("\nVerificando extensión pg_trgm (para búsqueda fuzzy)...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        conn.commit()
        print("✅ Extensión pg_trgm habilitada")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("🎉 SISTEMA DE EXPEDIENTES MÉDICOS LISTO")
        print("="*70)
        print("\n📌 Ahora puedes:")
        print("1. ✅ Reiniciar el backend si está corriendo (Ctrl+C)")
        print("2. ✅ Iniciar con: python -m uvicorn main:app --reload --host 0.0.0.0")
        print("3. ✅ El frontend está listo, solo refresca el navegador (F5)")
        print("\n🔍 Endpoints disponibles:")
        print("   - GET  /api/medical-records/search?q={query}")
        print("   - GET  /api/medical-records/upcoming-appointments")
        print("   - GET  /api/medical-records/patients")
        print("   - GET  /api/medical-records/patients/{id}/record")
        print("   - POST /api/medical-records/patients/{id}/consultations")
        print("   - POST /api/medical-records/consultations/{id}/finalize")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    check_and_refresh()
