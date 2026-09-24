
from app.config.database import db_saia


ACCION_CREAR       = "CREAR"
ACCION_ACTUALIZAR  = "ACTUALIZAR"
ACCION_BLOQUEAR    = "BLOQUEAR"
ACCION_HABILITAR   = "HABILITAR"
ACCION_ELIMINAR    = "ELIMINAR"
ACCION_LOGIN       = "LOGIN"
ACCION_LOGOUT      = "LOGOUT"

ENTIDAD_GUARDA     = "Guarda"
ENTIDAD_APRENDIZ   = "Aprendiz"
ENTIDAD_CUENTA     = "Cuenta"
ENTIDAD_INSUMO     = "Insumo"
ENTIDAD_SESION     = "Sesión"


class AuditoriaModel:

    @staticmethod
    def registrar(tipo_accion: str, entidad: str, num_doc: int,
                  descripcion: str, realizado_por: int = None):
        q = """
            INSERT INTO auditoria_actividad
                (tipo_accion, entidad, num_doc, descripcion, realizado_por)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            db_saia.execute(q, (tipo_accion, entidad, num_doc,
                                descripcion or "", realizado_por))
        except Exception as e:
            print(f"[Auditoria] No se pudo registrar: {e}")

    @staticmethod
    def get_all(search: str = "", accion: str = None, entidad: str = None,
                fecha_inicio: str = None, fecha_fin: str = None,
                limit: int = 200) -> list[dict]:
        where = ["1=1"]
        params = []

        if search:
            where.append("(aa.descripcion LIKE %s OR aa.entidad LIKE %s "
                         "OR aa.tipo_accion LIKE %s "
                         "OR IFNULL(CONCAT(p.nombres,' ',p.p_ape),'') LIKE %s)")
            like = f"%{search}%"
            params += [like, like, like, like]
        if accion and accion != "Todas":
            where.append("aa.tipo_accion = %s")
            params.append(accion)
        if entidad and entidad != "Todas":
            where.append("aa.entidad = %s")
            params.append(entidad)
        if fecha_inicio:
            where.append("DATE(aa.fecha_hora) >= %s")
            params.append(fecha_inicio)
        if fecha_fin:
            where.append("DATE(aa.fecha_hora) <= %s")
            params.append(fecha_fin)

        q = f"""
            SELECT aa.*,
                   IFNULL(CONCAT(p.nombres,' ',p.p_ape),
                          CAST(aa.realizado_por AS CHAR)) AS usuario,
                   pa.nombres AS afectado_nombres,
                   pa.p_ape   AS afectado_ape
            FROM auditoria_actividad aa
            LEFT JOIN persona p  ON aa.realizado_por = p.num_doc
            LEFT JOIN persona pa ON aa.num_doc        = pa.num_doc
            WHERE {' AND '.join(where)}
            ORDER BY aa.fecha_hora DESC
            LIMIT %s
        """
        params.append(limit)
        return db_saia.fetch_all(q, tuple(params))

    @staticmethod
    def get_acciones() -> list[str]:
        rows = db_saia.fetch_all(
            "SELECT DISTINCT tipo_accion FROM auditoria_actividad ORDER BY tipo_accion"
        )
        return ["Todas"] + [r["tipo_accion"] for r in rows if r["tipo_accion"]]

    @staticmethod
    def get_entidades() -> list[str]:
        rows = db_saia.fetch_all(
            "SELECT DISTINCT entidad FROM auditoria_actividad ORDER BY entidad"
        )
        return ["Todas"] + [r["entidad"] for r in rows if r["entidad"]]

    @staticmethod
    def table_exists() -> bool:
        try:
            db_saia.fetch_one("SELECT 1 FROM auditoria_actividad LIMIT 1")
            return True
        except Exception:
            return False

    @staticmethod
    def create_table():
        """Crea la tabla si no existe."""
        q = """
            CREATE TABLE IF NOT EXISTS auditoria_actividad (
                id_actividad  INT          NOT NULL AUTO_INCREMENT,
                tipo_accion   VARCHAR(30)  NOT NULL,
                entidad       VARCHAR(50)  NOT NULL,
                num_doc       BIGINT       NULL,
                descripcion   VARCHAR(300) NOT NULL,
                realizado_por BIGINT       NULL,
                fecha_hora    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id_actividad),
                INDEX idx_auditoria_fecha (fecha_hora DESC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        db_saia.execute(q)
