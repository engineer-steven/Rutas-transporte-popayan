# ==============================================================================
# ARCHIVO: backend/servicio_monitoreo/config.py
# RESPONSABILIDAD: Configuración del Servicio Central de Monitoreo, Despacho y JWT.
# PATRÓN: 12-Factor App (Configuración por variables de entorno).
# PUERTO: 5003
# ==============================================================================

# Importa os para leer variables de entorno del sistema.
import os

# Carga variables desde el archivo .env si la librería está disponible.
try:
    from dotenv import load_dotenv
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)
except ImportError:
    pass


class Config:
    """Clase estática que centraliza la configuración de red, BD y criptografía de MS3."""

    # Dirección del host MySQL (por defecto: localhost).
    DB_HOST = os.getenv("DB_HOST", "localhost")

    # Usuario de base de datos MySQL (por defecto: root).
    DB_USER = os.getenv("DB_USER", "root")

    # Contraseña de la base de datos MySQL.
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Nombre de la base de datos (Enrutate).
    DB_NAME = os.getenv("DB_NAME", "Enrutate")

    # Puerto de comunicación de MySQL (3306).
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # Host local del servidor web Flask.
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")

    # Puerto asignado para el Microservicio 3 de Monitoreo y Despacho (Puerto 5003).
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5003))

    # Clave criptográfica simétrica utilizada para firmar los tokens JWT emitidos.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
    if len(JWT_SECRET_KEY) < 32 or JWT_SECRET_KEY == "popayan_secreto_transporte_jwt_2026":
        raise RuntimeError("Configura JWT_SECRET_KEY con un secreto aleatorio de al menos 32 caracteres.")

    # Tiempo de vigencia del token JWT en horas (por defecto: 24 horas).
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
