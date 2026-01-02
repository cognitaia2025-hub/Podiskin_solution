/**
 * Ajustes Page
 * 
 * Settings page for administrators with tabs for:
 * - Roles y Permisos
 * - Personal/Usuarios
 * - Proveedores
 * - Productos/Inventario
 * - Horarios
 */

import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { Navigate } from 'react-router-dom';
import {
    mockRoles,
    mockPersonal,
    mockProveedores,
    mockProductos,
    mockHorarios,
    getCategoriaColor,
    getProveedorNombre,
    type Role,
    type Personal,
    type Proveedor,
    type Producto,
    type Horario,
} from '../services/adminMockData';

type TabType = 'roles' | 'personal' | 'proveedores' | 'productos' | 'horarios';

const AjustesPage: React.FC = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState<TabType>('roles');

    // Redirect non-admin users
    if (user?.rol !== 'Admin') {
        return <Navigate to="/calendar" replace />;
    }

    const tabs: { id: TabType; label: string; icon: JSX.Element }[] = [
        {
            id: 'roles',
            label: 'Roles',
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
            ),
        },
        {
            id: 'personal',
            label: 'Personal',
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            ),
        },
        {
            id: 'proveedores',
            label: 'Proveedores',
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
            ),
        },
        {
            id: 'productos',
            label: 'Productos',
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
            ),
        },
        {
            id: 'horarios',
            label: 'Horarios',
            icon: (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            ),
        },
    ];

    const renderRolesTab = () => (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">Roles y Permisos</h3>
                <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Nuevo Rol</span>
                </button>
            </div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Permisos</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {mockRoles.map((role) => (
                            <tr key={role.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className="font-medium text-gray-900">{role.nombre_rol}</span>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">{role.descripcion}</td>
                                <td className="px-6 py-4">
                                    <div className="flex flex-wrap gap-1">
                                        {role.permisos?.map((permiso, idx) => (
                                            <span key={idx} className="inline-flex px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                                                {permiso}
                                            </span>
                                        ))}
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-right space-x-2">
                                    <button className="text-primary-600 hover:text-primary-800 text-sm">Editar</button>
                                    <button className="text-red-600 hover:text-red-800 text-sm">Eliminar</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    const renderPersonalTab = () => (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">Personal</h3>
                <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Nuevo Usuario</span>
                </button>
            </div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Teléfono</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {mockPersonal.map((persona) => (
                            <tr key={persona.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className="font-medium text-gray-900">{persona.nombre_completo}</span>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">{persona.email}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">{persona.telefono}</td>
                                <td className="px-6 py-4">
                                    <span className="inline-flex px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                                        {persona.rol}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${persona.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {persona.activo ? 'Activo' : 'Inactivo'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right space-x-2">
                                    <button className="text-primary-600 hover:text-primary-800 text-sm">Editar</button>
                                    <button className="text-red-600 hover:text-red-800 text-sm">
                                        {persona.activo ? 'Desactivar' : 'Activar'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    const renderProveedoresTab = () => (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">Proveedores</h3>
                <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Nuevo Proveedor</span>
                </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mockProveedores.map((proveedor) => (
                    <div key={proveedor.id} className={`bg-white rounded-lg shadow p-4 border-l-4 ${proveedor.activo ? 'border-green-500' : 'border-gray-300'}`}>
                        <div className="flex justify-between items-start mb-3">
                            <h4 className="font-semibold text-gray-900">{proveedor.nombre_comercial}</h4>
                            <span className={`inline-flex px-2 py-0.5 text-xs rounded-full ${proveedor.activo ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                                {proveedor.activo ? 'Activo' : 'Inactivo'}
                            </span>
                        </div>
                        {proveedor.razon_social && (
                            <p className="text-xs text-gray-500 mb-2">{proveedor.razon_social}</p>
                        )}
                        <div className="space-y-1 text-sm text-gray-600">
                            <p className="flex items-center space-x-2">
                                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                </svg>
                                <span>{proveedor.telefono}</span>
                            </p>
                            {proveedor.email && (
                                <p className="flex items-center space-x-2">
                                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                    </svg>
                                    <span>{proveedor.email}</span>
                                </p>
                            )}
                        </div>
                        <div className="mt-4 flex space-x-2">
                            <button className="flex-1 text-center py-1 text-sm text-primary-600 hover:bg-primary-50 rounded">Editar</button>
                            <button className="flex-1 text-center py-1 text-sm text-red-600 hover:bg-red-50 rounded">
                                {proveedor.activo ? 'Desactivar' : 'Activar'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const renderProductosTab = () => (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">Productos e Inventario</h3>
                <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Nuevo Producto</span>
                </button>
            </div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P. Compra</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P. Venta</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Proveedor</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {mockProductos.map((producto) => (
                            <tr key={producto.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className="font-medium text-gray-900">{producto.nombre}</span>
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${getCategoriaColor(producto.categoria)}`}>
                                        {producto.categoria.replace('_', ' ')}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center">
                                        <span className={`font-medium ${producto.stock_actual <= producto.stock_minimo ? 'text-red-600' : 'text-gray-900'}`}>
                                            {producto.stock_actual}
                                        </span>
                                        {producto.stock_actual <= producto.stock_minimo && (
                                            <svg className="w-4 h-4 ml-1 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                            </svg>
                                        )}
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">${producto.precio_compra.toFixed(2)}</td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-900">${producto.precio_venta.toFixed(2)}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">
                                    {producto.proveedor_id ? getProveedorNombre(producto.proveedor_id) : '-'}
                                </td>
                                <td className="px-6 py-4 text-right space-x-2">
                                    <button className="text-primary-600 hover:text-primary-800 text-sm">Editar</button>
                                    <button className="text-red-600 hover:text-red-800 text-sm">Eliminar</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    const renderHorariosTab = () => (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800">Horarios de Atención</h3>
                <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Nuevo Horario</span>
                </button>
            </div>

            {/* Group by podologist */}
            {Array.from(new Set(mockHorarios.map(h => h.podologo_id))).map(podologoId => {
                const horarios = mockHorarios.filter(h => h.podologo_id === podologoId);
                const nombrePodologo = horarios[0]?.podologo_nombre;

                return (
                    <div key={podologoId} className="bg-white rounded-lg shadow overflow-hidden">
                        <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
                            <h4 className="font-medium text-gray-900">{nombrePodologo}</h4>
                        </div>
                        <div className="p-4">
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                                {horarios.map((horario) => (
                                    <div
                                        key={horario.id}
                                        className={`p-3 rounded-lg border text-center ${horario.activo ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'
                                            }`}
                                    >
                                        <p className="font-medium text-gray-900 text-sm">{horario.dia_semana}</p>
                                        <p className="text-xs text-gray-600 mt-1">
                                            {horario.hora_inicio} - {horario.hora_fin}
                                        </p>
                                        <button className="mt-2 text-xs text-primary-600 hover:text-primary-800">
                                            Editar
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );

    const renderTabContent = () => {
        switch (activeTab) {
            case 'roles':
                return renderRolesTab();
            case 'personal':
                return renderPersonalTab();
            case 'proveedores':
                return renderProveedoresTab();
            case 'productos':
                return renderProductosTab();
            case 'horarios':
                return renderHorariosTab();
            default:
                return renderRolesTab();
        }
    };

    return (
        <div className="min-h-full p-6">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Ajustes</h1>
                <p className="text-gray-600 mt-1">Configuración del sistema y administración</p>
            </div>

            {/* Tabs */}
            <div className="mb-6 border-b border-gray-200">
                <nav className="flex space-x-4" aria-label="Tabs">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.id
                                    ? 'border-primary-600 text-primary-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            {tab.icon}
                            <span>{tab.label}</span>
                        </button>
                    ))}
                </nav>
            </div>

            {/* Tab Content */}
            <div className="animate-fadeIn">
                {renderTabContent()}
            </div>
        </div>
    );
};

export default AjustesPage;
