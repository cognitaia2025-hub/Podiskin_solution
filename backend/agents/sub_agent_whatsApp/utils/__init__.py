"""
Utilities - Sub-Agente WhatsApp
================================

Módulo de utilidades del sub-agente.
"""

from .database import (
    init_db_pool,
    close_db_pool,
    get_db_connection,
    fetch,
    fetchrow,
    fetchval,
    execute,
    execute_many,
    execute_transaction,
    get_or_create_contact,
    get_or_create_conversation,
    save_message,
    update_conversation_summary,
    check_db_health,
)

from .embeddings import (
    LocalEmbeddings,
    get_embeddings_service,
    chunk_text,
    preprocess_text,
)

from .sentiment import (
    analyze_sentiment,
    should_escalate_by_sentiment,
    get_response_tone,
    Sentiment,
)

from .conversation_memory import (
    ConversationMemory,
    ConversationContext,
    get_conversation_memory,
)

from .metrics import (
    MetricsCollector,
    get_metrics_collector,
    timed_node,
)

__all__ = [
    # Database
    "init_db_pool",
    "close_db_pool",
    "get_db_connection",
    "fetch",
    "fetchrow",
    "fetchval",
    "execute",
    "execute_many",
    "execute_transaction",
    "get_or_create_contact",
    "get_or_create_conversation",
    "save_message",
    "update_conversation_summary",
    "check_db_health",
    # Embeddings
    "LocalEmbeddings",
    "get_embeddings_service",
    "chunk_text",
    "preprocess_text",
    # Sentiment
    "analyze_sentiment",
    "should_escalate_by_sentiment",
    "get_response_tone",
    "Sentiment",
    # Conversation Memory
    "ConversationMemory",
    "ConversationContext",
    "get_conversation_memory",
    # Metrics
    "MetricsCollector",
    "get_metrics_collector",
    "timed_node",
]
