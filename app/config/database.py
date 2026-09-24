
import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from app.config.settings import DB_SAIA, DB_SENA


class DatabaseManager:

    def __init__(self, config: dict, pool_name: str, pool_size: int = 5):
        self._config = config
        self._pool_name = pool_name
        self._pool_size = pool_size
        self._pool = None
        self._init_pool()

    def _init_pool(self):
        try:
            pool_config = {**self._config, "pool_name": self._pool_name, "pool_size": self._pool_size}
            self._pool = pooling.MySQLConnectionPool(**pool_config)
        except Error as e:
            print(f"[DB] Error al crear pool '{self._pool_name}': {e}")
            self._pool = None

    def get_connection(self):
        if self._pool is None:
            self._init_pool()
        try:
            return self._pool.get_connection()
        except Error:
            self._init_pool()
            if self._pool:
                return self._pool.get_connection()
            raise

    @contextmanager
    def cursor(self, dictionary: bool = True):
        conn = self.get_connection()
        cur = conn.cursor(dictionary=dictionary, buffered=True)
        try:
            yield cur
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    def execute(self, query: str, params: tuple = None) -> int:
        with self.cursor() as cur:
            cur.execute(query, params or ())
            return cur.lastrowid if cur.lastrowid else cur.rowcount

    def fetch_one(self, query: str, params: tuple = None) -> dict | None:
        """Ejecuta SELECT y retorna la primera fila como dict."""
        with self.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()

    def fetch_all(self, query: str, params: tuple = None) -> list[dict]:
        with self.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def test_connection(self) -> bool:
        try:
            with self.cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"[DB] Error de conexión ({self._pool_name}): {e}")
            return False

db_saia = DatabaseManager(DB_SAIA, pool_name="saia_pool", pool_size=5)
db_sena = DatabaseManager(DB_SENA, pool_name="sena_pool", pool_size=3)
