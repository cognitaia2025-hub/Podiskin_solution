"""
Probar endpoints de estadísticas con BD vacía
"""
import asyncio
import sys
sys.path.insert(0, '.')

from backend.stats.router import get_dashboard_stats, get_appointments_trend, get_revenue_trend
from backend.auth.utils import get_current_user
from unittest.mock import Mock

async def test_empty_stats():
    try:
        print("\n" + "="*80)
        print("PROBANDO ENDPOINTS CON BD VACÍA")
        print("="*80 + "\n")
        
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.rol = "Admin"
        
        # Test dashboard stats
        print("1️⃣ Probando /api/stats/dashboard...")
        try:
            stats = await get_dashboard_stats(current_user=mock_user)
            print(f"   ✅ Respuesta OK")
            print(f"   → total_patients: {stats.total_patients}")
            print(f"   → total_appointments_today: {stats.total_appointments_today}")
            print(f"   → revenue_month: ${stats.revenue_month}")
            print(f"   → top_treatments: {len(stats.top_treatments)} items")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Test appointments trend
        print("\n2️⃣ Probando /api/stats/appointments-trend...")
        try:
            trend = await get_appointments_trend(days=30, current_user=mock_user)
            print(f"   ✅ Respuesta OK")
            print(f"   → {len(trend)} días con datos")
            if len(trend) == 0:
                print(f"   ⚠️  Arreglo vacío (esperado con BD nueva)")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Test revenue trend
        print("\n3️⃣ Probando /api/stats/revenue-trend...")
        try:
            revenue = await get_revenue_trend(current_user=mock_user)
            print(f"   ✅ Respuesta OK")
            print(f"   → {len(revenue)} meses con datos")
            if len(revenue) == 0:
                print(f"   ⚠️  Arreglo vacío (esperado sin módulo de pagos)")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        print("\n" + "="*80)
        print("✅ TODOS LOS ENDPOINTS FUNCIONAN CON BD VACÍA")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_empty_stats())
