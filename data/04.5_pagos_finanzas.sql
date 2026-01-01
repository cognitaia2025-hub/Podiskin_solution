-- ============================================================================
-- Archivo: 04.5_pagos_finanzas.sql
-- Descripción: Tablas de gestión financiera (gastos, cortes de caja, facturas)
-- Dependencias: 02_usuarios.sql, 04_citas_tratamientos.sql
-- Nota: Este archivo va entre 04 y 05 en el orden de ejecución
-- ============================================================================

-- ============================================================================
-- TABLA: gastos
-- Descripción: Registro de gastos operativos del consultorio
-- ============================================================================

CREATE TABLE gastos (
    id bigint NOT NULL,
    categoria text NOT NULL CHECK (categoria IN (
        'Renta', 'Servicios', 'Insumos', 'Marketing', 
        'Mantenimiento', 'Capacitacion', 'Papeleria', 
        'Limpieza', 'Varios'
    )),
    concepto text NOT NULL,
    monto numeric(10,2) NOT NULL,
    fecha_gasto timestamp without time zone NOT NULL,
    metodo_pago text NOT NULL CHECK (metodo_pago IN (
        'Efectivo', 'Transferencia', 'Tarjeta_Debito', 
        'Tarjeta_Credito', 'Cheque'
    )),
    factura_disponible boolean DEFAULT false,
    folio_factura text,
    registrado_por bigint,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE gastos ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME gastos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- TABLA: cortes_caja
-- Descripción: Cierres diarios de caja con resumen de ingresos y gastos
-- ============================================================================

CREATE TABLE cortes_caja (
    id bigint NOT NULL,
    fecha_corte date NOT NULL,
    ingresos_efectivo numeric(10,2) DEFAULT 0,
    ingresos_tarjeta numeric(10,2) DEFAULT 0,
    ingresos_transferencia numeric(10,2) DEFAULT 0,
    total_ingresos numeric(10,2) DEFAULT 0,
    gastos_dia numeric(10,2) DEFAULT 0,
    saldo_final numeric(10,2) DEFAULT 0,
    realizado_por bigint,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE cortes_caja ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME cortes_caja_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- TABLA: facturas
-- Descripción: Facturación fiscal CFDI (Comprobante Fiscal Digital por Internet)
-- ============================================================================

CREATE TABLE facturas (
    id bigint NOT NULL,
    id_pago bigint,
    folio_fiscal text NOT NULL,
    serie text,
    folio integer,
    rfc_emisor text NOT NULL,
    rfc_receptor text NOT NULL,
    nombre_receptor text,
    uso_cfdi text DEFAULT 'G03', -- G03=Gastos en general, G01=Adquisición de mercancías, P01=Por definir
    metodo_pago text NOT NULL, -- Clave SAT: '01'=Efectivo, '04'=Tarjeta de crédito, '03'=Transferencia
    forma_pago text NOT NULL, -- Descripción: 'Efectivo', 'Tarjeta de crédito', 'Transferencia'
    subtotal numeric(10,2) NOT NULL,
    iva numeric(10,2) NOT NULL,
    total numeric(10,2) NOT NULL,
    fecha_emision timestamp without time zone NOT NULL,
    fecha_timbrado timestamp without time zone,
    uuid_sat text,
    estado_factura text DEFAULT 'Vigente' CHECK (estado_factura IN (
        'Vigente', 'Cancelada', 'Pendiente_Timbrado'
    )),
    xml_url text,
    pdf_url text,
    generado_por bigint,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE facturas ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME facturas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CONSTRAINTS
-- ============================================================================

ALTER TABLE ONLY gastos
    ADD CONSTRAINT gastos_pkey PRIMARY KEY (id);

ALTER TABLE ONLY cortes_caja
    ADD CONSTRAINT cortes_caja_pkey PRIMARY KEY (id);

ALTER TABLE ONLY cortes_caja
    ADD CONSTRAINT cortes_caja_fecha_corte_key UNIQUE (fecha_corte);

ALTER TABLE ONLY facturas
    ADD CONSTRAINT facturas_pkey PRIMARY KEY (id);

ALTER TABLE ONLY facturas
    ADD CONSTRAINT facturas_folio_fiscal_key UNIQUE (folio_fiscal);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_gastos_categoria ON gastos USING btree (categoria);
CREATE INDEX idx_gastos_fecha ON gastos USING btree (fecha_gasto DESC);
CREATE INDEX idx_gastos_registrado_por ON gastos USING btree (registrado_por);
CREATE INDEX idx_gastos_metodo_pago ON gastos USING btree (metodo_pago);

CREATE INDEX idx_cortes_caja_fecha ON cortes_caja USING btree (fecha_corte DESC);
CREATE INDEX idx_cortes_caja_realizado_por ON cortes_caja USING btree (realizado_por);

CREATE INDEX idx_facturas_id_pago ON facturas USING btree (id_pago);
CREATE INDEX idx_facturas_rfc_receptor ON facturas USING btree (rfc_receptor);
CREATE INDEX idx_facturas_fecha_emision ON facturas USING btree (fecha_emision DESC);
CREATE INDEX idx_facturas_estado ON facturas USING btree (estado_factura);
CREATE INDEX idx_facturas_uuid_sat ON facturas USING btree (uuid_sat);

-- ============================================================================
-- FOREIGN KEYS
-- ============================================================================

ALTER TABLE ONLY gastos
    ADD CONSTRAINT gastos_registrado_por_fkey FOREIGN KEY (registrado_por) REFERENCES usuarios(id);

ALTER TABLE ONLY cortes_caja
    ADD CONSTRAINT cortes_caja_realizado_por_fkey FOREIGN KEY (realizado_por) REFERENCES usuarios(id);

ALTER TABLE ONLY facturas
    ADD CONSTRAINT facturas_id_pago_fkey FOREIGN KEY (id_pago) REFERENCES pagos(id);

ALTER TABLE ONLY facturas
    ADD CONSTRAINT facturas_generado_por_fkey FOREIGN KEY (generado_por) REFERENCES usuarios(id);
