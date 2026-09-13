"""
Modelo para operaciones CRUD sobre persona y cuenta en la BD saia.
"""
import bcrypt
from app.config.database import db_saia


class PersonaModel:

    # ── Persona ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_all(search: str = "") -> list[dict]:
        if search:
            q = """
                SELECT p.*, c.id_rol, r.nom_rol, c.estado AS cuenta_estado,
                       c.id_cuenta, c.fecha_creacion, c.imagen, c.id_ficha,
                       c.id_programa, c.id_centro
                FROM persona p
                LEFT JOIN cuenta c ON p.num_doc = c.num_doc
                LEFT JOIN rol r ON c.id_rol = r.id_rol
                WHERE p.nombres LIKE %s OR p.p_ape LIKE %s OR p.num_doc LIKE %s
                ORDER BY p.nombres
            """
            like = f"%{search}%"
            return db_saia.fetch_all(q, (like, like, like))
        q = """
            SELECT p.*, c.id_rol, r.nom_rol, c.estado AS cuenta_estado,
                   c.id_cuenta, c.fecha_creacion, c.imagen, c.id_ficha,
                   c.id_programa, c.id_centro
            FROM persona p
            LEFT JOIN cuenta c ON p.num_doc = c.num_doc
            LEFT JOIN rol r ON c.id_rol = r.id_rol
            ORDER BY p.nombres
        """
        return db_saia.fetch_all(q)

    @staticmethod
    def get_by_doc(num_doc: int) -> dict | None:
        q = """
            SELECT p.*, c.id_rol, r.nom_rol, c.estado AS cuenta_estado,
                   c.id_cuenta, c.fecha_creacion, c.imagen, c.id_ficha,
                   c.id_programa, c.id_centro
            FROM persona p
            LEFT JOIN cuenta c ON p.num_doc = c.num_doc
            LEFT JOIN rol r ON c.id_rol = r.id_rol
            WHERE p.num_doc = %s
        """
        return db_saia.fetch_one(q, (num_doc,))

    @staticmethod
    def create(data: dict) -> int:
        q = """
            INSERT INTO persona (num_doc, tip_doc, nombres, p_ape, tel,
                                 tip_sang, sexo, fecha_nac, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return db_saia.execute(q, (
            data["num_doc"], data["tip_doc"], data["nombres"], data["p_ape"],
            data.get("tel"), data.get("tip_sang"), data.get("sexo"),
            data.get("fecha_nac"), data.get("email"),
        ))

    @staticmethod
    def update(num_doc: int, data: dict) -> int:
        q = """
            UPDATE persona SET tip_doc=%s, nombres=%s, p_ape=%s, tel=%s,
                               tip_sang=%s, sexo=%s, fecha_nac=%s, email=%s
            WHERE num_doc=%s
        """
        return db_saia.execute(q, (
            data["tip_doc"], data["nombres"], data["p_ape"],
            data.get("tel"), data.get("tip_sang"), data.get("sexo"),
            data.get("fecha_nac"), data.get("email"), num_doc,
        ))

    @staticmethod
    def delete(num_doc: int) -> int:
        return db_saia.execute("DELETE FROM persona WHERE num_doc=%s", (num_doc,))

    @staticmethod
    def exists(num_doc: int) -> bool:
        row = db_saia.fetch_one("SELECT 1 FROM persona WHERE num_doc=%s", (num_doc,))
        return row is not None


class CuentaModel:

    # ── Cuenta ──────────────────────────────────────────────────────────────────

    @staticmethod
    def create(num_doc: int, id_rol: int, password_plain: str,
               id_ficha: int = None, id_programa: int = None,
               id_centro: int = None) -> int:
        hashed = bcrypt.hashpw(password_plain.encode(), bcrypt.gensalt()).decode()
        q = """
            INSERT INTO cuenta (id_rol, num_doc, estado, fecha_creacion,
                                password, id_ficha, id_programa, id_centro)
            VALUES (%s, %s, 1, NOW(), %s, %s, %s, %s)
        """
        return db_saia.execute(q, (id_rol, num_doc, hashed, id_ficha, id_programa, id_centro))

    @staticmethod
    def get_by_doc(num_doc: int) -> dict | None:
        return db_saia.fetch_one(
            "SELECT * FROM cuenta WHERE num_doc=%s", (num_doc,)
        )

    @staticmethod
    def toggle_estado(id_cuenta: int, nuevo_estado: int) -> int:
        return db_saia.execute(
            "UPDATE cuenta SET estado=%s WHERE id_cuenta=%s",
            (nuevo_estado, id_cuenta)
        )

    @staticmethod
    def update_password(id_cuenta: int, nueva_password: str) -> int:
        hashed = bcrypt.hashpw(nueva_password.encode(), bcrypt.gensalt()).decode()
        return db_saia.execute(
            "UPDATE cuenta SET password=%s WHERE id_cuenta=%s",
            (hashed, id_cuenta)
        )

    @staticmethod
    def update_imagen(id_cuenta: int, imagen: str) -> int:
        return db_saia.execute(
            "UPDATE cuenta SET imagen=%s WHERE id_cuenta=%s",
            (imagen, id_cuenta)
        )

    @staticmethod
    def verify_password(num_doc: int, password_plain: str) -> bool:
        row = db_saia.fetch_one(
            "SELECT password FROM cuenta WHERE num_doc=%s AND estado=1",
            (num_doc,)
        )
        if not row:
            return False
        return bcrypt.checkpw(password_plain.encode(), row["password"].encode())

    @staticmethod
    def get_login_data(num_doc: int) -> dict | None:
        """Busca cuenta por num_doc sin filtrar por estado (el login maneja eso)."""
        q = """
            SELECT c.*, p.nombres, p.p_ape, p.email, r.nom_rol
            FROM cuenta c
            JOIN persona p ON c.num_doc = p.num_doc
            JOIN rol r ON c.id_rol = r.id_rol
            WHERE c.num_doc = %s
        """
        return db_saia.fetch_one(q, (num_doc,))

    @staticmethod
    def get_login_by_email(email: str) -> dict | None:
        """Busca cuenta por email del administrador para el login."""
        q = """
            SELECT c.*, p.nombres, p.p_ape, p.email, r.nom_rol
            FROM cuenta c
            JOIN persona p ON c.num_doc = p.num_doc
            JOIN rol r ON c.id_rol = r.id_rol
            WHERE p.email = %s
        """
        return db_saia.fetch_one(q, (email.strip().lower(),))
