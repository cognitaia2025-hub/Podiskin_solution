-- ============================================================================ 
-- Script: 10_catalogo_servicios.sql
-- Descripción: Catálogo dinámico de servicios/tratamientos para administración de precios
-- Dependencias: Ninguna
-- ============================================================================

CREATE TABLE IF NOT EXISTS catalogo_servicios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10,2) NOT NULL,
    duracion_minutos INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_catalogo_servicios_activo ON catalogo_servicios(activo);
CREATE INDEX IF NOT EXISTS idx_catalogo_servicios_nombre ON catalogo_servicios(nombre);
