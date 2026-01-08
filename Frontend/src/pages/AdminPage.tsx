/**
 * Admin Page
 * 
 * Administrative dashboard with:
 * - KPI cards for key metrics
 * - Revenue/Expense charts
 * - Cash closing history
 * - Expense breakdown
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../auth/AuthContext';
import { Navigate } from 'react-router-dom';
import KPICard from '../components/dashboard/KPICard';
import ReportGeneratorComponent from '../components/reports/ReportGeneratorComponent';
import { API_BASE_URL } from '../services/api';

type DateRange = '7d' | '30d' | '90d' | '12m';

interface KPIData {
  ingresos_mes: number;
  gastos_mes: number;
  citas_mes: number;
  pacientes_nuevos: number;
  ingresos_tendencia: number;
  gastos_tendencia: number;
  citas_tendencia: number;
  pacientes_tendencia: number;
}

interface Gasto {
  id: string;
  fecha: string;
  categoria: string;
  concepto: string;
  monto: number;
}

interface CorteCaja {
  id: string;
  fecha: string;
  total_ingresos: number;
  total_gastos: number;
  saldo_efectivo: number;
  cerrado_por: string;
}

// --- Helper Reemplazado (Antes estaba en mockData) ---
const getCategoriaColor = (categoria: string): string => {
  const colors: Record<string, string> = {
    'Insumos': 'bg-blue-100 text-blue-800',
    'Medicamentos': 'bg-green-100 text-green-800',
    'Instrumental': 'bg-purple-100 text-purple-800',
    'Papelería': 'bg-gray-100 text-gray-800',
    'Limpieza': 'bg-yellow-100 text-yellow-800',
    'Mobiliario': 'bg-indigo-100 text-indigo-800',
    'Epp': 'bg-red-100 text-red-800',
    'Ortopodología': 'bg-pink-100 text-pink-800'
  };
  return colors[categoria] || 'bg-gray-100 text-gray-800';
};
// -----------------------------------------------------

const AdminPage: React.FC = () => {
    const { user } = useAuth();
    const [dateRange, setDateRange] = useState<DateRange>('30d');
    
    const [kpis, setKpis] = useState<KPIData>({
      ingresos_mes: 0,
      gastos_mes: 0,
      citas_mes: 0,
      pacientes_nuevos: 0,
      ingresos_tendencia: 0,
      gastos_tendencia: 0,
      citas_tendencia: 0,
      pacientes_tendencia: 0
    });
    const [gastos, setGastos] = useState<Gasto[]>([]);
    const [cortesCaja, setCortesCaja] = useState<CorteCaja[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Redirect non-admin users
    if (user?.rol !== 'Admin') {
        return <Navigate to="/calendar" replace />;
    }
    
    // Cargar datos al montar el componente
    useEffect(() => {
        const loadDashboardData = async () => {
            setLoading(true);
            setError(null);
            
            const token = localStorage.getItem('access_token');
            if (!token) {
                setError('No hay token de autenticación');
                setLoading(false);
                return;
            }

            const headers = {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            };

            try {
                // Calcular fechas
                const hoy = new Date();
                const primerDiaMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
                const ultimoDiaMes = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);

                // 1. Obtener gastos del mes
                let gastosMes = 0;
                let gastosData: Gasto[] = [];
                try {
                    const gastosResponse = await fetch(
                        `${API_BASE_URL}/gastos?desde=${primerDiaMes.toISOString().split('T')[0]}&hasta=${ultimoDiaMes.toISOString().split('T')[0]}`,
                        { headers }
                    );
                    if (gastosResponse.ok) {
                        gastosData = await gastosResponse.json();
                        gastosMes = gastosData.reduce((sum, g) => sum + (g.monto || 0), 0);
                        setGastos(gastosData);
                    }
                } catch (err) {
                    console.error('Error al obtener gastos:', err);
                }

                // 2. Obtener cortes de caja del mes (ingresos)
                let ingresosMes = 0;
                let cortesData: CorteCaja[] = [];
                try {
                    const cortesResponse = await fetch(`${API_BASE_URL}/cortes-caja`, { headers });
                    if (cortesResponse.ok) {
                        cortesData = await cortesResponse.json();
                        // Filtrar cortes del mes actual
                        const cortesDelMes = cortesData.filter(c => {
                            const fechaCorte = new Date(c.fecha);
                            return fechaCorte >= primerDiaMes && fechaCorte <= ultimoDiaMes;
                        });
                        ingresosMes = cortesDelMes.reduce((sum, c) => sum + (c.total_ingresos || 0), 0);
                        setCortesCaja(cortesData);
                    }
                } catch (err) {
                    console.error('Error al obtener cortes de caja:', err);
                }

                // 3. Obtener citas del mes
                let citasMes = 0;
                try {
                    const citasResponse = await fetch(
                        `${API_BASE_URL}/appointments?start_date=${primerDiaMes.toISOString()}&end_date=${ultimoDiaMes.toISOString()}`,
                        { headers }
                    );
                    if (citasResponse.ok) {
                        const citasData: any[] = await citasResponse.json();
                        citasMes = citasData.length;
                    }
                } catch (err) {
                    console.error('Error al obtener citas:', err);
                }

                // Actualizar KPIs
                setKpis({
                    ingresos_mes: ingresosMes,
                    gastos_mes: gastosMes,
                    citas_mes: citasMes,
                    pacientes_nuevos: 0, // TODO: Implementar endpoint
                    ingresos_tendencia: 0, // TODO: Calcular tendencia
                    gastos_tendencia: 0,
                    citas_tendencia: 0,
                    pacientes_tendencia: 0,
                });
            } catch (err: any) {
                setError(err.message || 'Error al cargar datos del dashboard');
                console.error('Error loading dashboard data:', err);
            } finally {
                setLoading(false);
            }
        };

        loadDashboardData();
    }, [dateRange]);

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 0,
        }).format(value);
    };

    // Calculate expense breakdown by category
    const gastosPorCategoria = gastos.reduce((acc, gasto) => {
        acc[gasto.categoria] = (acc[gasto.categoria] || 0) + gasto.monto;
        return acc;
    }, {} as Record<string, number>);

    const totalGastos = Object.values(gastosPorCategoria).reduce((a, b) => (a as number) + (b as number), 0);
    
    if (loading) {
        return (
            <div className="min-h-full p-6 flex justify-center items-center">
                <p className="text-gray-500">Cargando dashboard...</p>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="min-h-full p-6">
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    Error: {error}
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-full p-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Panel Administrativo</h1>
                    <p className="text-gray-600 mt-1">Resumen financiero y operativo</p>
                </div>
                <div className="mt-4 md:mt-0 flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Período:</span>
                    <select
                        value={dateRange}
                        onChange={(e) => setDateRange(e.target.value as DateRange)}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                        <option value="7d">Últimos 7 días</option>
                        <option value="30d">Últimos 30 días</option>
                        <option value="90d">Últimos 90 días</option>
                        <option value="12m">Últimos 12 meses</option>
                    </select>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <KPICard
                    title="Ingresos del Mes"
                    value={formatCurrency(kpis.ingresos_mes)}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    }
                    trend={{ value: kpis.ingresos_tendencia, isPositive: kpis.ingresos_tendencia > 0 }}
                    color="green"
                />
                <KPICard
                    title="Gastos del Mes"
                    value={formatCurrency(kpis.gastos_mes)}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                    }
                    trend={{ value: Math.abs(kpis.gastos_tendencia), isPositive: kpis.gastos_tendencia < 0 }}
                    color="orange"
                />
                <KPICard
                    title="Citas del Mes"
                    value={kpis.citas_mes}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    }
                    trend={{ value: kpis.citas_tendencia, isPositive: kpis.citas_tendencia > 0 }}
                    color="blue"
                />
                <KPICard
                    title="Pacientes Nuevos"
                    value={kpis.pacientes_nuevos}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                        </svg>
                    }
                    trend={{ value: kpis.pacientes_tendencia, isPositive: kpis.pacientes_tendencia > 0 }}
                    color="purple"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                {/* Revenue Chart - Simple Bar representation */}
                <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Ingresos vs Gastos (Últimos 6 meses)</h3>
                    <div className="flex items-center justify-center h-64 text-gray-500">
                        <p>Gráfico de tendencias próximamente</p>
                    </div>
                </div>

                {/* Expense Breakdown */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Desglose de Gastos</h3>
                    <div className="space-y-3">
                        {Object.entries(gastosPorCategoria).length === 0 ? (
                            <p className="text-center text-gray-500 py-4">No hay gastos registrados</p>
                        ) : (
                            Object.entries(gastosPorCategoria)
                                .sort((a, b) => (b[1] as number) - (a[1] as number))
                                .map(([categoria, monto]) => (
                                <div key={categoria} className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <span className={`inline-flex px-2 py-0.5 text-xs rounded-full ${getCategoriaColor(categoria as any)}`}>
                                            {categoria}
                                        </span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-sm font-medium text-gray-900">{formatCurrency(monto as number)}</span>
                                        <span className="text-xs text-gray-500">
                                            ({(((monto as number) / totalGastos) * 100).toFixed(0)}%)
                                        </span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="flex justify-between font-semibold">
                            <span className="text-gray-700">Total</span>
                            <span className="text-gray-900">{formatCurrency(totalGastos)}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Cash Closings Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-800">Últimos Cortes de Caja</h3>
                </div>
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Saldo Inicial</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ingresos</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gastos</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Saldo Final</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cerrado por</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {cortesCaja.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                                    No hay cortes de caja registrados
                                </td>
                            </tr>
                        ) : (
                            cortesCaja.slice(0, 10).map((corte) => (
                            <tr key={corte.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {new Date(corte.fecha).toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short' })}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                    {formatCurrency(corte.saldo_efectivo || 0)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                                    +{formatCurrency(corte.total_ingresos)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                                    -{formatCurrency(corte.total_gastos)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                                    {formatCurrency((corte.saldo_efectivo || 0) + corte.total_ingresos - corte.total_gastos)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                    {corte.cerrado_por}
                                </td>
                            </tr>
                        )))}
                    </tbody>
                </table>
            </div>

            {/* Report Generator Component */}
            <div className="mt-6">
                <ReportGeneratorComponent />
            </div>

            {/* Recent Expenses */}
            <div className="mt-6 bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-800">Gastos Recientes</h3>
                    <button className="text-sm text-primary-600 hover:text-primary-800 font-medium">
                        Ver todos →
                    </button>
                </div>
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Concepto</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Monto</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {gastos.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                                    No hay gastos registrados este mes
                                </td>
                            </tr>
                        ) : (
                            gastos.slice(0, 10).map((gasto) => (
                            <tr key={gasto.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                    {new Date(gasto.fecha).toLocaleDateString('es-MX')}
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${getCategoriaColor(gasto.categoria)}`}>
                                        {gasto.categoria}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-900">{gasto.concepto}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                                    {formatCurrency(gasto.monto)}
                                </td>
                            </tr>
                        )))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminPage;
