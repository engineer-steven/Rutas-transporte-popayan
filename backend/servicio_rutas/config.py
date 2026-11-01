# ==============================================================================
# ARCHIVO: backend/servicio_rutas/config.py
# RESPONSABILIDAD: Centralizar las variables de configuración del Microservicio 1.
# PATRÓN: 12-Factor App (Configuración almacenada en variables de entorno).
# ==============================================================================

# Importa el módulo estándar del sistema operativo para acceder a variables de entorno.
import os

# Bloque condicional defensivo para intentar cargar variables desde un archivo .env si existe.
try:
    # Importa la función load_dotenv de la librería python-dotenv si está instalada.
    from dotenv import load_dotenv
    # Lee y carga las variables de entorno definidas en el archivo .env local.
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)
except ImportError:
    # Si la librería python-dotenv no está instalada, no rompe la ejecución y continúa.
    pass


class Config:
    """Clase estática que agrupa todos los parámetros de conexión y arranque."""

    # Dirección IP o nombre de host del servidor MySQL (por defecto: localhost).
    DB_HOST = os.getenv("DB_HOST", "localhost")

    # Nombre de usuario autorizado para autenticarse en MySQL (por defecto: root).
    DB_USER = os.getenv("DB_USER", "root")

    # Contraseña del usuario en MySQL (por defecto: cadena vacía típica en entornos locales).
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Nombre de la base de datos relacional a utilizar (por defecto: Enrutate).
    DB_NAME = os.getenv("DB_NAME", "Enrutate")

    # Puerto TCP en el que escucha el motor de base de datos MySQL (por defecto: 3306).
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # Dirección IP local en la que se vinculará el servidor HTTP Flask (127.0.0.1 = localhost).
    SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")

    # Puerto de red exclusivo asignado a este microservicio de Rutas (Puerto 5001).
    SERVER_PORT = int(os.getenv("SERVER_PORT", 5001))

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
    if len(JWT_SECRET_KEY) < 32 or JWT_SECRET_KEY == "popayan_secreto_transporte_jwt_2026":
        raise RuntimeError("Configura JWT_SECRET_KEY con un secreto aleatorio de al menos 32 caracteres.")
