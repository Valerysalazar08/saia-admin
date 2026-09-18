"""Consultas y gestión de rechazos de ingreso registrados por guardas."""
from app.config.database import db_saia


class RechazoIngresoModel:
    @staticmethod
    def asegurar_campos_gestion():
        """Añade los campos de gestión a instalaciones creadas con el esquema anterior."""
        campos = {
            "estado_gestion": "VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE'",
            "comentario_gestion": "TEXT NULL",
            "fecha_gestion": "DATETIME NULL",
            "gestionado_por": "BIGINT NULL",
        }
        existentes = db_saia.fetch_all("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'rechazo_ingreso'
        """)
        nombres = {r["COLUMN_NAME"] for r in existentes}
        for nombre, definicion in campos.items():
            if nombre not in nombres:
                db_saia.execute(
                    f"ALTER TABLE rechazo_ingreso ADD COLUMN {nombre} {definicion}"
                )

    @staticmethod
    def get_all(search: str = "", estado: str = "Todos") -> list[dict]:
        RechazoIngresoModel.asegurar_campos_gestion()
        where, params = ["1=1"], []
        if search:
            where.append("(p.nombres LIKE %s OR p.p_ape LIKE %s OR r.num_doc LIKE %s)")
            like = f"%{search}%"
            params.extend([like, like, like])
        if estado != "Todos":
            where.append("r.estado_gestion = %s")
            params.append(estado)
        q = f"""
            SELECT r.*, p.nombres, p.p_ape,
                   CONCAT(pg.nombres, ' ', pg.p_ape) AS guarda,
                   CONCAT(pa.nombres, ' ', pa.p_ape) AS gestionado_por_nombre
            FROM rechazo_ingreso r
            JOIN persona p ON p.num_doc = r.num_doc
            JOIN personal_seguridad ps ON ps.id_guarda = r.id_guarda
            JOIN persona pg ON pg.num_doc = ps.num_doc
            LEFT JOIN persona pa ON pa.num_doc = r.gestionado_por
            WHERE {' AND '.join(where)}
            ORDER BY r.fecha_hora DESC
        """
        return db_saia.fetch_all(q, tuple(params))

    @staticmethod
    def gestionar(id_rechazo: int, comentario: str, gestionado_por: int):
        RechazoIngresoModel.asegurar_campos_gestion()
        return db_saia.execute("""
            UPDATE rechazo_ingreso
            SET estado_gestion='GESTIONADO', comentario_gestion=%s,
                fecha_gestion=NOW(), gestionado_por=%s
            WHERE id_rechazo=%s AND estado_gestion='PENDIENTE'
        """, (comentario.strip(), gestionado_por, id_rechazo))
