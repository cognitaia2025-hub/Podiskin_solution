-- ============================================================================
-- Archivo: 09_inventario_materiales.sql
-- Descripción: Control de inventario de materiales médicos y productos
-- Dependencias: 02_usuarios.sql, 04_citas_tratamientos.sql
-- ============================================================================

-- ============================================================================
-- CATÁLOGO DE PROVEEDORES
-- ============================================================================

CREATE TABLE proveedores (
    id bigint NOT NULL,
    nombre_comercial text NOT NULL,
    razon_social text,
    rfc text,
    tipo_proveedor text,
    telefono text,
    email text,
    direccion text,
    ciudad text,
    estado text,
    codigo_postal text,
    contacto_principal text,
    dias_credito integer DEFAULT 0,
    activo boolean DEFAULT true,
    notas text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE proveedores ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME proveedores_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

-- ============================================================================
-- CATÁLOGO DE PRODUCTOS E INVENTARIO
-- ============================================================================

CREATE TABLE inventario_productos (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    
    -- Identificación
    codigo_producto text UNIQUE NOT NULL,
    codigo_barras text,
    nombre text NOT NULL,
    descripcion text,
    
    -- Categorización
    categoria text NOT NULL CHECK (categoria IN (
        'Material_Curacion',      -- Gasas, vendas, algodón
        'Instrumental',           -- Tijeras, pinzas, bisturí
        'Medicamento',            -- Antibióticos, analgésicos
        'Consumible',             -- Guantes, cubrebocas, jeringas
        'Equipo_Medico',          -- Autoclave, lámpara, etc.
        'Producto_Venta',         -- Cremas, plantillas ortopédicas
        'Material_Limpieza',      -- Desinfectantes, jabones
        'Papeleria'               -- Recetas, formatos
    )),
    subcategoria text,
    
    -- Stock
    stock_actual integer DEFAULT 0,
    stock_minimo integer DEFAULT 5,
    stock_maximo integer DEFAULT 100,
    unidad_medida text NOT NULL, -- 'pieza', 'caja', 'litro', 'kilogramo', 'paquete'
    
    -- Costos y precios
    costo_unitario numeric(10,2),
    precio_venta numeric(10,2),
    margen_ganancia numeric(5,2), -- Porcentaje
    
    -- Proveedor
    id_proveedor bigint,
    tiempo_reposicion_dias integer DEFAULT 7,
    
    -- Control especial
    requiere_receta boolean DEFAULT false,
    controlado boolean DEFAULT false, -- Medicamentos controlados
    
    -- Caducidad
    tiene_caducidad boolean DEFAULT false,
    fecha_caducidad date,
    lote text,
    
    -- Ubicación física
    ubicacion_almacen text, -- "Estante A, Nivel 2"
    
    -- Estado
    activo boolean DEFAULT true,
    fecha_registro timestamp DEFAULT NOW(),
    registrado_por bigint REFERENCES usuarios(id)
);

CREATE INDEX idx_inventario_categoria ON inventario_productos(categoria, activo);
CREATE INDEX idx_inventario_codigo ON inventario_productos(codigo_producto);
CREATE INDEX idx_inventario_stock_bajo ON inventario_productos(stock_actual, stock_minimo) 
WHERE stock_actual <= stock_minimo AND activo = true;
CREATE INDEX idx_inventario_proveedor ON inventario_productos(id_proveedor);

-- ============================================================================
-- CONSTRAINTS Y FOREIGN KEYS PARA PROVEEDORES E INVENTARIO
-- ============================================================================

ALTER TABLE ONLY proveedores
    ADD CONSTRAINT proveedores_pkey PRIMARY KEY (id);

CREATE INDEX idx_proveedores_nombre ON proveedores USING btree (nombre_comercial);
CREATE INDEX idx_proveedores_activo ON proveedores USING btree (activo);
CREATE INDEX idx_proveedores_tipo ON proveedores USING btree (tipo_proveedor);

ALTER TABLE ONLY inventario_productos
    ADD CONSTRAINT inventario_productos_id_proveedor_fkey FOREIGN KEY (id_proveedor) REFERENCES proveedores(id);

-- ============================================================================
-- MOVIMIENTOS DE INVENTARIO
-- ============================================================================

CREATE TABLE movimientos_inventario (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_producto bigint NOT NULL REFERENCES inventario_productos(id),
    
    -- Tipo de movimiento
    tipo_movimiento text NOT NULL CHECK (tipo_movimiento IN (
        'Entrada',          -- Compra o donación
        'Salida',           -- Uso en consulta
        'Ajuste_Positivo',  -- Corrección de inventario
        'Ajuste_Negativo',  -- Corrección de inventario
        'Merma',            -- Producto caducado o dañado
        'Devolucion',       -- Devolución a proveedor
        'Traspaso'          -- Entre ubicaciones
    )),
    
    -- Cantidad
    cantidad integer NOT NULL,
    stock_anterior integer NOT NULL,
    stock_nuevo integer NOT NULL,
    
    -- Costos (para entradas)
    costo_unitario numeric(10,2),
    costo_total numeric(10,2),
    
    -- Relaciones
    id_cita bigint REFERENCES citas(id),
    id_tratamiento bigint REFERENCES tratamientos(id),
    
    -- Detalles
    motivo text NOT NULL,
    numero_factura_proveedor text, -- Para entradas
    
    -- Caducidad (para entradas)
    lote text,
    fecha_caducidad date,
    
    -- Auditoría
    registrado_por bigint NOT NULL REFERENCES usuarios(id),
    fecha_movimiento timestamp DEFAULT NOW()
);

CREATE INDEX idx_movimientos_producto ON movimientos_inventario(id_producto, fecha_movimiento DESC);
CREATE INDEX idx_movimientos_tipo ON movimientos_inventario(tipo_movimiento, fecha_movimiento DESC);
CREATE INDEX idx_movimientos_cita ON movimientos_inventario(id_cita) WHERE id_cita IS NOT NULL;

-- ============================================================================
-- RELACIÓN TRATAMIENTO-PRODUCTO (Receta de materiales)
-- ============================================================================

CREATE TABLE tratamiento_materiales (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    id_tratamiento bigint NOT NULL REFERENCES tratamientos(id),
    id_producto bigint NOT NULL REFERENCES inventario_productos(id),
    
    cantidad_requerida numeric(10,2) DEFAULT 1,
    es_opcional boolean DEFAULT false,
    
    notas text,
    activo boolean DEFAULT true
);

CREATE INDEX idx_tratamiento_materiales ON tratamiento_materiales(id_tratamiento);

-- ============================================================================
-- TRIGGER: ACTUALIZAR STOCK AUTOMÁTICAMENTE
-- ============================================================================

CREATE OR REPLACE FUNCTION actualizar_stock_inventario() RETURNS trigger AS $$
BEGIN
    -- Calcular nuevo stock
    NEW.stock_nuevo := NEW.stock_anterior + 
        CASE 
            WHEN NEW.tipo_movimiento IN ('Entrada', 'Ajuste_Positivo', 'Devolucion') THEN NEW.cantidad
            WHEN NEW.tipo_movimiento IN ('Salida', 'Ajuste_Negativo', 'Merma') THEN -NEW.cantidad
            ELSE 0
        END;
    
    -- Actualizar stock en tabla de productos
    UPDATE inventario_productos
    SET stock_actual = NEW.stock_nuevo
    WHERE id = NEW.id_producto;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_stock
BEFORE INSERT ON movimientos_inventario
FOR EACH ROW
EXECUTE FUNCTION actualizar_stock_inventario();

-- ============================================================================
-- TRIGGER: DESCONTAR MATERIALES AL COMPLETAR CITA
-- ============================================================================

CREATE OR REPLACE FUNCTION descontar_materiales_cita() RETURNS trigger AS $$
DECLARE
    v_material RECORD;
BEGIN
    -- Solo cuando cambia a estado Completada
    IF NEW.estado = 'Completada' AND OLD.estado != 'Completada' THEN
        
        -- Obtener materiales del tratamiento
        FOR v_material IN
            SELECT 
                tm.id_producto,
                tm.cantidad_requerida,
                p.nombre,
                p.stock_actual
            FROM detalle_cita dc
            JOIN tratamiento_materiales tm ON dc.id_tratamiento = tm.id_tratamiento
            JOIN inventario_productos p ON tm.id_producto = p.id
            WHERE dc.id_cita = NEW.id
              AND tm.activo = true
        LOOP
            -- Registrar salida de inventario
            INSERT INTO movimientos_inventario (
                id_producto,
                tipo_movimiento,
                cantidad,
                stock_anterior,
                id_cita,
                motivo,
                registrado_por
            ) VALUES (
                v_material.id_producto,
                'Salida',
                v_material.cantidad_requerida,
                v_material.stock_actual,
                NEW.id,
                'Uso en consulta - ' || v_material.nombre,
                NEW.creado_por
            );
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_descontar_materiales
AFTER UPDATE ON citas
FOR EACH ROW
EXECUTE FUNCTION descontar_materiales_cita();

-- ============================================================================
-- VISTAS DE ANÁLISIS
-- ============================================================================

-- Vista: Productos con stock bajo
CREATE VIEW alertas_stock_bajo AS
SELECT 
    p.id,
    p.codigo_producto,
    p.nombre,
    p.categoria,
    p.stock_actual,
    p.stock_minimo,
    (p.stock_minimo - p.stock_actual) AS cantidad_requerida,
    prov.nombre_comercial AS proveedor,
    prov.telefono AS telefono_proveedor,
    p.tiempo_reposicion_dias,
    p.costo_unitario,
    (p.stock_minimo - p.stock_actual) * p.costo_unitario AS costo_reposicion
FROM inventario_productos p
LEFT JOIN proveedores prov ON p.id_proveedor = prov.id
WHERE p.stock_actual <= p.stock_minimo
  AND p.activo = true
ORDER BY (p.stock_minimo - p.stock_actual) DESC;

-- Vista: Productos próximos a caducar
CREATE VIEW productos_proximos_caducar AS
SELECT 
    p.id,
    p.codigo_producto,
    p.nombre,
    p.lote,
    p.fecha_caducidad,
    p.stock_actual,
    (p.fecha_caducidad - CURRENT_DATE) AS dias_para_caducar,
    p.costo_unitario * p.stock_actual AS valor_inventario
FROM inventario_productos p
WHERE p.tiene_caducidad = true
  AND p.fecha_caducidad IS NOT NULL
  AND p.fecha_caducidad <= CURRENT_DATE + INTERVAL '30 days'
  AND p.stock_actual > 0
  AND p.activo = true
ORDER BY p.fecha_caducidad;

-- Vista: Valor del inventario
CREATE VIEW valor_inventario AS
SELECT 
    categoria,
    COUNT(*) AS total_productos,
    SUM(stock_actual) AS total_unidades,
    SUM(stock_actual * costo_unitario) AS valor_costo,
    SUM(stock_actual * precio_venta) AS valor_venta,
    SUM(stock_actual * precio_venta) - SUM(stock_actual * costo_unitario) AS ganancia_potencial
FROM inventario_productos
WHERE activo = true
GROUP BY categoria
ORDER BY valor_costo DESC;

-- Vista: Productos más usados
CREATE VIEW productos_mas_usados AS
SELECT 
    p.id,
    p.nombre,
    p.categoria,
    COUNT(m.id) AS total_movimientos,
    SUM(m.cantidad) FILTER (WHERE m.tipo_movimiento = 'Salida') AS total_usado,
    AVG(m.cantidad) FILTER (WHERE m.tipo_movimiento = 'Salida') AS promedio_uso,
    MAX(m.fecha_movimiento) AS ultima_salida
FROM inventario_productos p
LEFT JOIN movimientos_inventario m ON p.id = m.id_producto
WHERE m.tipo_movimiento = 'Salida'
  AND m.fecha_movimiento >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.id, p.nombre, p.categoria
ORDER BY total_usado DESC
LIMIT 20;

-- ============================================================================
-- FUNCIÓN: REGISTRAR ENTRADA DE INVENTARIO
-- ============================================================================

CREATE OR REPLACE FUNCTION registrar_entrada_inventario(
    p_id_producto bigint,
    p_cantidad integer,
    p_costo_unitario numeric,
    p_numero_factura text,
    p_lote text DEFAULT NULL,
    p_fecha_caducidad date DEFAULT NULL,
    p_registrado_por bigint DEFAULT NULL
) RETURNS bigint AS $$
DECLARE
    v_stock_actual integer;
    v_id_movimiento bigint;
BEGIN
    -- Obtener stock actual
    SELECT stock_actual INTO v_stock_actual
    FROM inventario_productos
    WHERE id = p_id_producto;
    
    -- Registrar movimiento
    INSERT INTO movimientos_inventario (
        id_producto,
        tipo_movimiento,
        cantidad,
        stock_anterior,
        costo_unitario,
        costo_total,
        motivo,
        numero_factura_proveedor,
        lote,
        fecha_caducidad,
        registrado_por
    ) VALUES (
        p_id_producto,
        'Entrada',
        p_cantidad,
        v_stock_actual,
        p_costo_unitario,
        p_cantidad * p_costo_unitario,
        'Compra a proveedor',
        p_numero_factura,
        p_lote,
        p_fecha_caducidad,
        p_registrado_por
    ) RETURNING id INTO v_id_movimiento;
    
    -- Actualizar lote y caducidad en producto si aplica
    IF p_lote IS NOT NULL THEN
        UPDATE inventario_productos
        SET lote = p_lote,
            fecha_caducidad = p_fecha_caducidad
        WHERE id = p_id_producto;
    END IF;
    
    RETURN v_id_movimiento;
END;
$$ LANGUAGE plpgsql;
