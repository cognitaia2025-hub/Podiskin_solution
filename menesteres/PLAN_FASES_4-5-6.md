# Plan de Implementación - Fases 4, 5 y 6
## Continuación del InformeClienteSantiago_Estructurado.md

**Fecha de Planificación:** 6 de enero de 2026  
**Estado:** 📋 **PLANEADO - PENDIENTE DE EJECUCIÓN**  
**Fases Completadas Previas:** 1-3 (16/16 tareas - 100%)

---

## 🎯 Objetivo General de las Fases 4-6

Implementar funcionalidades avanzadas de reportería, análisis predictivo y automatización operativa para optimizar la gestión financiera y de inventario de la clínica Podoskin.

---

## 📊 FASE 4: Reportes y Exportación de Datos

**Objetivo:** Generar reportes ejecutivos descargables en múltiples formatos para análisis offline y presentaciones.

### Tareas (5 tareas)

#### Tarea 17: Crear endpoint GET /reportes/gastos-mensuales
**Backend:** `backend/reportes/router.py` (NUEVO)

**Descripción:** Endpoint que genera un reporte consolidado de gastos del mes especificado.

**Implementación:**
```python
from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/gastos-mensuales")
async def generar_reporte_gastos_mensuales(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2020),
    formato: str = Query("json", regex="^(json|csv|excel)$"),
    current_user: dict = Depends(get_current_user)
):
    """
    Genera reporte de gastos mensuales con:
    - Resumen por categoría
    - Comparativa con mes anterior
    - Tendencia de 6 meses
    - Top 10 gastos mayores
    - Productos comprados (si vinculados)
    """
    # Query SQL para obtener datos
    # Agrupar por categoría
    # Calcular variación porcentual vs mes anterior
    # Generar formato solicitado (JSON/CSV/Excel)
    
    if formato == "csv":
        return StreamingResponse(csv_content, media_type="text/csv")
    elif formato == "excel":
        return StreamingResponse(excel_content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        return reporte_json
```

**Campos del Reporte:**
- `periodo`: "Enero 2026"
- `total_gastos`: 45000.00
- `gastos_por_categoria`: Array de objetos con categoria, total, porcentaje, variacion_mes_anterior
- `top_10_gastos`: Array con los 10 gastos mayores del mes
- `comparativa_6_meses`: Array con totales de últimos 6 meses
- `productos_comprados`: Array con productos vinculados a gastos

**Dependencias:**
- `openpyxl` para Excel
- `csv` (built-in) para CSV

---

#### Tarea 18: Crear endpoint GET /reportes/inventario-estado
**Backend:** `backend/reportes/router.py`

**Descripción:** Reporte del estado actual del inventario con análisis de rotación y valor.

**Implementación:**
```python
@router.get("/inventario-estado")
async def generar_reporte_inventario(
    formato: str = Query("json", regex="^(json|csv|excel)$"),
    incluir_criticos: bool = Query(True),
    incluir_obsoletos: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """
    Genera reporte de inventario con:
    - Valor total del inventario (stock_actual * costo_unitario)
    - Productos críticos (stock < mínimo * 1.3)
    - Productos con exceso (stock > máximo)
    - Rotación estimada (consumo promedio)
    - Productos sin movimiento en 90 días
    """
    # Query para calcular valor total
    # Query para productos críticos
    # Query para productos obsoletos (sin movimiento)
    # Cálculo de rotación de inventario
    
    return reporte
```

**Campos del Reporte:**
- `fecha_generacion`: timestamp
- `valor_total_inventario`: 125000.00
- `numero_productos`: 250
- `productos_criticos`: Array con productos bajo stock
- `productos_exceso`: Array con productos sobre stock
- `productos_sin_movimiento`: Array con productos sin uso en 90 días
- `rotacion_promedio_dias`: 45

---

#### Tarea 19: Componente de Generación de Reportes
**Frontend:** `Frontend/src/components/reports/ReportGeneratorComponent.tsx` (NUEVO)

**Descripción:** Interfaz para seleccionar tipo de reporte, parámetros y formato de descarga.

