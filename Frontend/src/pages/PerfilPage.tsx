/**
 * Perfil Page
 * 
 * User profile page with:
 * - Profile information display and edit
 * - Change password functionality
 * - Profile picture (placeholder for now)
 */

import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';

interface ProfileFormData {
    nombre_completo: string;
    email: string;
    telefono: string;
}

interface PasswordFormData {
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
}

const PerfilPage: React.FC = () => {
    const { user, updateUser } = useAuth();
    const [isEditing, setIsEditing] = useState(false);
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    const [formData, setFormData] = useState<ProfileFormData>({
        nombre_completo: user?.nombre_completo || '',
        email: user?.email || '',
        telefono: (user as any)?.telefono || '',
    });

    const [passwordData, setPasswordData] = useState<PasswordFormData>({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({ ...prev, [name]: value }));
    };

    const handleSaveProfile = async () => {
        setIsSaving(true);
        setSaveMessage(null);

        try {
            // Simulated API call - replace with real endpoint later
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Update user context
            updateUser({
                nombre_completo: formData.nombre_completo,
                email: formData.email,
            });

            setSaveMessage({ type: 'success', text: 'Perfil actualizado correctamente' });
            setIsEditing(false);
        } catch (error) {
            setSaveMessage({ type: 'error', text: 'Error al actualizar el perfil' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleChangePassword = async () => {
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            setSaveMessage({ type: 'error', text: 'Las contraseñas no coinciden' });
            return;
        }

        if (passwordData.newPassword.length < 8) {
            setSaveMessage({ type: 'error', text: 'La contraseña debe tener al menos 8 caracteres' });
            return;
        }

        setIsSaving(true);
        setSaveMessage(null);

        try {
            // Simulated API call - replace with real endpoint later
            await new Promise(resolve => setTimeout(resolve, 1000));

            setSaveMessage({ type: 'success', text: 'Contraseña actualizada correctamente' });
            setShowPasswordModal(false);
            setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
        } catch (error) {
            setSaveMessage({ type: 'error', text: 'Error al cambiar la contraseña' });
        } finally {
            setIsSaving(false);
        }
    };

    const getUserInitials = () => {
        if (!user) return 'U';
        if (user.nombre_completo) {
            const parts = user.nombre_completo.split(' ');
            return parts.length > 1
                ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
                : parts[0][0].toUpperCase();
        }
        return user.username[0].toUpperCase();
    };

    return (
        <div className="min-h-full p-6">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">Mi Perfil</h1>
                    <p className="text-gray-600 mt-1">Gestiona tu información personal</p>
                </div>

                {/* Message */}
                {saveMessage && (
                    <div className={`mb-4 p-4 rounded-lg ${saveMessage.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
                        }`}>
                        {saveMessage.text}
                    </div>
                )}

                {/* Profile Card */}
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    {/* Profile Header */}
                    <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-8">
                        <div className="flex items-center space-x-4">
                            <div className="w-20 h-20 rounded-full bg-white flex items-center justify-center text-primary-600 text-2xl font-bold shadow-lg">
                                {getUserInitials()}
                            </div>
                            <div className="text-white">
                                <h2 className="text-xl font-semibold">{user?.nombre_completo || user?.username}</h2>
                                <p className="text-primary-200">{user?.rol}</p>
                                <p className="text-primary-200 text-sm mt-1">{user?.email}</p>
                            </div>
                        </div>
                    </div>

                    {/* Profile Form */}
                    <div className="p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-lg font-semibold text-gray-800">Información Personal</h3>
                            {!isEditing ? (
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                                >
                                    Editar
                                </button>
                            ) : (
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => {
                                            setIsEditing(false);
                                            setFormData({
                                                nombre_completo: user?.nombre_completo || '',
                                                email: user?.email || '',
                                                telefono: (user as any)?.telefono || '',
                                            });
                                        }}
                                        className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        onClick={handleSaveProfile}
                                        disabled={isSaving}
                                        className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
                                    >
                                        {isSaving ? 'Guardando...' : 'Guardar'}
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Nombre Completo
                                </label>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        name="nombre_completo"
                                        value={formData.nombre_completo}
                                        onChange={handleInputChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    />
                                ) : (
                                    <p className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900">
                                        {user?.nombre_completo || '-'}
                                    </p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Email
                                </label>
                                {isEditing ? (
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    />
                                ) : (
                                    <p className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900">
                                        {user?.email || '-'}
                                    </p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Teléfono
                                </label>
                                {isEditing ? (
                                    <input
                                        type="tel"
                                        name="telefono"
                                        value={formData.telefono}
                                        onChange={handleInputChange}
                                        placeholder="686-555-0000"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    />
                                ) : (
                                    <p className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900">
                                        {formData.telefono || 'No especificado'}
                                    </p>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Rol
                                </label>
                                <p className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900">
                                    {user?.rol || '-'}
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Usuario
                                </label>
                                <p className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900">
                                    {user?.username || '-'}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Security Section */}
                    <div className="border-t border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Seguridad</h3>
                        <button
                            onClick={() => setShowPasswordModal(true)}
                            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                            </svg>
                            <span>Cambiar Contraseña</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Password Modal */}
            {showPasswordModal && (
                <>
                    <div
                        className="fixed inset-0 bg-black bg-opacity-50 z-40"
                        onClick={() => setShowPasswordModal(false)}
                    />
                    <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Cambiar Contraseña</h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Contraseña Actual
                                    </label>
                                    <input
                                        type="password"
                                        name="currentPassword"
                                        value={passwordData.currentPassword}
                                        onChange={handlePasswordChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Nueva Contraseña
                                    </label>
                                    <input
                                        type="password"
                                        name="newPassword"
                                        value={passwordData.newPassword}
                                        onChange={handlePasswordChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Mínimo 8 caracteres</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Confirmar Nueva Contraseña
                                    </label>
                                    <input
                                        type="password"
                                        name="confirmPassword"
                                        value={passwordData.confirmPassword}
                                        onChange={handlePasswordChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    onClick={() => {
                                        setShowPasswordModal(false);
                                        setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
                                    }}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button
                                    onClick={handleChangePassword}
                                    disabled={isSaving}
                                    className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {isSaving ? 'Guardando...' : 'Cambiar Contraseña'}
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default PerfilPage;
