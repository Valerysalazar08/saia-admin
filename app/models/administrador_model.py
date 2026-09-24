"""Gestión de cuentas administradores (superadministrador)"""
from app.config.database import db_saia


class AdministradorModel:
    @staticmethod
    def get_all(search: str = "") -> list[dict]:
        q = """
            SELECT p.num_doc, p.tip_doc, p.nombres, p.p_ape, p.email, p.tel,
                   c.id_cuenta, c.estado, c.fecha_creacion
            FROM persona p
            JOIN cuenta c ON c.num_doc=p.num_doc
            WHERE c.id_rol=2 AND c.estado=1
        """
        params = ()
        if search:
            like = f"%{search}%"
            q += " AND (p.nombres LIKE %s OR p.p_ape LIKE %s OR p.num_doc LIKE %s)"
            params = (like, like, like)
        q += " ORDER BY p.nombres"
        return db_saia.fetch_all(q, params)

    @staticmethod
    def create(persona: dict, password: str) -> int:
        from app.models.persona_model import PersonaModel, CuentaModel
        PersonaModel.create(persona)
        CuentaModel.create(persona["num_doc"], id_rol=2, password_plain=password)
        return db_saia.execute(
            "INSERT INTO administrador (num_doc) VALUES (%s)", (persona["num_doc"],))

    @staticmethod
    def update(num_doc: int, persona: dict) -> int:
        from app.models.persona_model import PersonaModel
        return PersonaModel.update(num_doc, persona)
