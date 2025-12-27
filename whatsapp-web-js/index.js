/**
 * Cliente WhatsApp para Maya - Podoskin Solution
 * ================================================
 * 
 * Conecta WhatsApp Web con el agente Maya via Bridge API
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Configuración
const BRIDGE_API_URL = process.env.BRIDGE_API_URL || 'http://localhost:8000';
const TYPING_SPEED_MS_PER_CHAR = 30;  // millisegundos por caracter
const MIN_TYPING_TIME = 1000;  // mínimo 1 segundo
const MAX_TYPING_TIME = 5000;  // máximo 5 segundos

// Crear cliente WhatsApp con autenticación persistente
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './session'
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Función para simular escritura
async function simulateTyping(chat, responseLength) {
    // Calcular tiempo de "escritura" basado en caracteres
    let typingTime = responseLength * TYPING_SPEED_MS_PER_CHAR;
    typingTime = Math.max(MIN_TYPING_TIME, Math.min(MAX_TYPING_TIME, typingTime));

    // Mostrar indicador de "escribiendo..."
    await chat.sendStateTyping();

    // Esperar el tiempo calculado
    await new Promise(resolve => setTimeout(resolve, typingTime));
}

// Cuando necesita escanear QR
client.on('qr', (qr) => {
    console.log('\n📱 Escanea este código QR con WhatsApp:');
    console.log('----------------------------------------');
    qrcode.generate(qr, { small: true });
    console.log('----------------------------------------\n');
});

// Cuando está autenticando
client.on('authenticated', () => {
    console.log('✅ Autenticación exitosa');
});

// Cuando está listo
client.on('ready', () => {
    console.log('');
    console.log('='.repeat(50));
    console.log('   🟢 MAYA - WhatsApp Bot Activo');
    console.log('   Podoskin Solution');
    console.log('='.repeat(50));
    console.log('');
    console.log('Esperando mensajes...');
});

// Cuando recibe un mensaje
client.on('message', async (message) => {
    // Ignorar mensajes de grupos y broadcasts
    if (message.from.includes('@g.us') || message.from.includes('@broadcast')) {
        return;
    }

    // Ignorar mensajes propios
    if (message.fromMe) {
        return;
    }

    // Obtener datos
    const chatId = message.from;
    const userMessage = message.body;
    const userPhone = chatId.replace('@c.us', '');

    // IGNORAR MENSAJES VACÍOS
    if (!userMessage || !userMessage.trim()) {
        console.log(`⚠️ Mensaje vacío de ${userPhone}, ignorando...`);
        return;
    }

    // Nombre del remitente
    const userName = message._data.notifyName || 'Usuario';

    console.log(`\n📩 Mensaje de ${userName} (${userPhone}):`);
    console.log(`   "${userMessage}"`);

    try {
        // Obtener objeto chat para simular escritura
        const chat = await message.getChat();

        // Enviar al Bridge API (Maya)
        const response = await axios.post(`${BRIDGE_API_URL}/webhook/whatsapp`, {
            chat_id: chatId,
            phone: userPhone,
            name: userName,
            message: userMessage
        }, {
            timeout: 60000
        });

        const botResponse = response.data.response;
        const intent = response.data.intent;

        // CASO 1: Maya escaló una duda al admin
        if (intent === 'escalated' && response.data.admin_message) {
            console.log(`📤 Escalando duda al admin...`);

            // Enviar al paciente
            if (botResponse && botResponse.trim()) {
                await simulateTyping(chat, botResponse.length);
                await chat.sendMessage(botResponse);
            }

            // Enviar notificación al admin
            try {
                const adminChatId = response.data.admin_chat_id;
                const adminMessage = response.data.admin_message;

                await client.sendMessage(adminChatId, adminMessage);
                console.log(`✅ Notificación enviada al admin`);
            } catch (adminError) {
                console.error(`❌ Error enviando al admin: ${adminError.message}`);
            }
            return;
        }

        // CASO 2: Admin respondió una duda
        if (intent === 'admin_response' && response.data.target_chat_id) {
            console.log(`📨 Enviando respuesta del admin al paciente...`);

            try {
                const targetChatId = response.data.target_chat_id;
                await client.sendMessage(targetChatId, botResponse);
                console.log(`✅ Respuesta enviada al paciente`);
            } catch (sendError) {
                console.error(`❌ Error enviando al paciente: ${sendError.message}`);
            }
            return;
        }

        // CASO 3: Respuesta normal
        if (botResponse && botResponse.trim()) {
            console.log(`🤖 Maya responde:`);
            console.log(`   "${botResponse}"`);

            // Simular escritura antes de enviar
            await simulateTyping(chat, botResponse.length);

            // Enviar respuesta
            await chat.sendMessage(botResponse);
        }

    } catch (error) {
        console.error('❌ Error al procesar mensaje:', error.message);

        const chat = await message.getChat();
        const errorMsg = 'Disculpe, estoy teniendo problemas técnicos. Por favor llame al 686-108-3647.';

        await simulateTyping(chat, errorMsg.length);
        await chat.sendMessage(errorMsg);
    }
});

// Manejar desconexión
client.on('disconnected', (reason) => {
    console.log('⚠️ Cliente desconectado:', reason);
    console.log('Intentando reconectar...');
    client.initialize();
});

// Manejar errores de autenticación
client.on('auth_failure', (msg) => {
    console.error('❌ Error de autenticación:', msg);
});

// Iniciar cliente
console.log('');
console.log('🚀 Iniciando cliente WhatsApp...');
console.log('');
client.initialize();
