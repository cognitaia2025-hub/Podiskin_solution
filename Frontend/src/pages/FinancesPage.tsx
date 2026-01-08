import React, { useState, useEffect } from 'react';
import { TrendingUp, Plus, DollarSign, Package, Calendar, FileText, BarChart3, PieChart } from 'lucide-react';
import GastosChartsComponent from '../components/finances/GastosChartsComponent';
import MetricasFinancierasComponent from '../components/finances/MetricasFinancierasComponent';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface Gasto {
    gasto_id: number;
    concepto: string;
    monto: number;
    fecha_gasto: string;
    metodo_pago: string;
    categoria?: string;
    notas?: string;
}

interface ProductoInventario {
    producto_id: number;
    nombre: string;
    cantidad_comprada: number;
    precio_unitario: number;
}

interface GastoConInventarioRequest {
    concepto: string;
    monto: number;
    fecha_gasto: string;
    metodo_pago: string;
    categoria: string;
    notas?: string;
    productos: ProductoInventario[];
}

interface Product {
    producto_id: number;
    nombre: string;
    stock_actual: number;
}

const CATEGORIAS_GASTO = [
    { value: 'SERVICIOS_BASICOS', label: 'Servicios Básicos (Luz, Agua, Internet)' },
    { value: 'MATERIAL_MEDICO', label: 'Material Médico y Consumibles' },
    { value: 'SALARIOS_PERSONAL', label: 'Salarios y Nómina' },
    { value: 'RENTA_LOCAL', label: 'Renta del Local' },
    { value: 'MARKETING_PUBLICIDAD', label: 'Marketing y Publicidad' },
    { value: 'MATERIAL_OFICINA', label: 'Material de Oficina' },
    { value: 'CAPACITACION_CERTIFICACIONES', label: 'Capacitación y Certificaciones' },
    { value: 'MANTENIMIENTO_EQUIPOS', label: 'Mantenimiento de Equipos' },
    { value: 'SERVICIOS_PROFESIONALES', label: 'Servicios Profesionales (Contador, Abogado)' }
];

const METODOS_PAGO = [
    { value: 'efectivo', label: 'Efectivo' },
    { value: 'tarjeta', label: 'Tarjeta' },
    { value: 'transferencia', label: 'Transferencia' },
    { value: 'cheque', label: 'Cheque' }
];

