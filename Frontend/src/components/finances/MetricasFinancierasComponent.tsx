import React, { useEffect, useState } from 'react';
import {
    DollarSign,
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    Award,
    Package,
    Users,
    Calendar,
    RefreshCw
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface GastoPorCategoria {
    categoria: string;
    total: number;
    porcentaje: number;
}

interface ServicioRentable {
    servicio_nombre: string;
    total_ingresos: number;
    numero_sesiones: number;
    margen_estimado: number;
}

interface ProductoCritico {
    producto_id: number;
    nombre: string;
    stock_actual: number;
    stock_minimo: number;
    dias_restantes_estimados: number;
}

interface MetricasFinancieras {
    gastos_fijos_mes: number;
    gastos_variables_mes: number;
    total_gastos_mes: number;
    costo_promedio_paciente: number;
    servicios_rentables: ServicioRentable[];
    productos_criticos: ProductoCritico[];
    utilidad_bruta: number;
    margen_utilidad: number;
    ingresos_mes: number;
    pacientes_atendidos: number;
    gastos_por_categoria: GastoPorCategoria[];
}

const CATEGORIA_LABELS: Record<string, string> = {
    'SERVICIOS_BASICOS': 'Servicios Básicos',
    'MATERIAL_MEDICO': 'Material Médico',
    'SALARIOS_PERSONAL': 'Salarios',
    'RENTA_LOCAL': 'Renta',
    'MARKETING_PUBLICIDAD': 'Marketing',
    'MATERIAL_OFICINA': 'Material Oficina',
    'CAPACITACION_CERTIFICACIONES': 'Capacitación',
    'MANTENIMIENTO_EQUIPOS': 'Mantenimiento',
    'SERVICIOS_PROFESIONALES': 'Servicios Profesionales'
};

const MetricasFinancierasComponent: React.FC = () => {
    const [metricas, setMetricas] = useState<MetricasFinancieras | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    useEffect(() => {
        loadMetricas();
    }, []);

    const loadMetricas = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');

            const response = await fetch(`${API_BASE_URL}/api/stats/metricas-financieras`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!response.ok) {
                throw new Error('Error al cargar métricas financieras');
            }

            const data = await response.json();
            setMetricas(data);
            setLastUpdate(new Date());
            setError(null);
        } catch (err) {
            console.error('Error cargando métricas:', err);
            setError('Error al cargar las métricas financieras');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-12">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando métricas financieras...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-6 h-6 text-red-600" />
                    <h3 className="text-lg font-semibold text-red-800">Error</h3>
                </div>
                <p className="text-red-700 mb-4">{error}</p>
                <button
                    onClick={loadMetricas}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    if (!metricas) {
        return (
            <div className="text-center py-12 text-gray-500">
                <p>No hay datos de métricas disponibles</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header con última actualización */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Dashboard Financiero</h2>
                    {lastUpdate && (
                        <p className="text-sm text-gray-500 mt-1">
                            Última actualización: {lastUpdate.toLocaleString()}
                        </p>
                    )}
                </div>
                <button
                    onClick={loadMetricas}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    <RefreshCw className="w-4 h-4" />
                    Actualizar
                </button>
            </div>

            {/* KPIs Principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Ingresos del Mes */}
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6 shadow-lg">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-medium opacity-90">Ingresos del Mes</h3>
                        <DollarSign className="w-6 h-6 opacity-75" />
                    </div>
                    <p className="text-3xl font-bold mb-1">${(metricas.ingresos_mes || 0).toFixed(2)}</p>
                    <p className="text-xs opacity-75">{(metricas.pacientes_atendidos || 0)} pacientes</p>
                </div>

                {/* Gastos Totales */}
                <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6 shadow-lg">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-medium opacity-90">Gastos del Mes</h3>
                        <TrendingDown className="w-6 h-6 opacity-75" />
                    </div>
                    <p className="text-3xl font-bold mb-1">${(metricas.total_gastos_mes || 0).toFixed(2)}</p>
                    <div className="text-xs opacity-75 space-y-1">
                        <div>Fijos: ${(metricas.gastos_fijos_mes || 0).toFixed(2)}</div>
                        <div>Variables: ${(metricas.gastos_variables_mes || 0).toFixed(2)}</div>
                    </div>
                </div>

                {/* Utilidad Bruta */}
                <div className={`bg-gradient-to-br ${(metricas.utilidad_bruta || 0) >= 0
                        ? 'from-blue-500 to-blue-600'
                        : 'from-orange-500 to-orange-600'
                    } text-white rounded-lg p-6 shadow-lg`}>
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-medium opacity-90">Utilidad Bruta</h3>
                        {(metricas.utilidad_bruta || 0) >= 0 ? (
                            <TrendingUp className="w-6 h-6 opacity-75" />
                        ) : (
                            <TrendingDown className="w-6 h-6 opacity-75" />
                        )}
                    </div>
                    <p className="text-3xl font-bold mb-1">${(metricas.utilidad_bruta || 0).toFixed(2)}</p>
                    <p className="text-xs opacity-75">
                        Margen: {(metricas.margen_utilidad || 0).toFixed(1)}%
                    </p>
                </div>

                {/* Costo Promedio por Paciente */}
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6 shadow-lg">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-sm font-medium opacity-90">Costo por Paciente</h3>
                        <Users className="w-6 h-6 opacity-75" />
                    </div>
                    <p className="text-3xl font-bold mb-1">${(metricas.costo_promedio_paciente || 0).toFixed(2)}</p>
                    <p className="text-xs opacity-75">Promedio mensual</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gastos por Categoría */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Calendar className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold">Gastos por Categoría</h3>
                    </div>

                    {metricas.gastos_por_categoria.length > 0 ? (
                        <div className="space-y-3">
                            {metricas.gastos_por_categoria.map((cat) => (
                                <div key={cat.categoria} className="space-y-1">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="font-medium text-gray-700">
                                            {CATEGORIA_LABELS[cat.categoria] || cat.categoria}
                                        </span>
                                        <span className="text-gray-900 font-semibold">
                                            ${cat.total.toFixed(2)} ({cat.porcentaje.toFixed(1)}%)
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all"
                                            style={{ width: `${cat.porcentaje}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-6">No hay gastos categorizados</p>
                    )}
                </div>

                {/* Servicios Más Rentables */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Award className="w-5 h-5 text-amber-600" />
                        <h3 className="text-lg font-semibold">Top 5 Servicios Rentables</h3>
                    </div>

                    {metricas.servicios_rentables.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-3 py-2 text-left font-medium text-gray-700">Servicio</th>
                                        <th className="px-3 py-2 text-right font-medium text-gray-700">Ingresos</th>
                                        <th className="px-3 py-2 text-center font-medium text-gray-700">Sesiones</th>
                                        <th className="px-3 py-2 text-right font-medium text-gray-700">Margen</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y">
                                    {metricas.servicios_rentables.slice(0, 5).map((servicio, idx) => (
                                        <tr key={idx} className="hover:bg-gray-50">
                                            <td className="px-3 py-2 text-gray-800">{servicio.servicio_nombre}</td>
                                            <td className="px-3 py-2 text-right font-semibold text-green-600">
                                                ${servicio.total_ingresos.toFixed(2)}
                                            </td>
                                            <td className="px-3 py-2 text-center text-gray-600">
                                                {servicio.numero_sesiones}
                                            </td>
                                            <td className="px-3 py-2 text-right">
                                                <span className={`px-2 py-1 rounded text-xs font-semibold ${servicio.margen_estimado >= 60
                                                    ? 'bg-green-100 text-green-800'
                                                    : servicio.margen_estimado >= 40
                                                        ? 'bg-yellow-100 text-yellow-800'
                                                        : 'bg-red-100 text-red-800'
                                                    }`}>
                                                    {servicio.margen_estimado.toFixed(0)}%
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-6">No hay datos de servicios</p>
                    )}
                </div>
            </div>

            {/* Alertas de Productos Críticos */}
            {metricas.productos_criticos.length > 0 && (
                <div className="bg-gradient-to-r from-orange-50 to-red-50 border-l-4 border-orange-500 rounded-lg p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <AlertTriangle className="w-6 h-6 text-orange-600" />
                        <h3 className="text-lg font-semibold text-gray-800">
                            Productos con Stock Crítico
                        </h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {metricas.productos_criticos.map((producto) => (
                            <div
                                key={producto.producto_id}
                                className="bg-white rounded-lg p-4 shadow border-l-4 border-orange-400"
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <Package className="w-5 h-5 text-orange-600" />
                                        <h4 className="font-semibold text-gray-800 text-sm">
                                            {producto.nombre}
                                        </h4>
                                    </div>
                                </div>

                                <div className="space-y-1 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Stock actual:</span>
                                        <span className="font-semibold text-orange-600">
                                            {producto.stock_actual}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Stock mínimo:</span>
                                        <span className="font-semibold text-gray-700">
                                            {producto.stock_minimo}
                                        </span>
                                    </div>
                                    {producto.dias_restantes_estimados > 0 && (
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Días restantes:</span>
                                            <span className={`font-semibold ${producto.dias_restantes_estimados <= 7
                                                ? 'text-red-600'
                                                : 'text-orange-600'
                                                }`}>
                                                ~{producto.dias_restantes_estimados}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                <div className="mt-3 pt-3 border-t">
                                    <p className="text-xs text-gray-600">
                                        ⚠️ {producto.stock_actual <= producto.stock_minimo
                                            ? 'Stock por debajo del mínimo'
                                            : 'Stock cerca del mínimo'}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-4 p-3 bg-white rounded border border-orange-200">
                        <p className="text-sm text-gray-700">
                            <strong>Recomendación:</strong> Se detectaron {metricas.productos_criticos.length} productos
                            con stock crítico. Considera realizar pedidos pronto para evitar desabastecimiento.
                        </p>
                    </div>
                </div>
            )}

            {/* Mensaje si no hay productos críticos */}
            {metricas.productos_criticos.length === 0 && (
                <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4 flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                        <Package className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h4 className="font-semibold text-green-800">Inventario Saludable</h4>
                        <p className="text-sm text-green-700">
                            Todos los productos mantienen niveles de stock adecuados.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MetricasFinancierasComponent;
