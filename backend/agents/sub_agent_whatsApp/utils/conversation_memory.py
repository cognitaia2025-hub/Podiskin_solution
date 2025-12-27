"""
Conversation Memory - Sub-Agente WhatsApp
==========================================

Gestión de memoria y contexto de conversaciones.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .database import fetch, fetchrow, execute

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Contexto de una conversación."""

    conversation_id: int
    contact_id: int
    patient_id: Optional[int] = None
    messages: List[Dict] = field(default_factory=list)
    intents_history: List[str] = field(default_factory=list)
    entities_collected: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    session_start: datetime = field(default_factory=datetime.now)


class ConversationMemory:
    """
    Gestiona la memoria de conversaciones para mantener contexto.
    """

    def __init__(self, max_messages: int = 10, session_timeout_minutes: int = 30):
        self.max_messages = max_messages
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._contexts: Dict[int, ConversationContext] = {}

    async def get_context(
        self, conversation_id: int, contact_id: int
    ) -> ConversationContext:
        """
        Obtiene o crea el contexto de una conversación.

        Args:
            conversation_id: ID de la conversación
            contact_id: ID del contacto

        Returns:
            Contexto de la conversación
        """
        # Verificar si existe en caché y está activo
        if conversation_id in self._contexts:
            ctx = self._contexts[conversation_id]
            if datetime.now() - ctx.last_activity < self.session_timeout:
                ctx.last_activity = datetime.now()
                return ctx

        # Crear nuevo contexto
        ctx = ConversationContext(
            conversation_id=conversation_id, contact_id=contact_id
        )

        # Cargar mensajes recientes de BD
        await self._load_recent_messages(ctx)

        # Verificar si es paciente
        patient = await fetchrow(
            "SELECT id FROM pacientes WHERE id_contacto = %s", contact_id
        )
        if patient:
            ctx.patient_id = patient["id"]

        self._contexts[conversation_id] = ctx
        return ctx

    async def _load_recent_messages(self, ctx: ConversationContext):
        """Carga mensajes recientes de la BD."""
        try:
            messages = await fetch(
                """
                SELECT rol, contenido, fecha_envio
                FROM mensajes
                WHERE id_conversacion = %s
                ORDER BY fecha_envio DESC
                LIMIT %s
                """,
                ctx.conversation_id,
                self.max_messages,
            )

            # Invertir para orden cronológico
            ctx.messages = [
                {
                    "role": m["rol"],
                    "content": m["contenido"],
                    "timestamp": m["fecha_envio"].isoformat(),
                }
                for m in reversed(messages)
            ]

        except Exception as e:
            logger.error(f"Error loading messages: {e}")

    def add_message(self, conversation_id: int, role: str, content: str):
        """
        Añade un mensaje al contexto.

        Args:
            conversation_id: ID de la conversación
            role: Rol (user/assistant)
            content: Contenido del mensaje
        """
        if conversation_id not in self._contexts:
            return

        ctx = self._contexts[conversation_id]
        ctx.messages.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

        # Mantener límite de mensajes
        if len(ctx.messages) > self.max_messages:
            ctx.messages = ctx.messages[-self.max_messages :]

        ctx.last_activity = datetime.now()

    def add_intent(self, conversation_id: int, intent: str):
        """Registra una intención detectada."""
        if conversation_id in self._contexts:
            self._contexts[conversation_id].intents_history.append(intent)

    def add_entity(self, conversation_id: int, key: str, value: Any):
        """Añade una entidad extraída al contexto."""
        if conversation_id in self._contexts:
            self._contexts[conversation_id].entities_collected[key] = value

    def get_entity(self, conversation_id: int, key: str, default: Any = None) -> Any:
        """Obtiene una entidad del contexto."""
        if conversation_id in self._contexts:
            return self._contexts[conversation_id].entities_collected.get(key, default)
        return default

    def get_messages_for_llm(
        self, conversation_id: int, max_messages: int = 5
    ) -> List[Dict[str, str]]:
        """
        Obtiene mensajes formateados para el LLM.

        Args:
            conversation_id: ID de la conversación
            max_messages: Número máximo de mensajes

        Returns:
            Lista de mensajes en formato LLM
        """
        if conversation_id not in self._contexts:
            return []

        messages = self._contexts[conversation_id].messages[-max_messages:]
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    def get_summary(self, conversation_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen del contexto de conversación.

        Args:
            conversation_id: ID de la conversación

        Returns:
            Resumen del contexto
        """
        if conversation_id not in self._contexts:
            return {"active": False}

        ctx = self._contexts[conversation_id]
        return {
            "active": True,
            "message_count": len(ctx.messages),
            "intents": ctx.intents_history[-5:],
            "entities": ctx.entities_collected,
            "patient_id": ctx.patient_id,
            "session_duration": (datetime.now() - ctx.session_start).total_seconds(),
        }

    def clear_context(self, conversation_id: int):
        """Limpia el contexto de una conversación."""
        if conversation_id in self._contexts:
            del self._contexts[conversation_id]

    def cleanup_expired(self):
        """Limpia contextos expirados."""
        now = datetime.now()
        expired = [
            cid
            for cid, ctx in self._contexts.items()
            if now - ctx.last_activity > self.session_timeout
        ]
        for cid in expired:
            del self._contexts[cid]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired contexts")


# Instancia global
_memory: Optional[ConversationMemory] = None


def get_conversation_memory() -> ConversationMemory:
    """Obtiene la instancia global de ConversationMemory."""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
