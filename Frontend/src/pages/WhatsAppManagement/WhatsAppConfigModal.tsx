/**
 * WhatsApp Configuration Modal
 * Modal para configurar admin, contactos especiales y grupos
 */

import React, { useState } from 'react';
import { X, Plus, Trash2, Save } from 'lucide-react';
import api from '../../services/api';

interface ConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (config: WhatsAppConfig) => Promise<void>;
}

interface WhatsAppConfig {
    telefono_admin: string;
    telefonos_respaldo: string[];
    grupos_activos: boolean;
}

interface ContactoEspecial {
    telefono: string;
    nombre: string;
    etiqueta: string;
    descripcion: string;
    comportamiento: string;
    contexto_ia: string;
    notificar_admin: boolean;
}

export const WhatsAppConfigModal: React.FC<ConfigModalProps> = ({ isOpen, onClose, onSave }) => {
    const [config, setConfig] = useState<WhatsAppConfig>({
        telefono_admin: '',
        telefonos_respaldo: [],
        grupos_activos: true
    });

    const [contactos, setContactos] = useState<ContactoEspecial[]>([]);
    const [newRespaldo, setNewRespaldo] = useState('');
    const [saving, setSaving] = useState(false);

    const handleAddRespaldo = () => {
        if (newRespaldo.trim()) {
            setConfig({
                ...config,
                telefonos_respaldo: [...config.telefonos_respaldo, newRespaldo.trim()]
            });
            setNewRespaldo('');
        }
    };

    const handleRemoveRespaldo = (index: number) => {
        setConfig({
            ...config,
            telefonos_respaldo: config.telefonos_respaldo.filter((_, i) => i !== index)
        });
    };

    const handleAddContacto = () => {
        setContactos([...contactos, {
            telefono: '',
            nombre: '',
            etiqueta: 'otro',
            descripcion: '',
            comportamiento: 'normal',
            contexto_ia: '',
            notificar_admin: false
        }]);
    };

    const handleRemoveContacto = (index: number) => {
        setContactos(contactos.filter((_, i) => i !== index));
    };

    const handleUpdateContacto = (index: number, field: keyof ContactoEspecial, value: any) => {
        const updated = [...contactos];
        updated[index] = { ...updated[index], [field]: value };
        setContactos(updated);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Guardar configuración (usa api con token)
            await api.post('/api/whatsapp-bridge/config', config);

            // Guardar contactos
            if (contactos.length > 0) {
                await api.post('/api/whatsapp-bridge/contacts', contactos);
            }

            await onSave(config);
            onClose();
        } catch (error) {
            console.error('Error saving config:', error);
            alert('Error al guardar la configuración');
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-900">Configuración de WhatsApp</h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Administración */}
                    <section>
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Administración</h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Teléfono Admin Principal
                                </label>
                                <input
                                    type="tel"
                                    value={config.telefono_admin}
                                    onChange={(e) => setConfig({ ...config, telefono_admin: e.target.value })}
                                    placeholder="5215512345678"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Teléfonos de Respaldo
                                </label>
                                <div className="flex gap-2 mb-2">
                                    <input
                                        type="tel"
                                        value={newRespaldo}
                                        onChange={(e) => setNewRespaldo(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleAddRespaldo()}
                                        placeholder="5215512345679"
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                    />
                                    <button
                                        onClick={handleAddRespaldo}
                                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                                    >
                                        <Plus className="w-5 h-5" />
                                    </button>
                                </div>
                                <div className="space-y-2">
                                    {config.telefonos_respaldo.map((tel, index) => (
                                        <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
                                            <span className="flex-1 text-sm">{tel}</span>
                                            <button
                                                onClick={() => handleRemoveRespaldo(index)}
                                                className="p-1 text-red-600 hover:bg-red-50 rounded"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="grupos_activos"
                                    checked={config.grupos_activos}
                                    onChange={(e) => setConfig({ ...config, grupos_activos: e.target.checked })}
                                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                                />
                                <label htmlFor="grupos_activos" className="text-sm font-medium text-gray-700">
                                    Activar bot en grupos
                                </label>
                            </div>
                        </div>
                    </section>

                    {/* Contactos Especiales */}
                    <section>
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-medium text-gray-900">Contactos Especiales</h3>
                            <button
                                onClick={handleAddContacto}
                                className="flex items-center gap-2 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                            >
                                <Plus className="w-4 h-4" />
                                Agregar Contacto
                            </button>
                        </div>

                        <div className="space-y-4">
                            {contactos.map((contacto, index) => (
                                <div key={index} className="p-4 border border-gray-200 rounded-lg space-y-3">
                                    <div className="flex items-start justify-between">
                                        <h4 className="font-medium text-gray-900">Contacto #{index + 1}</h4>
                                        <button
                                            onClick={() => handleRemoveContacto(index)}
                                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>

                                    <div className="grid grid-cols-2 gap-3">
                                        <input
                                            type="tel"
                                            value={contacto.telefono}
                                            onChange={(e) => handleUpdateContacto(index, 'telefono', e.target.value)}
                                            placeholder="Teléfono"
                                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                        />
                                        <input
                                            type="text"
                                            value={contacto.nombre}
                                            onChange={(e) => handleUpdateContacto(index, 'nombre', e.target.value)}
                                            placeholder="Nombre"
                                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                        />
                                        <select
                                            value={contacto.etiqueta}
                                            onChange={(e) => handleUpdateContacto(index, 'etiqueta', e.target.value)}
                                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                        >
                                            <option value="proveedor">Proveedor</option>
                                            <option value="familiar">Familiar</option>
                                            <option value="emergencia">Emergencia</option>
                                            <option value="vip">VIP</option>
                                            <option value="bloqueado">Bloqueado</option>
                                            <option value="otro">Otro</option>
                                        </select>
                                        <select
                                            value={contacto.comportamiento}
                                            onChange={(e) => handleUpdateContacto(index, 'comportamiento', e.target.value)}
                                            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                        >
                                            <option value="normal">Normal</option>
                                            <option value="prioritario">Prioritario</option>
                                            <option value="no_responder">No Responder</option>
                                            <option value="solo_humano">Solo Humano</option>
                                        </select>
                                    </div>

                                    <textarea
                                        value={contacto.descripcion}
                                        onChange={(e) => handleUpdateContacto(index, 'descripcion', e.target.value)}
                                        placeholder="Descripción"
                                        rows={2}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                    />

                                    <textarea
                                        value={contacto.contexto_ia}
                                        onChange={(e) => handleUpdateContacto(index, 'contexto_ia', e.target.value)}
                                        placeholder="Contexto para IA (ej: 'Este es nuestro proveedor principal de insumos médicos')"
                                        rows={2}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                                    />

                                    <div className="flex items-center gap-2">
                                        <input
                                            type="checkbox"
                                            id={`notificar_${index}`}
                                            checked={contacto.notificar_admin}
                                            onChange={(e) => handleUpdateContacto(index, 'notificar_admin', e.target.checked)}
                                            className="w-4 h-4 text-primary-600 rounded"
                                        />
                                        <label htmlFor={`notificar_${index}`} className="text-sm text-gray-700">
                                            Notificar admin en cada mensaje
                                        </label>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                    >
                        {saving ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Guardando...
                            </>
                        ) : (
                            <>
                                <Save className="w-4 h-4" />
                                Guardar
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};
