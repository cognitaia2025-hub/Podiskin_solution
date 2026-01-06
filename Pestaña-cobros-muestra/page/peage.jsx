import React, { useState } from 'react';
import { X, Search, Filter, Plus, Eye, Printer, Receipt, FileText, DollarSign, Calendar, CreditCard, Clock, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

const GestionCobros = () => {
  const [modalAbierto, setModalAbierto] = useState(null);
  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [busqueda, setBusqueda] = useState('');

  // Datos de ejemplo
  const pagos = [
    { id: 1, paciente: 'Juan Pérez', edad: 40, fecha: '03/01/26', hora: '14:30', total: 850, pagado: 850, adeudo: 0, metodo: 'Efectivo', estado: 'completo', factura: false },
    { id: 2, paciente: 'María López', edad: 35, fecha: '03/01/26', hora: '10:15', total: 1200, pagado: 600, adeudo: 600, metodo: 'Tarjeta', estado: 'parcial', factura: false },
    { id: 3, paciente: 'Carlos Ruiz', edad: 52, fecha: '02/01/26', hora: '16:00', total: 450, pagado: 0, adeudo: 450, metodo: '', estado: 'pendiente', factura: false },
    { id: 4, paciente: 'Ana Martínez', edad: 28, fecha: '03/01/26', hora: '11:30', total: 950, pagado: 950, adeudo: 0, metodo: 'Transferencia', estado: 'completo', factura: true },
  ];

  const getEstadoColor = (estado) => {
    switch(estado) {
      case 'completo': return 'text-green-600 bg-green-50';
      case 'parcial': return 'text-yellow-600 bg-yellow-50';
      case 'pendiente': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getEstadoIcon = (estado) => {
    switch(estado) {
      case 'completo': return <CheckCircle className="w-4 h-4" />;
      case 'parcial': return <Clock className="w-4 h-4" />;
      case 'pendiente': return <AlertCircle className="w-4 h-4" />;
      default: return null;
    }
  };

  const totalCobrado = pagos.filter(p => p.estado === 'completo').reduce((sum, p) => sum + p.pagado, 0);
  const totalPendiente = pagos.reduce((sum, p) => sum + p.adeudo, 0);
  const pagosCompletos = pagos.filter(p => p.estado === 'completo').length;
  const adeudos = pagos.filter(p => p.adeudo > 0).length;

  const pagosFiltrados = pagos.filter(p => {
    const coincideBusqueda = p.paciente.toLowerCase().includes(busqueda.toLowerCase());
    const coincideEstado = filtroEstado === 'todos' || p.estado === filtroEstado;
    return coincideBusqueda && coincideEstado;
  });

  // Modal de Registro de Pago
  const ModalRegistroPago = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <DollarSign className="w-6 h-6" />
                Registrar Pago
              </h2>
              <p className="text-blue-100 text-sm mt-1">Complete la información del pago</p>
            </div>
            <button onClick={() => setModalAbierto(null)} className="hover:bg-blue-800 p-2 rounded-full">
              <X className="w-6 h-6" />
            </button>
          </div>
          <div className="mt-4 bg-blue-800 rounded-full h-2">
            <div className="bg-white rounded-full h-2 w-3/5"></div>
          </div>
          <p className="text-xs text-blue-200 mt-1">Progreso: 60%</p>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              🔍 Seleccionar Paciente/Cita *
            </label>
            <select className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              <option>Juan Pérez - Cita #145 (03/01/2026 - 14:30)</option>
              <option>María López - Cita #146 (03/01/2026 - 10:15)</option>
            </select>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm font-semibold text-gray-700 mb-3">💵 Montos</p>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Monto Total *</label>
                <input type="number" defaultValue="850.00" className="w-full border border-gray-300 rounded-lg p-2 text-center font-bold" />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Monto Pagado *</label>
                <input type="number" defaultValue="850.00" className="w-full border border-gray-300 rounded-lg p-2 text-center font-bold text-green-600" />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Saldo Pendiente</label>
                <input type="number" value="0.00" disabled className="w-full border border-gray-300 rounded-lg p-2 text-center font-bold bg-gray-100 text-gray-500" />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              💳 Método de Pago *
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button className="border-2 border-blue-500 bg-blue-50 text-blue-700 rounded-lg p-3 font-medium hover:bg-blue-100">
                💵 Efectivo
              </button>
              <button className="border-2 border-gray-300 text-gray-700 rounded-lg p-3 font-medium hover:border-blue-500 hover:bg-blue-50">
                💳 Tarjeta
              </button>
              <button className="border-2 border-gray-300 text-gray-700 rounded-lg p-3 font-medium hover:border-blue-500 hover:bg-blue-50">
                🏦 Transferencia
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              📝 Referencia/Folio (Opcional)
            </label>
            <input type="text" placeholder="Ej: Ref-12345, Aprob-6789" className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500" />
          </div>

          <div className="flex items-center gap-4 bg-blue-50 p-4 rounded-lg">
            <input type="checkbox" id="factura" className="w-5 h-5" />
            <label htmlFor="factura" className="text-sm font-medium text-gray-700">
              🧾 ¿Requiere Factura?
            </label>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              📄 RFC (si requiere factura)
            </label>
            <input type="text" placeholder="XAXX010101000" className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500" />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              📝 Notas adicionales (opcional)
            </label>
            <textarea rows="3" placeholder="Pago correspondiente a tratamiento..." className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500"></textarea>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Estado del Pago:
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="estado" defaultChecked className="w-4 h-4" />
                <span className="text-sm font-medium text-green-700">● Completo</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="estado" className="w-4 h-4" />
                <span className="text-sm font-medium text-yellow-700">● Parcial</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="estado" className="w-4 h-4" />
                <span className="text-sm font-medium text-red-700">● Pendiente</span>
              </label>
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 bg-gray-50 p-6 rounded-b-lg flex gap-3 border-t">
          <button onClick={() => setModalAbierto(null)} className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-100">
            ❌ Cancelar
          </button>
          <button className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
            💾 Guardar Pago
          </button>
        </div>
      </div>
    </div>
  );

  // Modal de Vista Previa de Comprobante
  const ModalComprobante = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md">
        <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-4 rounded-t-lg flex justify-between items-center">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Receipt className="w-5 h-5" />
            Comprobante de Pago
          </h2>
          <button onClick={() => setModalAbierto(null)} className="hover:bg-green-800 p-2 rounded-full">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center space-y-4">
            <div className="text-sm text-gray-500">CLÍNICA PODOLÓGICA</div>
            <div className="text-2xl font-bold text-gray-800">$850.00</div>
            <div className="text-xs text-gray-500">FOLIO: #001-2026</div>
            
            <div className="border-t border-gray-200 pt-4 space-y-2 text-left text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Paciente:</span>
                <span className="font-medium">Juan Pérez</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Fecha:</span>
                <span className="font-medium">03/01/2026 - 14:30</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Método:</span>
                <span className="font-medium">💵 Efectivo</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Estado:</span>
                <span className="font-medium text-green-600">✅ Completo</span>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4 text-xs text-gray-400">
              Recibido por: Santiago Ornelas
            </div>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-b-lg flex gap-3">
          <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 flex items-center justify-center gap-2">
            <Printer className="w-4 h-4" />
            Imprimir
          </button>
          <button className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-100">
            📧 Enviar
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header Principal */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
              <DollarSign className="w-8 h-8 text-blue-600" />
              Gestión de Cobros
            </h1>
            <p className="text-sm text-gray-500 mt-1">Control de pagos, adeudos y facturación</p>
          </div>
          <div className="text-right text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              📅 Hoy: 03 Ene 2026
            </div>
            <div className="text-gray-500">👤 Santiago Ornelas</div>
          </div>
        </div>

        {/* Resumen Rápido */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
            <div className="text-sm text-gray-600 mb-1">💵 Total Cobrado</div>
            <div className="text-2xl font-bold text-green-600">${totalCobrado.toFixed(2)}</div>
            <div className="text-xs text-gray-500 mt-1">✅ {pagosCompletos} pagos completos</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
            <div className="text-sm text-gray-600 mb-1">⏳ Pendientes</div>
            <div className="text-2xl font-bold text-red-600">${totalPendiente.toFixed(2)}</div>
            <div className="text-xs text-gray-500 mt-1">⚠️ {adeudos} adeudos</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <div className="text-sm text-gray-600 mb-1">📊 Promedio</div>
            <div className="text-2xl font-bold text-blue-600">${(totalCobrado / pagosCompletos).toFixed(2)}</div>
            <div className="text-xs text-gray-500 mt-1">por paciente</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
            <div className="text-sm text-gray-600 mb-1">🧾 Facturas</div>
            <div className="text-2xl font-bold text-purple-600">1</div>
            <div className="text-xs text-gray-500 mt-1">solicitadas hoy</div>
          </div>
        </div>
      </div>

      {/* Barra de Herramientas */}
      <div className="bg-white rounded-lg shadow mb-4 p-4">
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="🔍 Buscar paciente..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select 
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500"
          >
            <option value="todos">🏷️ Todos los estados</option>
            <option value="completo">✅ Completos</option>
            <option value="parcial">⚠️ Parciales</option>
            <option value="pendiente">🔴 Pendientes</option>
          </select>
          <button 
            onClick={() => setModalAbierto('registro')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Nuevo Pago
          </button>
        </div>
      </div>

      {/* Tabla de Pagos */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Paciente</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Fecha</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Total</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Pagado</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Adeudo</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Método</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Estado</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {pagosFiltrados.map((pago) => (
                <tr key={pago.id} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-4 text-sm font-medium text-gray-900">#{pago.id.toString().padStart(3, '0')}</td>
                  <td className="px-4 py-4">
                    <div className="font-medium text-gray-900">{pago.paciente}</div>
                    <div className="text-xs text-gray-500">{pago.edad} años</div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="text-sm text-gray-900">{pago.fecha}</div>
                    <div className="text-xs text-gray-500">{pago.hora}</div>
                  </td>
                  <td className="px-4 py-4 text-right font-medium text-gray-900">${pago.total.toFixed(2)}</td>
                  <td className="px-4 py-4 text-right font-medium text-green-600">${pago.pagado.toFixed(2)}</td>
                  <td className="px-4 py-4 text-right font-medium text-red-600">${pago.adeudo.toFixed(2)}</td>
                  <td className="px-4 py-4 text-sm text-gray-700">{pago.metodo}</td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getEstadoColor(pago.estado)}`}>
                      {getEstadoIcon(pago.estado)}
                      {pago.estado.charAt(0).toUpperCase() + pago.estado.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center justify-center gap-2">
                      <button 
                        onClick={() => setModalAbierto('comprobante')}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                        title="Ver comprobante"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg" title="Imprimir">
                        <Printer className="w-4 h-4" />
                      </button>
                      {pago.adeudo > 0 && (
                        <button className="p-2 text-orange-600 hover:bg-orange-50 rounded-lg" title="Registrar pago">
                          <DollarSign className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Acciones Rápidas */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <button className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left border-l-4 border-purple-500">
          <div className="flex items-center gap-3">
            <FileText className="w-8 h-8 text-purple-600" />
            <div>
              <div className="font-semibold text-gray-800">🧾 Facturas</div>
              <div className="text-xs text-gray-500">Gestionar facturación</div>
            </div>
          </div>
        </button>
        <button className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left border-l-4 border-orange-500">
          <div className="flex items-center gap-3">
            <Receipt className="w-8 h-8 text-orange-600" />
            <div>
              <div className="font-semibold text-gray-800">📊 Corte de Caja</div>
              <div className="text-xs text-gray-500">Realizar corte diario</div>
            </div>
          </div>
        </button>
        <button className="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left border-l-4 border-indigo-500">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-indigo-600" />
            <div>
              <div className="font-semibold text-gray-800">📈 Reportes</div>
              <div className="text-xs text-gray-500">Ver análisis financiero</div>
            </div>
          </div>
        </button>
      </div>

      {/* Modales */}
      {modalAbierto === 'registro' && <ModalRegistroPago />}
      {modalAbierto === 'comprobante' && <ModalComprobante />}
    </div>
  );
};

export default GestionCobros;