
from app.config.database import db_saia


class HistorialModel:

    @staticmethod
    def esta_dentro(num_doc: int) -> bool:
        """Indica si la persona tiene un ingreso sin salida registrada."""
        row = db_saia.fetch_one(
            """SELECT 1 FROM historial
               WHERE num_doc=%s AND fecha_hora_salida IS NULL
               LIMIT 1""",
            (num_doc,)
        )
        return row is not None

    @staticmethod
    def get_all(search: str = "", limit: int = 200,
                fecha_inicio: str = None, fecha_fin: str = None) -> list[dict]:
        where = []
        params = []

        if search:
            where.append("(p.nombres LIKE %s OR p.p_ape LIKE %s OR h.num_doc LIKE %s)")
            like = f"%{search}%"
            params += [like, like, like]
        if fecha_inicio:
            where.append("DATE(h.fecha_hora_ingreso) >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where.append("DATE(h.fecha_hora_ingreso) <= %s")
            params.append(fecha_fin)

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        q = f"""
            SELECT * FROM (
                SELECT h.id_ingreso, h.id_guarda, h.num_doc, h.fecha_hora_ingreso,
                       NULL AS fecha_hora_salida, 'INGRESO' AS estado_movimiento,
                       h.observacion, COALESCE(NULLIF(h.porteria, ''), 'Porteria N.2') AS porteria_mostrada,
                       h.fecha_hora_ingreso AS fecha_evento,
                       p.nombres, p.p_ape, p.tip_doc,
                       pg.nombres AS guarda_nombres, pg.p_ape AS guarda_ape
                FROM historial h
                JOIN persona p ON h.num_doc = p.num_doc
                JOIN personal_seguridad ps ON h.id_guarda = ps.id_guarda
                JOIN persona pg ON ps.num_doc = pg.num_doc
                {where_sql}
                UNION ALL
                SELECT h.id_ingreso, h.id_guarda, h.num_doc, h.fecha_hora_ingreso,
                       h.fecha_hora_salida, 'SALIDA' AS estado_movimiento,
                       h.observacion, COALESCE(NULLIF(h.porteria, ''), 'Porteria N.2') AS porteria_mostrada,
                       h.fecha_hora_salida AS fecha_evento,
                       p.nombres, p.p_ape, p.tip_doc,
                       pg.nombres AS guarda_nombres, pg.p_ape AS guarda_ape
                FROM historial h
                JOIN persona p ON h.num_doc = p.num_doc
                JOIN personal_seguridad ps ON h.id_guarda = ps.id_guarda
                JOIN persona pg ON ps.num_doc = pg.num_doc
                {where_sql}{' AND ' if where_sql else 'WHERE '}h.fecha_hora_salida IS NOT NULL
            ) movimientos
            ORDER BY fecha_evento DESC
            LIMIT %s
        """
        return db_saia.fetch_all(q, tuple(params + params + [limit]))

    @staticmethod
    def get_recientes(limit: int = 10) -> list[dict]:
        q = """
            SELECT h.id_ingreso, h.fecha_hora_ingreso, h.fecha_hora_salida,
                   h.estado_movimiento, h.porteria,
                   p.nombres, p.p_ape, p.num_doc
            FROM historial h
            JOIN persona p ON h.num_doc = p.num_doc
            ORDER BY h.fecha_hora_ingreso DESC
            LIMIT %s
        """
        return db_saia.fetch_all(q, (limit,))

    @staticmethod
    def count_hoy() -> int:
        row = db_saia.fetch_one(
            "SELECT COUNT(*) AS total FROM historial WHERE DATE(fecha_hora_ingreso)=CURDATE()"
        )
        return row["total"] if row else 0

    @staticmethod
    def count_mes() -> int:
        row = db_saia.fetch_one(
            """SELECT COUNT(*) AS total FROM historial
               WHERE MONTH(fecha_hora_ingreso)=MONTH(CURDATE())
                 AND YEAR(fecha_hora_ingreso)=YEAR(CURDATE())"""
        )
        return row["total"] if row else 0

    @staticmethod
    def ingresos_por_dia(dias: int = 30) -> list[dict]:
        q = """
            SELECT DATE(fecha_hora_ingreso) AS fecha,
                   COUNT(*) AS total
            FROM historial
            WHERE fecha_hora_ingreso >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(fecha_hora_ingreso)
            ORDER BY fecha
        """
        return db_saia.fetch_all(q, (dias,))

    @staticmethod
    def ingresos_por_porteria() -> list[dict]:
        q = """
            SELECT porteria, COUNT(*) AS total
            FROM historial
            WHERE porteria IS NOT NULL
            GROUP BY porteria
            ORDER BY total DESC
        """
        return db_saia.fetch_all(q)

    @staticmethod
    def ingresos_por_hora() -> list[dict]:
        q = """
            SELECT HOUR(fecha_hora_ingreso) AS hora, COUNT(*) AS total
            FROM historial
            GROUP BY HOUR(fecha_hora_ingreso)
            ORDER BY hora
        """
        return db_saia.fetch_all(q)


class InsumoModel:

    @staticmethod
    def get_all(search: str = "") -> list[dict]:
        if search:
            q = """
                SELECT i.*, p.nombres, p.p_ape
                FROM insumo i
                JOIN persona p ON i.num_doc = p.num_doc
                WHERE i.nom_insumo LIKE %s OR i.num_serie LIKE %s OR i.marca LIKE %s
                ORDER BY i.nom_insumo
            """
            like = f"%{search}%"
            return db_saia.fetch_all(q, (like, like, like))
        q = """
            SELECT i.*, p.nombres, p.p_ape
            FROM insumo i
            JOIN persona p ON i.num_doc = p.num_doc
            ORDER BY i.nom_insumo
        """
        return db_saia.fetch_all(q)

    @staticmethod
    def create(data: dict) -> int:
        q = """
            INSERT INTO insumo (nom_insumo, estado, marca, num_serie,
                                desc_insumo, imagen, num_doc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return db_saia.execute(q, (
            data["nom_insumo"], data.get("estado", 1),
            data.get("marca"), data.get("num_serie"),
            data.get("desc_insumo"), data.get("imagen"),
            data["num_doc"],
        ))

    @staticmethod
    def update(id_insumo: int, data: dict) -> int:
        q = """
            UPDATE insumo SET nom_insumo=%s, estado=%s, marca=%s,
                              num_serie=%s, desc_insumo=%s, imagen=%s
            WHERE id_insumo=%s
        """
        return db_saia.execute(q, (
            data["nom_insumo"], data.get("estado", 1),
            data.get("marca"), data.get("num_serie"),
            data.get("desc_insumo"), data.get("imagen"),
            id_insumo,
        ))

    @staticmethod
    def delete(id_insumo: int) -> int:
        return db_saia.execute("DELETE FROM insumo WHERE id_insumo=%s", (id_insumo,))

    @staticmethod
    def count() -> int:
        row = db_saia.fetch_one("SELECT COUNT(*) AS total FROM insumo WHERE estado=1")
        return row["total"] if row else 0
