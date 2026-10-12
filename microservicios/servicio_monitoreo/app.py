import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from rutas.login import login_bp, init_limiter
from rutas.despacho import despacho_bp
from rutas.alertas import alertas_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # --------------------------------------------------------------------------
    # RATE LIMITER
    # Limita peticiones por IP para proteger el login de ataques de fuerza bruta.
    # Estrategia: memoria local (sin Redis). Para produccion usar Redis.
    # --------------------------------------------------------------------------
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[],          # Sin limite global; cada ruta define el suyo
        storage_uri="memory://"
    )

    # --------------------------------------------------------------------------
    # REGISTRO DE BLUEPRINTS
    # --------------------------------------------------------------------------
    app.register_blueprint(login_bp)      # POST /login, POST /register, GET /me
    app.register_blueprint(despacho_bp)   # POST /despacho/...
    app.register_blueprint(alertas_bp)    # PUT /monitoreo/alertas/<id>, DELETE /monitoreo/alertas/<id>

    # Limites por endpoint de autenticacion (despues de registrar blueprints)
    if "login_bp.login" in app.view_functions:
        limiter.limit("5 per minute")(app.view_functions["login_bp.login"])
    if "login_bp.register" in app.view_functions:
        limiter.limit("3 per minute")(app.view_functions["login_bp.register"])

    init_limiter(limiter)

    # --------------------------------------------------------------------------
    # MANEJADOR DE ERRORES DE RATE LIMIT (429)
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
    # RAIZ
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
                "api_key":    "X-API-Key: 123"
            },
            "auth": {
                "login":    "POST /login               (publica, rate limit 5/min)",
                "register": "POST /register            (protegida, rate limit 3/min)",
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

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Ruta no encontrada"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.SERVER_PORT, debug=True)