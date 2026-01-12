"""
Configuración del Agente WhatsApp
=================================

Configura el checkpointer de Postgres, LLM y embedder local.
"""

import os
import logging
from sqlalchemy import create_engine
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_anthropic import ChatAnthropic
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "podoskin_db")
DB_USER = os.getenv("DB_USER", "podoskin_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")

# URL de conexión para psycopg (usado por PostgresSaver)
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Determinar entorno (producción vs desarrollo)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Inicializar checkpointer
if ENVIRONMENT == "production":
    logger.info("✅ Usando PostgresSaver (persistente)")
    try:
        # PostgresSaver.from_conn_string retorna un context manager
        # Necesitamos usar __enter__ para obtener la instancia
        conn_string = DB_URL
        checkpointer_cm = PostgresSaver.from_conn_string(conn_string)
        checkpointer = checkpointer_cm.__enter__()
        # Setup crea la tabla langgraph_checkpoints si no existe
        checkpointer.setup()
        logger.info("✅ PostgresSaver initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize PostgresSaver: {e}")
        logger.warning("⚠️ Fallback: usando MemorySaver (no persistente)")
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()
else:
    logger.info("⚠️ Usando MemorySaver (desarrollo, no persistente)")
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()

# Configurar LLM (Claude Haiku 3 - rápido y económico)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-haiku-20240307")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

if not ANTHROPIC_API_KEY:
    logger.warning("⚠️ ANTHROPIC_API_KEY not found in environment")

llm = ChatAnthropic(
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    max_tokens=500,
    anthropic_api_key=ANTHROPIC_API_KEY,
)

logger.info(f"✅ LLM configured: {LLM_MODEL} (temp={LLM_TEMPERATURE})")

# Configurar Embedder Local (all-MiniLM-L6-v2)
# Ligero (80MB), rápido en CPU, 384 dimensiones
try:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("✅ Embedder loaded: all-MiniLM-L6-v2 (384 dims)")
except Exception as e:
    logger.error(f"❌ Failed to load embedder: {e}")
    embedder = None
