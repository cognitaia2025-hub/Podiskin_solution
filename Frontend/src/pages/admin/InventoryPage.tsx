/**
 * Inventory Page
 * Location: Frontend/src/pages/admin/InventoryPage.tsx
 * 
 * Orchestrates inventory management operations.
 * Delegates UI rendering to specialized components.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../auth/AuthContext';
import { Navigate } from 'react-router-dom';
import { Package, Plus, Search, Loader2, AlertTriangle } from 'lucide-react';
import { toast } from 'react-toastify';
import {
    inventoryService,
    type ProductListItem,
    type CreateProductRequest,
    type UpdateProductRequest,
    type StockAdjustmentRequest,
    type StockAlert
} from '../../services/inventoryService';
import InventoryTable from '../../components/inventory/InventoryTable';
import ProductFormModal from '../../components/inventory/ProductFormModal';
import StockAdjustmentModal from '../../components/inventory/StockAdjustmentModal';

const InventoryPage: React.FC = () => {
    const { user } = useAuth();

    // Redirect non-authorized users
    if (!user || !['Admin', 'Podologo', 'Recepcionista'].includes(user.rol)) {
        return <Navigate to="/calendar" replace />;
    }

    // State
    const [products, setProducts] = useState<ProductListItem[]>([]);
    const [alerts, setAlerts] = useState<StockAlert[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isProductModalOpen, setIsProductModalOpen] = useState(false);
    const [isStockModalOpen, setIsStockModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<ProductListItem | null>(null);
    const [adjustingProduct, setAdjustingProduct] = useState<ProductListItem | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showInactive, setShowInactive] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState<string>('');

    // Pagination
    const [currentPage, setCurrentPage] = useState(0);
    const [totalProducts, setTotalProducts] = useState(0);
    const itemsPerPage = 50;

    // Load products and alerts
    const loadData = async () => {
        setIsLoading(true);
        try {
            const [productsData, alertsData] = await Promise.all([
                inventoryService.getProducts({
                    limit: itemsPerPage,
                    offset: currentPage * itemsPerPage,
                    categoria: selectedCategory || undefined,
                    activo: !showInactive,
                }),
                inventoryService.getLowStockAlerts()
            ]);
            setProducts(productsData.productos);
            setTotalProducts(productsData.total);
            setAlerts(alertsData);
        } catch (error: any) {
            toast.error(error.message || 'Error al cargar datos');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [currentPage, selectedCategory, showInactive]);

    // Open modal for creating new product
    const handleOpenCreateModal = () => {
        setEditingProduct(null);
        setIsProductModalOpen(true);
    };

    // Open modal for editing product
    const handleOpenEditModal = (product: ProductListItem) => {
        setEditingProduct(product);
        setIsProductModalOpen(true);
    };

    // Open stock adjustment modal
    const handleOpenStockModal = (product: ProductListItem) => {
        setAdjustingProduct(product);
        setIsStockModalOpen(true);
    };

    // Handle product create/update
    const handleProductSubmit = async (data: CreateProductRequest) => {
        try {
            if (editingProduct) {
                const updateData: UpdateProductRequest = { ...data };
                await inventoryService.updateProduct(editingProduct.id, updateData);
                toast.success('Producto actualizado correctamente');
            } else {
                await inventoryService.createProduct(data);
                toast.success('Producto creado correctamente');
            }

            setIsProductModalOpen(false);
            loadData();
        } catch (error: any) {
            toast.error(error.message || 'Error al guardar producto');
            throw error;
        }
    };

    // Handle stock adjustment
    const handleStockAdjustment = async (adjustment: StockAdjustmentRequest) => {
        if (!adjustingProduct) return;

        try {
            await inventoryService.adjustStock(adjustingProduct.id, adjustment);
            toast.success('Stock ajustado correctamente');
            setIsStockModalOpen(false);
            loadData();
        } catch (error: any) {
            toast.error(error.message || 'Error al ajustar stock');
            throw error;
        }
    };

    const totalPages = Math.ceil(totalProducts / itemsPerPage);

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                    <Package className="w-8 h-8" />
                    Gestión de Inventario
                </h1>
                <p className="text-gray-600 mt-2">
                    Administra productos, stock y alertas de inventario
                </p>
            </div>

            {/* Low Stock Alerts */}
            {alerts.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                        <div className="flex-1">
                            <h3 className="font-semibold text-red-900">
                                {alerts.length} producto{alerts.length > 1 ? 's' : ''} con stock bajo
                            </h3>
                            <p className="text-sm text-red-700 mt-1">
                                Los siguientes productos necesitan reposición: {alerts.slice(0, 3).map(a => a.nombre).join(', ')}
                                {alerts.length > 3 && ` y ${alerts.length - 3} más`}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Actions Bar */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6 space-y-4">
                <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                    {/* Search */}
                    <div className="relative flex-1 w-full sm:w-auto">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Buscar por nombre, código o categoría..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>

                    {/* Category Filter */}
                    <select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="">Todas las categorías</option>
                        <option value="Material_Curacion">Material Curación</option>
                        <option value="Instrumental">Instrumental</option>
                        <option value="Medicamento">Medicamento</option>
                        <option value="Consumible">Consumible</option>
                        <option value="Equipo_Medico">Equipo Médico</option>
                        <option value="Producto_Venta">Producto Venta</option>
                        <option value="Material_Limpieza">Material Limpieza</option>
                        <option value="Papeleria">Papelería</option>
                    </select>

                    {/* Toggle inactive */}
                    <label className="flex items-center gap-2 cursor-pointer whitespace-nowrap">
                        <input
                            type="checkbox"
                            checked={showInactive}
                            onChange={(e) => setShowInactive(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">Mostrar inactivos</span>
                    </label>

                    {/* Create button */}
                    {user.rol === 'Admin' && (
                        <button
                            onClick={handleOpenCreateModal}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 whitespace-nowrap"
                        >
                            <Plus className="w-5 h-5" />
                            Nuevo Producto
                        </button>
                    )}
                </div>
            </div>

            {/* Products List */}
            {isLoading ? (
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
            ) : (
                <>
                    <InventoryTable
                        products={products}
                        searchQuery={searchQuery}
                        onEdit={handleOpenEditModal}
                        onAdjustStock={handleOpenStockModal}
                        loading={isLoading}
                    />

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="mt-6 flex items-center justify-between">
                            <p className="text-sm text-gray-700">
                                Mostrando {currentPage * itemsPerPage + 1} - {Math.min((currentPage + 1) * itemsPerPage, totalProducts)} de {totalProducts} productos
                            </p>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
                                    disabled={currentPage === 0}
                                    className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Anterior
                                </button>
                                <button
                                    onClick={() => setCurrentPage(p => Math.min(totalPages - 1, p + 1))}
                                    disabled={currentPage >= totalPages - 1}
                                    className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Siguiente
                                </button>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Modals */}
            <ProductFormModal
                isOpen={isProductModalOpen}
                product={editingProduct}
                onClose={() => setIsProductModalOpen(false)}
                onSubmit={handleProductSubmit}
            />

            <StockAdjustmentModal
                isOpen={isStockModalOpen}
                product={adjustingProduct}
                onClose={() => setIsStockModalOpen(false)}
                onSubmit={handleStockAdjustment}
            />
        </div>
    );
};

export default InventoryPage;
