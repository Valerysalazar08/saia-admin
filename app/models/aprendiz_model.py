"""
Modelo para aprendices.
Consulta la BD sena (solo lectura) para validar si existe como aprendiz activo,
y la BD saia para los datos de cuenta/persona.
"""
from app.config.database import db_saia, db_sena


class AprendizSenaModel:
    """Consultas sobre la BD sena — solo lectura."""

    @staticmethod
    def get_all(search: str = "") -> list[dict]:
        if search:
            q = """
                SELECT a.id_aprendiz, a.num_doc, a.estado,
                       f.id_ficha, f.fecha_inicio, f.fecha_finalizacion,
                       pf.nombre_programa, pf.carrera,
                       cf.nombre_centro
                FROM aprendiz a
                JOIN ficha f ON a.id_ficha = f.id_ficha
                JOIN programa_formacion pf ON f.id_programa = pf.id_programa
                JOIN centro_formacion cf ON pf.id_centro = cf.id_centro
                WHERE a.num_doc LIKE %s
                ORDER BY a.id_aprendiz
            """
            return db_sena.fetch_all(q, (f"%{search}%",))
        q = """
            SELECT a.id_aprendiz, a.num_doc, a.estado,
                   f.id_ficha, f.fecha_inicio, f.fecha_finalizacion,
                   pf.nombre_programa, pf.carrera,
                   cf.nombre_centro
            FROM aprendiz a
            JOIN ficha f ON a.id_ficha = f.id_ficha
            JOIN programa_formacion pf ON f.id_programa = pf.id_programa
            JOIN centro_formacion cf ON pf.id_centro = cf.id_centro
            ORDER BY a.id_aprendiz
        """
        return db_sena.fetch_all(q)

    @staticmethod
    def is_active_aprendiz(num_doc: int) -> bool:
        """Verifica si el num_doc existe en sena.aprendiz con estado=1."""
        row = db_sena.fetch_one(
            "SELECT id_aprendiz FROM aprendiz WHERE num_doc=%s AND estado=1",
            (num_doc,)
        )
        return row is not None

    @staticmethod
    def get_by_doc(num_doc: int) -> dict | None:
        q = """
            SELECT a.*, f.fecha_inicio, f.fecha_finalizacion,
                   pf.nombre_programa, pf.carrera, pf.descripcion_programa,
                   cf.nombre_centro, cf.descripcion_centro
            FROM aprendiz a
            JOIN ficha f ON a.id_ficha = f.id_ficha
            JOIN programa_formacion pf ON f.id_programa = pf.id_programa
            JOIN centro_formacion cf ON pf.id_centro = cf.id_centro
            WHERE a.num_doc = %s
        """
        return db_sena.fetch_one(q, (num_doc,))

    @staticmethod
    def get_fichas() -> list[dict]:
        q = """
            SELECT f.id_ficha, f.fecha_inicio, f.fecha_finalizacion,
                   pf.nombre_programa, cf.nombre_centro
            FROM ficha f
            JOIN programa_formacion pf ON f.id_programa = pf.id_programa
            JOIN centro_formacion cf ON pf.id_centro = cf.id_centro
        """
        return db_sena.fetch_all(q)

    @staticmethod
    def get_programas() -> list[dict]:
        return db_sena.fetch_all(
            "SELECT id_programa, nombre_programa, carrera FROM programa_formacion ORDER BY nombre_programa"
        )

    @staticmethod
    def get_centros() -> list[dict]:
        return db_sena.fetch_all(
            "SELECT id_centro, nombre_centro FROM centro_formacion ORDER BY nombre_centro"
        )


class AprendizSaiaModel:
    """Aprendices en la BD saia — los que tienen cuenta con rol aprendiz."""

    @staticmethod
    def get_all(search: str = "") -> list[dict]:
        """Retorna todos los aprendices registrados en saia con info de sena."""
        if search:
            q = """
                SELECT p.num_doc, p.tip_doc, p.nombres, p.p_ape, p.tel,
                       p.email, p.sexo, p.fecha_nac,
                       c.id_cuenta, c.estado AS cuenta_estado, c.fecha_creacion,
                       c.id_ficha, c.id_programa, c.id_centro, c.imagen
                FROM persona p
                JOIN cuenta c ON p.num_doc = c.num_doc
                WHERE c.id_rol = 1 AND c.estado = 1
                  AND (p.nombres LIKE %s OR p.p_ape LIKE %s OR p.num_doc LIKE %s)
                ORDER BY p.nombres
            """
            like = f"%{search}%"
            return db_saia.fetch_all(q, (like, like, like))
        q = """
            SELECT p.num_doc, p.tip_doc, p.nombres, p.p_ape, p.tel,
                   p.email, p.sexo, p.fecha_nac,
                   c.id_cuenta, c.estado AS cuenta_estado, c.fecha_creacion,
                   c.id_ficha, c.id_programa, c.id_centro, c.imagen
            FROM persona p
            JOIN cuenta c ON p.num_doc = c.num_doc
            WHERE c.id_rol = 1 AND c.estado = 1
            ORDER BY p.nombres
        """
        return db_saia.fetch_all(q)

    @staticmethod
    def count() -> int:
        row = db_saia.fetch_one(
            "SELECT COUNT(*) AS total FROM cuenta WHERE id_rol=1"
        )
        return row["total"] if row else 0

    @staticmethod
    def count_con_qr() -> int:
        """Aprendices que tienen QR habilitado (validados en sena)."""
        row = db_saia.fetch_one(
            "SELECT COUNT(*) AS total FROM cuenta WHERE id_rol=1 AND estado=1"
        )
        return row["total"] if row else 0