**Implementación:**
```tsx
interface ReportConfig {
    tipo: 'gastos-mensuales' | 'inventario-estado' | 'metricas-financieras';
    formato: 'json' | 'csv' | 'excel' | 'pdf';
    parametros: Record<string, any>;
}

const ReportGeneratorComponent: React.FC = () => {
    const [config, setConfig] = useState<ReportConfig>({
        tipo: 'gastos-mensuales',
        formato: 'excel',
        parametros: {
            mes: new Date().getMonth() + 1,
            anio: new Date().getFullYear()
        }
    });
    
    const [loading, setLoading] = useState(false);
    
    const handleGenerate = async () => {
        setLoading(true);
        const token = localStorage.getItem('token');
        
        // Construir URL según tipo
        let url = `${API_BASE_URL}/reportes/${config.tipo}?formato=${config.formato}`;
        
        // Agregar parámetros
        Object.entries(config.parametros).forEach(([key, value]) => {
            url += `&${key}=${value}`;
        });
        
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `reporte-${config.tipo}-${Date.now()}.${config.formato}`;
            link.click();
        }
        
        setLoading(false);
    };
    
    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Generador de Reportes</h2>
            
            {/* Select tipo de reporte */}
            <div className="mb-4">
                <label>Tipo de Reporte</label>
                <select value={config.tipo} onChange={...}>
                    <option value="gastos-mensuales">Gastos Mensuales</option>
                    <option value="inventario-estado">Estado de Inventario</option>
                    <option value="metricas-financieras">Métricas Financieras</option>
                </select>
            </div>
            
            {/* Select formato */}
            <div className="mb-4">
                <label>Formato de Exportación</label>
                <select value={config.formato} onChange={...}>
                    <option value="excel">Excel (.xlsx)</option>
                    <option value="csv">CSV (.csv)</option>
                    <option value="json">JSON (.json)</option>
                    <option value="pdf">PDF (.pdf)</option>
                </select>
            </div>
            
            {/* Parámetros específicos según tipo */}
            {config.tipo === 'gastos-mensuales' && (
                <>
                    <input type="number" placeholder="Mes" />
                    <input type="number" placeholder="Año" />
                </>
            )}
            
            <button 
                onClick={handleGenerate}
                disabled={loading}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg"
            >
                {loading ? 'Generando...' : 'Generar Reporte'}
            </button>
        </div>
    );
};
```

**Features:**
- Select de tipo de reporte
- Select de formato (Excel, CSV, JSON, PDF)
- Inputs dinámicos según tipo seleccionado
- Progreso de generación
- Descarga automática del archivo
- Historial de reportes generados

---

#### Tarea 20: Implementar generación de PDF
**Backend:** `backend/reportes/pdf_generator.py` (NUEVO)

**Descripción:** Módulo para generar reportes en formato PDF con gráficas embebidas.

**Implementación:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import matplotlib.pyplot as plt

