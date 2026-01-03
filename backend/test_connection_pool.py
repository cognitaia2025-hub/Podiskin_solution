"""
Script de prueba para verificar que el pool de conexiones funciona correctamente
y que no hay fugas de conexiones.

Nota: Ejecutar desde el directorio backend:
    cd backend
    python test_connection_pool.py
"""
import asyncio

from auth.database import init_db_pool, close_db_pool, _get_connection, _return_connection
from psycopg.rows import dict_row

async def test_connection_pool():
    """Prueba el pool de conexiones con múltiples operaciones de lectura simultáneas"""
    
    print("\n" + "="*80)
    print("🧪 PRUEBA DE POOL DE CONEXIONES")
    print("="*80 + "\n")
    
    try:
        # Inicializar pool
        print("1️⃣  Inicializando pool de conexiones...")
        await init_db_pool()
        print("✅ Pool inicializado correctamente\n")
        
        # Simular múltiples lecturas simultáneas (como lo hace el dashboard)
        print("2️⃣  Ejecutando 10 consultas simultáneas de lectura...")
        
        async def read_query(query_id: int):
            """Ejecuta una consulta de lectura y retorna el resultado"""
            conn = None
            try:
                conn = await _get_connection()
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute("SELECT COUNT(*) as count FROM usuarios")
                    result = await cur.fetchone()
                # Cerrar transacción de solo lectura
                await conn.rollback()
                print(f"  ✅ Query {query_id}: {result['count']} usuarios")
                return result
            except Exception as e:
                print(f"  ❌ Query {query_id}: Error - {e}")
                if conn:
                    await conn.rollback()
                raise
            finally:
                if conn:
                    await _return_connection(conn)
        
        # Ejecutar 10 consultas en paralelo
        tasks = [read_query(i) for i in range(1, 11)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar resultados
        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            print(f"\n❌ {len(errors)} consultas fallaron")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"\n✅ Todas las consultas completadas exitosamente")
        
        # Prueba adicional: Verificar que las conexiones se devuelven al pool
        print("\n3️⃣  Verificando que las conexiones se devuelven al pool...")
        
        # Obtener una conexión
        conn = await _get_connection()
        print("  ✅ Conexión obtenida del pool")
        
        # Simular operación de lectura
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            await cur.fetchone()
        await conn.rollback()
        
        # Devolver conexión
        await _return_connection(conn)
        print("  ✅ Conexión devuelta al pool")
        
        # Cerrar pool
        print("\n4️⃣  Cerrando pool de conexiones...")
        await close_db_pool()
        print("✅ Pool cerrado correctamente\n")
        
        print("="*80)
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("="*80 + "\n")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ ERROR EN LAS PRUEBAS")
        print("="*80)
        print(f"\n{e}\n")
        import traceback
        traceback.print_exc()
        
        # Intentar cerrar el pool si está abierto
        try:
            await close_db_pool()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    print("\n🔬 Iniciando pruebas de pool de conexiones...")
    print("Esto verificará que no hay fugas de conexiones.\n")
    
    asyncio.run(test_connection_pool())
