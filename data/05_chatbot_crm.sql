-- ============================================================================
-- Archivo: tablas_chatbot_crm.sql
-- Descripción: Tablas de chatbot, CRM y mensajería (sin schemas explícitos)
-- Para usar con database.build
-- ============================================================================

CREATE TABLE contactos (
    id bigint NOT NULL,
    whatsapp_id text,
    telegram_id text,
    facebook_id text,
    nombre text,
    telefono text,
    email text,
    tipo text DEFAULT 'Prospecto'::text,
    id_paciente bigint,
    origen text,
    utm_source text,
    utm_campaign text,
    activo boolean DEFAULT true,
    bloqueado boolean DEFAULT false,
    acepto_terminos boolean DEFAULT false,
    fecha_primer_contacto timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_interaccion timestamp without time zone,
    creado_por bigint,
    CONSTRAINT contactos_tipo_check CHECK ((tipo = ANY (ARRAY['Prospecto'::text, 'Lead_Calificado'::text, 'Paciente_Convertido'::text])))
);

ALTER TABLE contactos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME contactos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE conversaciones (
    id bigint NOT NULL,
    id_contacto bigint NOT NULL,
    canal text NOT NULL,
    estado text DEFAULT 'Activa'::text,
    categoria text,
    intencion_detectada text,
    confianza_intencion numeric(3,2),
    entidades_extraidas jsonb,
    asunto text,
    prioridad text DEFAULT 'Media'::text,
    asignado_a bigint,
    id_cita_relacionada bigint,
    fecha_inicio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre timestamp without time zone,
    fecha_ultima_actividad timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    tiempo_primera_respuesta_segundos integer,
    tiempo_resolucion_minutos integer,
    numero_mensajes integer DEFAULT 0,
    numero_mensajes_bot integer DEFAULT 0,
    numero_mensajes_humano integer DEFAULT 0,
    calificacion integer,
    comentario_calificacion text,
    CONSTRAINT conversaciones_calificacion_check CHECK (((calificacion >= 1) AND (calificacion <= 5))),
    CONSTRAINT conversaciones_canal_check CHECK ((canal = ANY (ARRAY['whatsapp'::text, 'telegram'::text, 'facebook'::text, 'web'::text, 'sms'::text]))),
    CONSTRAINT conversaciones_categoria_check CHECK ((categoria = ANY (ARRAY['Informacion_General'::text, 'Agendar_Cita'::text, 'Modificar_Cita'::text, 'Cancelar_Cita'::text, 'Consulta_Precios'::text, 'Consulta_Medica'::text, 'Queja'::text, 'Sugerencia'::text, 'Soporte_Tecnico'::text, 'Otro'::text]))),
    CONSTRAINT conversaciones_estado_check CHECK ((estado = ANY (ARRAY['Activa'::text, 'Esperando_Bot'::text, 'Esperando_Humano'::text, 'Resuelta'::text, 'Abandonada'::text, 'Cerrada'::text]))),
    CONSTRAINT conversaciones_prioridad_check CHECK ((prioridad = ANY (ARRAY['Baja'::text, 'Media'::text, 'Alta'::text, 'Urgente'::text])))
);

ALTER TABLE conversaciones ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME conversaciones_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE mensajes (
    id bigint NOT NULL,
    id_conversacion bigint NOT NULL,
    direccion text NOT NULL,
    enviado_por_tipo text NOT NULL,
    enviado_por_usuario bigint,
    tipo_contenido text DEFAULT 'Texto'::text,
    contenido text NOT NULL,
    url_archivo text,
    mime_type text,
    tamanio_bytes bigint,
    mensaje_id_externo text,
    respuesta_a_mensaje_id bigint,
    estado_entrega text DEFAULT 'Enviado'::text,
    fecha_envio timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega timestamp without time zone,
    fecha_lectura timestamp without time zone,
    procesado_por_bot boolean DEFAULT false,
    sentimiento text,
    idioma_detectado text,
    requiere_atencion_humana boolean DEFAULT false,
    metadata jsonb,
    CONSTRAINT mensajes_direccion_check CHECK ((direccion = ANY (ARRAY['Entrante'::text, 'Saliente'::text]))),
    CONSTRAINT mensajes_enviado_por_tipo_check CHECK ((enviado_por_tipo = ANY (ARRAY['Contacto'::text, 'Bot'::text, 'Usuario_Sistema'::text]))),
    CONSTRAINT mensajes_estado_entrega_check CHECK ((estado_entrega = ANY (ARRAY['Enviado'::text, 'Entregado'::text, 'Leido'::text, 'Fallido'::text]))),
    CONSTRAINT mensajes_sentimiento_check CHECK ((sentimiento = ANY (ARRAY['Positivo'::text, 'Neutral'::text, 'Negativo'::text]))),
    CONSTRAINT mensajes_tipo_contenido_check CHECK ((tipo_contenido = ANY (ARRAY['Texto'::text, 'Imagen'::text, 'Video'::text, 'Audio'::text, 'Documento'::text, 'Ubicacion'::text, 'Contacto'::text, 'Sticker'::text, 'Template'::text])))
);

