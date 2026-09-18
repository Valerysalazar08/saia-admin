-- Ejecutar una sola vez si se prefiere actualizar la BD manualmente.
ALTER TABLE rechazo_ingreso
  ADD COLUMN estado_gestion VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
  ADD COLUMN comentario_gestion TEXT NULL,
  ADD COLUMN fecha_gestion DATETIME NULL,
  ADD COLUMN gestionado_por BIGINT NULL;
