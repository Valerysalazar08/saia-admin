"""
Modelo para personal_seguridad, historial_turno_guarda en BD saia.
"""
from app.config.database import db_saia


class GuardaModel:

    @staticmethod
    def get_all(search: str = "") -> list[dict]:
        if search:
            q = """
                SELECT ps.*, p.nombres, p.p_ape, p.tip_doc, p.email, p.tel,
                       p.sexo, p.fecha_nac, p.tip_sang,
                       c.imagen, c.id_cuenta, c.estado AS cuenta_estado
                FROM personal_seguridad ps
                JOIN persona p ON ps.num_doc = p.num_doc
                JOIN cuenta c ON p.num_doc = c.num_doc AND c.estado = 1
                WHERE p.nombres LIKE %s OR p.p_ape LIKE %s OR p.num_doc LIKE %s
                ORDER BY p.nombres
            """
            like = f"%{search}%"
            return db_saia.fetch_all(q, (like, like, like))
        q = """
            SELECT ps.*, p.nombres, p.p_ape, p.tip_doc, p.email, p.tel,
                   p.sexo, p.fecha_nac, p.tip_sang,
                   c.imagen, c.id_cuenta, c.estado AS cuenta_estado
            FROM personal_seguridad ps
            JOIN persona p ON ps.num_doc = p.num_doc
            JOIN cuenta c ON p.num_doc = c.num_doc AND c.estado = 1
            ORDER BY p.nombres
        """
        return db_saia.fetch_all(q)

    @staticmethod
    def get_by_id(id_guarda: int) -> dict | None:
        q = """
            SELECT ps.*, p.nombres, p.p_ape, p.tip_doc, p.email, p.tel,
                   p.sexo, p.fecha_nac, p.tip_sang
            FROM personal_seguridad ps
            JOIN persona p ON ps.num_doc = p.num_doc
            WHERE ps.id_guarda = %s
        """
        return db_saia.fetch_one(q, (id_guarda,))

    @staticmethod
    def get_by_doc(num_doc: int) -> dict | None:
        return db_saia.fetch_one(
            "SELECT * FROM personal_seguridad WHERE num_doc=%s", (num_doc,)
        )

    @staticmethod
    def create(num_doc: int, turno: str = None, empresa_seg: str = None) -> int:
        q = """
            INSERT INTO personal_seguridad
                (num_doc, turno, empresa_seg)
            VALUES (%s, %s, %s)
        """
        return db_saia.execute(q, (num_doc, turno, empresa_seg))

    @staticmethod
    def update(id_guarda: int, data: dict) -> int:
        q = """
            UPDATE personal_seguridad
            SET empresa_seg=%s
            WHERE id_guarda=%s
        """
        return db_saia.execute(q, (
            data.get("empresa_seg"), id_guarda
        ))

    @staticmethod
    def historial_resumen(id_guarda: int) -> dict:
        """Indica los registros que impiden borrar físicamente a un guarda.

        La identidad del guarda debe mantenerse mientras existan ingresos o
        turnos históricos que lo referencian; de lo contrario esos registros
        perderían su responsable.
        """
        ingresos = db_saia.fetch_one(
            "SELECT COUNT(*) AS total FROM historial WHERE id_guarda=%s",
            (id_guarda,),
        )
        turnos = db_saia.fetch_one(
            "SELECT COUNT(*) AS total FROM historial_turno_guarda WHERE id_guarda=%s",
            (id_guarda,),
        )
        return {
            "ingresos": int((ingresos or {}).get("total", 0)),
            "turnos": int((turnos or {}).get("total", 0)),
        }

    @staticmethod
    def desactivar(id_guarda: int) -> int:
        """Desactiva el acceso, conservando el guarda y sus referencias."""
        guarda = db_saia.fetch_one(
            "SELECT num_doc FROM personal_seguridad WHERE id_guarda=%s", (id_guarda,)
        )
        if not guarda:
            return 0
        return db_saia.execute(
            "UPDATE cuenta SET estado=0 WHERE num_doc=%s", (guarda["num_doc"],)
        )

    @staticmethod
    def delete(id_guarda: int) -> int:
        """Implementa Delete como borrado lógico.

        El registro se retira de la operación activa bloqueando su cuenta,
        pero persona, guarda e historial se conservan para auditoría.
        """
        return GuardaModel.desactivar(id_guarda)

    @staticmethod
    def count() -> int:
        row = db_saia.fetch_one("""
            SELECT COUNT(*) AS total
            FROM personal_seguridad ps
            JOIN cuenta c ON c.num_doc = ps.num_doc
            WHERE c.id_rol = 3 AND c.estado = 1
        """)
        return row["total"] if row else 0

    # ── Turnos ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_turnos(id_guarda: int = None, limit: int = 50) -> list[dict]:
        if id_guarda:
            q = """
                SELECT ht.*, p.nombres, p.p_ape
                FROM historial_turno_guarda ht
                JOIN personal_seguridad ps ON ht.id_guarda = ps.id_guarda
                JOIN persona p ON ps.num_doc = p.num_doc
                WHERE ht.id_guarda = %s
                ORDER BY ht.fecha DESC, ht.inicio_turno DESC
                LIMIT %s
            """
            return db_saia.fetch_all(q, (id_guarda, limit))
        q = """
            SELECT ht.*, p.nombres, p.p_ape
            FROM historial_turno_guarda ht
            JOIN personal_seguridad ps ON ht.id_guarda = ps.id_guarda
            JOIN persona p ON ps.num_doc = p.num_doc
            ORDER BY ht.fecha DESC, ht.inicio_turno DESC
            LIMIT %s
        """
        return db_saia.fetch_all(q, (limit,))
