/**
 * Simulador de Mensajes WhatsApp
 * ==============================
 *
 * Simula mensajes entrantes para probar el backend sin WhatsApp real.
 *
 * Uso: node test-simulator.js
 */

const axios = require('axios');
const readline = require('readline');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Colores para la terminal
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    red: '\x1b[31m'
};

// Números de prueba simulados
const testNumbers = [
    { number: '5215512345678@c.us', name: 'Juan Pérez (Paciente nuevo)' },
    { number: '5215598765432@c.us', name: 'María García (Paciente frecuente)' },
    { number: '5215511111111@c.us', name: 'Dr. López (Proveedor)' },
];

let currentNumber = testNumbers[0];

console.log('');
console.log(colors.cyan + '╔══════════════════════════════════════════════════════════╗' + colors.reset);
console.log(colors.cyan + '║' + colors.bright + '     SIMULADOR DE MENSAJES WHATSAPP - PODOSKIN           ' + colors.cyan + '║' + colors.reset);
console.log(colors.cyan + '╠══════════════════════════════════════════════════════════╣' + colors.reset);
console.log(colors.cyan + '║' + colors.reset + ' Comandos:                                                ' + colors.cyan + '║' + colors.reset);
console.log(colors.cyan + '║' + colors.reset + '   /cambiar  - Cambiar número simulado                    ' + colors.cyan + '║' + colors.reset);
console.log(colors.cyan + '║' + colors.reset + '   /status   - Ver estado del servicio                    ' + colors.cyan + '║' + colors.reset);
console.log(colors.cyan + '║' + colors.reset + '   /salir    - Salir del simulador                        ' + colors.cyan + '║' + colors.reset);
console.log(colors.cyan + '║' + colors.reset + '   (cualquier otro texto) - Enviar como mensaje           ' + colors.cyan + '║' + colors.reset);
console.log(colors.cyan + '╚══════════════════════════════════════════════════════════╝' + colors.reset);
console.log('');
console.log(colors.yellow + `Backend: ${BACKEND_URL}` + colors.reset);
console.log(colors.green + `Simulando como: ${currentNumber.name}` + colors.reset);
console.log(colors.green + `Número: ${currentNumber.number}` + colors.reset);
console.log('');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function prompt() {
    rl.question(colors.magenta + '📱 Tu mensaje > ' + colors.reset, async (input) => {
        const trimmed = input.trim();

        if (!trimmed) {
            prompt();
            return;
        }

        // Comandos especiales
        if (trimmed === '/salir' || trimmed === '/exit') {
            console.log(colors.yellow + '\n👋 ¡Hasta luego!' + colors.reset);
            rl.close();
            process.exit(0);
        }

        if (trimmed === '/cambiar') {
            console.log('\nNúmeros disponibles:');
            testNumbers.forEach((t, i) => {
                console.log(`  ${i + 1}. ${t.name} (${t.number})`);
            });
            rl.question('Selecciona número (1-3): ', (choice) => {
                const idx = parseInt(choice) - 1;
                if (idx >= 0 && idx < testNumbers.length) {
                    currentNumber = testNumbers[idx];
                    console.log(colors.green + `\n✅ Ahora simulando como: ${currentNumber.name}` + colors.reset);
                }
                prompt();
            });
            return;
        }

        if (trimmed === '/status') {
            try {
                const response = await axios.get(`${BACKEND_URL}/api/whatsapp-bridge/control/status`, {
                    timeout: 5000
                });
                console.log(colors.cyan + '\n📊 Estado del servicio:' + colors.reset);
                console.log(JSON.stringify(response.data, null, 2));
            } catch (error) {
                console.log(colors.red + `\n❌ Error obteniendo estado: ${error.message}` + colors.reset);
            }
            prompt();
            return;
        }

        // Enviar mensaje simulado
        await sendSimulatedMessage(trimmed);
        prompt();
    });
}

async function sendSimulatedMessage(body) {
    const timestamp = new Date().toISOString();

    console.log('');
    console.log(colors.blue + '════════════════════════════════════════════════════' + colors.reset);
    console.log(colors.blue + `📤 ENVIANDO MENSAJE SIMULADO` + colors.reset);
    console.log(colors.blue + `   De: ${currentNumber.number}` + colors.reset);
    console.log(colors.blue + `   Mensaje: ${body}` + colors.reset);
    console.log(colors.blue + '════════════════════════════════════════════════════' + colors.reset);

    try {
        const response = await axios.post(
            `${BACKEND_URL}/api/whatsapp-bridge/internal/message`,
            {
                from_number: currentNumber.number,
                body: body,
                timestamp: timestamp,
                is_group: false,
                message_id: `sim_${Date.now()}`
            },
            {
                timeout: 30000
            }
        );

        console.log('');
        console.log(colors.green + '════════════════════════════════════════════════════' + colors.reset);
        console.log(colors.green + `📥 RESPUESTA DEL BACKEND` + colors.reset);
        console.log(colors.green + `   Status: ${response.data.status}` + colors.reset);

        if (response.data.respuesta) {
            console.log(colors.green + `   Respuesta: ${response.data.respuesta}` + colors.reset);
        }

        if (response.data.contacto_id) {
            console.log(colors.green + `   Contacto ID: ${response.data.contacto_id}` + colors.reset);
        }

        if (response.data.conversacion_id) {
            console.log(colors.green + `   Conversación ID: ${response.data.conversacion_id}` + colors.reset);
        }

        console.log(colors.green + '════════════════════════════════════════════════════' + colors.reset);

        if (response.data.debe_responder && response.data.respuesta) {
            console.log('');
            console.log(colors.cyan + '🤖 BOT RESPONDERÍA:' + colors.reset);
            console.log(colors.bright + `   "${response.data.respuesta}"` + colors.reset);
        }

    } catch (error) {
        console.log('');
        console.log(colors.red + '════════════════════════════════════════════════════' + colors.reset);
        console.log(colors.red + `❌ ERROR` + colors.reset);

        if (error.response) {
            console.log(colors.red + `   Status: ${error.response.status}` + colors.reset);
            console.log(colors.red + `   Detalle: ${JSON.stringify(error.response.data)}` + colors.reset);
        } else {
            console.log(colors.red + `   ${error.message}` + colors.reset);
        }

        console.log(colors.red + '════════════════════════════════════════════════════' + colors.reset);
    }

    console.log('');
}

// Verificar conexión al inicio
async function checkConnection() {
    console.log(colors.yellow + '🔌 Verificando conexión con backend...' + colors.reset);

    try {
        await axios.get(`${BACKEND_URL}/health`, { timeout: 5000 });
        console.log(colors.green + '✅ Backend conectado correctamente\n' + colors.reset);
        prompt();
    } catch (error) {
        console.log(colors.red + `❌ No se puede conectar al backend (${BACKEND_URL})` + colors.reset);
        console.log(colors.yellow + '   Asegúrate de que el backend esté corriendo: python main.py' + colors.reset);
        console.log('');
        rl.close();
        process.exit(1);
    }
}

checkConnection();
