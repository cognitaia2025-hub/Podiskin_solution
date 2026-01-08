import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, AlertCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface GastoPorCategoria {
    categoria: string;
    total: number;
    porcentaje: number;
    [key: string]: string | number; // Index signature para recharts
}

interface GastoMensual {
    mes: string;
    total: number;
    fijos: number;
    variables: number;
}

const COLORS = [
    '#3B82F6', // blue-500
    '#10B981', // green-500
    '#F59E0B', // amber-500
    '#EF4444', // red-500
    '#8B5CF6', // purple-500
    '#EC4899', // pink-500
    '#06B6D4', // cyan-500
    '#84CC16', // lime-500
    '#F97316', // orange-500
];

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

const GastosChartsComponent: React.FC = () => {
    const [gastosPorCategoria, setGastosPorCategoria] = useState<GastoPorCategoria[]>([]);
    const [gastosMensuales, setGastosMensuales] = useState<GastoMensual[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadChartData();
    }, []);

    const loadChartData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');

            // Cargar gastos por categoría
            const categoriasResponse = await fetch(`${API_BASE_URL}/api/gastos`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!categoriasResponse.ok) {
                throw new Error('Error al cargar datos de gastos');
            }

            const gastos = await categoriasResponse.json();

            // Agrupar por categoría
            const categoriaMap = new Map<string, number>();
            let totalGastos = 0;

            gastos.forEach((gasto: any) => {
                const categoria = gasto.categoria || 'SIN_CATEGORIA';
                const monto = gasto.monto || 0;
                categoriaMap.set(categoria, (categoriaMap.get(categoria) || 0) + monto);
                totalGastos += monto;
            });

            const categoriasData: GastoPorCategoria[] = Array.from(categoriaMap.entries()).map(([categoria, total]) => ({
                categoria,
                total,
                porcentaje: totalGastos > 0 ? (total / totalGastos) * 100 : 0
            })).sort((a, b) => b.total - a.total);

            setGastosPorCategoria(categoriasData);

            // Agrupar por mes (últimos 6 meses)
            const mesesMap = new Map<string, { total: number; fijos: number; variables: number }>();
            const categoriasFijas = ['SERVICIOS_BASICOS', 'RENTA_LOCAL', 'SALARIOS_PERSONAL', 'SERVICIOS_PROFESIONALES'];

            gastos.forEach((gasto: any) => {
                const fecha = new Date(gasto.fecha_gasto);
                const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
                const monto = gasto.monto || 0;
                const esFijo = categoriasFijas.includes(gasto.categoria);

                if (!mesesMap.has(mesKey)) {
                    mesesMap.set(mesKey, { total: 0, fijos: 0, variables: 0 });
                }

                const mesData = mesesMap.get(mesKey)!;
                mesData.total += monto;
                if (esFijo) {
                    mesData.fijos += monto;
                } else {
                    mesData.variables += monto;
                }
            });

            const mesesData: GastoMensual[] = Array.from(mesesMap.entries())
                .map(([mes, data]) => ({
                    mes,
                    ...data
                }))
                .sort((a, b) => a.mes.localeCompare(b.mes))
                .slice(-6); // Últimos 6 meses

            setGastosMensuales(mesesData);
            setError(null);
        } catch (err) {
            console.error('Error cargando datos de charts:', err);
            setError('Error al cargar las gráficas');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-12">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando gráficas...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <p className="text-red-800">{error}</p>
            </div>
        );
    }

    const totalGastosCategoria = gastosPorCategoria.reduce((sum, g) => sum + g.total, 0);
    const totalFijos = gastosMensuales.length > 0 ? gastosMensuales.reduce((sum, m) => sum + m.fijos, 0) / gastosMensuales.length : 0;
    const totalVariables = gastosMensuales.length > 0 ? gastosMensuales.reduce((sum, m) => sum + m.variables, 0) / gastosMensuales.length : 0;

    return (
        <div className="space-y-6">
            {/* Resumen de Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium opacity-90">Total Gastos</h3>
                        <DollarSign className="w-5 h-5 opacity-75" />
                    </div>
                    <p className="text-3xl font-bold">${totalGastosCategoria.toFixed(2)}</p>
                    <p className="text-xs opacity-75 mt-1">Todos los registros</p>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium opacity-90">Gastos Fijos</h3>
                        <TrendingUp className="w-5 h-5 opacity-75" />
                    </div>
                    <p className="text-3xl font-bold">${totalFijos.toFixed(2)}</p>
                    <p className="text-xs opacity-75 mt-1">Promedio mensual</p>
                </div>

                <div className="bg-gradient-to-br from-amber-500 to-amber-600 text-white rounded-lg p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium opacity-90">Gastos Variables</h3>
                        <TrendingUp className="w-5 h-5 opacity-75" />
                    </div>
                    <p className="text-3xl font-bold">${totalVariables.toFixed(2)}</p>
                    <p className="text-xs opacity-75 mt-1">Promedio mensual</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gráfica de Pie - Distribución por Categoría */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        Distribución por Categoría
                    </h3>
                    {gastosPorCategoria.length > 0 ? (
                        <>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={gastosPorCategoria}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={(entry: any) =>
                                            `${CATEGORIA_LABELS[entry.categoria] || entry.categoria}: ${entry.porcentaje.toFixed(1)}%`
                                        }
                                        outerRadius={100}
                                        fill="#8884d8"
                                        dataKey="total"
                                    >
                                        {gastosPorCategoria.map((_entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        formatter={(value: number | undefined) => value ? `$${value.toFixed(2)}` : '$0.00'}
                                        labelFormatter={(label) => CATEGORIA_LABELS[label] || label}
                                    />
                                </PieChart>
                            </ResponsiveContainer>

                            <div className="mt-4 space-y-2">
                                {gastosPorCategoria.slice(0, 5).map((cat, idx) => (
                                    <div key={cat.categoria} className="flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="w-3 h-3 rounded-full"
                                                style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                                            ></div>
                                            <span className="text-gray-700">{CATEGORIA_LABELS[cat.categoria] || cat.categoria}</span>
                                        </div>
                                        <span className="font-semibold text-gray-900">${cat.total.toFixed(2)}</span>
                                    </div>
                                ))}
                            </div>
                        </>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <p>No hay datos de categorías para mostrar</p>
                        </div>
                    )}
                </div>

                {/* Gráfica de Barras - Fijos vs Variables */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                        Gastos Fijos vs Variables
                    </h3>
                    {gastosMensuales.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={gastosMensuales}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="mes"
                                    tick={{ fontSize: 12 }}
                                    tickFormatter={(value) => {
                                        const [year, month] = value.split('-');
                                        const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                                        return `${monthNames[parseInt(month) - 1]} ${year.slice(-2)}`;
                                    }}
                                />
                                <YAxis tick={{ fontSize: 12 }} />
                                <Tooltip
                                    formatter={(value: number | undefined) => value ? `$${value.toFixed(2)}` : '$0.00'}
                                    labelFormatter={(label) => {
                                        const [year, month] = label.split('-');
                                        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                                        return `${monthNames[parseInt(month) - 1]} ${year}`;
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="fijos" fill="#10B981" name="Gastos Fijos" />
                                <Bar dataKey="variables" fill="#F59E0B" name="Gastos Variables" />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <p>No hay datos mensuales para mostrar</p>
                        </div>
                    )}
                </div>

                {/* Gráfica de Línea - Tendencia Mensual */}
                <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
                        Tendencia Mensual de Gastos
                    </h3>
                    {gastosMensuales.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={gastosMensuales}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="mes"
                                    tick={{ fontSize: 12 }}
                                    tickFormatter={(value) => {
                                        const [year, month] = value.split('-');
                                        const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                                        return `${monthNames[parseInt(month) - 1]} ${year.slice(-2)}`;
                                    }}
                                />
                                <YAxis tick={{ fontSize: 12 }} />
                                <Tooltip
                                    formatter={(value: number | undefined) => value ? `$${value.toFixed(2)}` : '$0.00'}
                                    labelFormatter={(label) => {
                                        const [year, month] = label.split('-');
                                        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                                        return `${monthNames[parseInt(month) - 1]} ${year}`;
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="total"
                                    stroke="#8B5CF6"
                                    strokeWidth={3}
                                    name="Total Gastos"
                                    dot={{ fill: '#8B5CF6', r: 5 }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="fijos"
                                    stroke="#10B981"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    name="Gastos Fijos"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="variables"
                                    stroke="#F59E0B"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    name="Gastos Variables"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="text-center py-12 text-gray-500">
                            <p>No hay datos de tendencia para mostrar</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default GastosChartsComponent;
