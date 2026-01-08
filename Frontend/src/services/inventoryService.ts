/**
 * Inventory Service
 * 
 * Service for managing inventory products and stock.
 * Consumes the real API endpoints from /api/inventory
 */

import api from './api';

// ============================================================================
// TYPES
// ============================================================================

export interface Product {
    id: number;
    codigo_producto: string;
    codigo_barras?: string | null;
    nombre: string;
    descripcion?: string | null;
    categoria: string;
    subcategoria?: string | null;
    stock_actual: number;
    stock_minimo: number;
    stock_maximo: number;
    unidad_medida: string;
    costo_unitario?: number | null;
    precio_venta?: number | null;
    margen_ganancia?: number | null;
    id_proveedor?: number | null;
    tiempo_reposicion_dias: number;
    requiere_receta: boolean;
    controlado: boolean;
    tiene_caducidad: boolean;
    fecha_caducidad?: string | null;
    lote?: string | null;
    ubicacion_almacen?: string | null;
    activo: boolean;
    fecha_registro?: string | null;
    registrado_por?: number | null;
}

export interface ProductListItem {
    id: number;
    codigo_producto: string;
    nombre: string;
    categoria: string;
    stock_actual: number;
    stock_minimo: number;
    stock_maximo: number;
    unidad_medida: string;
    cantidad_por_unidad?: number;
    costo_unitario?: number | null;
    precio_venta?: number | null;
    activo: boolean;
}

export interface ProductListResponse {
    total: number;
    productos: ProductListItem[];
}

export interface StockAlert {
    id: number;
    codigo_producto: string;
    nombre: string;
    categoria: string;
    stock_actual: number;
    stock_minimo: number;
    cantidad_requerida: number;
    proveedor?: string | null;
    telefono_proveedor?: string | null;
    tiempo_reposicion_dias: number;
    costo_unitario?: number | null;
    costo_reposicion?: number | null;
}

export interface StockMovement {
    id: number;
    id_producto: number;
    tipo_movimiento: string;
    cantidad: number;
    stock_anterior: number;
    stock_nuevo: number;
    motivo: string;
    registrado_por: number;
    fecha_movimiento: string;
}

export interface CreateProductRequest {
    codigo_producto: string;
    codigo_barras?: string;
    nombre: string;
    descripcion?: string;
    categoria: string;
    subcategoria?: string;
    stock_actual?: number;
    stock_minimo?: number;
    stock_maximo?: number;
    unidad_medida: string;
    cantidad_por_unidad?: number;
    costo_unitario?: number;
    precio_venta?: number;
    margen_ganancia?: number;
    id_proveedor?: number;
    tiempo_reposicion_dias?: number;
    requiere_receta?: boolean;
    controlado?: boolean;
    tiene_caducidad?: boolean;
    fecha_caducidad?: string;
    lote?: string;
    ubicacion_almacen?: string;
}

export interface UpdateProductRequest {
    codigo_barras?: string;
    nombre?: string;
    descripcion?: string;
    categoria?: string;
    subcategoria?: string;
    stock_minimo?: number;
    stock_maximo?: number;
    unidad_medida?: string;
    costo_unitario?: number;
    precio_venta?: number;
    margen_ganancia?: number;
    id_proveedor?: number;
    tiempo_reposicion_dias?: number;
    requiere_receta?: boolean;
    controlado?: boolean;
    tiene_caducidad?: boolean;
    fecha_caducidad?: string;
    lote?: string;
    ubicacion_almacen?: string;
    activo?: boolean;
}

export interface StockAdjustmentRequest {
    tipo_movimiento: 'Entrada' | 'Salida' | 'Ajuste_Positivo' | 'Ajuste_Negativo' | 'Merma' | 'Devolucion';
    cantidad: number;
    motivo: string;
    costo_unitario?: number;
    numero_factura_proveedor?: string;
    lote?: string;
    fecha_caducidad?: string;
}

// ============================================================================
// SERVICE
// ============================================================================

class InventoryService {
    /**
     * Lista todos los productos con paginación y filtros
     */
    async getProducts(params?: {
        limit?: number;
        offset?: number;
        categoria?: string;
        activo?: boolean;
    }): Promise<ProductListResponse> {
        try {
            const response = await api.get('/api/inventory', { params });
            return response.data;
        } catch (error: any) {
            console.error('Error fetching products:', error);
            throw new Error(
                error.response?.data?.detail || 'Error al cargar los productos'
            );
        }
    }

    /**
     * Obtiene un producto por ID
     */
    async getProductById(productId: number): Promise<Product> {
        try {
            const response = await api.get(`/api/inventory/${productId}`);
            return response.data;
        } catch (error: any) {
            console.error('Error fetching product:', error);
            throw new Error(
                error.response?.data?.detail || 'Error al cargar el producto'
            );
        }
    }

    /**
     * Crea un nuevo producto
     */
    async createProduct(data: CreateProductRequest): Promise<ProductListItem> {
        try {
            const response = await api.post('/api/inventory', data);
            return response.data;
        } catch (error: any) {
            console.error('Error creating product:', error);
            throw new Error(
                error.response?.data?.detail || 'Error al crear el producto'
            );
        }
    }

    /**
     * Actualiza un producto existente
     */
    async updateProduct(
        productId: number,
        data: UpdateProductRequest
    ): Promise<ProductListItem> {
        try {
            const response = await api.put(`/api/inventory/${productId}`, data);
            return response.data;
        } catch (error: any) {
            console.error('Error updating product:', error);
            throw new Error(
                error.response?.data?.detail || 'Error al actualizar el producto'
            );
        }
    }

    /**
     * Ajusta el stock de un producto
     */
    async adjustStock(
        productId: number,
        adjustment: StockAdjustmentRequest
    ): Promise<StockMovement> {
        try {
            const response = await api.post(
                `/api/inventory/${productId}/adjust`,
                adjustment
            );
            return response.data;
        } catch (error: any) {
            console.error('Error adjusting stock:', error);
            throw new Error(
                error.response?.data?.detail || 'Error al ajustar el stock'
            );
        }
    }

    /**
     * Obtiene alertas de stock bajo
     */
    async getLowStockAlerts(): Promise<StockAlert[]> {
        try {
            const response = await api.get('/api/inventory/alerts/low-stock');
            return response.data;
        } catch (error: any) {
            console.error('Error fetching low stock alerts:', error);
            throw new Error(
                error.response?.data?.detail || 'Error al cargar las alertas'
            );
        }
    }
}

export const inventoryService = new InventoryService();

// Export convenience functions
export const getProducts = (params?: {
    limit?: number;
    offset?: number;
    categoria?: string;
    activo?: boolean;
}) => inventoryService.getProducts(params);

export const getProductById = (productId: number) => inventoryService.getProductById(productId);
export const createProduct = (data: CreateProductRequest) => inventoryService.createProduct(data);
export const updateProduct = (productId: number, data: UpdateProductRequest) => inventoryService.updateProduct(productId, data);
export const deleteProduct = (productId: number) => inventoryService.deleteProduct(productId);
export const adjustStock = (productId: number, data: StockAdjustmentRequest) => inventoryService.adjustStock(productId, data);
export const getLowStockAlerts = () => inventoryService.getLowStockAlerts();
