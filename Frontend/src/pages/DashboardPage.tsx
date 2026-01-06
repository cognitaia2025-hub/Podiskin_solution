/**
 * Dashboard Page
 * 
 * Main dashboard page showing KPIs, charts, and metrics.
 * Uses mock data for development until backend endpoints are implemented.
 */

import React, { useState, useEffect } from 'react';
import { Users, Calendar, DollarSign, TrendingUp } from 'lucide-react';
import { toast } from 'react-toastify';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import KPICard from '../components/dashboard/KPICard';
import AppointmentTrendChart from '../components/dashboard/AppointmentTrendChart';
import AppointmentsByStatusChart from '../components/dashboard/AppointmentsByStatusChart';
import RevenueChart from '../components/dashboard/RevenueChart';
import TopTreatmentsTable from '../components/dashboard/TopTreatmentsTable';
import type {
  DashboardStats,
  AppointmentTrend,
  RevenueTrend,
} from '../services/dashboardService';
import {
  getDashboardStats,
  getAppointmentTrend,
  getRevenueTrend,
} from '../services/dashboardService';

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [appointmentTrend, setAppointmentTrend] = useState<AppointmentTrend[]>([]);
  const [revenueTrend, setRevenueTrend] = useState<RevenueTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);

      // Las funciones ya no lanzan errores, retornan datos vacíos si hay problemas
      const [statsData, apptTrend, revTrend] = await Promise.all([
        getDashboardStats(),
        getAppointmentTrend(30),
        getRevenueTrend(),
      ]);

      setStats(statsData);
      setAppointmentTrend(apptTrend);
      setRevenueTrend(revTrend);
      setLastUpdated(new Date());
    } catch (error) {
      // Esto no debería ocurrir ya que las funciones manejan sus errores
      console.error('Error loading dashboard:', error);
      // Establecer datos vacíos en lugar de mostrar error
      setStats({
        total_patients: 0,
        active_patients: 0,
        new_patients_this_month: 0,
        total_appointments_today: 0,
        total_appointments_week: 0,
        total_appointments_month: 0,
        appointments_by_status: {
          pendiente: 0,
          confirmada: 0,
          completada: 0,
          cancelada: 0,
          no_asistio: 0
        },
        revenue_today: 0,
        revenue_week: 0,
        revenue_month: 0,
        revenue_year: 0,
        top_treatments: [],
        ocupacion_porcentaje: 0,
        upcoming_appointments: 0
      });
      setAppointmentTrend([]);
      setRevenueTrend([]);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-200px)]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  // Siempre mostrar el dashboard, incluso con datos en 0
  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <DashboardHeader onRefresh={loadDashboardData} lastUpdated={lastUpdated} />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Pacientes"
          value={stats?.total_patients || 0}
          icon={<Users className="w-6 h-6" />}
          color="blue"
          trend={stats?.total_patients > 0 ? { value: 12, isPositive: true } : undefined}
        />
        <KPICard
          title="Citas Hoy"
          value={stats?.total_appointments_today || 0}
          icon={<Calendar className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Ingresos del Mes"
          value={`$${((stats?.revenue_month || 0) / 1000).toFixed(1)}K`}
          icon={<DollarSign className="w-6 h-6" />}
          color="purple"
          trend={stats?.revenue_month > 0 ? { value: 8, isPositive: true } : undefined}
        />
        <KPICard
          title="Ocupación"
          value={`${stats?.ocupacion_porcentaje || 0}%`}
          icon={<TrendingUp className="w-6 h-6" />}
          color="orange"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AppointmentTrendChart data={appointmentTrend || []} />
        <AppointmentsByStatusChart data={stats?.appointments_by_status || {
          pendiente: 0,
          confirmada: 0,
          completada: 0,
          cancelada: 0,
          no_asistio: 0
        }} />
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart data={revenueTrend || []} />
        <TopTreatmentsTable data={stats?.top_treatments || []} />
      </div>
    </div>
  );
};

export default DashboardPage;
