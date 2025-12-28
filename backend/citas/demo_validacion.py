"""
Ejemplo de uso del módulo de citas - Podoskin Solution
======================================================

Este script demuestra cómo usar el módulo de citas y validar
la funcionalidad de gestión de conflictos.
"""

import asyncio
from datetime import datetime, timedelta
import os

# Configurar path para importar módulos
import sys
sys.path.insert(0, "/home/runner/work/Podiskin_solution/Podiskin_solution/backend")

from citas import service


async def demo_validacion_conflictos():
    """
    Demuestra la validación de conflictos de horario.
    """
    print("=" * 70)
    print("DEMOSTRACIÓN: Validación de Conflictos de Horario")
    print("=" * 70)
    
    # Inicializar conexión a base de datos
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/podoskin"
    )
    
    try:
        service.init_db_pool(database_url)
        print("✅ Conexión a base de datos establecida\n")
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print("\nNOTA: Este es un ejemplo de validación. La base de datos debe estar configurada.")
        return
    
    # Ejemplo 1: Verificar disponibilidad
    print("\n1️⃣  VERIFICAR DISPONIBILIDAD")
    print("-" * 70)
    
    id_podologo = 1
    fecha = datetime.now().date() + timedelta(days=1)  # Mañana
    
    print(f"📅 Consultando disponibilidad del podólogo {id_podologo} para {fecha}")
    
    try:
        disponibilidad = await service.obtener_disponibilidad(id_podologo, fecha)
        
        print(f"\n✅ Podólogo: {disponibilidad['podologo']['nombre_completo']}")
        print(f"📆 Fecha: {disponibilidad['fecha']}")
        print(f"\n📊 Slots disponibles:")
        
        slots_disponibles = [s for s in disponibilidad['slots'] if s['disponible']]
        slots_ocupados = [s for s in disponibilidad['slots'] if not s['disponible']]
        
        print(f"   • Disponibles: {len(slots_disponibles)}")
        print(f"   • Ocupados: {len(slots_ocupados)}")
        
        # Mostrar primeros 5 slots disponibles
        print(f"\n🕐 Primeros 5 slots disponibles:")
        for slot in slots_disponibles[:5]:
            print(f"   • {slot['hora']} ✓")
        
    except ValueError as e:
        print(f"⚠️  Error de validación: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Ejemplo 2: Crear cita exitosa
    print("\n\n2️⃣  CREAR CITA EXITOSA")
    print("-" * 70)
    
    fecha_hora_inicio = datetime.now() + timedelta(days=1, hours=10)  # Mañana a las 10:00
    
    print(f"📝 Intentando crear cita:")
    print(f"   • Paciente ID: 1")
    print(f"   • Podólogo ID: 1")
    print(f"   • Fecha/Hora: {fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}")
    print(f"   • Tipo: Consulta")
    
    try:
        cita = await service.crear_cita(
            id_paciente=1,
            id_podologo=1,
            fecha_hora_inicio=fecha_hora_inicio,
            tipo_cita="Consulta",
            motivo_consulta="Dolor en el talón derecho",
            notas_recepcion="Primera consulta del paciente"
        )
        
        print(f"\n✅ Cita creada exitosamente!")
        print(f"   • ID: {cita['id']}")
        print(f"   • Estado: {cita['estado']}")
        print(f"   • Es primera vez: {cita['es_primera_vez']}")
        print(f"   • Inicio: {cita['fecha_hora_inicio']}")
        print(f"   • Fin: {cita['fecha_hora_fin']}")
        
        cita_id = cita['id']
        
    except ValueError as e:
        print(f"⚠️  Error de validación: {e}")
        cita_id = None
    except Exception as e:
        print(f"❌ Error: {e}")
        cita_id = None
    
    # Ejemplo 3: Intentar crear cita con conflicto
    print("\n\n3️⃣  VALIDAR DETECCIÓN DE CONFLICTO")
    print("-" * 70)
    
    if cita_id:
        print(f"🔄 Intentando crear otra cita en el mismo horario:")
        print(f"   • Paciente ID: 2")
        print(f"   • Podólogo ID: 1 (mismo podólogo)")
        print(f"   • Fecha/Hora: {fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')} (mismo horario)")
        
        try:
            cita_conflicto = await service.crear_cita(
                id_paciente=2,
                id_podologo=1,
                fecha_hora_inicio=fecha_hora_inicio,
                tipo_cita="Consulta",
                motivo_consulta="Consulta de seguimiento"
            )
            
            print(f"\n❌ ERROR: No se detectó el conflicto! Esto no debería pasar.")
            
        except ValueError as e:
            print(f"\n✅ Conflicto detectado correctamente!")
            print(f"   • Mensaje: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    else:
        print("⏭️  Saltando prueba (no se pudo crear la cita inicial)")
    
    # Ejemplo 4: Cancelar cita
    print("\n\n4️⃣  CANCELAR CITA")
    print("-" * 70)
    
    if cita_id:
        print(f"🗑️  Cancelando cita ID {cita_id}")
        
        try:
            cita_cancelada = await service.cancelar_cita(
                id_cita=cita_id,
                motivo_cancelacion="Demostración completada - Prueba de validación"
            )
            
            print(f"\n✅ Cita cancelada exitosamente!")
            print(f"   • Estado: {cita_cancelada['estado']}")
            print(f"   • Motivo: {cita_cancelada['motivo_cancelacion']}")
            
        except ValueError as e:
            print(f"⚠️  Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⏭️  Saltando prueba (no se creó cita para cancelar)")
    
    # Cerrar conexión
    service.close_db_pool()
    print("\n" + "=" * 70)
    print("DEMOSTRACIÓN COMPLETADA")
    print("=" * 70)


async def main():
    """Función principal."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         PODOSKIN SOLUTION - MÓDULO DE CITAS                        ║")
    print("║         Demostración de Validación de Conflictos                   ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    await demo_validacion_conflictos()
    
    print("\n")
    print("📚 RESUMEN DE FUNCIONALIDADES IMPLEMENTADAS:")
    print("   ✓ GET /citas - Lista de citas con filtros")
    print("   ✓ GET /citas/{id} - Obtener cita por ID")
    print("   ✓ POST /citas - Crear nueva cita")
    print("   ✓ PUT /citas/{id} - Actualizar cita")
    print("   ✓ DELETE /citas/{id} - Cancelar cita")
    print("   ✓ GET /citas/disponibilidad - Consultar horarios disponibles")
    print("\n")
    print("🔒 VALIDACIONES IMPLEMENTADAS:")
    print("   ✓ Verificar existencia de paciente y podólogo")
    print("   ✓ Validar fecha mínima (1 hora de anticipación)")
    print("   ✓ Detectar conflictos de horario")
    print("   ✓ Evitar múltiples citas del mismo paciente el mismo día")
    print("   ✓ Cálculo automático de duración (30 minutos)")
    print("   ✓ Determinar si es primera vez del paciente")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