ALTER TABLE mensajes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME mensajes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE etiquetas (
    id bigint NOT NULL,
    nombre text NOT NULL,
    color text,
    descripcion text,
    activo boolean DEFAULT true,
    creado_por bigint
);

ALTER TABLE etiquetas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME etiquetas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE conversacion_etiquetas (
    id_conversacion bigint NOT NULL,
    id_etiqueta bigint NOT NULL,
    asignado_por bigint,
    fecha_asignacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE log_eventos_bot (
    id bigint NOT NULL,
    id_conversacion bigint,
    id_mensaje bigint,
    tipo_evento text NOT NULL,
    nivel text DEFAULT 'info'::text,
    descripcion text,
    datos jsonb,
    fecha_evento timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT log_eventos_bot_nivel_check CHECK ((nivel = ANY (ARRAY['info'::text, 'warning'::text, 'error'::text, 'critical'::text]))),
    CONSTRAINT log_eventos_bot_tipo_evento_check CHECK ((tipo_evento = ANY (ARRAY['mensaje_recibido'::text, 'mensaje_enviado'::text, 'intent_detectado'::text, 'error_procesamiento'::text, 'escalamiento_humano'::text, 'conversacion_cerrada'::text, 'cita_creada'::text, 'webhook_recibido'::text, 'webhook_error'::text])))
);

ALTER TABLE log_eventos_bot ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME log_eventos_bot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE integraciones_webhook (
    id bigint NOT NULL,
    proveedor text NOT NULL,
    nombre text NOT NULL,
    api_key text,
    webhook_url text,
    webhook_secret text,
    configuracion jsonb,
    activo boolean DEFAULT true,
    ultimo_mensaje_recibido timestamp without time zone,
    ultimo_mensaje_enviado timestamp without time zone,
    mensajes_enviados_hoy integer DEFAULT 0,
    cuota_diaria integer,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT integraciones_webhook_proveedor_check CHECK ((proveedor = ANY (ARRAY['whatsapp_business'::text, 'telegram_bot'::text, 'facebook_messenger'::text, 'twilio'::text, 'custom'::text])))
);

ALTER TABLE integraciones_webhook ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME integraciones_webhook_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE plantillas_mensajes (
    id bigint NOT NULL,
    nombre text NOT NULL,
    categoria text NOT NULL,
    contenido text NOT NULL,
    variables jsonb,
    canal text,
    tipo_contenido text DEFAULT 'Texto'::text,
    url_archivo text,
    activo boolean DEFAULT true,
    requiere_aprobacion boolean DEFAULT false,
    descripcion text,
    ejemplo_uso text,
    creado_por bigint,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    modificado_por bigint,
    fecha_modificacion timestamp without time zone,
    veces_usado integer DEFAULT 0,
    tasa_respuesta numeric(5,2),
    CONSTRAINT plantillas_mensajes_canal_check CHECK ((canal = ANY (ARRAY['whatsapp'::text, 'telegram'::text, 'facebook'::text, 'sms'::text, 'email'::text, 'todos'::text]))),
    CONSTRAINT plantillas_mensajes_categoria_check CHECK ((categoria = ANY (ARRAY['Bienvenida'::text, 'Confirmacion_Cita'::text, 'Recordatorio_Cita'::text, 'Cancelacion_Cita'::text, 'Informacion_Precios'::text, 'Instrucciones_Pre_Cita'::text, 'Instrucciones_Post_Cita'::text, 'Seguimiento'::text, 'Encuesta_Satisfaccion'::text, 'Promocional'::text, 'Informacion_General'::text, 'Otro'::text]))),
    CONSTRAINT plantillas_mensajes_tipo_contenido_check CHECK ((tipo_contenido = ANY (ARRAY['Texto'::text, 'Imagen'::text, 'Template'::text])))
);

ALTER TABLE plantillas_mensajes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME plantillas_mensajes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE respuestas_automaticas (
    id bigint NOT NULL,
    tipo_trigger text NOT NULL,
    trigger_valor text,
    condiciones jsonb,
    mensaje text NOT NULL,
    id_plantilla bigint,
    acciones jsonb,
    prioridad integer DEFAULT 0,
    activo boolean DEFAULT true,
    solo_primera_vez boolean DEFAULT false,
    nombre text NOT NULL,
    descripcion text,
    veces_activada integer DEFAULT 0,
    tasa_exito numeric(5,2),
    creado_por bigint,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT respuestas_automaticas_tipo_trigger_check CHECK ((tipo_trigger = ANY (ARRAY['Palabra_Clave'::text, 'Intencion'::text, 'Horario'::text, 'Primer_Mensaje'::text, 'Inactividad'::text, 'Menu_Opcion'::text, 'Evento_Sistema'::text])))
);

ALTER TABLE respuestas_automaticas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME respuestas_automaticas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_pkey PRIMARY KEY (id);
ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_whatsapp_id_key UNIQUE (whatsapp_id);
ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_telegram_id_key UNIQUE (telegram_id);
ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_facebook_id_key UNIQUE (facebook_id);
ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_id_paciente_key UNIQUE (id_paciente);
ALTER TABLE ONLY conversaciones ADD CONSTRAINT conversaciones_pkey PRIMARY KEY (id);
ALTER TABLE ONLY mensajes ADD CONSTRAINT mensajes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY etiquetas ADD CONSTRAINT etiquetas_pkey PRIMARY KEY (id);
ALTER TABLE ONLY etiquetas ADD CONSTRAINT etiquetas_nombre_key UNIQUE (nombre);
ALTER TABLE ONLY conversacion_etiquetas ADD CONSTRAINT conversacion_etiquetas_pkey PRIMARY KEY (id_conversacion, id_etiqueta);
ALTER TABLE ONLY log_eventos_bot ADD CONSTRAINT log_eventos_bot_pkey PRIMARY KEY (id);
ALTER TABLE ONLY integraciones_webhook ADD CONSTRAINT integraciones_webhook_pkey PRIMARY KEY (id);
ALTER TABLE ONLY plantillas_mensajes ADD CONSTRAINT plantillas_mensajes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY plantillas_mensajes ADD CONSTRAINT plantillas_mensajes_nombre_key UNIQUE (nombre);
ALTER TABLE ONLY respuestas_automaticas ADD CONSTRAINT respuestas_automaticas_pkey PRIMARY KEY (id);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_contactos_activo ON contactos USING btree (activo, bloqueado);
CREATE INDEX idx_contactos_tipo ON contactos USING btree (tipo);
CREATE INDEX idx_contactos_whatsapp ON contactos USING btree (whatsapp_id) WHERE (whatsapp_id IS NOT NULL);
CREATE INDEX idx_contactos_telefono ON contactos USING btree (telefono) WHERE (telefono IS NOT NULL);
CREATE INDEX idx_contactos_paciente ON contactos USING btree (id_paciente) WHERE (id_paciente IS NOT NULL);
CREATE INDEX idx_conversaciones_contacto ON conversaciones USING btree (id_contacto);
CREATE INDEX idx_conversaciones_estado ON conversaciones USING btree (estado, fecha_ultima_actividad DESC);
CREATE INDEX idx_conversaciones_canal ON conversaciones USING btree (canal);
CREATE INDEX idx_conversaciones_categoria ON conversaciones USING btree (categoria);
CREATE INDEX idx_conversaciones_asignado ON conversaciones USING btree (asignado_a) WHERE (asignado_a IS NOT NULL);
CREATE INDEX idx_conversaciones_cita ON conversaciones USING btree (id_cita_relacionada) WHERE (id_cita_relacionada IS NOT NULL);
CREATE INDEX idx_mensajes_conversacion ON mensajes USING btree (id_conversacion, fecha_envio DESC);
CREATE INDEX idx_mensajes_direccion ON mensajes USING btree (direccion, fecha_envio DESC);
CREATE INDEX idx_mensajes_externo ON mensajes USING btree (mensaje_id_externo) WHERE (mensaje_id_externo IS NOT NULL);
CREATE INDEX idx_mensajes_atencion ON mensajes USING btree (requiere_atencion_humana) WHERE (requiere_atencion_humana = true);
CREATE INDEX idx_conv_etiquetas_conv ON conversacion_etiquetas USING btree (id_conversacion);
CREATE INDEX idx_conv_etiquetas_etiq ON conversacion_etiquetas USING btree (id_etiqueta);
CREATE INDEX idx_log_eventos_conversacion ON log_eventos_bot USING btree (id_conversacion) WHERE (id_conversacion IS NOT NULL);
CREATE INDEX idx_log_eventos_fecha ON log_eventos_bot USING btree (fecha_evento DESC);
CREATE INDEX idx_log_eventos_tipo ON log_eventos_bot USING btree (tipo_evento, fecha_evento DESC);
CREATE INDEX idx_plantillas_categoria ON plantillas_mensajes USING btree (categoria, activo);
CREATE INDEX idx_respuestas_trigger ON respuestas_automaticas USING btree (tipo_trigger, activo);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER trigger_actualizar_ultima_actividad AFTER INSERT ON mensajes FOR EACH ROW EXECUTE FUNCTION actualizar_ultima_actividad();

-- ============================================================================
-- FOREIGN KEYS
-- ============================================================================

ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_id_paciente_fkey FOREIGN KEY (id_paciente) REFERENCES pacientes(id);
ALTER TABLE ONLY contactos ADD CONSTRAINT contactos_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY conversaciones ADD CONSTRAINT conversaciones_id_contacto_fkey FOREIGN KEY (id_contacto) REFERENCES contactos(id);
ALTER TABLE ONLY conversaciones ADD CONSTRAINT conversaciones_asignado_a_fkey FOREIGN KEY (asignado_a) REFERENCES usuarios(id);
ALTER TABLE ONLY conversaciones ADD CONSTRAINT conversaciones_id_cita_relacionada_fkey FOREIGN KEY (id_cita_relacionada) REFERENCES citas(id);
ALTER TABLE ONLY mensajes ADD CONSTRAINT mensajes_id_conversacion_fkey FOREIGN KEY (id_conversacion) REFERENCES conversaciones(id) ON DELETE CASCADE;
ALTER TABLE ONLY mensajes ADD CONSTRAINT mensajes_enviado_por_usuario_fkey FOREIGN KEY (enviado_por_usuario) REFERENCES usuarios(id);
ALTER TABLE ONLY mensajes ADD CONSTRAINT mensajes_respuesta_a_mensaje_id_fkey FOREIGN KEY (respuesta_a_mensaje_id) REFERENCES mensajes(id);
ALTER TABLE ONLY etiquetas ADD CONSTRAINT etiquetas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY conversacion_etiquetas ADD CONSTRAINT conversacion_etiquetas_id_conversacion_fkey FOREIGN KEY (id_conversacion) REFERENCES conversaciones(id) ON DELETE CASCADE;
ALTER TABLE ONLY conversacion_etiquetas ADD CONSTRAINT conversacion_etiquetas_id_etiqueta_fkey FOREIGN KEY (id_etiqueta) REFERENCES etiquetas(id);
ALTER TABLE ONLY conversacion_etiquetas ADD CONSTRAINT conversacion_etiquetas_asignado_por_fkey FOREIGN KEY (asignado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY log_eventos_bot ADD CONSTRAINT log_eventos_bot_id_conversacion_fkey FOREIGN KEY (id_conversacion) REFERENCES conversaciones(id);
ALTER TABLE ONLY log_eventos_bot ADD CONSTRAINT log_eventos_bot_id_mensaje_fkey FOREIGN KEY (id_mensaje) REFERENCES mensajes(id);
ALTER TABLE ONLY plantillas_mensajes ADD CONSTRAINT plantillas_mensajes_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY plantillas_mensajes ADD CONSTRAINT plantillas_mensajes_modificado_por_fkey FOREIGN KEY (modificado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY respuestas_automaticas ADD CONSTRAINT respuestas_automaticas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE ONLY respuestas_automaticas ADD CONSTRAINT respuestas_automaticas_id_plantilla_fkey FOREIGN KEY (id_plantilla) REFERENCES plantillas_mensajes(id);
