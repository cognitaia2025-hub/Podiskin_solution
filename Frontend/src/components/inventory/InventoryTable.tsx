/**
 * InventoryTable Component
 * Location: Frontend/src/components/inventory/InventoryTable.tsx
 * 
 * Displays the list of inventory products in a table format.
 * Shows color-coded stock indicators and action buttons.
 */

import React from 'react';
import { Edit2, Package, AlertTriangle, TrendingDown } from 'lucide-react';
import type { ProductListItem } from '../../services/inventoryService';

interface InventoryTableProps {
    products: ProductListItem[];
    searchQuery: string;
    onEdit: (product: ProductListItem) => void;
    onAdjustStock: (product: ProductListItem) => void;
    loading?: boolean;
}

const InventoryTable: React.FC<InventoryTableProps> = ({
    products,
    searchQuery,
    onEdit,
    onAdjustStock,
    loading = false,
}) => {
    // Filter products by search query
    const filteredProducts = products.filter(product =>
        product.nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.codigo_producto.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.categoria.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Get stock status color
    const getStockStatus = (product: ProductListItem) => {
        const { stock_actual, stock_minimo } = product;

        if (stock_actual < stock_minimo) {
            return {
                color: 'bg-red-100 text-red-800',
                icon: AlertTriangle,
                label: 'Crítico'
            };
        } else if (stock_actual <= stock_minimo * 1.2) {
            return {
                color: 'bg-yellow-100 text-yellow-800',
                icon: TrendingDown,
                label: 'Bajo'
            };
        }
        return {
            color: 'bg-green-100 text-green-800',
            icon: Package,
            label: 'Normal'
        };
    };

    // Get category badge color
    const getCategoryColor = (categoria: string) => {
        const colors: Record<string, string> = {
            'Material_Curacion': 'bg-blue-100 text-blue-800',
            'Instrumental': 'bg-purple-100 text-purple-800',
            'Medicamento': 'bg-pink-100 text-pink-800',
            'Consumible': 'bg-cyan-100 text-cyan-800',
            'Equipo_Medico': 'bg-indigo-100 text-indigo-800',
            'Producto_Venta': 'bg-green-100 text-green-800',
            'Material_Limpieza': 'bg-orange-100 text-orange-800',
            'Papeleria': 'bg-gray-100 text-gray-800',
        };
        return colors[categoria] || 'bg-gray-100 text-gray-800';
    };

    // Format currency
    const formatCurrency = (value: number | null | undefined) => {
        if (!value) return '-';
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN'
        }).format(value);
    };

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Package className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-pulse" />
                <p className="text-gray-600">Cargando productos...</p>
            </div>
        );
    }

    if (filteredProducts.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No se encontraron productos
                </h3>
                <p className="text-gray-600">
                    {searchQuery ? 'Intenta con otra búsqueda' : 'Agrega el primer producto al inventario'}
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Código
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Producto
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Categoría
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Stock
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Precio
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Estado
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Acciones
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {filteredProducts.map((product) => {
                        const stockStatus = getStockStatus(product);
                        const StatusIcon = stockStatus.icon;

                        return (
                            <tr key={product.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">
                                        {product.codigo_producto}
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="text-sm font-medium text-gray-900">
                                        {product.nombre}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                        {product.unidad_medida}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(product.categoria)}`}>
                                        {product.categoria.replace('_', ' ')}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        <span className="font-semibold">{product.stock_actual}</span>
                                        {' / '}
                                        <span className="text-gray-500">{product.stock_minimo}</span>
                                    </div>
                                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${stockStatus.color} mt-1`}>
                                        <StatusIcon className="w-3 h-3" />
                                        {stockStatus.label}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm text-gray-900">
                                        {formatCurrency(product.precio_venta)}
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        Costo: {formatCurrency(product.costo_unitario)}
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {product.activo ? (
                                        <span className="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                            Activo
                                        </span>
                                    ) : (
                                        <span className="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                            Inactivo
                                        </span>
                                    )}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => onAdjustStock(product)}
                                        className="text-green-600 hover:text-green-900 mr-4"
                                        title="Ajustar Stock"
                                    >
                                        <Package className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => onEdit(product)}
                                        className="text-blue-600 hover:text-blue-900"
                                        title="Editar"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};

export default InventoryTable;