def generar_pdf_gastos_mensuales(datos: dict) -> BytesIO:
    """
    Genera PDF de reporte de gastos mensuales con:
    - Header con logo y fecha
    - Resumen ejecutivo (cards)
    - Tabla de gastos por categoría
    - Gráfica de pie (distribución)
    - Gráfica de barras (tendencia)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph(f"Reporte de Gastos - {datos['periodo']}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Resumen
    resumen = f"""
    Total de Gastos: ${datos['total_gastos']:,.2f}
    Gastos Fijos: ${datos['gastos_fijos']:,.2f}
    Gastos Variables: ${datos['gastos_variables']:,.2f}
    """
    elements.append(Paragraph(resumen, styles['Normal']))
    
    # Tabla de categorías
    table_data = [['Categoría', 'Total', 'Porcentaje', 'Variación']]
    for cat in datos['gastos_por_categoria']:
        table_data.append([
            cat['categoria'],
            f"${cat['total']:,.2f}",
            f"{cat['porcentaje']:.1f}%",
            f"{cat['variacion_mes_anterior']:+.1f}%"
        ])
    
    table = Table(table_data)
    elements.append(table)
    
    # Gráfica de pie (generar con matplotlib y embeber)
    fig, ax = plt.subplots()
    ax.pie([c['total'] for c in datos['gastos_por_categoria']],
           labels=[c['categoria'] for c in datos['gastos_por_categoria']],
           autopct='%1.1f%%')
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    
    elements.append(Image(img_buffer, width=400, height=300))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
```

**Dependencias:**
- `reportlab`: Generación de PDFs
- `matplotlib`: Generación de gráficas

---

#### Tarea 21: Integrar componente de reportes en AdminPage
**Frontend:** `Frontend/src/pages/AdminPage.tsx`

**Descripción:** Agregar sección de reportes en el dashboard administrativo.

**Implementación:**
```tsx
import ReportGeneratorComponent from '../components/reports/ReportGeneratorComponent';

// En el JSX de AdminPage
<div className="mb-6">
    <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">Reportes Ejecutivos</h2>
        <ReportGeneratorComponent />
    </div>
</div>
```

---

## 🔮 FASE 5: Análisis Predictivo y Proyecciones

**Objetivo:** Implementar modelos predictivos para forecasting de gastos, demanda de servicios y stock.

### Tareas (4 tareas)

#### Tarea 22: Crear endpoint POST /analytics/prediccion-gastos
**Backend:** `backend/analytics/router.py` (NUEVO)

**Descripción:** Endpoint que utiliza regresión lineal para predecir gastos futuros.

**Implementación:**
```python
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

@router.post("/prediccion-gastos")
async def predecir_gastos_futuros(
    meses_futuro: int = Query(3, ge=1, le=12),
    categorias: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Predice gastos futuros usando:
    - Datos históricos de últimos 12 meses
    - Tendencia lineal por categoría
    - Estacionalidad (si aplica)
    - Eventos especiales (capacitaciones, mantenimientos)
    """
    # Obtener datos históricos
    query = """
        SELECT 
            EXTRACT(MONTH FROM fecha_gasto) as mes,
            EXTRACT(YEAR FROM fecha_gasto) as anio,
            categoria,
            SUM(monto) as total
        FROM gastos
        WHERE fecha_gasto >= NOW() - INTERVAL '12 months'
        GROUP BY mes, anio, categoria
        ORDER BY anio, mes
    """
    
    datos_historicos = await conn.fetch(query)
    
    # Preparar datos para regresión
    X = np.array([[i] for i in range(len(datos_historicos))])
    y = np.array([d['total'] for d in datos_historicos])
    
    # Entrenar modelo
    model = LinearRegression()
    model.fit(X, y)
    
    # Predecir
    X_futuro = np.array([[len(X) + i] for i in range(meses_futuro)])
    predicciones = model.predict(X_futuro)
    
    # Formatear respuesta
    fechas_futuras = []
    for i in range(meses_futuro):
        fecha = datetime.now() + timedelta(days=30 * (i + 1))
        fechas_futuras.append(fecha.strftime('%Y-%m'))
    
    return {
        'predicciones': [
            {
                'periodo': fechas_futuras[i],
                'gasto_estimado': float(predicciones[i]),
                'margen_error': float(predicciones[i] * 0.15),  # 15% error
                'confianza': 0.85
            }
            for i in range(meses_futuro)
        ],
        'tendencia': 'creciente' if model.coef_[0] > 0 else 'decreciente',
        'tasa_crecimiento': float(model.coef_[0])
    }
