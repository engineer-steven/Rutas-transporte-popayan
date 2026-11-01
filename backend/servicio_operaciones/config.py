# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/config.py
# RESPONSABILIDAD: Centralizar las variables de configuración del Microservicio 2.
# PATRÓN: 12-Factor App (Configuración por variables de entorno).
# PUERTO: 5002
# ==============================================================================

# Importa el módulo estándar del sistema operativo para consultar variables de entorno.
import os

# Carga defensiva del archivo .env si la librería dotenv está disponible en el entorno.
try:
    from dotenv import load_dotenv
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)
except ImportError:
    pass


class Config:
    """Clase estática que agrupa todos los parámetros de conexión y arranque del servicio."""

    # Host o IP del servidor MySQL (por defecto: localhost).
    DB_HOST = os.getenv("DB_HOST", "localhost")

    # Usuario de acceso a MySQL (por defecto: root).
    DB_USER = os.getenv("DB_USER", "root")

    # Contraseña de MySQL.
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Nombre de la base de datos relacional (Enrutate).
    DB_NAME = os.getenv("DB_NAME", "Enrutate")

    # Puerto de comunicación de MySQL (3306).
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # Host local en el que se ejecutará el servidor Flask.
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")

    # Puerto asignado para el Microservicio 2 de Operaciones e Incidentes (Puerto 5002).
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5002))

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
    if len(JWT_SECRET_KEY) < 32 or JWT_SECRET_KEY == "popayan_secreto_transporte_jwt_2026":
        raise RuntimeError("Configura JWT_SECRET_KEY con un secreto aleatorio de al menos 32 caracteres.")
