# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/database.py
# RESPONSABILIDAD: Administrar el ciclo de vida de las conexiones TCP a MySQL en MS2.
# PATRONES: Context Manager (@contextmanager), Garantía de Transacción ACID.
# ==============================================================================

# Importa el decorador contextmanager para construir administradores de contexto.
from contextlib import contextmanager

# Importa el conector de base de datos MySQL puro en Python.
import pymysql

# Importa los cursores de pymysql para trabajar con registros en forma de diccionario.
import pymysql.cursors

# Importa la configuración de base de datos de este microservicio.
from config import Config


def _get_connection():
    """Abre y retorna un socket TCP de conexión hacia la base de datos MySQL."""
    return pymysql.connect(
        host=Config.DB_HOST,                      # Dirección del servidor de BD
        user=Config.DB_USER,                      # Usuario autenticado
        password=Config.DB_PASSWORD,              # Contraseña de acceso
        db=Config.DB_NAME,                        # Esquema de persistencia
        port=Config.DB_PORT,                      # Puerto de escucha
        cursorclass=pymysql.cursors.DictCursor,   # Retorna registros como diccionarios {'campo': valor}
        charset="utf8mb4",                        # Codificación completa de caracteres UTF-8
        autocommit=False                          # Desactiva autocommit para manejo de transacciones manual
    )


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context Manager que entrega un cursor activo y garantiza el cierre seguro de la conexión.
    Evita fugas de conexiones hacia el motor de base de datos bajo excepciones.
    
    :param commit: True para transacciones de escritura (INSERT, UPDATE, DELETE), False para lectura (SELECT).
    """
    # Abre la conexión al motor de base de datos.
    conn = _get_connection()
    try:
        # Abre el cursor para ejecutar sentencias.
        with conn.cursor() as cursor:
            # Entrega el cursor al bloque 'with' consumidor.
            yield cursor
            # Si se indicó escritura y todo fue correcto, confirma la transacción en la base de datos.
            if commit:
                conn.commit()
    except Exception:
        # En caso de excepción durante la escritura, revierte los cambios para mantener la consistencia ACID.
        if commit:
            conn.rollback()
        raise
    finally:
        # Libera siempre la conexión cerrando el socket de red.
        conn.close()
