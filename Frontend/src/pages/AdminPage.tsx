/**
 * Admin Page
 * 
 * Administrative dashboard with:
 * - KPI cards for key metrics
 * - Revenue/Expense charts
 * - Cash closing history
 * - Expense breakdown
 */

import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { Navigate } from 'react-router-dom';
import KPICard from '../components/dashboard/KPICard';
import {
    mockKPIs,
    mockGastos,
    mockCortesCaja,
    mockIngresosMensuales,
    getCategoriaColor,
} from '../services/adminMockData';

type DateRange = '7d' | '30d' | '90d' | '12m';

const AdminPage: React.FC = () => {
    const { user } = useAuth();
    const [dateRange, setDateRange] = useState<DateRange>('30d');

    // Redirect non-admin users
    if (user?.rol !== 'Admin') {
        return <Navigate to="/calendar" replace />;
    }

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 0,
        }).format(value);
    };

    // Calculate expense breakdown by category
    const gastosPorCategoria = mockGastos.reduce((acc, gasto) => {
        acc[gasto.categoria] = (acc[gasto.categoria] || 0) + gasto.monto;
        return acc;
    }, {} as Record<string, number>);

    const totalGastos = Object.values(gastosPorCategoria).reduce((a, b) => a + b, 0);

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
                    value={formatCurrency(mockKPIs.ingresos_mes)}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    }
                    trend={{ value: mockKPIs.ingresos_tendencia, isPositive: mockKPIs.ingresos_tendencia > 0 }}
                    color="green"
                />
                <KPICard
                    title="Gastos del Mes"
                    value={formatCurrency(mockKPIs.gastos_mes)}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                    }
                    trend={{ value: Math.abs(mockKPIs.gastos_tendencia), isPositive: mockKPIs.gastos_tendencia < 0 }}
                    color="orange"
                />
                <KPICard
                    title="Citas del Mes"
                    value={mockKPIs.citas_mes}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    }
                    trend={{ value: mockKPIs.citas_tendencia, isPositive: mockKPIs.citas_tendencia > 0 }}
                    color="blue"
                />
                <KPICard
                    title="Pacientes Nuevos"
                    value={mockKPIs.pacientes_nuevos}
                    icon={
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                        </svg>
                    }
                    trend={{ value: mockKPIs.pacientes_tendencia, isPositive: mockKPIs.pacientes_tendencia > 0 }}
                    color="purple"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                {/* Revenue Chart - Simple Bar representation */}
                <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Ingresos vs Gastos (Últimos 6 meses)</h3>
                    <div className="space-y-4">
                        {mockIngresosMensuales.map((mes) => (
                            <div key={mes.mes} className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="font-medium text-gray-700">{mes.mes}</span>
                                    <div className="flex space-x-4">
                                        <span className="text-green-600">{formatCurrency(mes.ingresos)}</span>
                                        <span className="text-red-600">-{formatCurrency(mes.gastos)}</span>
                                    </div>
                                </div>
                                <div className="flex space-x-1 h-6">
                                    <div
                                        className="bg-green-500 rounded-l"
                                        style={{ width: `${(mes.ingresos / 50000) * 100}%` }}
                                    />
                                    <div
                                        className="bg-red-400 rounded-r"
                                        style={{ width: `${(mes.gastos / 50000) * 100}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-4 flex items-center justify-end space-x-4 text-sm">
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-green-500 rounded" />
                            <span className="text-gray-600">Ingresos</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-red-400 rounded" />
                            <span className="text-gray-600">Gastos</span>
                        </div>
                    </div>
                </div>

                {/* Expense Breakdown */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Desglose de Gastos</h3>
                    <div className="space-y-3">
                        {Object.entries(gastosPorCategoria)
                            .sort((a, b) => b[1] - a[1])
                            .map(([categoria, monto]) => (
                                <div key={categoria} className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <span className={`inline-flex px-2 py-0.5 text-xs rounded-full ${getCategoriaColor(categoria as any)}`}>
                                            {categoria}
                                        </span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-sm font-medium text-gray-900">{formatCurrency(monto)}</span>
                                        <span className="text-xs text-gray-500">
                                            ({((monto / totalGastos) * 100).toFixed(0)}%)
                                        </span>
                                    </div>
                                </div>
                            ))}
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
                        {mockCortesCaja.map((corte) => (
                            <tr key={corte.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {new Date(corte.fecha_corte).toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short' })}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                    {formatCurrency(corte.saldo_inicial)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                                    +{formatCurrency(corte.total_ingresos)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                                    -{formatCurrency(corte.gastos_dia)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                                    {formatCurrency(corte.saldo_final)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                    {corte.usuario_cierre}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
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
                        {mockGastos.map((gasto) => (
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
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminPage;
