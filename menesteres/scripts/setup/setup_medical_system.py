"""
Script para crear tablas de expedientes médicos
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/podoskin_db")

def create_tables():
    try:
        print("Conectando a la base de datos...")
        conn = psycopg.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("\n📝 Creando tablas de expedientes médicos...")
        
        # 1. Tabla consultas
        print("  ✓ Creando tabla 'consultas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultas (
                id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                id_paciente bigint NOT NULL REFERENCES pacientes(id),
                id_podologo bigint NOT NULL REFERENCES usuarios(id),
                id_cita bigint REFERENCES citas(id),
                fecha_consulta timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                motivo_consulta text NOT NULL,
                sintomas text,
                exploracion_fisica text,
                plan_tratamiento text,
                indicaciones text,
                observaciones text,
                finalizada boolean DEFAULT false,
                fecha_finalizacion timestamp,
                fecha_registro timestamp DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Tabla diagnosticos
        print("  ✓ Creando tabla 'diagnosticos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnosticos (
                id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                id_consulta bigint NOT NULL REFERENCES consultas(id),
                id_paciente bigint NOT NULL REFERENCES pacientes(id),
                codigo_cie10 text,
                nombre_diagnostico text NOT NULL,
                tipo_diagnostico text DEFAULT 'Presuntivo' CHECK (tipo_diagnostico IN ('Presuntivo', 'Definitivo')),
                descripcion text,
                fecha_diagnostico date NOT NULL DEFAULT CURRENT_DATE,
                activo boolean DEFAULT true,
                fecha_registro timestamp DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Tabla historial_cambios_expediente
        print("  ✓ Creando tabla 'historial_cambios_expediente'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_cambios_expediente (
                id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                id_paciente bigint NOT NULL REFERENCES pacientes(id),
                seccion_modificada text NOT NULL,
                campo_modificado text NOT NULL,
                valor_anterior text,
                valor_nuevo text,
                modificado_por bigint NOT NULL REFERENCES usuarios(id),
                fecha_modificacion timestamp DEFAULT CURRENT_TIMESTAMP,
                motivo_cambio text
            )
        """)
        
        conn.commit()
        print("✅ Tablas creadas exitosamente")
        
        # 4. Crear índices
        print("\n📊 Creando índices...")
        indices = [
            ("idx_consultas_paciente", "consultas", "id_paciente"),
            ("idx_consultas_podologo", "consultas", "id_podologo"),
            ("idx_consultas_fecha", "consultas", "fecha_consulta DESC"),
            ("idx_consultas_finalizada", "consultas", "finalizada, fecha_consulta DESC"),
            ("idx_diagnosticos_paciente", "diagnosticos", "id_paciente"),
            ("idx_diagnosticos_consulta", "diagnosticos", "id_consulta"),
            ("idx_diagnosticos_activo", "diagnosticos", "id_paciente, activo"),
            ("idx_historial_paciente", "historial_cambios_expediente", "id_paciente, fecha_modificacion DESC"),
            ("idx_historial_usuario", "historial_cambios_expediente", "modificado_por"),
        ]
        
        for idx_name, table_name, columns in indices:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({columns})")
                print(f"  ✓ Índice '{idx_name}' creado")
            except Exception as e:
                print(f"  ⚠️  Índice '{idx_name}' ya existe")
        
        conn.commit()
        
        # 5. Crear vista materializada
        print("\n🔍 Creando vista materializada...")
        cursor.execute("DROP MATERIALIZED VIEW IF EXISTS expedientes_medicos_resumen CASCADE")
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
                (SELECT COUNT(*)::int FROM consultas WHERE id_paciente = p.id AND finalizada = true) as total_consultas,
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
        
        # 6. Crear función de refresco
        print("\n⚙️  Creando función de refresco...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION refrescar_expedientes_resumen()
            RETURNS void AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW CONCURRENTLY expedientes_medicos_resumen;
            EXCEPTION
                WHEN OTHERS THEN
                    REFRESH MATERIALIZED VIEW expedientes_medicos_resumen;
            END;
            $$ LANGUAGE plpgsql
        """)
        conn.commit()
        print("✅ Función creada")
        
        # 7. Habilitar extensión pg_trgm
        print("\n🔍 Habilitando extensión pg_trgm (búsqueda fuzzy)...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        conn.commit()
        print("✅ Extensión habilitada")
        
        # Verificar todo
        print("\n📋 Verificando instalación...")
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE activo = true")
        total_pacientes = cursor.fetchone()[0]
        print(f"  ✓ Total de pacientes activos: {total_pacientes}")
        
        cursor.execute("SELECT COUNT(*) FROM expedientes_medicos_resumen")
        total_resumen = cursor.fetchone()[0]
        print(f"  ✓ Pacientes en resumen: {total_resumen}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("🎉 SISTEMA DE EXPEDIENTES MÉDICOS INSTALADO CORRECTAMENTE")
        print("="*70)
        print("\n📌 TODO LISTO! Ahora puedes:")
        print("\n1️⃣  BACKEND:")
        print("   Si el backend está corriendo → Presiona Ctrl+C para detenerlo")
        print("   Luego ejecuta: python -m uvicorn main:app --reload --host 0.0.0.0")
        print("\n2️⃣  FRONTEND:")
        print("   Si el frontend está corriendo → Solo refresca el navegador (F5)")
        print("   Si no está corriendo → npm run dev")
        print("\n3️⃣  PROBAR:")
        print("   • Ve a 'Gestión Médica' → 'Atención Médica'")
        print("   • Se abrirá el modal para seleccionar paciente")
        print("   • Busca un paciente y selecciónalo")
        print("   • Se abrirá el formulario médico completo")
        print("\n✨ ¡Sistema listo para usar!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    create_tables()
