"""
Módulo de análisis predictivo con Machine Learning
Usa scikit-learn para predicciones de demanda y forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class DemandPredictor:
    """
    Predictor de demanda de servicios usando ML
    """
    
    def __init__(self):
        self.model_linear = LinearRegression()
        self.model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    async def predecir_demanda_servicio(
        self, 
        datos_historicos: List[Dict[str, Any]], 
        meses_adelante: int = 3
    ) -> Dict[str, Any]:
        """
        Predice la demanda de un servicio para los próximos N meses
        
        Args:
            datos_historicos: Lista de dicts con {fecha, cantidad, ingresos}
            meses_adelante: Número de meses a predecir
            
        Returns:
            Dict con predicciones, intervalos de confianza y métricas
        """
        if len(datos_historicos) < 3:
            return {
                'error': 'Insuficientes datos históricos (mínimo 3 meses)',
                'predicciones': []
            }
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos_historicos)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Feature engineering
        df['mes_numero'] = df['fecha'].dt.month
        df['anio'] = df['fecha'].dt.year
        df['mes_indice'] = range(len(df))
        df['tendencia'] = df['cantidad'].rolling(window=3, min_periods=1).mean()
        df['estacionalidad'] = df.groupby('mes_numero')['cantidad'].transform('mean')
        
        # Preparar datos de entrenamiento
        X = df[['mes_indice', 'mes_numero', 'tendencia', 'estacionalidad']].values
        y = df['cantidad'].values
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Entrenar modelos
        self.model_linear.fit(X_scaled, y)
        self.model_rf.fit(X_scaled, y)
        
        # Generar predicciones para los próximos meses
        ultima_fecha = df['fecha'].max()
        predicciones = []
        
        for i in range(1, meses_adelante + 1):
            fecha_futura = ultima_fecha + pd.DateOffset(months=i)
            mes_numero = fecha_futura.month
            mes_indice = len(df) + i - 1
            
            # Calcular tendencia y estacionalidad proyectadas
            tendencia_proy = df['cantidad'].tail(3).mean()
            estacionalidad_proy = df[df['mes_numero'] == mes_numero]['cantidad'].mean() if len(df[df['mes_numero'] == mes_numero]) > 0 else df['cantidad'].mean()
            
            # Feature vector
            X_futuro = np.array([[mes_indice, mes_numero, tendencia_proy, estacionalidad_proy]])
            X_futuro_scaled = self.scaler.transform(X_futuro)
            
            # Predicción con ambos modelos
            pred_linear = self.model_linear.predict(X_futuro_scaled)[0]
            pred_rf = self.model_rf.predict(X_futuro_scaled)[0]
            
            # Promedio ponderado (RF tiene más peso)
            pred_final = 0.3 * pred_linear + 0.7 * pred_rf
            
            # Calcular intervalo de confianza (±15% empírico)
            intervalo_inferior = max(0, pred_final * 0.85)
            intervalo_superior = pred_final * 1.15
            
            predicciones.append({
                'fecha': fecha_futura.strftime('%Y-%m-%d'),
                'mes': fecha_futura.strftime('%B %Y'),
                'cantidad_predicha': round(pred_final, 1),
                'intervalo_inferior': round(intervalo_inferior, 1),
                'intervalo_superior': round(intervalo_superior, 1),
                'confianza': 0.85  # 85% de confianza empírica
            })
        
        # Calcular métricas de calidad del modelo
        y_pred_train = 0.3 * self.model_linear.predict(X_scaled) + 0.7 * self.model_rf.predict(X_scaled)
        mae = np.mean(np.abs(y - y_pred_train))
        mse = np.mean((y - y_pred_train) ** 2)
        rmse = np.sqrt(mse)
        
        # R² Score
        from sklearn.metrics import r2_score
        r2 = r2_score(y, y_pred_train)
        
        return {
            'predicciones': predicciones,
            'datos_historicos_usados': len(df),
            'metricas': {
                'mae': round(mae, 2),
                'rmse': round(rmse, 2),
                'r2_score': round(r2, 3),
                'precision_estimada': f"{max(0, min(100, (1 - mae / y.mean()) * 100)):.1f}%"
            },
            'tendencia': 'creciente' if df['cantidad'].iloc[-1] > df['cantidad'].mean() else 'decreciente'
        }


class FinancialForecaster:
    """
    Forecaster de ingresos usando series temporales
    """
    
    async def forecast_ingresos(
        self,
        datos_historicos: List[Dict[str, Any]],
        meses_adelante: int = 6
    ) -> Dict[str, Any]:
        """
        Predice ingresos futuros usando regresión y promedios móviles
        
        Args:
            datos_historicos: Lista con {fecha, ingresos, gastos}
            meses_adelante: Meses a proyectar
            
        Returns:
            Dict con forecast de ingresos, gastos y utilidad neta
        """
        if len(datos_historicos) < 6:
            return {
                'error': 'Insuficientes datos (mínimo 6 meses)',
                'forecast': []
            }
        
        # Convertir a DataFrame
        df = pd.DataFrame(datos_historicos)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Calcular utilidad neta histórica
        df['utilidad_neta'] = df['ingresos'] - df['gastos']
        df['margen_utilidad'] = (df['utilidad_neta'] / df['ingresos']) * 100
        
        # Feature engineering temporal
        df['mes_indice'] = range(len(df))
        df['mes_numero'] = df['fecha'].dt.month
        df['ingresos_ma3'] = df['ingresos'].rolling(window=3, min_periods=1).mean()
        df['gastos_ma3'] = df['gastos'].rolling(window=3, min_periods=1).mean()
        
        # Modelo de regresión lineal para ingresos
        X = df[['mes_indice', 'mes_numero']].values
        y_ingresos = df['ingresos'].values
        y_gastos = df['gastos'].values
        
        model_ingresos = LinearRegression()
        model_gastos = LinearRegression()
        
        model_ingresos.fit(X, y_ingresos)
        model_gastos.fit(X, y_gastos)
        
        # Generar forecast
        ultima_fecha = df['fecha'].max()
        forecast = []
        
        for i in range(1, meses_adelante + 1):
            fecha_futura = ultima_fecha + pd.DateOffset(months=i)
            mes_numero = fecha_futura.month
            mes_indice = len(df) + i - 1
            
            X_futuro = np.array([[mes_indice, mes_numero]])
            
            # Predicción base
            ingresos_pred = model_ingresos.predict(X_futuro)[0]
            gastos_pred = model_gastos.predict(X_futuro)[0]
            
            # Ajuste por estacionalidad
            factor_estacional_ing = df[df['mes_numero'] == mes_numero]['ingresos'].mean() / df['ingresos'].mean() if len(df[df['mes_numero'] == mes_numero]) > 0 else 1.0
            factor_estacional_gas = df[df['mes_numero'] == mes_numero]['gastos'].mean() / df['gastos'].mean() if len(df[df['mes_numero'] == mes_numero]) > 0 else 1.0
            
            ingresos_pred *= factor_estacional_ing
            gastos_pred *= factor_estacional_gas
            
            # Asegurar valores positivos
            ingresos_pred = max(0, ingresos_pred)
            gastos_pred = max(0, gastos_pred)
            
            utilidad_pred = ingresos_pred - gastos_pred
            margen_pred = (utilidad_pred / ingresos_pred * 100) if ingresos_pred > 0 else 0
            
            forecast.append({
                'fecha': fecha_futura.strftime('%Y-%m-%d'),
                'mes': fecha_futura.strftime('%B %Y'),
                'ingresos_predichos': round(ingresos_pred, 2),
                'gastos_predichos': round(gastos_pred, 2),
                'utilidad_neta_predicha': round(utilidad_pred, 2),
                'margen_utilidad_predicho': round(margen_pred, 2),
                'intervalo_ingresos': {
                    'inferior': round(ingresos_pred * 0.90, 2),
                    'superior': round(ingresos_pred * 1.10, 2)
                }
            })
        
        # Métricas del modelo
        y_pred_ing = model_ingresos.predict(X)
        mae_ingresos = np.mean(np.abs(y_ingresos - y_pred_ing))
        
        return {
            'forecast': forecast,
            'metricas': {
                'datos_historicos': len(df),
                'mae_ingresos': round(mae_ingresos, 2),
                'tendencia_ingresos': 'creciente' if df['ingresos'].iloc[-1] > df['ingresos'].mean() else 'decreciente',
                'promedio_margen_utilidad': round(df['margen_utilidad'].mean(), 2)
            },
            'resumen_historico': {
                'ingresos_promedio': round(df['ingresos'].mean(), 2),
                'gastos_promedio': round(df['gastos'].mean(), 2),
                'utilidad_promedio': round(df['utilidad_neta'].mean(), 2),
                'mejor_mes': df.loc[df['ingresos'].idxmax(), 'fecha'].strftime('%B %Y'),
                'peor_mes': df.loc[df['ingresos'].idxmin(), 'fecha'].strftime('%B %Y')
            }
        }


class InventoryAnalyzer:
    """
    Analizador de inventario para alertas de reorden
    """
    
    async def analizar_puntos_reorden(
        self,
        productos: List[Dict[str, Any]],
        historial_movimientos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analiza inventario y genera alertas de reorden
        
        Args:
            productos: Lista de productos con stock actual, mínimo, máximo
            historial_movimientos: Historial de salidas para calcular rotación
            
        Returns:
            Dict con alertas, recomendaciones y análisis
        """
        alertas = []
        recomendaciones = []
        
        # Crear DataFrame de movimientos
        if historial_movimientos:
            df_mov = pd.DataFrame(historial_movimientos)
            df_mov['fecha'] = pd.to_datetime(df_mov['fecha'])
            
            # Calcular consumo promedio por producto (últimos 30 días)
            fecha_limite = datetime.now() - timedelta(days=30)
            df_reciente = df_mov[df_mov['fecha'] >= fecha_limite]
            
            consumo_diario = df_reciente.groupby('producto_id')['cantidad'].sum() / 30
            consumo_dict = consumo_diario.to_dict()
        else:
            consumo_dict = {}
        
        # Analizar cada producto
        for producto in productos:
            producto_id = producto['producto_id']
            stock_actual = producto['stock_actual']
            stock_minimo = producto['stock_minimo']
            stock_maximo = producto['stock_maximo']
            tiempo_reposicion = producto.get('tiempo_reposicion_dias', 7)
            
            # Punto de reorden = stock_minimo * 1.2
            punto_reorden = stock_minimo * 1.2
            
            # Calcular días de inventario restantes
            consumo_diario_producto = consumo_dict.get(producto_id, 0)
            if consumo_diario_producto > 0:
                dias_restantes = stock_actual / consumo_diario_producto
                cantidad_optima = consumo_diario_producto * (tiempo_reposicion + 7)  # Lead time + 1 semana buffer
            else:
                dias_restantes = float('inf')
                cantidad_optima = stock_maximo
            
            # Generar alertas según nivel de criticidad
            if stock_actual <= stock_minimo:
                alertas.append({
                    'producto_id': producto_id,
                    'codigo': producto['codigo_producto'],
                    'nombre': producto['nombre'],
                    'nivel': 'CRITICO',
                    'stock_actual': stock_actual,
                    'stock_minimo': stock_minimo,
                    'deficit': stock_minimo - stock_actual,
                    'dias_restantes': round(dias_restantes, 1) if dias_restantes != float('inf') else 'N/A',
                    'accion': 'ORDENAR INMEDIATAMENTE',
                    'cantidad_sugerida': max(stock_maximo - stock_actual, cantidad_optima)
                })
            elif stock_actual <= punto_reorden:
                alertas.append({
                    'producto_id': producto_id,
                    'codigo': producto['codigo_producto'],
                    'nombre': producto['nombre'],
                    'nivel': 'ADVERTENCIA',
                    'stock_actual': stock_actual,
                    'punto_reorden': punto_reorden,
                    'dias_restantes': round(dias_restantes, 1) if dias_restantes != float('inf') else 'N/A',
                    'accion': 'Planificar pedido pronto',
                    'cantidad_sugerida': cantidad_optima
                })
            
            # Generar recomendaciones de optimización
            if stock_actual > stock_maximo * 1.5:
                recomendaciones.append({
                    'producto_id': producto_id,
                    'nombre': producto['nombre'],
                    'tipo': 'EXCESO',
                    'stock_actual': stock_actual,
                    'stock_maximo': stock_maximo,
                    'exceso': stock_actual - stock_maximo,
                    'recomendacion': 'Reducir pedidos futuros o promocionar',
                    'costo_oportunidad': round((stock_actual - stock_maximo) * producto.get('costo_unitario', 0), 2)
                })
        
        # Ordenar alertas por nivel de criticidad
        alertas_criticas = [a for a in alertas if a['nivel'] == 'CRITICO']
        alertas_advertencia = [a for a in alertas if a['nivel'] == 'ADVERTENCIA']
        
        return {
            'alertas_criticas': alertas_criticas,
            'alertas_advertencia': alertas_advertencia,
            'recomendaciones': recomendaciones,
            'resumen': {
                'total_alertas': len(alertas),
                'criticos': len(alertas_criticas),
                'advertencias': len(alertas_advertencia),
                'productos_analizados': len(productos),
                'necesitan_reorden': len(alertas_criticas) + len(alertas_advertencia)
            }
        }


# Instancias globales
demand_predictor = DemandPredictor()
financial_forecaster = FinancialForecaster()
inventory_analyzer = InventoryAnalyzer()
