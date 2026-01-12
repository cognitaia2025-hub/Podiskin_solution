"""
Twilio Service
==============

Servicio para enviar mensajes de WhatsApp vía Twilio.

Referencias:
- https://www.twilio.com/docs/whatsapp/api#send-a-message
"""

from twilio.rest import Client
import os
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """Servicio de mensajería usando Twilio WhatsApp API."""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_from = os.getenv("TWILIO_PHONE_NUMBER")  # +16206986058
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_from]):
            raise ValueError("Twilio credentials not configured in environment")
        
        self.client = Client(self.account_sid, self.auth_token)
        logger.info(f"✅ TwilioService initialized with number {self.whatsapp_from}")
    
    async def enviar_mensaje(self, to_number: str, mensaje: str) -> dict:
        """
        Envía mensaje de WhatsApp via Twilio.
        
        Args:
            to_number: Número de teléfono (sin "whatsapp:" prefix)
            mensaje: Texto a enviar
            
        Returns:
            Dict con resultado: {
                "success": bool,
                "message_sid": str,
                "status": str,
                "error": Optional[str]
            }
        """
        try:
            # Normalizar número
            if not to_number.startswith("+"):
                to_number = f"+{to_number}"
            
            # Enviar mensaje
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_from}',
                body=mensaje,
                to=f'whatsapp:{to_number}'
            )
            
            logger.info(f"📤 Mensaje enviado a {to_number}: {message.sid}")
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": to_number
            }
        
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje a {to_number}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "to": to_number
            }
    
    async def enviar_recordatorio_cita(
        self,
        paciente_telefono: str,
        paciente_nombre: str,
        fecha_cita: str,
        hora_cita: str,
        tratamiento: str
    ) -> dict:
        """
        Envía recordatorio de cita estructurado.
        
        Args:
            paciente_telefono: Teléfono del paciente
            paciente_nombre: Nombre del paciente
            fecha_cita: Fecha de la cita (formato: "15/01/2026")
            hora_cita: Hora de la cita (formato: "14:00")
            tratamiento: Nombre del tratamiento
            
        Returns:
            Dict con resultado del envío
        """
        mensaje = f"""Hola {paciente_nombre}, le recordamos su cita:

📅 Fecha: {fecha_cita}
🕐 Hora: {hora_cita}
👨‍⚕️ Tratamiento: {tratamiento}
📍 Clínica Podoskin

Para confirmar responda: SÍ
Para cancelar responda: NO"""
        
        return await self.enviar_mensaje(paciente_telefono, mensaje)


# Instancia global
_twilio_service = None


def get_twilio_service() -> TwilioService:
    """Obtiene instancia singleton del servicio Twilio."""
    global _twilio_service
    
    if _twilio_service is None:
        _twilio_service = TwilioService()
    
    return _twilio_service
