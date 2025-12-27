-- ============================================================================
-- Archivo: 12_documentos_impresion.sql
-- Descripción: Sistema de generación e impresión de documentos médicos
-- Incluye: Notas de cobro, historial médico, evoluciones, consentimientos
-- Dependencias: Todos los archivos anteriores
-- ============================================================================

-- ============================================================================
-- PLANTILLAS DE DOCUMENTOS
-- ============================================================================

CREATE TABLE plantillas_documentos (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Identificación
    nombre text NOT NULL,
    tipo_documento text NOT NULL CHECK (tipo_documento IN (
        'Nota_Cobro',              -- Recibo de pago
        'Historial_Medico',        -- Expediente completo
        'Nota_Clinica',            -- Nota de consulta
        'Evolucion_Tratamiento',   -- Seguimiento de tratamiento
        'Consentimiento_Informado',-- Consentimiento para firma
        'Receta_Medica',           -- Prescripción
        'Orden_Estudios',          -- Orden de laboratorio/estudios
        'Referencia_Medica'        -- Referencia a otro especialista
    )),
    
    -- Contenido HTML
    contenido_html text NOT NULL,
    contenido_css text,
    
    -- Variables disponibles (JSON)
    variables_disponibles jsonb,
    -- Ejemplo: {"paciente": ["nombre", "edad", "curp"], "cita": ["fecha", "hora"]}
    
    -- Configuración de impresión
    tamano_papel text DEFAULT 'Letter' CHECK (tamano_papel IN ('Letter', 'A4', 'Legal')),
    orientacion text DEFAULT 'Portrait' CHECK (orientacion IN ('Portrait', 'Landscape')),
    margenes jsonb DEFAULT '{"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"}',
    
    -- Encabezado y pie de página
    incluir_encabezado boolean DEFAULT true,
    incluir_pie_pagina boolean DEFAULT true,
    encabezado_html text,
    pie_pagina_html text,
    
    -- Firmas
    requiere_firma_paciente boolean DEFAULT false,
    requiere_firma_podologo boolean DEFAULT true,
    posicion_firmas jsonb, -- {"paciente": {"x": 100, "y": 700}, "podologo": {"x": 400, "y": 700}}
    
    -- Estado
    version integer DEFAULT 1,
    activo boolean DEFAULT true,
    es_predeterminada boolean DEFAULT false,
    
    -- Auditoría
    creado_por bigint REFERENCES usuarios(id),
    fecha_creacion timestamp DEFAULT NOW(),
    modificado_por bigint REFERENCES usuarios(id),
    fecha_modificacion timestamp
);

CREATE INDEX idx_plantillas_tipo ON plantillas_documentos(tipo_documento, activo);

-- ============================================================================
-- DOCUMENTOS GENERADOS
-- ============================================================================

CREATE TABLE documentos_generados (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Relaciones
    id_plantilla bigint REFERENCES plantillas_documentos(id),
    id_paciente bigint NOT NULL REFERENCES pacientes(id),
    id_cita bigint REFERENCES citas(id),
    id_nota_clinica bigint REFERENCES nota_clinica(id),
    id_consentimiento bigint REFERENCES consentimientos_informados(id),
    
    -- Tipo y propósito
    tipo_documento text NOT NULL,
    proposito text, -- "Archivo físico COFEPRIS", "Entrega a paciente", etc.
    
    -- Contenido generado
    contenido_html text NOT NULL,
    contenido_pdf_url text, -- URL del PDF generado
    hash_documento text, -- SHA-256 para verificar integridad
    
    -- Firmas digitales
    firma_digital_paciente text, -- Base64 de la firma
    firma_digital_podologo text,
    fecha_firma_paciente timestamp,
    fecha_firma_podologo timestamp,
    
    -- Metadatos de firma
    ip_firma_paciente inet,
    ip_firma_podologo inet,
    dispositivo_firma_paciente text,
    dispositivo_firma_podologo text,
    
    -- Impresión física
    impreso boolean DEFAULT false,
    fecha_impresion timestamp,
    impreso_por bigint REFERENCES usuarios(id),
    numero_copias integer DEFAULT 1,
    
    -- Entrega
    entregado_paciente boolean DEFAULT false,
    fecha_entrega timestamp,
    recibido_por text, -- Nombre de quien recibió
    firma_recepcion text, -- Firma de quien recibió
    
    -- Archivo físico
    archivado_fisicamente boolean DEFAULT false,
    ubicacion_archivo_fisico text, -- "Expediente 2024-001, Carpeta A"
    fecha_archivo timestamp,
    
    -- Estado
    estado text DEFAULT 'Generado' CHECK (estado IN (
        'Generado',
        'Firmado_Digital',
        'Impreso',
        'Entregado',
        'Archivado',
        'Anulado'
    )),
    
    -- Auditoría
    generado_por bigint NOT NULL REFERENCES usuarios(id),
    fecha_generacion timestamp DEFAULT NOW(),
    anulado_por bigint REFERENCES usuarios(id),
    fecha_anulacion timestamp,
    motivo_anulacion text
);

