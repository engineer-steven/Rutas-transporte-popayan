# ==============================================================================
# ARCHIVO: backend/servicio_rutas/database.py
# RESPONSABILIDAD: Administrar el ciclo de vida de las conexiones TCP a MySQL.
# PATRONES: Context Manager (@contextmanager), Garantía de Transacción ACID.
# ==============================================================================

# Importa el decorador contextmanager para construir administradores de contexto con bloques 'with'.
from contextlib import contextmanager

# Importa el conector de base de datos MySQL puro en Python.
import pymysql

# Importa los tipos de cursores que provee pymysql (específicamente DictCursor).
import pymysql.cursors

# Importa la clase Config que contiene las credenciales y puertos de la base de datos.
from config import Config


def _get_connection():
    """Función privada que abre y retorna un socket de conexión física hacia MySQL."""
    return pymysql.connect(
        host=Config.DB_HOST,                      # Dirección del host de la base de datos
        user=Config.DB_USER,                      # Usuario de MySQL
        password=Config.DB_PASSWORD,              # Contraseña de acceso
        db=Config.DB_NAME,                        # Nombre de la base de datos
        port=Config.DB_PORT,                      # Puerto de conexión (3306)
        cursorclass=pymysql.cursors.DictCursor,   # Retorna registros como diccionarios {'columna': valor}
        charset="utf8mb4",                        # Codificación completa para tildes y caracteres especiales
        autocommit=False                          # Desactiva autocommit para permitir control transaccional explícito
    )


@contextmanager
def get_cursor(commit: bool = False):
    """
    Context Manager que entrega un cursor activo y garantiza el cierre de la conexión.
    Evita fugas de conexiones (Connection Leaks) ante cualquier excepción en tiempo de ejecución.
    
    :param commit: True si la operación realiza escritura (INSERT, UPDATE, DELETE), False para lecturas (SELECT).
    """
    # Abre la conexión física al motor de base de datos.
    conn = _get_connection()
    try:
        # Abre el cursor dentro de la conexión para ejecutar sentencias SQL.
        with conn.cursor() as cursor:
            # Pausa la función y cede el cursor al bloque 'with' que invocó a get_cursor().
            yield cursor
            # Si se indicó commit=True y el código consumidor terminó sin errores, confirma los cambios.
            if commit:
                conn.commit()
    except Exception:
        # Si ocurrió algún error inesperado durante la ejecución y era una escritura, revierte los cambios.
        if commit:
            conn.rollback()
        # Vuelve a propagar la excepción para que el controlador o servicio pueda gestionarla.
        raise
    finally:
        # Bloque de ejecución garantizada: cierra siempre la conexión física liberando el recurso en el servidor MySQL.
        conn.close()
