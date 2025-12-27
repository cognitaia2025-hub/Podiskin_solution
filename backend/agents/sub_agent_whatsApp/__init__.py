"""
Sub-Agente de WhatsApp - Podoskin Solution
===========================================

Este módulo contiene el sub-agente especializado en gestión de conversaciones
de WhatsApp con pacientes. Es completamente independiente y modular.

Responsabilidades:
- Clasificar intenciones de mensajes
- Recuperar contexto semántico (RAG)
- Gestionar agendamiento de citas
- Responder consultas sobre tratamientos
- Escalar a humanos cuando sea necesario

Interacciones externas:
- Consultar disponibilidad de agenda (DB)
- Confirmar citas desde frontend
- Actualizar estado de conversaciones
"""

__version__ = "1.0.0"
__author__ = "Podoskin Development Team"
