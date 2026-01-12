"""
Utilidades de Base de Datos [DEPRECADO]
=======================================

⚠️ DEPRECADO: Este módulo ya no está en uso.
Migrado a pool centralizado en backend/db.py con AsyncPG.

Si necesitas acceso a base de datos, usa:
    from db import get_connection, release_connection
"""

import logging

logger = logging.getLogger(__name__)
logger.warning(
    "DEPRECADO: backend/agents/sub_agent_operator/utils/database.py no está en uso. "
    "Usa db.py del backend principal."
)
