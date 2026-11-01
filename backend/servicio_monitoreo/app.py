# ==============================================================================
# ARCHIVO: backend/servicio_monitoreo/app.py
# RESPONSABILIDAD: Ensamblar la aplicación Flask para Monitoreo, Rate Limiting y Blueprints.
# PATRÓN: Application Factory Pattern (create_app), Rate Limiting contra ataques de fuerza bruta.
# ==============================================================================

# Importa sys para manipulación del entorno de ejecución.
import sys

# Importa os para resolver rutas relativas y absolutas.
import os

# Obtiene la ruta del directorio del servicio actual.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegura que las importaciones directas busquen primero en este directorio.
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Importa Flask y jsonify para construir respuestas JSON.
from flask import Flask, jsonify

# Importa CORS para soporte multi-origen.
from flask_cors import CORS

# Importa la extensión de control de tasa de peticiones (Rate Limiter).
from flask_limiter import Limiter

# Utilidad para obtener la dirección IP remota del cliente que realiza la petición.
from flask_limiter.util import get_remote_address

# Importa la configuración del microservicio.
from config import Config

# Importa el Blueprint de autenticación y la función para asociar el limitador de tasa.
from routes.login import login_bp

# Importa el Blueprint con las 5 lógicas de programación y despacho operativo.
from routes.despacho import despacho_bp

# Importa el Blueprint con el CRUD de alertas de emergencia de monitoreo.
from routes.alertas import alertas_bp


def create_app():
    """Fábrica de aplicación: inicializa Flask, configura Rate Limiting y registra Blueprints."""

    # Inicializa la aplicación Flask.
    app = Flask(__name__)

    # Activa CORS para permitir solicitudes desde clientes web o herramientas como Swagger/Postman.
    CORS(app)

    # --------------------------------------------------------------------------
    # CONFIGURACIÓN DEL RATE LIMITER
    # Protege el endpoint de login contra ataques automatizados de fuerza bruta (Brute Force).
    # Estrategia: almacenamiento en memoria interna (memory://).
    # --------------------------------------------------------------------------
    limiter = Limiter(
        key_func=get_remote_address,  # Agrupa las peticiones basándose en la IP del cliente
        app=app,                      # Vincula a la app de Flask
        default_limits=[],            # Sin límite global estricto; cada ruta define el suyo
        storage_uri="memory://"       # Almacenamiento volátil en memoria RAM
    )

    # --------------------------------------------------------------------------
    # REGISTRO DE BLUEPRINTS
    # --------------------------------------------------------------------------
    app.register_blueprint(login_bp)      # Rutas: POST /login, POST /register, GET /me
    app.register_blueprint(despacho_bp)   # Rutas: POST /despacho/horario, /frecuencias, /tipo-vehiculo, etc.
    app.register_blueprint(alertas_bp)    # Rutas: CRUD de alertas bajo /monitoreo/alertas

    # Aplica las reglas de Rate Limiting a las funciones de vista de autenticación
    if "login_bp.login" in app.view_functions:
        limiter.limit("5 per minute")(app.view_functions["login_bp.login"])      # Máximo 5 intentos por min
    if "login_bp.register" in app.view_functions:
        limiter.limit("3 per minute")(app.view_functions["login_bp.register"])   # Máximo 3 registros por min

    # --------------------------------------------------------------------------
    # MANEJADOR DE ERROR HTTP 429 (TOO MANY REQUESTS)
    # --------------------------------------------------------------------------
    @app.errorhandler(429)
    def ratelimit_error(e):
        return jsonify({
            "success": False,
            "error":   "Demasiadas peticiones",
            "mensaje": str(e.description),
            "limite":  "Maximo 5 intentos de login por minuto por IP."
        }), 429

    # --------------------------------------------------------------------------
    # ENDPOINT RAÍZ (SERVICE DISCOVERY)
    # --------------------------------------------------------------------------
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "servicio":  "MS4: PROGRAMACION Y DESPACHO OPERATIVO (REST)",
            "ciudad":    "Popayan, Cauca",
            "puerto":    Config.SERVER_PORT,
            "seguridad": {
                "rate_limit": "5 intentos de login por minuto por IP",
                "jwt":        "Authorization: Bearer <token>  (expira 24h)",
            },
            "auth": {
                "login":    "POST /login               (publica, rate limit 5/min)",
                "register": "POST /register            (publica como USUARIO, rate limit 3/min)",
                "perfil":   "GET  /me                  (protegida)"
            },
            "funcionalidades": {
                "1_tabla_horaria":      "POST /despacho/horario           (protegida)",
                "2_frecuencias":        "POST /despacho/frecuencias        (protegida)",
                "3_tipo_vehiculo":      "POST /despacho/tipo-vehiculo      (protegida)",
                "4_descanso_terminal":  "POST /despacho/descanso-terminal  (protegida)",
                "5_rotacion_conductor": "POST /despacho/rotacion-conductor (protegida)"
            },
            "alertas_monitoreo": {
                "crear":      "POST   /monitoreo/alertas            (protegida)",
                "listar":     "GET    /monitoreo/alertas            (protegida)",
                "obtener":    "GET    /monitoreo/alertas/<id>       (protegida)",
                "actualizar": "PUT    /monitoreo/alertas/<id>       (protegida)",
                "eliminar":   "DELETE /monitoreo/alertas/<id>       (protegida)"
            },
            "estado": "ACTIVO"
        }), 200

    # Manejo de ruta no encontrada
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Ruta no encontrada"}), 404

    # Manejo de error interno no capturado
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

    return app


# Instancia principal de la aplicación Flask
app = create_app()
