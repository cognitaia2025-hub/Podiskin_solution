"""
Router para análisis predictivo y forecasting
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta
from typing import Optional

from auth import get_current_user
from db import get_db_connection_citas
from analytics.predictor import (
    demand_predictor,
    financial_forecaster,
    inventory_analyzer
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/predicciones-demanda")
async def predecir_demanda_servicio(
    servicio_id: Optional[int] = Query(None, description="ID del servicio a predecir"),
    meses_adelante: int = Query(3, ge=1, le=12, description="Meses a predecir"),
    current_user: dict = Depends(get_current_user)
):
    """
    Predice la demanda de un servicio específico o todos los servicios
    usando modelos de Machine Learning
    """
    conn = await get_db_connection_citas()
    
    try:
        # Si se especifica servicio_id, predecir solo ese servicio
        if servicio_id:
            # Obtener datos históricos del servicio
            datos_historicos = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('month', c.fecha_cita) as fecha,
                    COUNT(*) as cantidad,
                    SUM(COALESCE(p.monto, cs.precio_base, 0)) as ingresos
                FROM citas c
                LEFT JOIN pagos p ON c.cita_id = p.cita_id
                LEFT JOIN catalogo_servicios cs ON c.tratamiento_id = cs.servicio_id
                WHERE c.tratamiento_id = $1
                  AND c.fecha_cita >= NOW() - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', c.fecha_cita)
                ORDER BY fecha
            """, servicio_id)
            
            if not datos_historicos:
                raise HTTPException(
                    status_code=404,
                    detail="No hay datos históricos suficientes para este servicio"
                )
            
            # Obtener nombre del servicio
            servicio_info = await conn.fetchrow("""
                SELECT servicio_id, nombre, categoria
                FROM catalogo_servicios
                WHERE servicio_id = $1
            """, servicio_id)
            
            # Convertir a lista de dicts
            datos = [
                {
                    'fecha': d['fecha'],
                    'cantidad': int(d['cantidad']),
                    'ingresos': float(d['ingresos'])
                }
                for d in datos_historicos
            ]
            
            # Generar predicción
            prediccion = await demand_predictor.predecir_demanda_servicio(
                datos, meses_adelante
            )
            
            return {
                'servicio': {
                    'servicio_id': servicio_info['servicio_id'],
                    'nombre': servicio_info['nombre'],
                    'categoria': servicio_info['categoria']
                },
                **prediccion
            }
        
        else:
            # Predecir demanda agregada de todos los servicios
            datos_historicos = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('month', c.fecha_cita) as fecha,
                    COUNT(*) as cantidad,
                    SUM(COALESCE(p.monto, 0)) as ingresos
                FROM citas c
                LEFT JOIN pagos p ON c.cita_id = p.cita_id
                WHERE c.fecha_cita >= NOW() - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', c.fecha_cita)
                ORDER BY fecha
            """)
            
            datos = [
                {
                    'fecha': d['fecha'],
                    'cantidad': int(d['cantidad']),
                    'ingresos': float(d['ingresos'])
                }
                for d in datos_historicos
            ]
            
            prediccion = await demand_predictor.predecir_demanda_servicio(
                datos, meses_adelante
            )
            
            return {
                'servicio': 'TODOS_LOS_SERVICIOS',
                **prediccion
            }
            
    finally:
        await conn.close()


@router.get("/forecast-ingresos")
async def forecast_ingresos_mensuales(
    meses_adelante: int = Query(6, ge=1, le=12),
    current_user: dict = Depends(get_current_user)
):
    """
    Forecast de ingresos, gastos y utilidad neta para los próximos meses
    usando series temporales y regresión
    """
    conn = await get_db_connection_citas()
    
    try:
        # Obtener datos históricos de ingresos y gastos por mes
        datos_historicos = await conn.fetch("""
            WITH ingresos_mensuales AS (
                SELECT 
                    DATE_TRUNC('month', fecha_pago) as fecha,
                    SUM(monto) as ingresos
                FROM pagos
                WHERE fecha_pago >= NOW() - INTERVAL '18 months'
                GROUP BY DATE_TRUNC('month', fecha_pago)
            ),
            gastos_mensuales AS (
                SELECT 
                    DATE_TRUNC('month', fecha_gasto) as fecha,
                    SUM(monto) as gastos
                FROM gastos
                WHERE fecha_gasto >= NOW() - INTERVAL '18 months'
                GROUP BY DATE_TRUNC('month', fecha_gasto)
            )
            SELECT 
                COALESCE(i.fecha, g.fecha) as fecha,
                COALESCE(i.ingresos, 0) as ingresos,
                COALESCE(g.gastos, 0) as gastos
            FROM ingresos_mensuales i
            FULL OUTER JOIN gastos_mensuales g ON i.fecha = g.fecha
            ORDER BY fecha
        """)
        
        if len(datos_historicos) < 6:
            raise HTTPException(
                status_code=400,
                detail="Insuficientes datos históricos (mínimo 6 meses)"
            )
        
        datos = [
            {
                'fecha': d['fecha'],
                'ingresos': float(d['ingresos']),
                'gastos': float(d['gastos'])
            }
            for d in datos_historicos
        ]
        
        # Generar forecast
        forecast = await financial_forecaster.forecast_ingresos(
            datos, meses_adelante
        )
        
        return forecast
        
    finally:
        await conn.close()


@router.get("/alertas-reorden")
async def obtener_alertas_reorden(
    incluir_recomendaciones: bool = Query(True),
    current_user: dict = Depends(get_current_user)
):
    """
    Analiza el inventario y genera alertas de reorden automático
    basadas en consumo histórico y puntos de reorden
    """
    conn = await get_db_connection_citas()
    
    try:
        # Obtener todos los productos activos
        productos = await conn.fetch("""
            SELECT 
                producto_id,
                codigo_producto,
                nombre,
                categoria,
                stock_actual,
                stock_minimo,
                stock_maximo,
                tiempo_reposicion_dias,
                costo_unitario
            FROM inventario_productos
            WHERE activo = TRUE
            ORDER BY categoria, nombre
        """)
        
        # Obtener historial de movimientos (salidas) de los últimos 90 días
        historial = await conn.fetch("""
            SELECT 
                producto_id,
                fecha_movimiento as fecha,
                ABS(cantidad_movimiento) as cantidad
            FROM stock_movements
            WHERE tipo_movimiento = 'salida'
              AND fecha_movimiento >= NOW() - INTERVAL '90 days'
            ORDER BY fecha_movimiento DESC
        """)
        
        # Convertir a listas de dicts
        productos_data = [
            {
                'producto_id': p['producto_id'],
                'codigo_producto': p['codigo_producto'],
                'nombre': p['nombre'],
                'categoria': p['categoria'],
                'stock_actual': float(p['stock_actual']),
                'stock_minimo': float(p['stock_minimo']),
                'stock_maximo': float(p['stock_maximo']),
                'tiempo_reposicion_dias': p['tiempo_reposicion_dias'] or 7,
                'costo_unitario': float(p['costo_unitario']) if p['costo_unitario'] else 0
            }
            for p in productos
        ]
        
        historial_data = [
            {
                'producto_id': h['producto_id'],
                'fecha': h['fecha'],
                'cantidad': float(h['cantidad'])
            }
            for h in historial
        ]
        
        # Analizar y generar alertas
        resultado = await inventory_analyzer.analizar_puntos_reorden(
            productos_data, historial_data
        )
        
        # Filtrar recomendaciones si no se solicitan
        if not incluir_recomendaciones:
            resultado.pop('recomendaciones', None)
        
        return resultado
        
    finally:
        await conn.close()


@router.get("/metricas-predictivas")
async def obtener_metricas_predictivas(
    current_user: dict = Depends(get_current_user)
):
    """
    Dashboard consolidado con todas las métricas predictivas:
    - Demanda de servicios top 5
    - Forecast financiero
    - Alertas de inventario
    """
    conn = await get_db_connection_citas()
    
    try:
        # Top 5 servicios más demandados
        top_servicios = await conn.fetch("""
            SELECT 
                cs.servicio_id,
                cs.nombre,
                COUNT(c.cita_id) as total_citas
            FROM catalogo_servicios cs
            JOIN citas c ON cs.servicio_id = c.tratamiento_id
            WHERE c.fecha_cita >= NOW() - INTERVAL '6 months'
            GROUP BY cs.servicio_id, cs.nombre
            ORDER BY total_citas DESC
            LIMIT 5
        """)
        
        # Forecast de demanda para top 3 servicios
        predicciones_servicios = []
        for servicio in top_servicios[:3]:
            datos_hist = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('month', fecha_cita) as fecha,
                    COUNT(*) as cantidad
                FROM citas
                WHERE tratamiento_id = $1
                  AND fecha_cita >= NOW() - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', fecha_cita)
                ORDER BY fecha
            """, servicio['servicio_id'])
            
            if len(datos_hist) >= 3:
                datos = [{'fecha': d['fecha'], 'cantidad': int(d['cantidad']), 'ingresos': 0} for d in datos_hist]
                pred = await demand_predictor.predecir_demanda_servicio(datos, 3)
                
                predicciones_servicios.append({
                    'servicio': servicio['nombre'],
                    'prediccion_proximo_mes': pred['predicciones'][0]['cantidad_predicha'] if pred.get('predicciones') else None
                })
        
        # Forecast financiero (3 meses)
        datos_financieros = await conn.fetch("""
            WITH ingresos AS (
                SELECT DATE_TRUNC('month', fecha_pago) as fecha, SUM(monto) as ingresos
                FROM pagos WHERE fecha_pago >= NOW() - INTERVAL '12 months'
                GROUP BY 1
            ),
            gastos AS (
                SELECT DATE_TRUNC('month', fecha_gasto) as fecha, SUM(monto) as gastos
                FROM gastos WHERE fecha_gasto >= NOW() - INTERVAL '12 months'
                GROUP BY 1
            )
            SELECT COALESCE(i.fecha, g.fecha) as fecha,
                   COALESCE(i.ingresos, 0) as ingresos,
                   COALESCE(g.gastos, 0) as gastos
            FROM ingresos i FULL OUTER JOIN gastos g ON i.fecha = g.fecha
            ORDER BY fecha
        """)
        
        forecast_fin = None
        if len(datos_financieros) >= 6:
            datos_fin = [
                {'fecha': d['fecha'], 'ingresos': float(d['ingresos']), 'gastos': float(d['gastos'])}
                for d in datos_financieros
            ]
            forecast_fin = await financial_forecaster.forecast_ingresos(datos_fin, 3)
        
        # Alertas de inventario
        productos = await conn.fetch("SELECT * FROM inventario_productos WHERE activo = TRUE")
        historial = await conn.fetch("""
            SELECT producto_id, fecha_movimiento as fecha, ABS(cantidad_movimiento) as cantidad
            FROM stock_movements WHERE tipo_movimiento = 'salida' AND fecha_movimiento >= NOW() - INTERVAL '30 days'
        """)
        
        productos_data = [
            {
                'producto_id': p['producto_id'], 'codigo_producto': p['codigo_producto'],
                'nombre': p['nombre'], 'categoria': p['categoria'],
                'stock_actual': float(p['stock_actual']), 'stock_minimo': float(p['stock_minimo']),
                'stock_maximo': float(p['stock_maximo']), 'tiempo_reposicion_dias': p['tiempo_reposicion_dias'] or 7,
                'costo_unitario': float(p['costo_unitario'] or 0)
            }
            for p in productos
        ]
        
        historial_data = [
            {'producto_id': h['producto_id'], 'fecha': h['fecha'], 'cantidad': float(h['cantidad'])}
            for h in historial
        ]
        
        alertas_inv = await inventory_analyzer.analizar_puntos_reorden(productos_data, historial_data)
        
        return {
            'top_servicios': [
                {
                    'servicio_id': s['servicio_id'],
                    'nombre': s['nombre'],
                    'citas_6_meses': s['total_citas']
                }
                for s in top_servicios
            ],
            'predicciones_demanda': predicciones_servicios,
            'forecast_financiero': forecast_fin['forecast'][:3] if forecast_fin else [],
            'alertas_inventario': {
                'criticas': len(alertas_inv['alertas_criticas']),
                'advertencias': len(alertas_inv['alertas_advertencia']),
                'top_3_criticos': alertas_inv['alertas_criticas'][:3]
            }
        }
        
    finally:
        await conn.close()
