/**
 * BillingPage - Página de Gestión de Cobros
 * ===========================================
 * Integra todos los componentes del módulo de cobros:
 * - Estadísticas de pagos
 * - Filtros y búsqueda
 * - Tabla de pagos
 * - Modal de registro/edición
 * - Vista previa de recibos
 */

import React, { useState, useEffect } from 'react';
import { DollarSign, Plus, AlertCircle } from 'lucide-react';
import { PermissionGuard } from '../components/common/PermissionGuard';
import {
  PaymentStats,
  PaymentFilters,
  PaymentTable,
  PaymentModal,
  ReceiptPreview,
} from '../components/billing';
import {
  getPayments,
  getPaymentStats,
  createPayment,
  updatePayment,
} from '../services/billingService';
import type { Payment, PaymentCreate, PaymentUpdate, PaymentStats as StatsType } from '../types/billing';
import { usePermissions } from '../hooks/usePermissions';

const BillingPage: React.FC = () => {
  const { canRead, canWrite } = usePermissions();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [stats, setStats] = useState<StatsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [estadoFilter, setEstadoFilter] = useState<string>('todos');
  const [metodoFilter, setMetodoFilter] = useState<string>('todos');

  // Modals
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [isReceiptModalOpen, setIsReceiptModalOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);

  // Cargar datos iniciales
  useEffect(() => {
    if (canRead('cobros')) {
      loadData();
    }
  }, [canRead]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [paymentsData, statsData] = await Promise.all([
        getPayments(),
        getPaymentStats(),
      ]);
      setPayments(paymentsData);
      setStats(statsData);
    } catch (err) {
      console.error('Error al cargar datos:', err);
      setError('Error al cargar los datos de cobros');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar pagos
  const filteredPayments = payments.filter((payment) => {
    const matchesSearch =
      payment.nombre_paciente?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payment.id_pago.toString().includes(searchTerm);

    const matchesEstado =
      estadoFilter === 'todos' || payment.estado_pago === estadoFilter;

    const matchesMetodo =
      metodoFilter === 'todos' || payment.metodo_pago === metodoFilter;

    return matchesSearch && matchesEstado && matchesMetodo;
  });

  // Handlers
  const handleCreatePayment = () => {
    setSelectedPayment(null);
    setIsPaymentModalOpen(true);
  };

  const handleEditPayment = (payment: Payment) => {
    setSelectedPayment(payment);
    setIsPaymentModalOpen(true);
  };

  const handleViewReceipt = (payment: Payment) => {
    setSelectedPayment(payment);
    setIsReceiptModalOpen(true);
  };

  const handleSubmitPayment = async (data: PaymentCreate | PaymentUpdate) => {
    try {
      if (selectedPayment) {
        await updatePayment(selectedPayment.id_pago, data as PaymentUpdate);
      } else {
        await createPayment(data as PaymentCreate);
      }
      await loadData();
      setIsPaymentModalOpen(false);
    } catch (err) {
      console.error('Error al guardar pago:', err);
      throw err;
    }
  };

  // Vista de permisos insuficientes
  if (!canRead('cobros')) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            Acceso Denegado
          </h2>
          <p className="text-gray-500">
            No tienes permisos para ver esta sección
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-50 overflow-auto">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Gestión de Cobros</h1>
              <p className="text-gray-600">Administra pagos y facturación</p>
            </div>
          </div>

          <PermissionGuard module="cobros" action="write">
            <button
              onClick={handleCreatePayment}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md"
            >
              <Plus className="w-5 h-5" />
              Nuevo Pago
            </button>
          </PermissionGuard>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800">{error}</p>
            <button
              onClick={loadData}
              className="ml-auto text-red-600 hover:text-red-800 font-medium"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Stats */}
        {stats && <PaymentStats stats={stats} loading={loading} />}

        {/* Filters */}
        <PaymentFilters
          searchQuery={searchTerm}
          onSearchChange={setSearchTerm}
          estadoFilter={estadoFilter}
          onEstadoChange={setEstadoFilter}
          metodoFilter={metodoFilter}
          onMetodoChange={setMetodoFilter}
          onNewPayment={handleCreatePayment}
          canCreate={canWrite('cobros')}
        />

        {/* Table */}
        <PaymentTable
          payments={filteredPayments}
          loading={loading}
          onEdit={handleEditPayment}
          onViewReceipt={handleViewReceipt}
          canEdit={canWrite('cobros')}
        />

        {/* Modals */}
        <PaymentModal
          isOpen={isPaymentModalOpen}
          onClose={() => setIsPaymentModalOpen(false)}
          onSubmit={handleSubmitPayment}
          payment={selectedPayment}
        />

        <ReceiptPreview
          isOpen={isReceiptModalOpen}
          onClose={() => setIsReceiptModalOpen(false)}
          payment={selectedPayment}
        />
      </div>
    </div>
  );
};

export default BillingPage;
