"""
Ejemplo de Uso - Sub-Agente WhatsApp
=====================================

Ejemplo básico de cómo usar el sub-agente de WhatsApp.
"""

import asyncio
import logging
from agents.sub_agent_whatsApp.state import create_initial_state
from agents.sub_agent_whatsApp.graph import run_agent
from agents.sub_agent_whatsApp.utils import (
    init_db_pool,
    close_db_pool,
    get_or_create_contact,
    get_or_create_conversation,
    save_message,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Ejemplo de uso del sub-agente"""

    try:
        # ====================================================================
        # 1. INICIALIZAR BASE DE DATOS
        # ====================================================================

        logger.info("Initializing database pool...")
        await init_db_pool()

        # ====================================================================
        # 2. SIMULAR MENSAJE DE WHATSAPP
        # ====================================================================

        whatsapp_number = "+523331234567"
        contact_name = "Juan Pérez"
        message = "Hola, quiero agendar una cita para mañana a las 2pm"

        logger.info(f"Processing message from {contact_name}: {message}")

        # ====================================================================
        # 3. OBTENER O CREAR CONTACTO Y CONVERSACIÓN
        # ====================================================================

        contact = await get_or_create_contact(
            telefono=whatsapp_number, nombre=contact_name
        )

        conversation = await get_or_create_conversation(contact_id=contact["id"])

        logger.info(
            f"Contact ID: {contact['id']}, " f"Conversation ID: {conversation['id']}"
        )

        # ====================================================================
        # 4. GUARDAR MENSAJE DEL USUARIO
        # ====================================================================

        await save_message(
            conversation_id=conversation["id"], rol="user", contenido=message
        )

        # ====================================================================
        # 5. CREAR ESTADO INICIAL
        # ====================================================================

        state = create_initial_state(
            conversation_id=str(conversation["id"]),
            contact_id=contact["id"],
            whatsapp_number=whatsapp_number,
            contact_name=contact_name,
            message=message,
            patient_id=contact.get("id_paciente"),
        )

        logger.info("Initial state created")

        # ====================================================================
        # 6. EJECUTAR AGENTE
        # ====================================================================

        logger.info("Running WhatsApp agent...")

        result = await run_agent(
            state=state, thread_id=f"whatsapp_{conversation['id']}"
        )

        # ====================================================================
        # 7. OBTENER RESPUESTA
        # ====================================================================

        last_msg = result["messages"][-1]
        assistant_message = (
            last_msg.content
            if hasattr(last_msg, "content")
            else last_msg.get("content", "")
        )

        logger.info(f"Agent response: {assistant_message}")

        # ====================================================================
        # 8. GUARDAR RESPUESTA
        # ====================================================================

        await save_message(
            conversation_id=conversation["id"],
            rol="assistant",
            contenido=assistant_message,
        )

        logger.info("Response saved to database")

        # ====================================================================
        # 9. MOSTRAR RESULTADO
        # ====================================================================

        print("\n" + "=" * 70)
        print("RESULTADO DEL AGENTE")
        print("=" * 70)
        print(f"\nUsuario: {message}")
        print(f"\nAsistente: {assistant_message}")
        print(
            f"\nIntención: {result['intent']} (confianza: {result['confidence']:.2f})"
        )
        print(f"Requiere humano: {result['requires_human']}")

        if result.get("error"):
            print(f"\n⚠️ Error: {result['error']}")

        print("\n" + "=" * 70)

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)

    finally:
        # ====================================================================
        # 10. CERRAR CONEXIONES
        # ====================================================================

        logger.info("Closing database pool...")
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(main())
