/**
 * WhatsApp Service - Main Server
 * ================================
 * 
 * Servicio Node.js que maneja WhatsApp.js con:
 * - Paro de emergencia
 * - Gestión de contactos especiales
 * - Integración con agente LangGraph
 */

const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// ============================================================================
// CONFIGURACIÓN
// ============================================================================

const CONFIG = {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
    PORT: process.env.PORT || 3000,
    SESSION_NAME: 'whatsapp-medico'
};

// ============================================================================
// ESTADO GLOBAL
// ============================================================================

let client = null;
let currentQR = null;
let serviceStatus = 'stopped'; // stopped, starting, running, error

// ============================================================================
// CLIENTE WHATSAPP
// ============================================================================

function createClient() {
    console.log('📱 Creando cliente WhatsApp...');

    client = new Client({
        authStrategy: new LocalAuth({
            clientId: CONFIG.SESSION_NAME
        }),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        }
    });

    // ========================================================================
    // EVENTOS DEL CLIENTE
    // ========================================================================

    client.on('qr', async (qr) => {
        console.log('📱 QR Code generado');

        try {
            // Generar QR en base64
            currentQR = await qrcode.toDataURL(qr);

            // Backend pulls QR, no need to push
            // const response = await axios.post(`${CONFIG.BACKEND_URL}/api/whatsapp-bridge/qr`, { ... });

            console.log('✅ QR generado localmente (Backend lo obtendrá bajo demanda)');
        } catch (error) {
            console.error('❌ Error generando QR:', error.message);
        }
    });

    client.on('authenticated', () => {
        console.log('✅ Autenticado exitosamente');
        serviceStatus = 'running';
    });

    client.on('ready', async () => {
        console.log('🟢 WhatsApp listo para recibir mensajes');
        serviceStatus = 'running';
        currentQR = null;

        // Backend pulls status, no need to push
        console.log('✅ Estado actualizado en memoria: RUNNING');
    });

    client.on('message', async (msg) => {
        await handleMessage(msg);
    });

    client.on('disconnected', (reason) => {
        console.log('🔴 Desconectado:', reason);
        serviceStatus = 'stopped';
        currentQR = null;
    });

    client.on('auth_failure', (error) => {
        console.error('❌ Error de autenticación:', error);
        serviceStatus = 'error';
    });
}

// ============================================================================
// MANEJO DE MENSAJES
// ============================================================================

async function handleMessage(msg) {
    const from = msg.from;
    const body = msg.body;
    const isGroup = from.endsWith('@g.us');
    const timestamp = new Date().toISOString();

    console.log('');
    console.log('════════════════════════════════════════════════════');
    console.log(`📨 MENSAJE RECIBIDO [${new Date().toLocaleTimeString()}]`);
    console.log(`   De: ${from}`);
    console.log(`   Tipo: ${isGroup ? 'Grupo' : 'Chat privado'}`);
    console.log(`   Mensaje: ${body}`);
    console.log('════════════════════════════════════════════════════');

    try {
        // 1. Ignorar grupos por ahora
        if (isGroup) {
            console.log('⏭️ Mensaje de grupo - ignorando');
            return;
        }

        // 2. Verificar contacto especial
        const contactInfo = await getContactInfo(from);

        if (contactInfo.comportamiento === 'no_responder') {
            console.log('🚫 Contacto en lista de no responder');
            return;
        }

        // 3. Enviar al nuevo endpoint interno (sin auth, solo localhost)
        console.log('📤 Enviando al backend...');
        const response = await axios.post(
            `${CONFIG.BACKEND_URL}/api/whatsapp-bridge/internal/message`,
            {
                from_number: from,
                body: body,
                timestamp: timestamp,
                is_group: isGroup,
                message_id: msg.id?.id || null
            },
            {
                timeout: 30000
            }
        );

        console.log(`📥 Respuesta del backend: ${response.data.status}`);

        // 4. Si el backend dice que debemos responder, enviamos la respuesta
        if (response.data.debe_responder && response.data.respuesta) {
            await msg.reply(response.data.respuesta);
            console.log('✅ Respuesta enviada al usuario');
        }

        // 5. Notificar admin si es contacto prioritario
        if (contactInfo.notificar_admin) {
            await notifyAdmin(`📨 Mensaje de ${contactInfo.nombre || from}: ${body.substring(0, 50)}...`);
        }

    } catch (error) {
        console.error('❌ Error procesando mensaje:', error.message);

        // Respuesta de emergencia si falla el backend
        try {
            await msg.reply('Disculpa, estamos experimentando dificultades técnicas. Por favor intenta de nuevo en unos minutos o llámanos directamente.');
            console.log('⚠️ Respuesta de emergencia enviada');
        } catch (replyError) {
            console.error('❌ No se pudo enviar respuesta de emergencia');
        }
    }
}

// ============================================================================
// FUNCIONES AUXILIARES
// ============================================================================

async function getContactInfo(phone) {
    try {
        const response = await axios.get(
            `${CONFIG.BACKEND_URL}/api/whatsapp-bridge/contacts/${phone}`,
            { timeout: 5000 }
        );
        return response.data;
    } catch (error) {
        // Si no se encuentra, retornar comportamiento normal
        return {
            comportamiento: 'normal',
            notificar_admin: false,
            contexto_ia: null
        };
    }
}

async function checkGroupActive(groupId) {
    try {
        const response = await axios.get(
            `${CONFIG.BACKEND_URL}/api/whatsapp-bridge/groups/${groupId}`,
            { timeout: 5000 }
        );
        return response.data.bot_activo || false;
    } catch (error) {
        return false;
    }
}

