-- ============================================================================
-- Archivo: 00_inicializacion.sql
-- Descripción: Preparación inicial del entorno de base de datos
-- ============================================================================

-- Habilitar la extensión pgvector para búsquedas semánticas
-- Nota: Requiere que la imagen de Docker tenga pgvector instalado (ej: pgvector/pgvector:pg16)
CREATE EXTENSION IF NOT EXISTS vector;
