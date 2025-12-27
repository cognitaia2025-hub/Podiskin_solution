-- ============================================================================
-- Archivo: funciones_sistema.sql
-- Descripción: Funciones y triggers del sistema (sin schemas explícitos)
-- Para usar con database.build
-- ============================================================================

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

CREATE FUNCTION calcular_imc() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.peso_kg IS NOT NULL AND NEW.talla_cm IS NOT NULL THEN
        NEW.imc := ROUND((NEW.peso_kg / POWER(NEW.talla_cm / 100, 2))::NUMERIC, 2);
    END IF;
    RETURN NEW;
END;
$$;

CREATE FUNCTION calcular_precio_final() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.precio_final := NEW.precio_aplicado - (NEW.precio_aplicado * NEW.descuento_porcentaje / 100);
    RETURN NEW;
END;
$$;

CREATE FUNCTION calcular_saldo() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.saldo_pendiente := NEW.monto_total - NEW.monto_pagado;
    RETURN NEW;
END;
$$;

CREATE FUNCTION vincular_contacto_paciente() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_id_contacto BIGINT;
BEGIN
    SELECT id INTO v_id_contacto
    FROM contactos co
    WHERE co.telefono = (SELECT telefono_principal FROM pacientes WHERE id = NEW.id_paciente)
       OR co.email = (SELECT email FROM pacientes WHERE id = NEW.id_paciente)
    LIMIT 1;
    
    IF v_id_contacto IS NOT NULL THEN
        UPDATE contactos 
        SET id_paciente = NEW.id_paciente,
            tipo = 'Paciente_Convertido',
            fecha_ultima_interaccion = NOW()
        WHERE id = v_id_contacto
          AND id_paciente IS NULL;
    END IF;
    
    RETURN NEW;
END;
$$;

CREATE FUNCTION actualizar_ultima_actividad() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE conversaciones 
    SET fecha_ultima_actividad = NEW.fecha_envio,
        numero_mensajes = numero_mensajes + 1,
        numero_mensajes_bot = numero_mensajes_bot + CASE WHEN NEW.enviado_por_tipo = 'Bot' THEN 1 ELSE 0 END,
        numero_mensajes_humano = numero_mensajes_humano + CASE WHEN NEW.enviado_por_tipo = 'Usuario_Sistema' THEN 1 ELSE 0 END
    WHERE id = NEW.id_conversacion;
    RETURN NEW;
END;
$$;
