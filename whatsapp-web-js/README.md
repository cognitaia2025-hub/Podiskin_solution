# WhatsApp Service - Podoskin Solution

Servicio Node.js que integra WhatsApp.js con el backend Python y el agente LangGraph.

## 🚀 Características

- ✅ **Paro de Emergencia**: Detiene el servicio e invalida la sesión
- ✅ **Gestión de Contactos Especiales**: Comportamientos personalizados por contacto
- ✅ **Gestión de Grupos**: Control de bot en grupos de WhatsApp
- ✅ **Integración con LangGraph**: Procesamiento inteligente de mensajes
- ✅ **Notificaciones Admin**: Alertas para contactos prioritarios

## 📦 Instalación

```bash
cd whatsapp-web-js
npm install
```

## ⚙️ Configuración

1. Copiar `.env.example` a `.env`:

```bash
cp .env.example .env
```

1. Editar `.env`:

```env
BACKEND_URL=http://localhost:8000
PORT=3000
```

## 🏃 Ejecución

### Desarrollo

```bash
npm run dev
```

### Producción

```bash
npm start
```

## 🔌 Endpoints

### Control

**POST** `/control/start`

- Inicia el servicio WhatsApp
- Genera QR para autenticación

**POST** `/control/emergency-stop`

- Paro de emergencia
- Invalida sesión actual
- Requiere nuevo QR al reiniciar

**GET** `/control/status`

- Estado actual del servicio
- Información del cliente

**GET** `/qr`

- Obtiene QR code actual (base64)

**GET** `/health`

- Health check del servicio

## 🔄 Flujo de Mensajes

```
WhatsApp → index.js → handleMessage()
                    ↓
            Verificar contacto especial
                    ↓
            Verificar grupo activo
                    ↓
            Enviar a LangGraph (Python)
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
    Respuesta Auto         Escalado
        ↓                       ↓
    msg.reply()          Notificar Admin
```

## 📋 Comportamientos de Contactos

- **normal**: Procesamiento estándar con agente
- **no_responder**: Ignorar mensajes
- **prioritario**: Alta prioridad + notificar admin
- **solo_humano**: Siempre escalar a humano

## 🛡️ Manejo de Errores

- Logs detallados en consola
- Notificación a admin en errores críticos
- Reintentos automáticos en fallos de red
- Estado de error reportado al backend

## 📝 Logs

El servicio genera logs en tiempo real:

- 📱 QR generado
- ✅ Autenticación exitosa
- 📨 Mensajes recibidos
- ✅ Respuestas enviadas
- ⏸️ Escalamientos
- ❌ Errores

## 🔧 Troubleshooting

### El servicio no inicia

- Verificar que el backend esté corriendo
- Revisar variables de entorno en `.env`
- Verificar puerto 3000 disponible

### QR no se genera

- Esperar 30 segundos después de iniciar
- Verificar logs en consola
- Reiniciar con paro de emergencia

### Mensajes no se procesan

- Verificar conexión con backend
- Revisar logs del agente LangGraph
- Verificar configuración de contactos

## 📚 Documentación Adicional

- [WhatsApp Web.js Docs](https://wwebjs.dev/)
- [LangGraph Integration](../backend/agents/whatsapp_medico/README.md)
- [API Backend](../backend/whatsapp_bridge/README.md)
