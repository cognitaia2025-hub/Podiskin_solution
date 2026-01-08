"""
Generador de reportes en PDF con gráficos embebidos
Usa reportlab para estructura PDF y matplotlib para charts
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
from typing import Dict, List, Any

# Estilos globales
COLORS = {
    'primary': colors.HexColor('#366092'),
    'secondary': colors.HexColor('#4A90E2'),
    'success': colors.HexColor('#10B981'),
    'warning': colors.HexColor('#F59E0B'),
    'danger': colors.HexColor('#EF4444'),
    'gray': colors.HexColor('#6B7280'),
}


def crear_grafico_pie_categorias(datos: List[Dict[str, Any]], titulo: str) -> io.BytesIO:
    """
    Crea gráfico de pie para gastos por categoría
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    categorias = [d['categoria'] for d in datos[:7]]  # Top 7
    valores = [d['total'] for d in datos[:7]]
    
    colors_chart = ['#366092', '#4A90E2', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
    
    ax.pie(valores, labels=categorias, autopct='%1.1f%%', colors=colors_chart, startangle=90)
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
    
    # Guardar en BytesIO
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    
    return buf


def crear_grafico_barras_tendencia(datos: List[Dict[str, Any]], titulo: str) -> io.BytesIO:
    """
    Crea gráfico de barras para tendencia temporal
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    periodos = [d['periodo'] for d in datos]
    valores = [d['total'] for d in datos]
    
    ax.bar(periodos, valores, color='#4A90E2', edgecolor='#366092', linewidth=1.5)
    ax.set_title(titulo, fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel('Periodo', fontsize=10)
    ax.set_ylabel('Monto Total ($)', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Rotar etiquetas del eje X
    plt.xticks(rotation=45, ha='right')
    
    # Formatear valores en el eje Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    
    return buf


def generar_pdf_gastos(reporte: Dict[str, Any]) -> io.BytesIO:
    """
    Genera PDF completo del reporte de gastos mensuales
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLORS['primary'],
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLORS['primary'],
        spaceAfter=12,
        spaceBefore=16
    )
    
    # Contenido del PDF
    story = []
    
    # Título principal
    story.append(Paragraph(f"Reporte de Gastos Mensuales", title_style))
    story.append(Paragraph(f"<b>Periodo:</b> {reporte['periodo']}", styles['Normal']))
    story.append(Paragraph(
        f"<b>Generado:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Resumen ejecutivo
    story.append(Paragraph("Resumen Ejecutivo", heading_style))
    
    data_resumen = [
        ['Concepto', 'Valor'],
        ['Total Gastos Mes Actual', f"${reporte['total_gastos']:,.2f}"],
        ['Total Gastos Mes Anterior', f"${reporte['total_gastos_mes_anterior']:,.2f}"],
        ['Variación Porcentual', f"{reporte['variacion_porcentual']:+.2f}%"],
    ]
    
    tabla_resumen = Table(data_resumen, colWidths=[3.5*inch, 2*inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(tabla_resumen)
    story.append(Spacer(1, 0.3*inch))
    
    # Gastos por categoría (tabla)
    story.append(Paragraph("Desglose por Categoría", heading_style))
    
    data_categorias = [['Categoría', 'Total', 'Cantidad', '%', 'Var. vs Anterior']]
    for cat in reporte['gastos_por_categoria']:
        data_categorias.append([
            cat['categoria'],
            f"${cat['total']:,.2f}",
            str(cat['cantidad']),
            f"{cat['porcentaje']:.1f}%",
            f"{cat['variacion_mes_anterior']:+.1f}%"
        ])
    
    tabla_categorias = Table(data_categorias, colWidths=[2*inch, 1.3*inch, 0.8*inch, 0.8*inch, 1.2*inch])
    tabla_categorias.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(tabla_categorias)
    story.append(Spacer(1, 0.4*inch))
    
    # Gráfico de pie de categorías
    if reporte['gastos_por_categoria']:
        grafico_pie = crear_grafico_pie_categorias(
            reporte['gastos_por_categoria'],
            'Distribución de Gastos por Categoría'
        )
        img_pie = Image(grafico_pie, width=5*inch, height=5*inch)
        story.append(img_pie)
        story.append(PageBreak())
    
    # Top 10 gastos mayores
    story.append(Paragraph("Top 10 Gastos Mayores", heading_style))
    
    data_top = [['Concepto', 'Monto', 'Fecha', 'Método', 'Categoría']]
    for g in reporte['top_10_gastos'][:10]:
        data_top.append([
            g['concepto'][:30],  # Truncar si es muy largo
            f"${g['monto']:,.2f}",
            g['fecha'],
            g['metodo_pago'],
            g['categoria'][:15]
        ])
    
    tabla_top = Table(data_top, colWidths=[2.2*inch, 1.1*inch, 0.9*inch, 0.9*inch, 1*inch])
    tabla_top.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(tabla_top)
    story.append(Spacer(1, 0.4*inch))
    
    # Gráfico de tendencia de 6 meses
    if reporte['tendencia_6_meses']:
        story.append(Paragraph("Tendencia de Gastos (Últimos 6 Meses)", heading_style))
        grafico_barras = crear_grafico_barras_tendencia(
            reporte['tendencia_6_meses'],
            'Evolución de Gastos Mensuales'
        )
        img_barras = Image(grafico_barras, width=6*inch, height=3*inch)
        story.append(img_barras)
    
    # Productos comprados (si hay)
    if reporte['productos_comprados']:
        story.append(PageBreak())
        story.append(Paragraph("Productos Comprados en el Periodo", heading_style))
        
        data_productos = [['Producto', 'Cantidad', 'P. Unit.', 'Subtotal', 'Fecha']]
        for p in reporte['productos_comprados'][:20]:  # Máximo 20
            data_productos.append([
                p['producto'][:35],
                f"{p['cantidad']:.1f}",
                f"${p['precio_unitario']:,.2f}",
                f"${p['subtotal']:,.2f}",
                p['fecha']
            ])
        
        tabla_productos = Table(data_productos, colWidths=[2.5*inch, 0.9*inch, 1*inch, 1*inch, 0.9*inch])
        tabla_productos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(tabla_productos)
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Reporte generado por Podoskin Solution - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        footer_style
    ))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer


def generar_pdf_inventario(reporte: Dict[str, Any]) -> io.BytesIO:
    """
    Genera PDF completo del reporte de estado del inventario
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLORS['primary'],
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLORS['primary'],
        spaceAfter=12,
        spaceBefore=16
    )
    
    story = []
    
    # Título
    story.append(Paragraph("Reporte de Estado del Inventario", title_style))
    story.append(Paragraph(
        f"<b>Fecha de Generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Resumen general
    story.append(Paragraph("Resumen General", heading_style))
    
    data_resumen = [
        ['Indicador', 'Valor'],
        ['Valor Total del Inventario', f"${reporte['valor_total_inventario']:,.2f}"],
        ['Número Total de Productos', str(reporte['numero_productos'])],
        ['Productos Críticos (Stock Bajo)', str(reporte['num_criticos'])],
        ['Productos con Exceso', str(reporte['num_exceso'])],
        ['Productos Sin Movimiento', str(reporte['num_sin_movimiento'])],
        ['Rotación Promedio', f"{reporte['rotacion_promedio_dias']:.1f} días"],
    ]
    
    tabla_resumen = Table(data_resumen, colWidths=[3.5*inch, 2*inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(tabla_resumen)
    story.append(Spacer(1, 0.4*inch))
    
    # Productos críticos
    if reporte['productos_criticos']:
        story.append(Paragraph("⚠️ Productos Críticos (Requieren Reabastecimiento)", heading_style))
        
        data_criticos = [['Código', 'Nombre', 'Stock', 'Mínimo', 'Déficit', 'Valor']]
        for p in reporte['productos_criticos'][:15]:  # Máximo 15
            data_criticos.append([
                p['codigo'],
                p['nombre'][:30],
                f"{p['stock_actual']:.1f}",
                f"{p['stock_minimo']:.1f}",
                f"{p['deficit']:.1f}",
                f"${p['valor_stock']:,.0f}"
            ])
        
        tabla_criticos = Table(data_criticos, colWidths=[1*inch, 2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
        tabla_criticos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['danger']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightpink]),
        ]))
        
        story.append(tabla_criticos)
        story.append(Spacer(1, 0.3*inch))
    
    # Productos con exceso
    if reporte['productos_exceso']:
        story.append(PageBreak())
        story.append(Paragraph("📦 Productos con Exceso de Stock", heading_style))
        
        data_exceso = [['Código', 'Nombre', 'Stock Actual', 'Máximo', 'Exceso']]
        for p in reporte['productos_exceso'][:15]:
            data_exceso.append([
                p['codigo'],
                p['nombre'][:40],
                f"{p['stock_actual']:.1f}",
                f"{p['stock_maximo']:.1f}",
                f"{p['exceso']:.1f}"
            ])
        
        tabla_exceso = Table(data_exceso, colWidths=[1*inch, 2.5*inch, 1*inch, 1*inch, 0.9*inch])
        tabla_exceso.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['warning']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgoldenrodyellow]),
        ]))
        
        story.append(tabla_exceso)
    
    # Productos sin movimiento
    if reporte['productos_sin_movimiento']:
        story.append(PageBreak())
        story.append(Paragraph("🔴 Productos Sin Movimiento (>90 días)", heading_style))
        
        data_sin_mov = [['Código', 'Nombre', 'Stock', 'Último Movimiento']]
        for p in reporte['productos_sin_movimiento'][:15]:
            data_sin_mov.append([
                p['codigo'],
                p['nombre'][:45],
                f"{p['stock_actual']:.1f}",
                p['ultimo_movimiento']
            ])
        
        tabla_sin_mov = Table(data_sin_mov, colWidths=[1*inch, 2.8*inch, 0.9*inch, 1.6*inch])
        tabla_sin_mov.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['gray']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(tabla_sin_mov)
    
    # Pie de página
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Reporte generado por Podoskin Solution - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        footer_style
    ))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
