-- ============================================================================
-- Archivo: vistas_sistema.sql
-- Descripción: Vistas de consulta del sistema (sin schemas explícitos)
-- Para usar con database.build
-- ============================================================================

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE VIEW conversaciones_pendientes AS
 SELECT c.id,
    c.id_contacto,
    co.nombre,
    co.telefono,
    c.canal,
    c.categoria,
    c.prioridad,
    c.fecha_ultima_actividad,
    c.asignado_a,
    u.nombre_completo AS asignado_a_nombre,
    (EXTRACT(epoch FROM (now() - (c.fecha_ultima_actividad)::timestamp with time zone)) / (60)::numeric) AS minutos_sin_atencion
   FROM ((conversaciones c
     JOIN contactos co ON ((c.id_contacto = co.id)))
     LEFT JOIN usuarios u ON ((c.asignado_a = u.id)))
  WHERE ((c.estado = ANY (ARRAY['Activa'::text, 'Esperando_Humano'::text])) AND (co.activo = true) AND (co.bloqueado = false))
  ORDER BY c.prioridad DESC, c.fecha_ultima_actividad;

CREATE VIEW metricas_bot_diarias AS
 SELECT date(m.fecha_envio) AS fecha,
    c.canal,
    count(DISTINCT c.id) AS conversaciones_totales,
    count(m.id) FILTER (WHERE (m.direccion = 'Entrante'::text)) AS mensajes_recibidos,
    count(m.id) FILTER (WHERE ((m.direccion = 'Saliente'::text) AND (m.enviado_por_tipo = 'Bot'::text))) AS mensajes_bot,
    count(m.id) FILTER (WHERE ((m.direccion = 'Saliente'::text) AND (m.enviado_por_tipo = 'Usuario_Sistema'::text))) AS mensajes_humano,
    avg(c.tiempo_primera_respuesta_segundos) AS avg_primera_respuesta_seg,
    avg(c.tiempo_resolucion_minutos) FILTER (WHERE (c.estado = 'Resuelta'::text)) AS avg_resolucion_min,
    count(DISTINCT c.id) FILTER (WHERE (c.estado = 'Resuelta'::text)) AS conversaciones_resueltas,
    avg(c.calificacion) FILTER (WHERE (c.calificacion IS NOT NULL)) AS calificacion_promedio
   FROM (conversaciones c
     JOIN mensajes m ON ((c.id = m.id_conversacion)))
  GROUP BY (date(m.fecha_envio)), c.canal;

-- ============================================================================
-- Vista 23: Historial Médico Consolidado de Pacientes
-- Descripción: Consolida el expediente médico completo de cada paciente
-- ============================================================================
CREATE VIEW historial_medico_pacientes AS
SELECT 
    p.id AS id_paciente,
    p.primer_nombre || ' ' || p.primer_apellido AS nombre_completo,
    p.fecha_nacimiento,
    EXTRACT(YEAR FROM AGE(p.fecha_nacimiento)) AS edad,
    p.sexo,
    p.telefono_principal,
    p.email,
    -- Alergias activas
    COUNT(DISTINCT a.id) FILTER (WHERE a.activo = true) AS total_alergias,
    STRING_AGG(DISTINCT a.nombre_alergeno, ', ') FILTER (WHERE a.activo = true AND a.severidad IN ('Grave', 'Mortal')) AS alergias_graves,
    -- Antecedentes médicos activos
    COUNT(DISTINCT am.id) FILTER (WHERE am.activo = true) AS total_antecedentes,
    STRING_AGG(DISTINCT am.nombre_enfermedad, ', ') FILTER (WHERE am.activo = true AND am.tipo_categoria = 'Patologico') AS enfermedades_patologicas,
    -- Signos vitales más recientes
    (SELECT sv.peso_kg FROM signos_vitales sv WHERE sv.id_paciente = p.id ORDER BY sv.fecha_registro DESC LIMIT 1) AS peso_actual,
    (SELECT sv.talla_cm FROM signos_vitales sv WHERE sv.id_paciente = p.id ORDER BY sv.fecha_registro DESC LIMIT 1) AS talla_actual,
    (SELECT sv.ta_sistolica || '/' || sv.ta_diastolica FROM signos_vitales sv WHERE sv.id_paciente = p.id ORDER BY sv.fecha_registro DESC LIMIT 1) AS presion_arterial,
    -- Historial de citas
    COUNT(DISTINCT c.id) AS total_citas,
    COUNT(DISTINCT c.id) FILTER (WHERE c.estado = 'Completada') AS citas_completadas,
    COUNT(DISTINCT c.id) FILTER (WHERE c.estado = 'Cancelada') AS citas_canceladas,
    MAX(c.fecha_hora_inicio) AS ultima_cita,
    -- Tratamientos recibidos
    COUNT(DISTINCT dc.id_tratamiento) AS tratamientos_diferentes,
    -- Información de seguimiento
    p.activo AS paciente_activo,
    p.fecha_registro AS fecha_primera_consulta
FROM pacientes p
LEFT JOIN alergias a ON p.id = a.id_paciente
LEFT JOIN antecedentes_medicos am ON p.id = am.id_paciente
LEFT JOIN citas c ON p.id = c.id_paciente
LEFT JOIN detalle_cita dc ON c.id = dc.id_cita
WHERE p.activo = true
GROUP BY p.id, p.primer_nombre, p.primer_apellido, p.fecha_nacimiento, p.sexo, 
         p.telefono_principal, p.email, p.activo, p.fecha_registro;

-- ============================================================================
-- Vista 24: Productividad de Podólogos
-- NOTA: Esta vista se mueve a 11_horarios_personal.sql por dependencia con horarios_trabajo
-- ============================================================================
