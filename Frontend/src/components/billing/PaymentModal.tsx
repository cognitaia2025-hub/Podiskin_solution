/**
 * Componente PaymentModal
 * ========================
 * Modal para crear/editar pagos
 */

import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import type { Payment, PaymentCreate, PaymentUpdate, MetodoPago } from '../../types/billing';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payment: PaymentCreate | PaymentUpdate) => Promise<void>;
  payment?: Payment | null;
  citaId?: number;
}

export const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  payment,
  citaId,
}) => {
  const [formData, setFormData] = useState({
    id_cita: citaId || payment?.id_cita || 0,
    monto_total: payment?.monto_total || 0,
    monto_pagado: payment?.monto_pagado || 0,
    metodo_pago: (payment?.metodo_pago || 'Efectivo') as MetodoPago,
    referencia_pago: payment?.referencia_pago || '',
    factura_solicitada: payment?.factura_solicitada || false,
    rfc_factura: payment?.rfc_factura || '',
    notas: payment?.notas || '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (payment) {
      setFormData({
        id_cita: payment.id_cita,
        monto_total: payment.monto_total,
        monto_pagado: payment.monto_pagado,
        metodo_pago: payment.metodo_pago,
        referencia_pago: payment.referencia_pago || '',
        factura_solicitada: payment.factura_solicitada,
        rfc_factura: payment.rfc_factura || '',
        notas: payment.notas || '',
      });
    }
  }, [payment]);

  const saldoPendiente = formData.monto_total - formData.monto_pagado;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Error al guardar pago:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">
            {payment ? 'Editar Pago' : 'Registrar Nuevo Pago'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Montos */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Monto Total *
              </label>
              <input
                type="number"
                step="0.01"
                required
                value={formData.monto_total}
                onChange={(e) =>
                  setFormData({ ...formData, monto_total: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Monto Pagado *
              </label>
              <input
                type="number"
                step="0.01"
                required
                value={formData.monto_pagado}
                onChange={(e) =>
                  setFormData({ ...formData, monto_pagado: parseFloat(e.target.value) || 0 })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Saldo Pendiente
              </label>
              <input
                type="number"
                step="0.01"
                value={saldoPendiente}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-700"
              />
            </div>
          </div>

          {/* Método de Pago */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Método de Pago *
            </label>
            <div className="grid grid-cols-3 gap-3">
              {['Efectivo', 'Tarjeta_Debito', 'Tarjeta_Credito', 'Transferencia', 'Cheque', 'Otro'].map(
                (metodo) => (
                  <button
                    key={metodo}
                    type="button"
                    onClick={() => setFormData({ ...formData, metodo_pago: metodo as MetodoPago })}
                    className={`px-4 py-2 rounded-lg border-2 transition-colors ${
                      formData.metodo_pago === metodo
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-blue-300'
                    }`}
                  >
                    {metodo.replace('_', ' ')}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Referencia */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Referencia/Folio
            </label>
            <input
              type="text"
              value={formData.referencia_pago}
              onChange={(e) => setFormData({ ...formData, referencia_pago: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Número de referencia, folio, autorización..."
            />
          </div>

          {/* Factura */}
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.factura_solicitada}
                onChange={(e) =>
                  setFormData({ ...formData, factura_solicitada: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">
                ¿Requiere Factura?
              </span>
            </label>

            {formData.factura_solicitada && (
              <div className="mt-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RFC
                </label>
                <input
                  type="text"
                  value={formData.rfc_factura}
                  onChange={(e) => setFormData({ ...formData, rfc_factura: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="RFC para facturación"
                  maxLength={13}
                />
              </div>
            )}
          </div>

          {/* Notas */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notas adicionales
            </label>
            <textarea
              value={formData.notas}
              onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Observaciones, comentarios..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {isSubmitting ? 'Guardando...' : payment ? 'Actualizar' : 'Registrar Pago'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
