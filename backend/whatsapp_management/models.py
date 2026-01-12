"""
Modelos Pydantic para WhatsApp Management
==========================================

Modelos reutilizables para la gestión de conversaciones de WhatsApp.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS REUTILIZABLES
# ============================================================================


class EstadoQR(str, Enum):
    """Estados posibles de una sesión de QR"""

    PENDIENTE = "pendiente"
    ESCANEADO = "escaneado"
    CONECTADO = "conectado"
    DESCONECTADO = "desconectado"
    EXPIRADO = "expirado"
    ERROR = "error"


class ProveedorMensajeria(str, Enum):
    """Proveedores de mensajería soportados"""

    WHATSAPP_WEB_JS = "whatsapp-web-js"
    TWILIO = "twilio"
    WHATSAPP_BUSINESS_API = "whatsapp-business-api"
    OTRO = "otro"


class TonoCl(str, Enum):
    """Tonos detectados en mensajes de clientes"""

    MOLESTO = "molesto"
    CONTENTO = "contento"
    NEUTRAL = "neutral"
    URGENTE = "urgente"
    CONFUNDIDO = "confundido"
    AGRADECIDO = "agradecido"
    IMPACIENTE = "impaciente"


class IntencionCliente(str, Enum):
    """Intenciones detectadas en mensajes"""

    QUEJA = "queja"
    CONSULTA = "consulta"
    AGRADECIMIENTO = "agradecimiento"
    URGENCIA = "urgencia"
    CANCELACION = "cancelacion"
    CONFIRMACION = "confirmacion"
    OTRO = "otro"


class TonoRespuesta(str, Enum):
    """Tonos sugeridos para respuestas"""

    EMPATICO = "empático"
    PROFESIONAL = "profesional"
    AMIGABLE = "amigable"
    FORMAL = "formal"
    URGENTE = "urgente"


class Sentimiento(str, Enum):
    """Sentimientos detectados"""

    POSITIVO = "positivo"
    NEUTRAL = "neutral"
    NEGATIVO = "negativo"
    URGENTE = "urgente"


class OrigenAprendizaje(str, Enum):
    """Origen de un aprendizaje"""

    ESCALAMIENTO = "escalamiento"
    MANUAL = "manual"
    IMPORTADO = "importado"
    AUTO_APRENDIZAJE = "auto_aprendizaje"


# ============================================================================
# MODELOS BASE REUTILIZABLES
# ============================================================================


class TimestampMixin(BaseModel):
    """Mixin para timestamps comunes"""

    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None


class ContactoInfo(BaseModel):
    """Información del contacto (reutilizable)"""

    id: int
    whatsapp_id: Optional[str] = None
    nombre: str
    telefono: Optional[str] = None
    id_paciente: Optional[int] = None
    es_nuevo_paciente: bool


# ============================================================================
# MODELOS DE QR Y SESIÓN
# ============================================================================


class QRSessionCreate(BaseModel):
    """Payload para crear nueva sesión de QR"""

    proveedor: ProveedorMensajeria = ProveedorMensajeria.WHATSAPP_WEB_JS


class QRSessionInfo(TimestampMixin):
    """Información completa de sesión de QR"""

    id: int
    qr_code: str
    qr_image_url: Optional[str] = None
    estado: EstadoQR
    telefono_conectado: Optional[str] = None
    nombre_dispositivo: Optional[str] = None
    whatsapp_id: Optional[str] = None
    proveedor: ProveedorMensajeria
    fecha_generacion: datetime
    fecha_expiracion: Optional[datetime] = None
    fecha_escaneo: Optional[datetime] = None
    fecha_conexion: Optional[datetime] = None
    fecha_desconexion: Optional[datetime] = None

    class Config:
        use_enum_values = True


class QRSessionUpdate(BaseModel):
    """Actualización de estado de sesión QR"""

    estado: EstadoQR
    telefono_conectado: Optional[str] = None
    nombre_dispositivo: Optional[str] = None
    whatsapp_id: Optional[str] = None


# ============================================================================
# MODELOS DE MENSAJES Y CONVERSACIONES
# ============================================================================


class MensajeItem(BaseModel):
    """Mensaje individual en una conversación"""

    id: int
    direccion: str  # Entrante/Saliente
    enviado_por_tipo: str  # Contacto/Bot/Usuario_Sistema
    contenido: str
    fecha_envio: datetime
    estado_entrega: str
    requiere_atencion_humana: bool = False
    sentimiento: Optional[Sentimiento] = None
    tono: Optional[TonoCl] = None


class ConversacionListItem(BaseModel):
    """Item de lista de conversaciones (vista resumida)"""

    id: int
    contacto_nombre: str
    contacto_telefono: Optional[str] = None
    id_paciente: Optional[int] = None
    es_nuevo_paciente: bool
    ultimo_mensaje: str
    fecha_ultima_actividad: datetime
    requiere_atencion: bool
    numero_mensajes_sin_leer: int
    estado: str


class ConversacionDetalle(BaseModel):
    """Conversación completa con mensajes"""

    id: int
    contacto: ContactoInfo
    canal: str
    estado: str
    categoria: Optional[str] = None
    requiere_atencion: bool
    fecha_inicio: datetime
    fecha_ultima_actividad: datetime
    numero_mensajes: int
    mensajes: List[MensajeItem]
    notas_internas: Optional[str] = None


# ============================================================================
# MODELOS DE ESCALAMIENTO
# ============================================================================


class DudaPendienteItem(BaseModel):
    """Duda escalada pendiente de respuesta"""

    id: int
    paciente_nombre: str
    paciente_telefono: Optional[str] = None
    id_paciente: Optional[int] = None
    duda: str
    contexto: Optional[str] = None
    estado: str
    fecha_creacion: datetime
    id_conversacion: Optional[int] = None
    aprendizaje_generado: bool = False


class RespuestaAdminCreate(BaseModel):
    """Payload para responder una duda"""

    respuesta: str = Field(..., min_length=1)
    generar_aprendizaje: bool = True
    resumen_aprendizaje: Optional[str] = None
    categoria: Optional[str] = None
    tags: Optional[List[str]] = None
    tono_cliente: Optional[TonoCl] = None
    intencion_cliente: Optional[IntencionCliente] = None
    tono_respuesta: Optional[TonoRespuesta] = None


# ============================================================================
# MODELOS DE APRENDIZAJE AVANZADO
# ============================================================================


class AprendizajeAvanzadoCreate(BaseModel):
    """Crear aprendizaje con sistema de dos fases"""

    # Fase 1: Contexto/Trigger
    pregunta_original: str = Field(..., min_length=1, max_length=1000)
    contexto_trigger: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Cuándo aplicar este conocimiento",
    )
    palabras_clave: Optional[List[str]] = Field(None, max_items=20)

    # Fase 2: Respuesta
    respuesta_sugerida: str = Field(
        ..., min_length=1, max_length=2000, description="Qué responder"
    )
    respuesta_admin: str = Field(..., min_length=1, max_length=2000)

    # Análisis de tono
    tono_cliente: Optional[TonoCl] = None
    intencion_cliente: Optional[IntencionCliente] = None
    tono_respuesta: Optional[TonoRespuesta] = None

    # Metadata
    resumen_aprendizaje: Optional[str] = Field(None, max_length=500)
    categoria: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, max_items=10)

    @validator("palabras_clave")
    def validar_palabras_clave(cls, v):
        if v:
            # Limpiar y normalizar palabras clave
            return [palabra.strip().lower() for palabra in v if palabra.strip()]
        return v

    @validator("tags")
    def validar_tags(cls, v):
        if v:
            # Limpiar y normalizar tags
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v


class AprendizajeAvanzadoUpdate(BaseModel):
    """Actualizar aprendizaje existente"""

    contexto_trigger: Optional[str] = Field(None, max_length=2000)
    respuesta_sugerida: Optional[str] = Field(None, max_length=2000)
    resumen_aprendizaje: Optional[str] = Field(None, max_length=500)
    categoria: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, max_items=10)
    palabras_clave: Optional[List[str]] = Field(None, max_items=20)
    tono_cliente: Optional[TonoCl] = None
    intencion_cliente: Optional[IntencionCliente] = None
    tono_respuesta: Optional[TonoRespuesta] = None
    validado: Optional[bool] = None


class AprendizajeAvanzadoItem(TimestampMixin):
    """Item de aprendizaje avanzado (respuesta completa)"""

    id: int
    # Fase 1
    pregunta_original: str
    contexto_trigger: str
    palabras_clave: Optional[List[str]] = None
    # Fase 2
    respuesta_sugerida: str
    respuesta_admin: str
    # Tono
    tono_cliente: Optional[TonoCl] = None
    intencion_cliente: Optional[IntencionCliente] = None
    tono_respuesta: Optional[TonoRespuesta] = None
    # Metadata
    resumen_aprendizaje: str
    categoria: Optional[str] = None
    tags: Optional[List[str]] = None
    veces_utilizado: int
    efectividad: float
    validado: bool
    version: int = 1
    origen: OrigenAprendizaje
    fecha_ultimo_uso: Optional[datetime] = None

    class Config:
        use_enum_values = True


# ============================================================================
# MODELOS DE ANÁLISIS DE SENTIMIENTO
# ============================================================================


class AnalisisSentimiento(BaseModel):
    """Análisis de sentimiento de un mensaje"""

    id: int
    id_mensaje: int
    sentimiento: Sentimiento
    confianza_sentimiento: float = Field(..., ge=0.0, le=1.0)
    tono: TonoCl
    confianza_tono: float = Field(..., ge=0.0, le=1.0)
    intencion: IntencionCliente
    confianza_intencion: float = Field(..., ge=0.0, le=1.0)
    emociones: Optional[Dict[str, float]] = None
    palabras_clave_detectadas: Optional[List[str]] = None
    modelo_utilizado: str = "sentiment-analysis-v1"
    fecha_analisis: datetime

    class Config:
        use_enum_values = True


class AnalisisSentimientoCreate(BaseModel):
    """Payload para crear análisis de sentimiento"""

    id_mensaje: int
    id_conversacion: int
    sentimiento: Sentimiento
    confianza_sentimiento: float = Field(..., ge=0.0, le=1.0)
    tono: TonoCl
    confianza_tono: float = Field(..., ge=0.0, le=1.0)
    intencion: IntencionCliente
    confianza_intencion: float = Field(..., ge=0.0, le=1.0)
    emociones: Optional[Dict[str, float]] = None
    palabras_clave_detectadas: Optional[List[str]] = None


# ============================================================================
# MODELOS DE RESPUESTA AGREGADA
# ============================================================================


class ConversacionesResponse(BaseModel):
    """Respuesta con lista de conversaciones divididas"""

    atendidas: List[ConversacionListItem]
    escaladas: List[DudaPendienteItem]
    total_atendidas: int
    total_escaladas: int


class AprendizajesResponse(BaseModel):
    """Respuesta paginada de aprendizajes"""

    aprendizajes: List[AprendizajeAvanzadoItem]
    total: int
    page: int
    per_page: int
    total_pages: int


class EstadisticasAprendizaje(BaseModel):
    """Estadísticas de aprendizajes"""

    total_aprendizajes: int
    aprendizajes_validados: int
    aprendizajes_efectivos: int  # efectividad >= 0.6
    promedio_efectividad: float
    categorias: Dict[str, int]
    tonos_mas_comunes: Dict[str, int]


class ConversacionConSentimiento(BaseModel):
    """Conversación con análisis de sentimiento agregado"""

    conversacion: ConversacionDetalle
    sentimiento_general: Sentimiento
    tonos_predominantes: List[TonoCl]
    requiere_atencion_especial: bool
    analisis_mensajes: List[AnalisisSentimiento]


# ============================================================================
# MODELOS DE BÚSQUEDA
# ============================================================================


class BusquedaSemanticaRequest(BaseModel):
    """Request para búsqueda semántica de aprendizajes"""

    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(5, ge=1, le=20)
    categoria: Optional[str] = None
    solo_validados: bool = True
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Umbral de similitud")


class BusquedaSemanticaResult(BaseModel):
    """Resultado de búsqueda semántica"""

    aprendizaje: AprendizajeAvanzadoItem
    similitud: float = Field(..., ge=0.0, le=1.0)
    relevancia: str  # alta, media, baja


class BusquedaSemanticaResponse(BaseModel):
    """Respuesta de búsqueda semántica"""

    query: str
    resultados: List[BusquedaSemanticaResult]
    total_encontrados: int
