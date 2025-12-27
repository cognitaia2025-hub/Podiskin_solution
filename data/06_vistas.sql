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
