# ==============================================================================
# ARCHIVO: backend/servicio_monitoreo/database.py
# RESPONSABILIDAD: Conexiones TCP y administración transaccional a MySQL para MS3.
# PATRONES: Context Manager (@contextmanager), Garantía de Transacción ACID.
# ==============================================================================

# Importa el decorador contextmanager para estructurar bloques 'with'.
from contextlib import contextmanager

# Importa el conector pymysql.
import pymysql

# Importa los cursores tipo diccionario.
import pymysql.cursors

# Importa las credenciales de conexión desde config.py.
from config import Config


def _get_connection():
    """Establece y retorna una conexión física hacia la base de datos MySQL."""
    return pymysql.connect(
        host=Config.DB_HOST,                      # Dirección del servidor de BD
        user=Config.DB_USER,                      # Usuario autenticado
        password=Config.DB_PASSWORD,              # Contraseña
        db=Config.DB_NAME,                        # Nombre de la base de datos
        port=Config.DB_PORT,                      # Puerto TCP (3306)
        cursorclass=pymysql.cursors.DictCursor,   # Retorna registros como diccionarios asociativos
        charset="utf8mb4",                        # Soporte para caracteres UTF-8
        autocommit=False                          # Transacciones manuales para atomicidad
    )


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager que entrega un cursor activo y garantiza el cierre absoluto de la conexión.
    Previene Connection Leaks en el Microservicio Central.
    
    :param commit: True para transacciones de inserción, edición o borrado; False para consultas SELECT.
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
        # Cierre garantizado de la conexión física en MySQL.
        conn.close()
