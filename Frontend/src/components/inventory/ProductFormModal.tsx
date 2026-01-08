/**
 * ProductFormModal Component
 * Location: Frontend/src/components/inventory/ProductFormModal.tsx
 * 
 * Modal for creating/editing inventory products.
 * Handles form state and validation.
 */

import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import type { ProductListItem, CreateProductRequest } from '../../services/inventoryService';

interface ProductFormModalProps {
    isOpen: boolean;
    product: ProductListItem | null;
    onClose: () => void;
    onSubmit: (data: CreateProductRequest) => Promise<void>;
}

const CATEGORIAS = [
    'Material_Curacion',
    'Instrumental',
    'Medicamento',
    'Consumible',
    'Equipo_Medico',
    'Producto_Venta',
    'Material_Limpieza',
    'Papeleria'
];

const ProductFormModal: React.FC<ProductFormModalProps> = ({
    isOpen,
    product,
    onClose,
    onSubmit,
}) => {
    const [formData, setFormData] = useState<CreateProductRequest>({
        codigo_producto: '',
        nombre: '',
        categoria: 'Consumible',
        unidad_medida: 'PZA',
        cantidad_por_unidad: 1,
        stock_actual: 0,
        stock_minimo: 5,
        stock_maximo: 100,
    });

    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (product) {
            setFormData({
                codigo_producto: product.codigo_producto,
                nombre: product.nombre,
                categoria: product.categoria,
                unidad_medida: product.unidad_medida,
                cantidad_por_unidad: product.cantidad_por_unidad || 1,
                stock_minimo: product.stock_minimo,
                stock_maximo: product.stock_maximo,
                costo_unitario: product.costo_unitario || undefined,
                precio_venta: product.precio_venta || undefined,
            });
        } else {
            setFormData({
                codigo_producto: '',
                nombre: '',
                categoria: 'Consumible',
                unidad_medida: 'PZA',
                cantidad_por_unidad: 1,
                stock_actual: 0,
                stock_minimo: 5,
                stock_maximo: 100,
            });
        }
    }, [product]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await onSubmit(formData);
            onClose();
        } catch (error) {
            console.error('Error submitting form:', error);
        } finally {
            setSubmitting(false);
        }
    };

    const handleChange = (field: keyof CreateProductRequest, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
                    <h2 className="text-xl font-semibold text-gray-900">
                        {product ? 'Editar Producto' : 'Nuevo Producto'}
                    </h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        {/* Código Producto */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Código de Producto *
                            </label>
                            <input
                                type="text"
                                value={formData.codigo_producto}
                                onChange={(e) => handleChange('codigo_producto', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                                disabled={!!product}
                            />
                        </div>

                        {/* Código de Barras */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Código de Barras
                            </label>
                            <input
                                type="text"
                                value={formData.codigo_barras || ''}
                                onChange={(e) => handleChange('codigo_barras', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </div>

                    {/* Nombre */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nombre del Producto *
                        </label>
                        <input
                            type="text"
                            value={formData.nombre}
                            onChange={(e) => handleChange('nombre', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            required
                        />
                    </div>

                    {/* Descripción */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Descripción
                        </label>
                        <textarea
                            value={formData.descripcion || ''}
                            onChange={(e) => handleChange('descripcion', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            rows={2}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {/* Categoría */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Categoría *
                            </label>
                            <select
                                value={formData.categoria}
                                onChange={(e) => handleChange('categoria', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            >
                                {CATEGORIAS.map(cat => (
                                    <option key={cat} value={cat}>
                                        {cat.replace('_', ' ')}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Unidad de Medida */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Unidad de Medida *
                            </label>
                            <select
                                value={formData.unidad_medida}
                                onChange={(e) => handleChange('unidad_medida', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                            >
                                <option value="">Seleccione unidad...</option>
                                <option value="PZA">Piezas (PZA)</option>
                                <option value="CAJA">Cajas (CAJA)</option>
                                <option value="LITRO">Litros (LITRO)</option>
                                <option value="KG">Kilogramos (KG)</option>
                                <option value="BOTELLA">Botellas (BOTELLA)</option>
                                <option value="ROLLO">Rollos (ROLLO)</option>
                                <option value="BOLSA">Bolsas (BOLSA)</option>
                                <option value="UNIDAD">Unidad (UNIDAD)</option>
                            </select>
                        </div>

                        {/* Cantidad por Unidad */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Cantidad por Unidad
                                <span className="text-gray-500 text-xs ml-1">(ej: 100 pares por caja)</span>
                            </label>
                            <input
                                type="number"
                                value={formData.cantidad_por_unidad || 1}
                                onChange={(e) => handleChange('cantidad_por_unidad', parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                min="1"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        {/* Stock Actual (solo para nuevos) */}
                        {!product && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Stock Inicial
                                </label>
                                <input
                                    type="number"
                                    value={formData.stock_actual || 0}
                                    onChange={(e) => handleChange('stock_actual', parseInt(e.target.value))}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    min="0"
                                />
                            </div>
                        )}

                        {/* Stock Mínimo */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Stock Mínimo *
                            </label>
                            <input
                                type="number"
                                value={formData.stock_minimo || 5}
                                onChange={(e) => handleChange('stock_minimo', parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                min="0"
                                required
                            />
                        </div>

                        {/* Stock Máximo */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Stock Máximo *
                            </label>
                            <input
                                type="number"
                                value={formData.stock_maximo || 100}
                                onChange={(e) => handleChange('stock_maximo', parseInt(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                min="0"
                                required
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {/* Costo Unitario */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Costo Unitario
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                value={formData.costo_unitario || ''}
                                onChange={(e) => handleChange('costo_unitario', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                min="0"
                            />
                        </div>

                        {/* Precio Venta */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Precio de Venta
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                value={formData.precio_venta || ''}
                                onChange={(e) => handleChange('precio_venta', parseFloat(e.target.value))}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                min="0"
                            />
                        </div>
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
                            {submitting ? 'Guardando...' : (product ? 'Actualizar' : 'Crear')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProductFormModal;
