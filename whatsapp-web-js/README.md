# WhatsApp Maya Bridge

Cliente WhatsApp para conectar con el agente Maya de Podoskin Solution.

## Requisitos

- Node.js v18+
- Python 3.10+ (para el Bridge API)

## Instalación

### 1. Instalar dependencias de Node.js

```bash
cd whatsapp-web-js
npm install
```

### 2. Instalar dependencias de Python (Bridge)

```bash
cd backend
pip install fastapi uvicorn
```

## Ejecución

### Paso 1: Iniciar Bridge API (Python)

```bash
cd backend
.\venv\Scripts\Activate.ps1
python whatsapp_bridge.py
```

Debería mostrar:

```
🚀 Iniciando Bridge API...
✅ Conexión a base de datos establecida
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Paso 2: Iniciar cliente WhatsApp (Node.js)

En otra terminal:

```bash
cd whatsapp-web-js
npm start
```

### Paso 3: Escanear código QR

Cuando aparezca el código QR en la terminal:

1. Abre WhatsApp en tu teléfono
2. Ve a Configuración → Dispositivos vinculados
3. Escanea el código QR

Una vez conectado verás:

```
🟢 MAYA - WhatsApp Bot Activo
   Podoskin Solution
```

## Uso

Una vez activo, Maya responderá automáticamente a todos los mensajes de WhatsApp.

## Notas

- La sesión se guarda en `./session` para no re-escanear QR
- El teléfono debe tener conexión a internet
- Para desconectar, usa Ctrl+C en ambas terminales
