# Sistema de Voz Gemini Live - Podoskin Solution

Sistema de asistente de voz integrado con Gemini Live API para consultas médicas.

## Características

- **8 Funciones Médicas**: Control completo del expediente por voz
- **Seguridad**: API keys en backend, tokens efímeros
- **Audio Optimizado**: Resampling a 16kHz, PCM16 correcto
- **Arquitectura Híbrida**: 
  - Funciones simples → Endpoints REST directos
  - Funciones complejas → Orquestador → SubAgentes

## Estructura

```
Frontend/src/voice/
├── components/
│   └── VoiceController.tsx    # Componente React principal
├── services/
│   ├── secureLiveManager.ts   # Manager de Gemini Live con seguridad
│   ├── secureSession.ts       # Gestión de sesiones seguras
│   └── audioUtils.ts          # Utilidades de audio (resampling, PCM16)
├── types/
│   └── index.ts               # TypeScript types
├── constants.ts               # 8 funciones médicas + system instruction
├── index.ts                   # Exports principales
└── README.md                  # Esta documentación
```

## Funciones Médicas

### Funciones Simples (REST Directo)
1. **update_vital_signs** - Actualizar signos vitales
2. **create_clinical_note** - Crear/actualizar nota clínica
3. **query_patient_data** - Consultar datos del paciente
4. **add_allergy** - Registrar alergia
5. **navigate_to_section** - Navegar en la interfaz
6. **schedule_followup** - Programar seguimiento

### Funciones Complejas (Orquestador)
7. **search_patient_history** - Búsqueda semántica en historial
8. **generate_summary** - Generar resumen (usa SubAgente Resúmenes)

## Uso

### Integración Básica

```tsx
import { VoiceController } from '@/voice';

function ConsultaPage() {
  const sessionConfig = {
    patientId: currentPatient.id,
    appointmentId: currentAppointment.id,
    userId: currentUser.id
  };

  return (
    <VoiceController
      backendUrl="http://localhost:8000"
      sessionConfig={sessionConfig}
      onNavigate={(section) => navigateTo(section)}
      onDataUpdate={(data) => handleUpdate(data)}
    />
  );
}
```

### Uso Avanzado con LiveManager

```tsx
import { SecureLiveManager, MEDICAL_SYSTEM_INSTRUCTION } from '@/voice';

const liveManager = new SecureLiveManager('http://localhost:8000', {
  onLog: (msg, type) => console.log(`[${type}]`, msg),
  onStatusChange: (connected) => setConnected(connected),
  onError: (err) => console.error(err),
  onToolCall: async (name, args) => {
    // Implementar lógica de tool calls
    return { success: true, data: result };
  }
});

// Conectar
await liveManager.connect(
  VoiceName.Kore,
  MEDICAL_SYSTEM_INSTRUCTION,
  sessionConfig
);

// Desconectar
await liveManager.disconnect();
```

## Flujo de Seguridad

### 1. Backend Endpoints Requeridos

```python
# backend/api/live_sessions.py

@router.post("/api/live/session/start")
async def start_session(config: SessionConfig):
    """Crear sesión segura con token efímero"""
    token = create_ephemeral_token(config, ttl=3600)
    return {
        "token": token,
        "sessionId": session_id,
        "expiresAt": expires_at
    }

@router.post("/api/live/session/stop")
async def stop_session(session_id: str):
    """Cerrar sesión"""
    revoke_token(session_id)
    return {"status": "closed"}

@router.post("/api/live/tool/call")
async def execute_tool(request: ToolCallRequest):
    """Ejecutar tool crítica en backend"""
    validate_token(request.session_token)
    result = execute_tool_securely(request.tool_name, request.args)
    return result
```

### 2. Flujo de Sesión

```
1. Frontend solicita sesión
   POST /api/live/session/start
   Body: { patientId, appointmentId, userId }

2. Backend valida usuario y crea token efímero
   Token TTL: 3600s
   Guarda en Redis/DB

3. Frontend usa token para:
   - Obtener credenciales de Gemini (temporal)
   - Ejecutar tool calls críticas
   - Mantener sesión activa

4. Token se renueva automáticamente antes de expirar

5. Al desconectar:
   POST /api/live/session/stop
   Backend revoca token
```

## Audio Pipeline

### Entrada (Micrófono → Gemini)

```
1. Captura: getUserMedia() con echoCancellation
2. Procesamiento: ScriptProcessorNode (4096 buffer)
3. Resampling: OfflineAudioContext → 16kHz
4. Conversión: Float32Array → PCM16 base64
5. Envío: session.sendRealtimeInput()
```

### Salida (Gemini → Speaker)

```
1. Recepción: base64 PCM16 @ 24kHz
2. Decodificación: base64 → Int16Array → Float32Array
3. Buffer: AudioBuffer a 24kHz
4. Reproducción: AudioBufferSourceNode con scheduling
```

## Mejores Prácticas

### Seguridad

- ✅ **NUNCA** exponer API keys en cliente
- ✅ Usar tokens efímeros con TTL
- ✅ Validar permisos en cada tool call
- ✅ Logs de auditoría en backend
- ✅ Cifrar datos PHI en reposo y tránsito

### Audio

- ✅ Resamplear a 16kHz antes de enviar
- ✅ NO conectar ScriptProcessor a destination (evita feedback)
- ✅ Usar gain=0 si necesitas conectar
- ✅ Resume AudioContext después de user interaction
- ✅ Cleanup: stop tracks, close contexts

### Performance

- ✅ Buffer size: 4096 samples (balance latencia/CPU)
- ✅ Resampling asíncrono con OfflineAudioContext
- ✅ Scheduling de audio con nextStartTime
- ✅ Cleanup de sources al terminar

## Troubleshooting

### "AudioContext suspended"
```tsx
await resumeAudioContext(audioContext);
```

### "API key exposed"
- Mover API key a backend
- Implementar proxy o session tokens

### "Audio feedback / echo"
```tsx
// NO conectar a destination
// source.connect(scriptProcessor);
// scriptProcessor.connect(destination); // ❌ Evitar

// Usar gain silencioso
const silentGain = createSilentGainNode(audioContext);
scriptProcessor.connect(silentGain);
silentGain.connect(destination);
```

### "Sample rate incorrecto"
```tsx
// Siempre resamplear
const buffer = audioContext.createBuffer(1, data.length, audioContext.sampleRate);
buffer.copyToChannel(data, 0);
const resampled = await resampleTo16k(buffer);
```

## Dependencias

```json
{
  "@google/genai": "^1.30.0",
  "react": "^18.3.1"
}
```

## Referencias

- [GEMINI_LIVE_FUNCTIONS.md](../../../data/GEMINI_LIVE_FUNCTIONS.md)
- [FSD_Podoskin_Solution.md](../../../FSD_Podoskin_Solution.md) - Sección 3.3
- [recomendacionesLangGraph.md](../../../recomendacionesLangGraph.md)
- [gemini-live-voice-controller/](../../../gemini-live-voice-controller/)

## TODO

- [ ] Migrar de ScriptProcessor a AudioWorklet
- [ ] Implementar streaming de texto (modo híbrido)
- [ ] Añadir VAD (Voice Activity Detection)
- [ ] Soporte para interrupciones de usuario
- [ ] Métricas de latencia y calidad de audio
