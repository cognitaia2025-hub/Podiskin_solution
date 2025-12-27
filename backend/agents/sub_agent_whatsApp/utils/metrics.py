"""
Metrics - Sub-Agente WhatsApp
==============================

Sistema de métricas y logging avanzado.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Métricas del agente."""

    # Contadores
    total_messages: int = 0
    total_conversations: int = 0
    successful_responses: int = 0
    failed_responses: int = 0
    escalations_to_human: int = 0

    # Por intención
    intents_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Tiempos
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0
    min_processing_time: float = float("inf")
    max_processing_time: float = 0.0

    # Por nodo
    node_times: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    node_calls: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Errores
    errors_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None

    # Timestamp
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """
    Colector de métricas para el agente.
    """

    def __init__(self):
        self._metrics = AgentMetrics()

    def record_message(self):
        """Registra un mensaje procesado."""
        self._metrics.total_messages += 1
        self._metrics.last_activity = datetime.now()

    def record_conversation(self):
        """Registra una nueva conversación."""
        self._metrics.total_conversations += 1

    def record_intent(self, intent: str):
        """Registra una intención detectada."""
        self._metrics.intents_count[intent] += 1

    def record_success(self):
        """Registra una respuesta exitosa."""
        self._metrics.successful_responses += 1

    def record_failure(self):
        """Registra una respuesta fallida."""
        self._metrics.failed_responses += 1

    def record_escalation(self):
        """Registra un escalamiento a humano."""
        self._metrics.escalations_to_human += 1

    def record_error(self, error_type: str, message: str):
        """Registra un error."""
        self._metrics.errors_count[error_type] += 1
        self._metrics.last_error = message
        self._metrics.last_error_time = datetime.now()
        logger.error(f"[Metrics] Error recorded: {error_type} - {message}")

    def record_processing_time(self, duration: float):
        """Registra tiempo de procesamiento."""
        self._metrics.total_processing_time += duration
        self._metrics.min_processing_time = min(
            self._metrics.min_processing_time, duration
        )
        self._metrics.max_processing_time = max(
            self._metrics.max_processing_time, duration
        )

        # Actualizar promedio
        if self._metrics.total_messages > 0:
            self._metrics.avg_processing_time = (
                self._metrics.total_processing_time / self._metrics.total_messages
            )

    def record_node_time(self, node_name: str, duration: float):
        """Registra tiempo de ejecución de un nodo."""
        self._metrics.node_times[node_name] += duration
        self._metrics.node_calls[node_name] += 1

    @contextmanager
    def measure_time(self, node_name: str = None):
        """
        Context manager para medir tiempo de ejecución.

        Usage:
            with metrics.measure_time("classify_intent"):
                # código a medir
        """
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            if node_name:
                self.record_node_time(node_name, duration)
            else:
                self.record_processing_time(duration)

    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene todas las métricas."""
        m = self._metrics
        uptime = (datetime.now() - m.start_time).total_seconds()

        return {
            "summary": {
                "uptime_seconds": round(uptime, 2),
                "total_messages": m.total_messages,
                "total_conversations": m.total_conversations,
                "success_rate": (
                    round(m.successful_responses / max(m.total_messages, 1) * 100, 2)
                ),
                "escalation_rate": (
                    round(m.escalations_to_human / max(m.total_messages, 1) * 100, 2)
                ),
            },
            "timing": {
                "avg_processing_ms": round(m.avg_processing_time * 1000, 2),
                "min_processing_ms": (
                    round(m.min_processing_time * 1000, 2)
                    if m.min_processing_time != float("inf")
                    else 0
                ),
                "max_processing_ms": round(m.max_processing_time * 1000, 2),
            },
            "intents": dict(m.intents_count),
            "nodes": {
                name: {
                    "total_time_ms": round(m.node_times[name] * 1000, 2),
                    "calls": m.node_calls[name],
                    "avg_time_ms": round(
                        m.node_times[name] / max(m.node_calls[name], 1) * 1000, 2
                    ),
                }
                for name in m.node_times
            },
            "errors": {
                "total": sum(m.errors_count.values()),
                "by_type": dict(m.errors_count),
                "last_error": m.last_error,
                "last_error_time": (
                    m.last_error_time.isoformat() if m.last_error_time else None
                ),
            },
        }

    def get_summary(self) -> str:
        """Obtiene un resumen en texto."""
        m = self.get_metrics()
        return (
            f"📊 Agent Metrics:\n"
            f"  Messages: {m['summary']['total_messages']}\n"
            f"  Success Rate: {m['summary']['success_rate']}%\n"
            f"  Escalation Rate: {m['summary']['escalation_rate']}%\n"
            f"  Avg Processing: {m['timing']['avg_processing_ms']}ms\n"
            f"  Errors: {m['errors']['total']}"
        )

    def reset(self):
        """Reinicia las métricas."""
        self._metrics = AgentMetrics()


# Instancia global
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Obtiene el colector de métricas global."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


def timed_node(node_name: str):
    """
    Decorador para medir tiempo de ejecución de nodos.

    Usage:
        @timed_node("classify_intent")
        async def classify_intent_node(state):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            with collector.measure_time(node_name):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
