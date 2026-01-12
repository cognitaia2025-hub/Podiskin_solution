"""
Rate Limiting Middleware
========================

Limita mensajes por número de teléfono para prevenir spam y bucles.

Configuración:
- 5 mensajes por minuto por número
- 20 mensajes por hora por número
- Detecta bucles (mismo mensaje 3+ veces)

Nota: En producción, reemplazar dicts en memoria por Redis.
"""

from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Storage en memoria (en producción usar Redis)
message_counts = defaultdict(list)  # {phone: [timestamp1, timestamp2, ...]}
message_history = defaultdict(list)  # {phone: [message1, message2, ...]}

# Configuración
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_HOUR = 20
LOOP_DETECTION_THRESHOLD = 3


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware de rate limiting para webhook de Twilio.
    
    Previene:
    - Spam (límite por minuto/hora)
    - Bucles conversacionales (mensajes repetidos)
    
    TODO en producción:
    - Reemplazar dicts en memoria por Redis
    - Agregar lista blanca (whitelist) de números exentos
    - Agregar métricas/alertas (Prometheus, Grafana)
    """
    
    # Solo aplicar a webhook de Twilio
    if request.url.path != "/webhook/twilio":
        return await call_next(request)
    
    # Extraer número de teléfono del form data
    try:
        form = await request.form()
        phone = form.get("From", "").replace("whatsapp:+", "").replace("whatsapp:", "")
        message_body = form.get("Body", "")
        
        if not phone:
            # Si no hay teléfono, continuar (puede ser mensaje de prueba)
            return await call_next(request)
        
        now = datetime.now()
        
        # ====================================================================
        # LIMPIEZA: Remover timestamps antiguos (>1 hora)
        # ====================================================================
        cutoff_time = now - timedelta(hours=1)
        message_counts[phone] = [
            ts for ts in message_counts[phone] if ts > cutoff_time
        ]
        
        # ====================================================================
        # VERIFICACIÓN 1: Límite por minuto
        # ====================================================================
        recent_minute = [
            ts for ts in message_counts[phone] 
            if ts > now - timedelta(minutes=1)
        ]
        
        if len(recent_minute) >= RATE_LIMIT_PER_MINUTE:
            logger.warning(
                f"⚠️ Rate limit excedido (por minuto): {phone} "
                f"({len(recent_minute)} mensajes)"
            )
            raise HTTPException(
                status_code=429,
                detail="Demasiados mensajes, por favor espera un momento."
            )
        
        # ====================================================================
        # VERIFICACIÓN 2: Límite por hora
        # ====================================================================
        if len(message_counts[phone]) >= RATE_LIMIT_PER_HOUR:
            logger.warning(
                f"⚠️ Rate limit excedido (por hora): {phone} "
                f"({len(message_counts[phone])} mensajes)"
            )
            raise HTTPException(
                status_code=429,
                detail="Límite de mensajes alcanzado, intenta más tarde."
            )
        
        # ====================================================================
        # VERIFICACIÓN 3: Detectar bucles (mensaje repetido)
        # ====================================================================
        recent_messages = message_history[phone][-LOOP_DETECTION_THRESHOLD:]
        if len(recent_messages) == LOOP_DETECTION_THRESHOLD:
            # Verificar si todos los mensajes son idénticos
            if all(msg == message_body for msg in recent_messages):
                logger.warning(
                    f"⚠️ Bucle detectado: {phone} - "
                    f"Mensaje repetido '{message_body[:30]}...'"
                )
                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Mensaje repetido detectado. "
                        "Si necesitas ayuda, contacta directamente a la clínica."
                    )
                )
        
        # ====================================================================
        # REGISTRO: Guardar mensaje actual
        # ====================================================================
        message_counts[phone].append(now)
        message_history[phone].append(message_body)
        
        # Limitar historial a últimos 10 mensajes para ahorrar memoria
        if len(message_history[phone]) > 10:
            message_history[phone] = message_history[phone][-10:]
        
        logger.info(
            f"📊 Rate limit check passed: {phone} "
            f"({len(recent_minute)}/min, {len(message_counts[phone])}/hour)"
        )
        
    except HTTPException:
        # Re-lanzar HTTP exceptions (rate limit errors)
        raise
    except Exception as e:
        # Log error pero permitir que el request continúe
        logger.error(f"❌ Error en rate limit middleware: {e}", exc_info=True)
    
    # Continuar con el request
    response = await call_next(request)
    return response
