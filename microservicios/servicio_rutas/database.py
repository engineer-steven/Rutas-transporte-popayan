from contextlib import contextmanager
import pymysql
import pymysql.cursors
from config import Config

def _get_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        db=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=False
    )

@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager: abre conexión y cursor, y garantiza el cierre
    aunque ocurra una excepción (evita repetir try/finally en cada función).
    'commit=True' se usa en operaciones de escritura (INSERT/UPDATE/DELETE).
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
            if commit:
                conn.commit()
    except Exception:
        if commit:
            conn.rollback()
        raise
    finally:
        conn.close()