const FinancesPage: React.FC = () => {
    const [gastos, setGastos] = useState<Gasto[]>([]);
    const [productos, setProductos] = useState<Product[]>([]);
    const [loading, setLoading] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [showCharts, setShowCharts] = useState(false);
    const [showMetricas, setShowMetricas] = useState(false);

    const [formData, setFormData] = useState({
        concepto: '',
        monto: '',
        fecha_gasto: new Date().toISOString().split('T')[0],
        metodo_pago: 'efectivo',
        categoria: 'MATERIAL_MEDICO',
        notas: '',
        vincular_inventario: false
    });

    const [productosVinculados, setProductosVinculados] = useState<ProductoInventario[]>([]);
    const [productoActual, setProductoActual] = useState({
        producto_id: 0,
        cantidad_comprada: 1,
        precio_unitario: 0
    });

    useEffect(() => {
        loadGastos();
        loadProductos();
    }, []);

    const loadGastos = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/gastos`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                setGastos(data);
            }
        } catch (error) {
            console.error('Error cargando gastos:', error);
        }
    };

    const loadProductos = async () => {
        try {
            // Se usa el router en inglés /api/inventory
            const response = await fetch(`${API_BASE_URL}/api/inventory`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (response.ok) {
                const data = await response.json();
                // El endpoint de inventario devuelve { total: number, productos: Product[] }
                // pero el estado espera Product[], así que extraemos .productos si existe
                if (data.productos) {
                    setProductos(data.productos);
                } else if (Array.isArray(data)) {
                    setProductos(data);
                } else {
                    setProductos([]);
                }
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            setProductos([]);
        }
    };

    const handleAgregarProducto = () => {
        if (productoActual.producto_id === 0 || productoActual.cantidad_comprada <= 0 || productoActual.precio_unitario <= 0) {
            alert('Complete todos los campos del producto');
            return;
        }

        const producto = productos.find(p => p.producto_id === productoActual.producto_id);
        if (!producto) return;

        setProductosVinculados([...productosVinculados, {
            producto_id: productoActual.producto_id,
            nombre: producto.nombre,
            cantidad_comprada: productoActual.cantidad_comprada,
            precio_unitario: productoActual.precio_unitario
        }]);

        setProductoActual({
            producto_id: 0,
            cantidad_comprada: 1,
            precio_unitario: 0
        });
    };

    const handleEliminarProducto = (index: number) => {
        setProductosVinculados(productosVinculados.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            if (formData.vincular_inventario && productosVinculados.length > 0) {
                // Usar endpoint con inventario
                const request: GastoConInventarioRequest = {
                    concepto: formData.concepto,
                    monto: parseFloat(formData.monto),
                    fecha_gasto: formData.fecha_gasto,
                    metodo_pago: formData.metodo_pago,
                    categoria: formData.categoria,
                    notas: formData.notas || undefined,
                    productos: productosVinculados.map(p => ({
                        producto_id: p.producto_id,
                        nombre: p.nombre,
                        cantidad_comprada: p.cantidad_comprada,
                        precio_unitario: p.precio_unitario
                    }))
                };

                const response = await fetch(`${API_BASE_URL}/api/gastos/con-inventario`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify(request)
                });

                if (response.ok) {
                    alert('Gasto registrado y productos actualizados');
                    resetForm();
                    loadGastos();
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.detail}`);
                }
            } else {
                // Endpoint simple sin inventario
                const response = await fetch(`${API_BASE_URL}/api/gastos`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify({
                        concepto: formData.concepto,
                        monto: parseFloat(formData.monto),
                        fecha_gasto: formData.fecha_gasto,
                        metodo_pago: formData.metodo_pago,
                        categoria: formData.categoria,
                        notas: formData.notas || undefined
                    })
                });

                if (response.ok) {
                    alert('Gasto registrado');
                    resetForm();
                    loadGastos();
                } else {
                    const error = await response.json();
                    alert(`Error: ${error.detail}`);
                }
            }
        } catch (error) {
            console.error('Error registrando gasto:', error);
            alert('Error al registrar gasto');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setFormData({
            concepto: '',
            monto: '',
            fecha_gasto: new Date().toISOString().split('T')[0],
            metodo_pago: 'efectivo',
            categoria: 'MATERIAL_MEDICO',
            notas: '',
            vincular_inventario: false
        });
        setProductosVinculados([]);
        setShowForm(false);
    };

    const totalProductos = productosVinculados.reduce((sum, p) =>
        sum + (p.cantidad_comprada * p.precio_unitario), 0
    );

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <TrendingUp className="w-8 h-8 text-blue-600" />
                    <h1 className="text-3xl font-bold text-gray-800">Finanzas y Gastos</h1>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => {
                            setShowMetricas(!showMetricas);
                            if (!showMetricas) {
                                setShowCharts(false);
                            }
                        }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${showMetricas
                            ? 'bg-green-600 text-white hover:bg-green-700'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        <PieChart className="w-5 h-5" />
                        {showMetricas ? 'Ocultar Dashboard' : 'Ver Dashboard'}
                    </button>
                    <button
                        onClick={() => {
                            setShowCharts(!showCharts);
                            if (!showCharts) {
                                setShowMetricas(false);
                            }
                        }}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${showCharts
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        <BarChart3 className="w-5 h-5" />
                        {showCharts ? 'Ocultar Gráficas' : 'Ver Gráficas'}
                    </button>
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        <Plus className="w-5 h-5" />
                        Nuevo Gasto
                    </button>
                </div>
            </div>

            {/* Dashboard de Métricas Financieras */}
            {showMetricas && (
                <div className="mb-6">
                    <MetricasFinancierasComponent />
                </div>
            )}

            {/* Componente de Gráficas */}
            {showCharts && (
                <div className="mb-6">
                    <GastosChartsComponent />
                </div>
            )}

            {showForm && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Registrar Gasto</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Concepto */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    <FileText className="w-4 h-4 inline mr-1" />
                                    Concepto
                                </label>
                                <input
                                    type="text"
                                    value={formData.concepto}
                                    onChange={(e) => setFormData({ ...formData, concepto: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                    placeholder="Descripción del gasto"
                                />
                            </div>

                            {/* Monto */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    <DollarSign className="w-4 h-4 inline mr-1" />
                                    Monto
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.monto}
                                    onChange={(e) => setFormData({ ...formData, monto: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                    placeholder="0.00"
                                />
                            </div>

                            {/* Fecha */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    <Calendar className="w-4 h-4 inline mr-1" />
                                    Fecha
                                </label>
                                <input
                                    type="date"
                                    value={formData.fecha_gasto}
                                    onChange={(e) => setFormData({ ...formData, fecha_gasto: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            {/* Método de Pago */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Método de Pago
                                </label>
                                <select
                                    value={formData.metodo_pago}
                                    onChange={(e) => setFormData({ ...formData, metodo_pago: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    {METODOS_PAGO.map(m => (
                                        <option key={m.value} value={m.value}>{m.label}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Categoría */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Categoría del Gasto
                                </label>
                                <select
                                    value={formData.categoria}
                                    onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    {CATEGORIAS_GASTO.map(c => (
                                        <option key={c.value} value={c.value}>{c.label}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Notas */}
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Notas (opcional)
                                </label>
                                <textarea
                                    value={formData.notas}
                                    onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    rows={2}
                                    placeholder="Información adicional del gasto"
                                />
                            </div>
                        </div>

                        {/* Vincular con Inventario */}
                        <div className="border-t pt-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.vincular_inventario}
                                    onChange={(e) => setFormData({ ...formData, vincular_inventario: e.target.checked })}
                                    className="w-4 h-4"
                                />
                                <Package className="w-4 h-4 text-gray-600" />
                                <span className="text-sm font-medium text-gray-700">
                                    Vincular con productos de inventario
                                </span>
                            </label>

                            {formData.vincular_inventario && (
                                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                                    <h3 className="font-medium mb-3">Agregar Productos</h3>

                                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                                        <select
                                            value={productoActual.producto_id}
                                            onChange={(e) => setProductoActual({ ...productoActual, producto_id: parseInt(e.target.value) })}
                                            className="px-3 py-2 border rounded-lg"
                                        >
                                            <option value={0}>Seleccionar producto</option>
                                            {productos.map(p => (
                                                <option key={p.producto_id} value={p.producto_id}>
                                                    {p.nombre} (Stock: {p.stock_actual})
                                                </option>
                                            ))}
                                        </select>

                                        <input
                                            type="number"
                                            min="1"
                                            value={productoActual.cantidad_comprada}
                                            onChange={(e) => setProductoActual({ ...productoActual, cantidad_comprada: parseInt(e.target.value) })}
                                            placeholder="Cantidad"
                                            className="px-3 py-2 border rounded-lg"
                                        />

                                        <input
                                            type="number"
                                            step="0.01"
                                            min="0"
                                            value={productoActual.precio_unitario}
                                            onChange={(e) => setProductoActual({ ...productoActual, precio_unitario: parseFloat(e.target.value) })}
                                            placeholder="Precio unitario"
                                            className="px-3 py-2 border rounded-lg"
                                        />

                                        <button
                                            type="button"
                                            onClick={handleAgregarProducto}
                                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                                        >
                                            Agregar
                                        </button>
                                    </div>

                                    {productosVinculados.length > 0 && (
                                        <div className="mt-4">
                                            <table className="w-full text-sm">
                                                <thead className="bg-gray-100">
                                                    <tr>
                                                        <th className="px-3 py-2 text-left">Producto</th>
                                                        <th className="px-3 py-2 text-right">Cantidad</th>
                                                        <th className="px-3 py-2 text-right">Precio Unit.</th>
                                                        <th className="px-3 py-2 text-right">Subtotal</th>
                                                        <th className="px-3 py-2"></th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {productosVinculados.map((p, idx) => (
                                                        <tr key={idx} className="border-b">
                                                            <td className="px-3 py-2">{p.nombre}</td>
                                                            <td className="px-3 py-2 text-right">{p.cantidad_comprada}</td>
                                                            <td className="px-3 py-2 text-right">${p.precio_unitario.toFixed(2)}</td>
                                                            <td className="px-3 py-2 text-right">
                                                                ${(p.cantidad_comprada * p.precio_unitario).toFixed(2)}
                                                            </td>
                                                            <td className="px-3 py-2 text-right">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => handleEliminarProducto(idx)}
                                                                    className="text-red-600 hover:text-red-800"
                                                                >
                                                                    Eliminar
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                                <tfoot>
                                                    <tr className="font-bold">
                                                        <td colSpan={3} className="px-3 py-2 text-right">Total Productos:</td>
                                                        <td className="px-3 py-2 text-right">${totalProductos.toFixed(2)}</td>
                                                        <td></td>
                                                    </tr>
                                                </tfoot>
                                            </table>
                                            {parseFloat(formData.monto) > 0 && totalProductos > parseFloat(formData.monto) && (
                                                <p className="text-red-600 text-sm mt-2">
                                                    ⚠️ El total de productos (${totalProductos.toFixed(2)}) excede el monto del gasto (${parseFloat(formData.monto).toFixed(2)})
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Botones */}
                        <div className="flex gap-3 justify-end">
                            <button
                                type="button"
                                onClick={resetForm}
                                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? 'Guardando...' : 'Registrar Gasto'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Lista de Gastos */}
            <div className="bg-white rounded-lg shadow-md">
                <div className="p-4 border-b">
                    <h2 className="text-xl font-semibold">Gastos Registrados</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Fecha</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Concepto</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Categoría</th>
                                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Monto</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Método</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {gastos.map(g => (
                                <tr key={g.gasto_id} className="hover:bg-gray-50">
                                    <td className="px-4 py-3 text-sm">
                                        {new Date(g.fecha_gasto).toLocaleDateString()}
                                    </td>
                                    <td className="px-4 py-3 text-sm">{g.concepto}</td>
                                    <td className="px-4 py-3 text-sm">
                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                            {g.categoria || 'Sin categoría'}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-sm text-right font-medium">
                                        ${g.monto.toFixed(2)}
                                    </td>
                                    <td className="px-4 py-3 text-sm capitalize">{g.metodo_pago}</td>
                                </tr>
                            ))}
                            {gastos.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                                        No hay gastos registrados
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default FinancesPage;