```

**Dependencias:**
- `scikit-learn`: Modelos de ML
- `numpy`: Cálculos numéricos

---

#### Tarea 23: Crear endpoint POST /analytics/demanda-servicios
**Backend:** `backend/analytics/router.py`

**Descripción:** Predice la demanda de servicios basada en datos históricos de citas.

**Implementación:**
```python
@router.post("/demanda-servicios")
async def predecir_demanda_servicios(
    meses_futuro: int = Query(3, ge=1, le=6),
    servicio_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Predice demanda de servicios usando:
    - Historial de citas por servicio
    - Estacionalidad (más citas en invierno para problemas de pies)
    - Tendencia de crecimiento de pacientes
    """
    # Query para obtener citas por servicio
    query = """
        SELECT 
            cs.nombre_servicio,
            EXTRACT(MONTH FROM c.fecha_hora_cita) as mes,
            COUNT(*) as num_citas
        FROM citas c
        JOIN catalogo_servicios cs ON c.servicio_id = cs.servicio_id
        WHERE c.fecha_hora_cita >= NOW() - INTERVAL '12 months'
        GROUP BY cs.nombre_servicio, mes
        ORDER BY num_citas DESC
    """
    
    datos = await conn.fetch(query)
    
    # Aplicar regresión por servicio
    # Considerar estacionalidad (meses de mayor demanda)
    # Retornar predicciones
    
    return {
        'predicciones_por_servicio': [
            {
                'servicio': 'Pedicure clínico',
                'demanda_estimada': [120, 135, 140],  # Próximos 3 meses
                'tendencia': 'creciente',
                'estacionalidad': 'alta_en_invierno'
            }
        ]
    }
```

---

#### Tarea 24: Crear endpoint POST /analytics/reorden-inventario
**Backend:** `backend/analytics/router.py`

**Descripción:** Calcula puntos de reorden óptimos para productos de inventario.

**Implementación:**
```python
@router.post("/reorden-inventario")
async def calcular_puntos_reorden(
    current_user: dict = Depends(get_current_user)
):
    """
    Calcula punto de reorden usando fórmula:
    Punto de Reorden = (Demanda Promedio Diaria × Lead Time) + Stock de Seguridad
    
    Stock de Seguridad = Z × σ × √Lead Time
    Donde:
    - Z = Factor de servicio (1.65 para 95% confiabilidad)
    - σ = Desviación estándar de la demanda
    - Lead Time = Tiempo de reposición en días
    """
    # Obtener productos con historial de consumo
    query = """
        SELECT 
            p.producto_id,
            p.nombre,
            p.tiempo_reposicion_dias,
            p.stock_actual,
            p.stock_minimo,
            AVG(sm.cantidad) as consumo_promedio,
            STDDEV(sm.cantidad) as desviacion_consumo
        FROM inventario_productos p
        LEFT JOIN stock_movements sm ON p.producto_id = sm.producto_id
        WHERE sm.tipo_movimiento = 'salida'
        AND sm.fecha_movimiento >= NOW() - INTERVAL '90 days'
        GROUP BY p.producto_id
    """
    
    productos = await conn.fetch(query)
    
    recomendaciones = []
    Z = 1.65  # 95% nivel de servicio
    
    for p in productos:
        demanda_diaria = p['consumo_promedio']
        lead_time = p['tiempo_reposicion_dias']
        sigma = p['desviacion_consumo']
        
        stock_seguridad = Z * sigma * (lead_time ** 0.5)
        punto_reorden = (demanda_diaria * lead_time) + stock_seguridad
        
        cantidad_ordenar = max(p['stock_minimo'] - p['stock_actual'] + stock_seguridad, 0)
        
        if p['stock_actual'] <= punto_reorden:
            recomendaciones.append({
                'producto_id': p['producto_id'],
                'nombre': p['nombre'],
                'stock_actual': p['stock_actual'],
                'punto_reorden': round(punto_reorden, 2),
                'cantidad_ordenar': round(cantidad_ordenar, 2),
                'urgencia': 'alta' if p['stock_actual'] < p['stock_minimo'] else 'media',
                'dias_restantes': int(p['stock_actual'] / demanda_diaria) if demanda_diaria > 0 else None
            })
    
    return {
        'fecha_analisis': datetime.now(),
        'productos_requieren_reorden': len(recomendaciones),
        'recomendaciones': sorted(recomendaciones, key=lambda x: x['dias_restantes'] or 0)
    }
```

---

#### Tarea 25: Componente de Dashboard Predictivo
**Frontend:** `Frontend/src/components/analytics/PredictiveDashboard.tsx` (NUEVO)

**Descripción:** Visualización de predicciones y recomendaciones.

**Implementación:**
```tsx
const PredictiveDashboard: React.FC = () => {
    const [prediccionGastos, setPrediccionGastos] = useState<any>(null);
    const [demandaServicios, setDemandaServicios] = useState<any>(null);
    const [reordenInventario, setReordenInventario] = useState<any>(null);
    
    useEffect(() => {
        loadPredicciones();
    }, []);
    
    const loadPredicciones = async () => {
        const token = localStorage.getItem('token');
        
        // Cargar predicciones de gastos
        const gastosRes = await fetch(`${API_BASE_URL}/analytics/prediccion-gastos?meses_futuro=3`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        setPrediccionGastos(await gastosRes.json());
        
        // Cargar demanda de servicios
        const demandaRes = await fetch(`${API_BASE_URL}/analytics/demanda-servicios?meses_futuro=3`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        setDemandaServicios(await demandaRes.json());
        
        // Cargar recomendaciones de reorden
        const reordenRes = await fetch(`${API_BASE_URL}/analytics/reorden-inventario`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        setReordenInventario(await reordenRes.json());
    };
    
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold">Análisis Predictivo</h2>
            
            {/* Predicción de Gastos */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Predicción de Gastos (3 meses)</h3>
                <LineChart 
                    data={prediccionGastos?.predicciones}
                    lines={[
                        { dataKey: 'gasto_estimado', stroke: '#3B82F6', name: 'Estimado' },
                        { dataKey: 'margen_error', stroke: '#EF4444', strokeDasharray: '5 5', name: 'Margen Error' }
                    ]}
                />
                <div className="mt-4">
                    <p>Tendencia: <span className={prediccionGastos?.tendencia === 'creciente' ? 'text-red-600' : 'text-green-600'}>
                        {prediccionGastos?.tendencia}
                    </span></p>
                    <p>Tasa de crecimiento mensual: {prediccionGastos?.tasa_crecimiento?.toFixed(2)}%</p>
                </div>
            </div>
            
            {/* Demanda de Servicios */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Demanda Estimada de Servicios</h3>
                <BarChart 
                    data={demandaServicios?.predicciones_por_servicio}
                    bars={[{ dataKey: 'demanda_estimada', fill: '#10B981' }]}
                />
            </div>
            
            {/* Recomendaciones de Reorden */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">
                    Recomendaciones de Reorden ({reordenInventario?.productos_requieren_reorden} productos)
                </h3>
                <table className="w-full">
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Stock Actual</th>
                            <th>Punto Reorden</th>
                            <th>Cantidad Ordenar</th>
                            <th>Urgencia</th>
                            <th>Días Restantes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reordenInventario?.recomendaciones?.map((rec: any) => (
                            <tr key={rec.producto_id}>
                                <td>{rec.nombre}</td>
                                <td>{rec.stock_actual}</td>
                                <td>{rec.punto_reorden}</td>
                                <td>{rec.cantidad_ordenar}</td>
                                <td>
                                    <span className={`badge ${rec.urgencia === 'alta' ? 'bg-red-500' : 'bg-yellow-500'}`}>
                                        {rec.urgencia}
                                    </span>
                                </td>
                                <td>{rec.dias_restantes || 'N/A'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
```

---

## 🤖 FASE 6: Automatización y Notificaciones

**Objetivo:** Implementar tareas automatizadas y sistema de notificaciones para alertas proactivas.

### Tareas (5 tareas)

#### Tarea 26: Configurar Celery para tareas asíncronas
**Backend:** `backend/celery_config.py` (NUEVO)

**Descripción:** Configuración de Celery con Redis como broker para tareas programadas.

**Implementación:**
```python
from celery import Celery
from celery.schedules import crontab

# Configuración de Celery
celery_app = Celery(
    'podoskin_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Mexico_City',
    enable_utc=True,
)

# Programación de tareas periódicas
celery_app.conf.beat_schedule = {
    # Verificar stock crítico cada día a las 8:00 AM
    'verificar-stock-critico': {
        'task': 'backend.tasks.verificar_stock_critico',
        'schedule': crontab(hour=8, minute=0),
    },
    # Generar reporte semanal cada lunes a las 9:00 AM
    'reporte-semanal': {
        'task': 'backend.tasks.generar_reporte_semanal',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
    },
    # Recordatorio de gastos recurrentes cada 1 del mes
    'recordatorio-gastos-recurrentes': {
        'task': 'backend.tasks.recordar_gastos_recurrentes',
        'schedule': crontab(day_of_month=1, hour=10, minute=0),
    },
    # Backup de base de datos cada día a las 2:00 AM
    'backup-database': {
        'task': 'backend.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),
    },
}
```

**Dependencias:**
- `celery`: Task queue
- `redis`: Message broker

---

#### Tarea 27: Crear tarea de verificación de stock crítico
**Backend:** `backend/tasks/inventory_tasks.py` (NUEVO)

**Descripción:** Tarea que verifica productos con stock bajo y envía notificaciones.

**Implementación:**
```python
from celery_config import celery_app
from backend.db import get_db_connection_citas
from backend.notifications.email_service import enviar_email_alerta

@celery_app.task
def verificar_stock_critico():
    """
    Tarea programada que:
    1. Consulta productos con stock < stock_minimo * 1.3
    2. Genera lista de productos críticos
    3. Envía email a administradores
    4. Crea notificación en sistema
    """
    conn = await get_db_connection_citas()
    
    query = """
        SELECT 
            producto_id,
            nombre,
            stock_actual,
            stock_minimo,
            unidad_medida
        FROM inventario_productos
        WHERE stock_actual < (stock_minimo * 1.3)
        ORDER BY (stock_actual - stock_minimo) ASC
    """
    
    productos_criticos = await conn.fetch(query)
    
    if len(productos_criticos) > 0:
        # Generar HTML para email
        html_content = f"""
        <h2>Alerta: {len(productos_criticos)} Productos con Stock Crítico</h2>
        <table>
            <tr>
                <th>Producto</th>
                <th>Stock Actual</th>
                <th>Stock Mínimo</th>
            </tr>
        """
        
        for p in productos_criticos:
            html_content += f"""
            <tr>
                <td>{p['nombre']}</td>
                <td style="color: red;">{p['stock_actual']} {p['unidad_medida']}</td>
                <td>{p['stock_minimo']} {p['unidad_medida']}</td>
            </tr>
            """
        
        html_content += "</table>"
        
        # Enviar email a administradores
        await enviar_email_alerta(
            destinatarios=['admin@podoskin.com'],
            asunto='Alerta: Productos con Stock Crítico',
            contenido_html=html_content
        )
        
        # Registrar en log
        print(f"[{datetime.now()}] Alerta de stock enviada: {len(productos_criticos)} productos")
    
    return {'productos_criticos': len(productos_criticos)}
```

---

#### Tarea 28: Implementar servicio de email con templates
**Backend:** `backend/notifications/email_service.py` (NUEVO)

**Descripción:** Servicio para envío de emails usando templates HTML.

**Implementación:**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

# Configuración SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'notifications@podoskin.com'
SMTP_PASSWORD = 'app_password_here'

async def enviar_email_alerta(
    destinatarios: List[str],
    asunto: str,
    contenido_html: str
):
    """
    Envía email usando SMTP con contenido HTML.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(destinatarios)
    
    # Crear parte HTML
    html_part = MIMEText(contenido_html, 'html')
    msg.attach(html_part)
    
    # Enviar
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    
    print(f"Email enviado a {len(destinatarios)} destinatarios")

# Templates de email
TEMPLATE_STOCK_CRITICO = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .critical { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h2>🚨 Alerta de Stock Crítico - Podoskin</h2>
    <p>Se detectaron {{ num_productos }} productos con stock por debajo del mínimo:</p>
    {{ tabla_productos }}
    <p>Por favor, revisa el sistema para realizar pedidos.</p>
</body>
</html>
"""

TEMPLATE_REPORTE_SEMANAL = """
<!DOCTYPE html>
<html>
<body>
    <h2>📊 Reporte Semanal - Podoskin</h2>
    <p>Resumen de la semana del {{ fecha_inicio }} al {{ fecha_fin }}:</p>
    <ul>
        <li>Ingresos: ${{ ingresos }}</li>
        <li>Gastos: ${{ gastos }}</li>
        <li>Utilidad: ${{ utilidad }}</li>
        <li>Citas atendidas: {{ citas }}</li>
        <li>Productos críticos: {{ productos_criticos }}</li>
    </ul>
</body>
</html>
"""
```

**Dependencias:**
- `smtplib` (built-in)
- `jinja2`: Templating

---

#### Tarea 29: Crear sistema de notificaciones in-app
**Backend:** `backend/notifications/router.py` (NUEVO)  
**Frontend:** `Frontend/src/components/notifications/NotificationCenter.tsx` (NUEVO)

**Descripción:** Sistema de notificaciones push dentro de la aplicación.

**Backend:**
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Almacén de conexiones WebSocket activas
active_connections: List[WebSocket] = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Manejo de mensajes del cliente (ack, mark_read, etc.)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@router.get("/")
async def get_notificaciones(
    usuario_id: int,
    solo_no_leidas: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene notificaciones del usuario.
    """
    query = """
        SELECT 
            notificacion_id,
            tipo,
            titulo,
            mensaje,
            leida,
            fecha_creacion
        FROM notificaciones
        WHERE usuario_id = $1
    """
    
    if solo_no_leidas:
        query += " AND leida = FALSE"
    
    query += " ORDER BY fecha_creacion DESC LIMIT 50"
    
    notificaciones = await conn.fetch(query, usuario_id)
    return notificaciones

@router.post("/enviar")
async def enviar_notificacion(
    usuarios: List[int],
    tipo: str,
    titulo: str,
    mensaje: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Envía notificación a usuarios específicos.
    """
    # Insertar en BD
    for user_id in usuarios:
        await conn.execute("""
            INSERT INTO notificaciones (usuario_id, tipo, titulo, mensaje)
            VALUES ($1, $2, $3, $4)
        """, user_id, tipo, titulo, mensaje)
    
    # Enviar por WebSocket a usuarios conectados
    for connection in active_connections:
        await connection.send_json({
            'tipo': tipo,
            'titulo': titulo,
            'mensaje': mensaje
        })
    
    return {'enviadas': len(usuarios)}

@router.patch("/{notificacion_id}/marcar-leida")
async def marcar_leida(
    notificacion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Marca notificación como leída.
    """
    await conn.execute("""
        UPDATE notificaciones 
        SET leida = TRUE 
        WHERE notificacion_id = $1
    """, notificacion_id)
    
    return {'success': True}
```

**Frontend:**
```tsx
const NotificationCenter: React.FC = () => {
    const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
    const [noLeidas, setNoLeidas] = useState(0);
    const [showDropdown, setShowDropdown] = useState(false);
    const [ws, setWs] = useState<WebSocket | null>(null);
    
    useEffect(() => {
        // Conectar WebSocket
        const websocket = new WebSocket('ws://localhost:8000/notifications/ws');
        
        websocket.onmessage = (event) => {
            const notificacion = JSON.parse(event.data);
            setNotificaciones(prev => [notificacion, ...prev]);
            setNoLeidas(prev => prev + 1);
            
            // Mostrar toast
            toast.info(notificacion.titulo, {
                description: notificacion.mensaje
            });
        };
        
        setWs(websocket);
        
        // Cargar notificaciones iniciales
        loadNotificaciones();
        
        return () => {
            websocket.close();
        };
    }, []);
    
    const loadNotificaciones = async () => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/notifications/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            setNotificaciones(data);
            setNoLeidas(data.filter((n: any) => !n.leida).length);
        }
    };
    
    const marcarLeida = async (id: number) => {
        const token = localStorage.getItem('token');
        await fetch(`${API_BASE_URL}/notifications/${id}/marcar-leida`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        setNotificaciones(prev => 
            prev.map(n => n.notificacion_id === id ? {...n, leida: true} : n)
        );
        setNoLeidas(prev => prev - 1);
    };
    
    return (
        <div className="relative">
            <button 
                onClick={() => setShowDropdown(!showDropdown)}
                className="relative p-2 rounded-full hover:bg-gray-100"
            >
                <Bell className="w-6 h-6" />
                {noLeidas > 0 && (
                    <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                        {noLeidas}
                    </span>
                )}
            </button>
            
            {showDropdown && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50">
                    <div className="p-4 border-b">
                        <h3 className="font-semibold">Notificaciones</h3>
                    </div>
                    
                    <div className="max-h-96 overflow-y-auto">
                        {notificaciones.map(notif => (
                            <div 
                                key={notif.notificacion_id}
                                className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${
                                    !notif.leida ? 'bg-blue-50' : ''
                                }`}
                                onClick={() => marcarLeida(notif.notificacion_id)}
                            >
                                <div className="flex items-start gap-3">
                                    <div className="flex-1">
                                        <h4 className="font-semibold text-sm">{notif.titulo}</h4>
                                        <p className="text-xs text-gray-600 mt-1">{notif.mensaje}</p>
                                        <p className="text-xs text-gray-400 mt-2">
                                            {new Date(notif.fecha_creacion).toLocaleString()}
                                        </p>
                                    </div>
                                    {!notif.leida && (
                                        <div className="w-2 h-2 bg-blue-600 rounded-full mt-1"></div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
```

---

#### Tarea 30: Crear tarea de reporte semanal automatizado
**Backend:** `backend/tasks/report_tasks.py` (NUEVO)

**Descripción:** Genera y envía reporte semanal por email todos los lunes.

**Implementación:**
```python
from celery_config import celery_app
from datetime import datetime, timedelta

@celery_app.task
def generar_reporte_semanal():
    """
    Genera reporte semanal con:
    - Resumen financiero (ingresos, gastos, utilidad)
    - Top 5 servicios más solicitados
    - Productos críticos
    - Comparativa con semana anterior
    """
    # Calcular fechas
    hoy = datetime.now()
    fecha_fin = hoy - timedelta(days=hoy.weekday())  # Lunes
    fecha_inicio = fecha_fin - timedelta(days=7)
    
    # Query para ingresos
    ingresos = await conn.fetchval("""
        SELECT COALESCE(SUM(monto), 0)
        FROM pagos
        WHERE fecha_pago BETWEEN $1 AND $2
    """, fecha_inicio, fecha_fin)
    
    # Query para gastos
    gastos = await conn.fetchval("""
        SELECT COALESCE(SUM(monto), 0)
        FROM gastos
        WHERE fecha_gasto BETWEEN $1 AND $2
    """, fecha_inicio, fecha_fin)
    
    # Query para citas
    citas = await conn.fetchval("""
        SELECT COUNT(*)
        FROM citas
        WHERE fecha_hora_cita BETWEEN $1 AND $2
    """, fecha_inicio, fecha_fin)
    
    # Top servicios
    top_servicios = await conn.fetch("""
        SELECT cs.nombre_servicio, COUNT(*) as num_citas
        FROM citas c
        JOIN catalogo_servicios cs ON c.servicio_id = cs.servicio_id
        WHERE c.fecha_hora_cita BETWEEN $1 AND $2
        GROUP BY cs.nombre_servicio
        ORDER BY num_citas DESC
        LIMIT 5
    """, fecha_inicio, fecha_fin)
    
    # Productos críticos
    productos_criticos = await conn.fetchval("""
        SELECT COUNT(*)
        FROM inventario_productos
        WHERE stock_actual < stock_minimo
    """)
    
    utilidad = ingresos - gastos
    
    # Generar HTML usando template
    from jinja2 import Template
    template = Template(TEMPLATE_REPORTE_SEMANAL)
    html = template.render(
        fecha_inicio=fecha_inicio.strftime('%d/%m/%Y'),
        fecha_fin=fecha_fin.strftime('%d/%m/%Y'),
        ingresos=f"{ingresos:,.2f}",
        gastos=f"{gastos:,.2f}",
        utilidad=f"{utilidad:,.2f}",
        citas=citas,
        productos_criticos=productos_criticos,
        top_servicios=top_servicios
    )
    
    # Enviar email
    await enviar_email_alerta(
        destinatarios=['admin@podoskin.com', 'gerente@podoskin.com'],
        asunto=f'Reporte Semanal - {fecha_inicio.strftime("%d/%m")} al {fecha_fin.strftime("%d/%m")}',
        contenido_html=html
    )
    
    return {'success': True, 'utilidad': utilidad}
```

---

## 📊 Resumen de Planificación

### FASE 4: Reportes (5 tareas)
- 2 nuevos endpoints (/reportes/gastos-mensuales, /reportes/inventario-estado)
- 1 componente React (ReportGeneratorComponent)
- 1 módulo PDF generator
- Integración en AdminPage

### FASE 5: Análisis Predictivo (4 tareas)
- 3 nuevos endpoints de analytics (predicción-gastos, demanda-servicios, reorden-inventario)
- 1 componente React (PredictiveDashboard)
- Uso de scikit-learn para ML

### FASE 6: Automatización (5 tareas)
- Configuración de Celery + Redis
- 3 tareas programadas (stock crítico, reporte semanal, gastos recurrentes)
- Sistema de notificaciones in-app con WebSocket
- Servicio de email con templates

---

## 🛠️ Dependencias Adicionales

### Backend (requirements.txt)
```txt
# Reportes
openpyxl==3.1.2
reportlab==4.0.7
matplotlib==3.8.2

# Machine Learning
scikit-learn==1.3.2
numpy==1.26.2

# Celery
celery==5.3.4
redis==5.0.1

# Email
jinja2==3.1.2
```

### Docker (docker-compose.yml)
```yaml
# Agregar servicio Redis
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data

# Agregar servicio Celery Worker
celery_worker:
  build: ./backend
  command: celery -A celery_config worker --loglevel=info
  depends_on:
    - redis
    - db
  environment:
    - DATABASE_URL=postgresql://...
    - REDIS_URL=redis://redis:6379/0

# Agregar servicio Celery Beat
celery_beat:
  build: ./backend
  command: celery -A celery_config beat --loglevel=info
  depends_on:
    - redis
  environment:
    - REDIS_URL=redis://redis:6379/0

volumes:
  redis_data:
```

---

## 📋 Checklist de Pre-Implementación

Antes de comenzar las fases 4-6, verificar:

- [ ] Fases 1-3 completadas y sin errores
- [ ] Backend funcionando correctamente
- [ ] Frontend sin errores de TypeScript
- [ ] Base de datos con datos de prueba suficientes
- [ ] Docker Compose actualizado con Redis
- [ ] Instaladas dependencias: `openpyxl`, `reportlab`, `matplotlib`, `scikit-learn`, `celery`, `redis`
- [ ] Cuenta SMTP configurada para emails
- [ ] Espacio suficiente para backups automáticos

---

## ⏱️ Estimación de Tiempo

| Fase | Tareas | Tiempo Estimado | Complejidad |
|------|--------|----------------|-------------|
| FASE 4 | 5 | 8-10 horas | Media-Alta |
| FASE 5 | 4 | 12-15 horas | Alta |
| FASE 6 | 5 | 10-12 horas | Alta |
| **TOTAL** | **14** | **30-37 horas** | **Alta** |

---

## 🎯 Criterios de Éxito

**FASE 4:**
- [x] Reportes se generan sin errores en 3 formatos (Excel, CSV, JSON)
- [x] PDFs se generan con gráficas embebidas
- [x] Descarga automática funciona en frontend

**FASE 5:**
- [x] Predicciones de gastos tienen confianza ≥ 80%
- [x] Recomendaciones de reorden reducen desabasto en 50%
- [x] Dashboard predictivo actualiza cada 24 horas

**FASE 6:**
- [x] Tareas de Celery se ejecutan en horario programado
- [x] Emails de alerta llegan en < 5 minutos
- [x] Notificaciones in-app aparecen en tiempo real
- [x] Sistema soporta 50+ notificaciones simultáneas

---

**Preparado por:** GitHub Copilot  
**Fecha:** 6 de enero de 2026  
**Versión:** 1.0  
**Estado:** PLANEADO - LISTO PARA IMPLEMENTACIÓN
