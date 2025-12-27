-- Base de Conocimiento con Embeddings (Sin pgvector)
-- ====================================================
-- Solución alternativa: embeddings como BYTEA, búsqueda en Python

CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    
    -- Pregunta y respuesta
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    
    -- Embedding de la pregunta como BYTEA (numpy array serializado)
    -- all-MiniLM-L6-v2 = 384 dimensiones
    pregunta_embedding BYTEA,
    
    -- Metadata
    categoria TEXT,
    veces_consultada INT DEFAULT 0,
    confianza FLOAT DEFAULT 1.0,
    
    -- Timestamps
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP,
    
    -- Origen de la respuesta
    origen TEXT DEFAULT 'admin' CHECK (origen IN ('admin', 'manual', 'auto'))
);

-- Índices
CREATE INDEX IF NOT EXISTS knowledge_base_categoria_idx ON knowledge_base(categoria);
CREATE INDEX IF NOT EXISTS knowledge_base_fecha_idx ON knowledge_base(fecha_creacion DESC);

-- Comentarios
COMMENT ON TABLE knowledge_base IS 'Base de conocimiento con embeddings (búsqueda en Python)';
COMMENT ON COLUMN knowledge_base.pregunta_embedding IS 'Embedding serializado (384 dims, all-MiniLM-L6-v2)';
