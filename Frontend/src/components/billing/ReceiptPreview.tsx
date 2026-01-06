/**
 * Componente ReceiptPreview
 * ==========================
 * Vista previa e impresión de recibo de pago
 */

import React from 'react';
import { X, Printer } from 'lucide-react';
import type { Payment } from '../../types/billing';
import { formatCurrency, formatDate } from '../../services/billingService';

interface ReceiptPreviewProps {
  isOpen: boolean;
  onClose: () => void;
  payment: Payment | null;
}

export const ReceiptPreview: React.FC<ReceiptPreviewProps> = ({
  isOpen,
  onClose,
  payment,
}) => {
  if (!isOpen || !payment) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        {/* Header (no-print) */}
        <div className="flex items-center justify-between p-4 border-b print:hidden">
          <h2 className="text-xl font-bold text-gray-900">Vista Previa de Recibo</h2>
          <div className="flex gap-2">
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Printer className="w-4 h-4" />
              Imprimir
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Receipt Content (printable) */}
        <div className="p-8 print:p-0">
          <div className="border-2 border-gray-300 rounded-lg p-8 print:border-0">
            {/* Clinic Header */}
            <div className="text-center mb-8 pb-6 border-b-2 border-gray-200">
              <h1 className="text-3xl font-bold text-blue-900 mb-2">
                Podoski Solution
              </h1>
              <p className="text-gray-600 text-sm">Clínica Podológica Profesional</p>
              <p className="text-gray-500 text-xs mt-1">
                RFC: POD123456ABC | Tel: (55) 1234-5678
              </p>
            </div>

            {/* Receipt Title */}
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">RECIBO DE PAGO</h2>
              <p className="text-gray-600 mt-1">Folio: #{payment.id_pago.toString().padStart(6, '0')}</p>
            </div>

            {/* Payment Details */}
            <div className="space-y-4 mb-8">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Fecha:</p>
                  <p className="font-semibold">{formatDate(payment.fecha_pago)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Paciente:</p>
                  <p className="font-semibold">{payment.nombre_paciente || 'N/A'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Método de Pago:</p>
                  <p className="font-semibold">{payment.metodo_pago.replace('_', ' ')}</p>
                </div>
                {payment.referencia_pago && (
                  <div>
                    <p className="text-sm text-gray-600">Referencia:</p>
                    <p className="font-semibold">{payment.referencia_pago}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Amounts Table */}
            <div className="border-t-2 border-b-2 border-gray-300 py-4 mb-6">
              <div className="space-y-3">
                <div className="flex justify-between text-lg">
                  <span className="text-gray-700">Monto Total:</span>
                  <span className="font-semibold">{formatCurrency(payment.monto_total)}</span>
                </div>
                <div className="flex justify-between text-lg text-green-600">
                  <span>Monto Pagado:</span>
                  <span className="font-semibold">{formatCurrency(payment.monto_pagado)}</span>
                </div>
                <div className="flex justify-between text-lg">
                  <span className="text-gray-700">Saldo Pendiente:</span>
                  <span className={`font-bold ${payment.saldo_pendiente > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {formatCurrency(payment.saldo_pendiente)}
                  </span>
                </div>
              </div>
            </div>

            {/* Invoice Info */}
            {payment.factura_solicitada && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm font-semibold text-blue-900 mb-1">
                  ✓ Factura Solicitada
                </p>
                {payment.rfc_factura && (
                  <p className="text-sm text-blue-700">RFC: {payment.rfc_factura}</p>
                )}
                {payment.id_factura && (
                  <p className="text-sm text-blue-700">
                    Factura generada: #{payment.id_factura}
                  </p>
                )}
              </div>
            )}

            {/* Notes */}
            {payment.notas && (
              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-1">Notas:</p>
                <p className="text-sm text-gray-800 italic">{payment.notas}</p>
              </div>
            )}

            {/* Footer */}
            <div className="text-center mt-8 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-2">
                Gracias por su preferencia
              </p>
              <p className="text-xs text-gray-500">
                Este documento es un comprobante de pago válido
              </p>
              <p className="text-xs text-gray-400 mt-4">
                Impreso el: {new Date().toLocaleString('es-MX')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