async function escalateToHuman(from, message, contactInfo) {
    try {
        await axios.post(
            `${CONFIG.BACKEND_URL}/api/agents/whatsapp/${from}/mensaje`,
            {
                content: message,
                phone_number: from,
                force_escalate: true,
                contact_info: contactInfo
            }
        );
        console.log('✅ Mensaje escalado a humano');
    } catch (error) {
        console.error('❌ Error escalando mensaje:', error.message);
    }
}

async function notifyAdmin(message) {
    try {
        // Obtener configuración
        const response = await axios.get(
            `${CONFIG.BACKEND_URL}/api/whatsapp-bridge/config`,
            { timeout: 5000 }
        );

        const adminPhone = response.data.telefono_admin;

        if (adminPhone && client) {
            const chatId = `${adminPhone}@c.us`;
            await client.sendMessage(chatId, `🔔 ${message}`);
            console.log('✅ Admin notificado');
        }
    } catch (error) {
        console.error('⚠️ No se pudo notificar al admin:', error.message);
    }
}

// ============================================================================
// ENDPOINTS DE CONTROL
// ============================================================================

app.post('/control/start', async (req, res) => {
    if (serviceStatus === 'running') {
        return res.json({
            status: 'already_running',
            message: 'El servicio ya está en ejecución'
        });
    }

    if (serviceStatus === 'starting') {
        return res.json({
            status: 'starting',
            message: 'El servicio ya se está iniciando'
        });
    }

    try {
        console.log('🚀 Iniciando servicio WhatsApp...');
        serviceStatus = 'starting';

        createClient();
        await client.initialize();

        res.json({
            status: 'starting',
            message: 'Servicio iniciado, esperando QR o autenticación'
        });
    } catch (error) {
        console.error('❌ Error iniciando servicio:', error);
        serviceStatus = 'error';

        res.status(500).json({
            status: 'error',
            error: error.message
        });
    }
});

app.post('/control/stop', async (req, res) => {
    console.log('⏸️ Deteniendo servicio (Pausa)...');

    try {
        if (client) {
            await client.destroy();
            client = null;
        }

        serviceStatus = 'stopped';
        currentQR = null;

        res.json({
            status: 'stopped',
            message: 'Servicio pausado correctamente (Sesión conservada)'
        });
    } catch (error) {
        console.error('❌ Error deteniendo servicio:', error);
        res.status(500).json({ status: 'error', error: error.message });
    }
});

app.post('/control/logout', async (req, res) => {
    console.log('🛑 CERRANDO SESIÓN Y ELIMINANDO DATOS');

    try {
        if (client) {
            await client.logout().catch(() => { }); // Intentar logout gracioso
            await client.destroy();
            client = null;
        }

        // Eliminar sesión
        const fs = require('fs');
        const path = require('path');
        const sessionPath = path.join(__dirname, '.wwebjs_auth');

        if (fs.existsSync(sessionPath)) {
            fs.rmSync(sessionPath, { recursive: true, force: true });
            console.log('🗑️ Sesión eliminada del disco');
        }

        serviceStatus = 'stopped';
        currentQR = null;

        res.json({
            status: 'stopped',
            message: 'Sesión cerrada y datos eliminados. Requiere nuevo QR.'
        });
    } catch (error) {
        console.error('❌ Error en logout:', error);
        res.status(500).json({ status: 'error', error: error.message });
    }
});

// Alias para compatibilidad inversa temporal
app.post('/control/emergency-stop', async (req, res) => {
    res.redirect(307, '/control/logout');
});

app.get('/control/status', (req, res) => {
    res.json({
        status: serviceStatus,
        hasQR: !!currentQR,
        timestamp: new Date().toISOString(),
        clientReady: client ? client.info : null
    });
});

app.get('/qr', (req, res) => {
    if (!currentQR) {
        return res.status(404).json({
            error: 'No QR disponible',
            status: serviceStatus
        });
    }

    res.json({
        qr: currentQR,
        timestamp: new Date().toISOString()
    });
});

// ============================================================================
// HEALTH CHECK
// ============================================================================

app.get('/health', (req, res) => {
    res.json({
        service: 'whatsapp-service',
        status: serviceStatus,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

// ============================================================================
// INICIAR SERVIDOR
// ============================================================================

app.listen(CONFIG.PORT, () => {
    console.log('╔════════════════════════════════════════╗');
    console.log('║   WhatsApp Service - Podoskin          ║');
    console.log('╠════════════════════════════════════════╣');
    console.log(`║   Puerto: ${CONFIG.PORT.toString().padEnd(30)}║`);
    console.log(`║   Backend: ${CONFIG.BACKEND_URL.substring(0, 27).padEnd(27)}║`);
    console.log('╚════════════════════════════════════════╝');
    console.log('');
    console.log('🟢 Servidor listo');
    console.log('📡 Esperando comandos de control...');
    console.log('');
});

// ============================================================================
// MANEJO DE ERRORES
// ============================================================================

process.on('uncaughtException', (error) => {
    console.error('💥 Error no capturado:', error);
    serviceStatus = 'error';
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('💥 Promesa rechazada no manejada:', reason);
    serviceStatus = 'error';
});

process.on('SIGINT', async () => {
    console.log('\n🛑 Deteniendo servicio...');

    if (client) {
        await client.destroy();
    }

    process.exit(0);
});
