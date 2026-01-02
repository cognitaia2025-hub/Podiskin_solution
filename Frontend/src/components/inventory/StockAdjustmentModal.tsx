/**
 * StockAdjustmentModal Component
 * Location: Frontend/src/components/inventory/StockAdjustmentModal.tsx
 * 
 * Compact modal for quick stock adjustments.
 * Shows current stock and projected new stock.
 */

import React, { useState, useEffect } from 'react';
import { X, TrendingUp, TrendingDown, Package } from 'lucide-react';
import type { ProductListItem, StockAdjustmentRequest } from '../../services/inventoryService';

interface StockAdjustmentModalProps {
    isOpen: boolean;
    product: ProductListItem | null;
    onClose: () => void;
    onSubmit: (adjustment: StockAdjustmentRequest) => Promise<void>;
}

const MOVEMENT_TYPES: Array<{
    value: StockAdjustmentRequest['tipo_movimiento'];
    label: string;
    icon: any;
    color: string;
}> = [
        { value: 'Entrada', label: 'Entrada', icon: TrendingUp, color: 'text-green-600' },
        { value: 'Salida', label: 'Salida', icon: TrendingDown, color: 'text-red-600' },
        { value: 'Ajuste_Positivo', label: 'Ajuste +', icon: Package, color: 'text-blue-600' },
        { value: 'Ajuste_Negativo', label: 'Ajuste -', icon: Package, color: 'text-orange-600' },
    ];

const StockAdjustmentModal: React.FC<StockAdjustmentModalProps> = ({
    isOpen,
    product,
    onClose,
    onSubmit,
}) => {
    const [formData, setFormData] = useState<StockAdjustmentRequest>({
        tipo_movimiento: 'Entrada',
        cantidad: 1,
        motivo: '',
    });

    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setFormData({
                tipo_movimiento: 'Entrada',
                cantidad: 1,
                motivo: '',
            });
        }
    }, [isOpen, product]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await onSubmit(formData);
            onClose();
        } catch (error) {
            console.error('Error submitting adjustment:', error);
        } finally {
            setSubmitting(false);
        }
    };

    const calculateNewStock = () => {
        if (!product) return 0;
        const { tipo_movimiento, cantidad } = formData;

        if (tipo_movimiento === 'Entrada' || tipo_movimiento === 'Ajuste_Positivo') {
            return product.stock_actual + cantidad;
        } else {
            return product.stock_actual - cantidad;
        }
    };

    if (!isOpen || !product) return null;

    const newStock = calculateNewStock();
    const isIncrease = formData.tipo_movimiento === 'Entrada' || formData.tipo_movimiento === 'Ajuste_Positivo';

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-900">
                        Ajustar Stock
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Product Info */}
                    <div className="bg-gray-50 rounded-lg p-4">
                        <h3 className="font-medium text-gray-900">{product.nombre}</h3>
                        <p className="text-sm text-gray-600">Código: {product.codigo_producto}</p>
                        <div className="mt-2 flex items-center justify-between">
                            <span className="text-sm text-gray-600">Stock actual:</span>
                            <span className="text-lg font-semibold text-gray-900">
                                {product.stock_actual} {product.unidad_medida}
                            </span>
                        </div>
                    </div>

                    {/* Movement Type */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tipo de Movimiento *
                        </label>
                        <div className="grid grid-cols-2 gap-2">
                            {MOVEMENT_TYPES.map((type) => {
                                const Icon = type.icon;
                                const isSelected = formData.tipo_movimiento === type.value;

                                return (
                                    <button
                                        key={type.value}
                                        type="button"
                                        onClick={() => setFormData(prev => ({ ...prev, tipo_movimiento: type.value }))}
                                        className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-colors ${isSelected
                                                ? 'border-blue-500 bg-blue-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <Icon className={`w-4 h-4 ${isSelected ? 'text-blue-600' : type.color}`} />
                                        <span className={`text-sm font-medium ${isSelected ? 'text-blue-900' : 'text-gray-700'}`}>
                                            {type.label}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Quantity */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Cantidad *
                        </label>
                        <input
                            type="number"
                            value={formData.cantidad}
                            onChange={(e) => setFormData(prev => ({ ...prev, cantidad: parseInt(e.target.value) || 0 }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            min="1"
                            required
                        />
                    </div>

                    {/* Projected Stock */}
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-blue-900">Nuevo stock proyectado:</span>
                            <div className="flex items-center gap-2">
                                {isIncrease ? (
                                    <TrendingUp className="w-4 h-4 text-green-600" />
                                ) : (
                                    <TrendingDown className="w-4 h-4 text-red-600" />
                                )}
                                <span className={`text-xl font-bold ${newStock < product.stock_minimo ? 'text-red-600' : 'text-green-600'
                                    }`}>
                                    {newStock} {product.unidad_medida}
                                </span>
                            </div>
                        </div>
                        {newStock < product.stock_minimo && (
                            <p className="text-xs text-red-600 mt-2">
                                ⚠️ El stock quedará por debajo del mínimo ({product.stock_minimo})
                            </p>
                        )}
                    </div>

                    {/* Reason */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Motivo / Notas *
                        </label>
                        <textarea
                            value={formData.motivo}
                            onChange={(e) => setFormData(prev => ({ ...prev, motivo: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            rows={3}
                            placeholder="Describe el motivo del ajuste..."
                            required
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4 border-t">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                            disabled={submitting}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                            disabled={submitting}
                        >
                            {submitting ? 'Guardando...' : 'Confirmar Ajuste'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default StockAdjustmentModal;
