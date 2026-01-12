/**
 * Tipos TypeScript para WhatsApp Management
 * ==========================================
 * 
 * Interfaces sincronizadas con los modelos Pydantic del backend.
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum EstadoQR {
    PENDIENTE = "pendiente",
    ESCANEADO = "escaneado",
    CONECTADO = "conectado",
    DESCONECTADO = "desconectado",
    EXPIRADO = "expirado",
    ERROR = "error"
}

export enum ProveedorMensajeria {
    WHATSAPP_WEB_JS = "whatsapp-web-js",
    TWILIO = "twilio",
    WHATSAPP_BUSINESS_API = "whatsapp-business-api",
    OTRO = "otro"
}

export enum TonoCl {
    MOLESTO = "molesto",
    CONTENTO = "contento",
    NEUTRAL = "neutral",
    URGENTE = "urgente",
    CONFUNDIDO = "confundido",
    AGRADECIDO = "agradecido",
    IMPACIENTE = "impaciente"
}

export enum IntencionCliente {
    QUEJA = "queja",
    CONSULTA = "consulta",
    AGRADECIMIENTO = "agradecimiento",
    URGENCIA = "urgencia",
    CANCELACION = "cancelacion",
    CONFIRMACION = "confirmacion",
    OTRO = "otro"
}

export enum TonoRespuesta {
    EMPATICO = "empático",
    PROFESIONAL = "profesional",
    AMIGABLE = "amigable",
    FORMAL = "formal",
    URGENTE = "urgente"
}

export enum Sentimiento {
    POSITIVO = "positivo",
    NEUTRAL = "neutral",
    NEGATIVO = "negativo",
    URGENTE = "urgente"
}

export enum OrigenAprendizaje {
    ESCALAMIENTO = "escalamiento",
    MANUAL = "manual",
    IMPORTADO = "importado",
    AUTO_APRENDIZAJE = "auto_aprendizaje"
}

// ============================================================================
// INTERFACES DE QR Y SESIÓN
// ============================================================================

export interface QRSessionCreate {
    proveedor?: ProveedorMensajeria;
}

export interface QRSessionInfo {
    id: number;
    qr_code: string;
    qr_image_url?: string;
    estado: EstadoQR;
    telefono_conectado?: string;
    nombre_dispositivo?: string;
    whatsapp_id?: string;
    proveedor: ProveedorMensajeria;
    fecha_generacion: string;
    fecha_expiracion?: string;
    fecha_escaneo?: string;
    fecha_conexion?: string;
    fecha_desconexion?: string;
    fecha_creacion: string;
    fecha_actualizacion?: string;
}

export interface QRSessionUpdate {
    estado: EstadoQR;
    telefono_conectado?: string;
    nombre_dispositivo?: string;
    whatsapp_id?: string;
}

// ============================================================================
// INTERFACES DE CONTACTO Y MENSAJES
// ============================================================================

export interface ContactoInfo {
    id: number;
    whatsapp_id?: string;
    nombre: string;
    telefono?: string;
    id_paciente?: number;
    es_nuevo_paciente: boolean;
}

export interface MensajeItem {
    id: number;
    direccion: "Entrante" | "Saliente";
    enviado_por_tipo: "Contacto" | "Bot" | "Usuario_Sistema";
    contenido: string;
    fecha_envio: string;
    estado_entrega: string;
    requiere_atencion_humana: boolean;
    sentimiento?: Sentimiento;
    tono?: TonoCl;
}

export interface ConversacionListItem {
    id: number;
    contacto_nombre: string;
    contacto_telefono?: string;
    id_paciente?: number;
    es_nuevo_paciente: boolean;
    ultimo_mensaje: string;
    fecha_ultima_actividad: string;
    requiere_atencion: boolean;
    numero_mensajes_sin_leer: number;
    estado: string;
}

export interface ConversacionDetalle {
    id: number;
    contacto: ContactoInfo;
    canal: string;
    estado: string;
    categoria?: string;
    requiere_atencion: boolean;
    fecha_inicio: string;
    fecha_ultima_actividad: string;
    numero_mensajes: number;
    mensajes: MensajeItem[];
    notas_internas?: string;
}

// ============================================================================
// INTERFACES DE ESCALAMIENTO
// ============================================================================

export interface DudaPendienteItem {
    id: number;
    paciente_nombre: string;
    paciente_telefono?: string;
    id_paciente?: number;
    duda: string;
    contexto?: string;
    estado: string;
    fecha_creacion: string;
    id_conversacion?: number;
    aprendizaje_generado: boolean;
}

export interface RespuestaAdminCreate {
    respuesta: string;
    generar_aprendizaje?: boolean;
    resumen_aprendizaje?: string;
    categoria?: string;
    tags?: string[];
    tono_cliente?: TonoCl;
    intencion_cliente?: IntencionCliente;
    tono_respuesta?: TonoRespuesta;
}

// ============================================================================
// INTERFACES DE APRENDIZAJE
// ============================================================================

export interface AprendizajeAvanzadoCreate {
    // Fase 1: Contexto/Trigger
    pregunta_original: string;
    contexto_trigger: string;
    palabras_clave?: string[];

    // Fase 2: Respuesta
    respuesta_sugerida: string;
    respuesta_admin: string;

    // Análisis de tono
    tono_cliente?: TonoCl;
    intencion_cliente?: IntencionCliente;
    tono_respuesta?: TonoRespuesta;

    // Metadata
    resumen_aprendizaje?: string;
    categoria?: string;
    tags?: string[];
}

export interface AprendizajeAvanzadoUpdate {
    contexto_trigger?: string;
    respuesta_sugerida?: string;
    resumen_aprendizaje?: string;
    categoria?: string;
    tags?: string[];
    palabras_clave?: string[];
    tono_cliente?: TonoCl;
    intencion_cliente?: IntencionCliente;
    tono_respuesta?: TonoRespuesta;
    validado?: boolean;
}

export interface AprendizajeAvanzadoItem {
    id: number;
    // Fase 1
    pregunta_original: string;
    contexto_trigger: string;
    palabras_clave?: string[];
    // Fase 2
    respuesta_sugerida: string;
    respuesta_admin: string;
    // Tono
    tono_cliente?: TonoCl;
    intencion_cliente?: IntencionCliente;
    tono_respuesta?: TonoRespuesta;
    // Metadata
    resumen_aprendizaje: string;
    categoria?: string;
    tags?: string[];
    veces_utilizado: number;
    efectividad: number;
    validado: boolean;
    version: number;
    origen: OrigenAprendizaje;
    fecha_creacion: string;
    fecha_actualizacion?: string;
    fecha_ultimo_uso?: string;
}

// ============================================================================
// INTERFACES DE RESPUESTA AGREGADA
// ============================================================================

export interface ConversacionesResponse {
    atendidas: ConversacionListItem[];
    escaladas: DudaPendienteItem[];
    total_atendidas: number;
    total_escaladas: number;
}

export interface AprendizajesResponse {
    aprendizajes: AprendizajeAvanzadoItem[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
}

export interface EstadisticasAprendizaje {
    total_aprendizajes: number;
    aprendizajes_validados: number;
    aprendizajes_efectivos: number;
    promedio_efectividad: number;
    categorias: Record<string, number>;
    tonos_mas_comunes: Record<string, number>;
}

// ============================================================================
// INTERFACES DE ANÁLISIS DE SENTIMIENTO
// ============================================================================

export interface AnalisisSentimiento {
    id: number;
    id_mensaje: number;
    sentimiento: Sentimiento;
    confianza_sentimiento: number;
    tono: TonoCl;
    confianza_tono: number;
    intencion: IntencionCliente;
    confianza_intencion: number;
    emociones?: Record<string, number>;
    palabras_clave_detectadas?: string[];
    modelo_utilizado: string;
    fecha_analisis: string;
}

// ============================================================================
// HELPERS Y UTILIDADES
// ============================================================================

export const TONO_LABELS: Record<TonoCl, { label: string; emoji: string; color: string }> = {
    [TonoCl.MOLESTO]: { label: "Molesto", emoji: "😠", color: "red" },
    [TonoCl.CONTENTO]: { label: "Contento", emoji: "😊", color: "green" },
    [TonoCl.NEUTRAL]: { label: "Neutral", emoji: "😐", color: "gray" },
    [TonoCl.URGENTE]: { label: "Urgente", emoji: "🚨", color: "orange" },
    [TonoCl.CONFUNDIDO]: { label: "Confundido", emoji: "😕", color: "yellow" },
    [TonoCl.AGRADECIDO]: { label: "Agradecido", emoji: "🙏", color: "blue" },
    [TonoCl.IMPACIENTE]: { label: "Impaciente", emoji: "⏰", color: "purple" }
};

export const TONO_RESPUESTA_LABELS: Record<TonoRespuesta, { label: string; emoji: string }> = {
    [TonoRespuesta.EMPATICO]: { label: "Empático", emoji: "💙" },
    [TonoRespuesta.PROFESIONAL]: { label: "Profesional", emoji: "💼" },
    [TonoRespuesta.AMIGABLE]: { label: "Amigable", emoji: "😊" },
    [TonoRespuesta.FORMAL]: { label: "Formal", emoji: "🎩" },
    [TonoRespuesta.URGENTE]: { label: "Urgente", emoji: "⚡" }
};

export const INTENCION_LABELS: Record<IntencionCliente, { label: string; emoji: string }> = {
    [IntencionCliente.QUEJA]: { label: "Queja", emoji: "😤" },
    [IntencionCliente.CONSULTA]: { label: "Consulta", emoji: "💬" },
    [IntencionCliente.AGRADECIMIENTO]: { label: "Agradecimiento", emoji: "🙏" },
    [IntencionCliente.URGENCIA]: { label: "Urgencia", emoji: "🚨" },
    [IntencionCliente.CANCELACION]: { label: "Cancelación", emoji: "❌" },
    [IntencionCliente.CONFIRMACION]: { label: "Confirmación", emoji: "✅" },
    [IntencionCliente.OTRO]: { label: "Otro", emoji: "📝" }
};

export const ESTADO_QR_LABELS: Record<EstadoQR, { label: string; color: string }> = {
    [EstadoQR.PENDIENTE]: { label: "Pendiente", color: "yellow" },
    [EstadoQR.ESCANEADO]: { label: "Escaneado", color: "blue" },
    [EstadoQR.CONECTADO]: { label: "Conectado", color: "green" },
    [EstadoQR.DESCONECTADO]: { label: "Desconectado", color: "gray" },
    [EstadoQR.EXPIRADO]: { label: "Expirado", color: "red" },
    [EstadoQR.ERROR]: { label: "Error", color: "red" }
};