CREATE INDEX idx_documentos_paciente ON documentos_generados(id_paciente, tipo_documento);
CREATE INDEX idx_documentos_cita ON documentos_generados(id_cita);
CREATE INDEX idx_documentos_estado ON documentos_generados(estado, fecha_generacion DESC);
CREATE INDEX idx_documentos_pendientes_firma ON documentos_generados(id_paciente) 
WHERE estado = 'Generado' AND (firma_digital_paciente IS NULL OR firma_digital_podologo IS NULL);

-- ============================================================================
-- FUNCIÓN: GENERAR NOTA DE COBRO
-- ============================================================================

CREATE OR REPLACE FUNCTION generar_nota_cobro(
    p_id_pago bigint
) RETURNS bigint AS $$
DECLARE
    v_id_documento bigint;
    v_contenido_html text;
    v_datos jsonb;
BEGIN
    -- Obtener datos del pago
    SELECT jsonb_build_object(
        'folio', p.id,
        'fecha', p.fecha_pago,
        'paciente', jsonb_build_object(
            'nombre', pac.primer_nombre || ' ' || pac.primer_apellido,
            'telefono', pac.telefono_principal
        ),
        'monto_total', p.monto_total,
        'monto_pagado', p.monto_pagado,
        'saldo_pendiente', p.saldo_pendiente,
        'metodo_pago', p.metodo_pago,
        'tratamientos', (
            SELECT jsonb_agg(jsonb_build_object(
                'nombre', t.nombre_servicio,
                'precio', dc.precio_final
            ))
            FROM detalle_cita dc
            JOIN tratamientos t ON dc.id_tratamiento = t.id
            WHERE dc.id_cita = c.id
        )
    ) INTO v_datos
    FROM pagos p
    JOIN citas c ON p.id_cita = c.id
    JOIN pacientes pac ON c.id_paciente = pac.id
    WHERE p.id = p_id_pago;
    
    -- Generar HTML (simplificado, en producción usar plantilla)
    v_contenido_html := format('
        <html>
        <head>
            <style>
                body { font-family: Arial; }
                .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
                .content { margin: 20px; }
                .total { font-size: 18px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PODOSKIN SOLUTION</h1>
                <p>Nota de Cobro #%s</p>
                <p>Fecha: %s</p>
            </div>
            <div class="content">
                <p><strong>Paciente:</strong> %s</p>
                <p><strong>Teléfono:</strong> %s</p>
                <hr>
                <h3>Servicios:</h3>
                %s
                <hr>
                <p class="total">Total: $%s</p>
                <p>Pagado: $%s</p>
                <p>Saldo Pendiente: $%s</p>
                <p><strong>Método de Pago:</strong> %s</p>
            </div>
        </body>
        </html>
    ', 
        v_datos->>'folio',
        v_datos->>'fecha',
        v_datos->'paciente'->>'nombre',
        v_datos->'paciente'->>'telefono',
        '', -- Aquí irían los tratamientos
        v_datos->>'monto_total',
        v_datos->>'monto_pagado',
        v_datos->>'saldo_pendiente',
        v_datos->>'metodo_pago'
    );
    
    -- Insertar documento
    INSERT INTO documentos_generados (
        id_paciente,
        id_cita,
        tipo_documento,
        contenido_html,
        generado_por
    )
    SELECT 
        c.id_paciente,
        p.id_cita,
        'Nota_Cobro',
        v_contenido_html,
        1 -- Usuario sistema
    FROM pagos p
    JOIN citas c ON p.id_cita = c.id
    WHERE p.id = p_id_pago
    RETURNING id INTO v_id_documento;
    
    RETURN v_id_documento;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCIÓN: GENERAR HISTORIAL MÉDICO COMPLETO
-- ============================================================================

CREATE OR REPLACE FUNCTION generar_historial_medico_completo(
    p_id_paciente bigint
) RETURNS bigint AS $$
DECLARE
    v_id_documento bigint;
    v_contenido_html text;
BEGIN
    -- Generar HTML con todos los datos del paciente
    v_contenido_html := format('
        <html>
        <head>
            <style>
                body { font-family: Arial; font-size: 12px; }
                .header { text-align: center; margin-bottom: 20px; }
                .section { margin: 15px 0; page-break-inside: avoid; }
                .section-title { background: #f0f0f0; padding: 5px; font-weight: bold; }
                table { width: 100%%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                .firma-box { border: 1px solid #000; height: 80px; margin-top: 50px; }
                .firma-label { text-align: center; margin-top: 5px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>HISTORIAL MÉDICO COMPLETO</h1>
                <p>Paciente: %s</p>
                <p>Fecha de Generación: %s</p>
            </div>
            
            <div class="section">
                <div class="section-title">DATOS PERSONALES</div>
                <!-- Aquí van los datos del paciente -->
            </div>
            
            <div class="section">
                <div class="section-title">ALERGIAS</div>
                <!-- Tabla de alergias -->
            </div>
            
            <div class="section">
                <div class="section-title">ANTECEDENTES MÉDICOS</div>
                <!-- Tabla de antecedentes -->
            </div>
            
            <div class="section">
                <div class="section-title">HISTORIAL DE CITAS Y TRATAMIENTOS</div>
                <!-- Tabla de citas -->
            </div>
            
            <!-- Firmas -->
            <div style="margin-top: 100px;">
                <div style="float: left; width: 45%%;">
                    <div class="firma-box"></div>
                    <div class="firma-label">Firma del Paciente</div>
                </div>
                <div style="float: right; width: 45%%;">
                    <div class="firma-box"></div>
                    <div class="firma-label">Firma del Podólogo</div>
                </div>
            </div>
        </body>
        </html>
    ',
        (SELECT primer_nombre || ' ' || primer_apellido FROM pacientes WHERE id = p_id_paciente),
        CURRENT_DATE
    );
    
    -- Insertar documento
    INSERT INTO documentos_generados (
        id_paciente,
        tipo_documento,
        contenido_html,
        proposito,
        generado_por
    ) VALUES (
        p_id_paciente,
        'Historial_Medico',
        v_contenido_html,
        'Archivo físico COFEPRIS',
        1
    ) RETURNING id INTO v_id_documento;
    
    RETURN v_id_documento;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCIÓN: GENERAR EVOLUCIÓN DE TRATAMIENTO
-- ============================================================================

CREATE OR REPLACE FUNCTION generar_evolucion_tratamiento(
    p_id_detalle_cita bigint
) RETURNS bigint AS $$
DECLARE
    v_id_documento bigint;
    v_contenido_html text;
BEGIN
    -- Generar HTML con evoluciones del tratamiento
    v_contenido_html := format('
        <html>
        <head>
            <style>
                body { font-family: Arial; }
                .header { text-align: center; }
                table { width: 100%%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #000; padding: 8px; }
                th { background: #f0f0f0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>EVOLUCIÓN DE TRATAMIENTO</h2>
            </div>
            <table>
                <tr>
                    <th>Fase</th>
                    <th>Fecha</th>
                    <th>Descripción</th>
                    <th>Resultado</th>
                </tr>
                <!-- Aquí van las evoluciones -->
            </table>
            
            <div style="margin-top: 100px;">
                <div style="float: right; width: 45%%;">
                    <div style="border: 1px solid #000; height: 80px;"></div>
                    <div style="text-align: center; margin-top: 5px;">Firma del Podólogo</div>
                </div>
            </div>
        </body>
        </html>
    ');
    
    -- Insertar documento
    INSERT INTO documentos_generados (
        id_paciente,
        id_cita,
        tipo_documento,
        contenido_html,
        proposito,
        generado_por
    )
    SELECT 
        c.id_paciente,
        dc.id_cita,
        'Evolucion_Tratamiento',
        v_contenido_html,
        'Archivo físico COFEPRIS',
        1
    FROM detalle_cita dc
    JOIN citas c ON dc.id_cita = c.id
    WHERE dc.id = p_id_detalle_cita
    RETURNING id INTO v_id_documento;
    
    RETURN v_id_documento;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VISTA: DOCUMENTOS PENDIENTES DE FIRMA
-- ============================================================================

CREATE VIEW documentos_pendientes_firma AS
SELECT 
    d.id,
    d.tipo_documento,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre_paciente,
    d.fecha_generacion,
    CASE 
        WHEN d.firma_digital_paciente IS NULL THEN 'Paciente'
        WHEN d.firma_digital_podologo IS NULL THEN 'Podólogo'
        ELSE 'Ambos'
    END AS pendiente_firma,
    EXTRACT(DAY FROM NOW() - d.fecha_generacion) AS dias_pendiente
FROM documentos_generados d
JOIN pacientes p ON d.id_paciente = p.id
WHERE d.estado = 'Generado'
  AND (d.firma_digital_paciente IS NULL OR d.firma_digital_podologo IS NULL)
ORDER BY d.fecha_generacion;

-- ============================================================================
-- VISTA: DOCUMENTOS PENDIENTES DE ARCHIVO FÍSICO
-- ============================================================================

CREATE VIEW documentos_pendientes_archivo AS
SELECT 
    d.id,
    d.tipo_documento,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre_paciente,
    d.fecha_generacion,
    d.impreso,
    d.fecha_impresion,
    d.archivado_fisicamente,
    EXTRACT(DAY FROM NOW() - d.fecha_generacion) AS dias_sin_archivar
FROM documentos_generados d
JOIN pacientes p ON d.id_paciente = p.id
WHERE d.archivado_fisicamente = false
  AND d.tipo_documento IN ('Historial_Medico', 'Evolucion_Tratamiento', 'Consentimiento_Informado')
  AND d.estado != 'Anulado'
ORDER BY d.fecha_generacion;

-- ============================================================================
-- TRIGGER: ACTUALIZAR ESTADO AL FIRMAR
-- ============================================================================

CREATE OR REPLACE FUNCTION actualizar_estado_documento() RETURNS trigger AS $$
BEGIN
    -- Si ambas firmas están presentes
    IF NEW.firma_digital_paciente IS NOT NULL AND NEW.firma_digital_podologo IS NOT NULL THEN
        NEW.estado := 'Firmado_Digital';
    END IF;
    
    -- Si se imprimió
    IF NEW.impreso = true AND OLD.impreso = false THEN
        NEW.estado := 'Impreso';
    END IF;
    
    -- Si se archivó
    IF NEW.archivado_fisicamente = true AND OLD.archivado_fisicamente = false THEN
        NEW.estado := 'Archivado';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_estado_documento
BEFORE UPDATE ON documentos_generados
FOR EACH ROW
EXECUTE FUNCTION actualizar_estado_documento();
