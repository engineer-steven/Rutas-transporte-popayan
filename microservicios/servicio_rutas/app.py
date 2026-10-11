import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from rutas.rutas import rutas_bp
from rutas.logicas import logicas_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Registro de Blueprints
    app.register_blueprint(rutas_bp)
    app.register_blueprint(logicas_bp)

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "servicio": "MICROSERVICIO 1: GESTION DE RUTAS (REST)",
            "puerto": Config.SERVER_PORT,
            "seguridad": "X-API-KEY: 123  o  Authorization: Bearer <token>",
            "login_para_token": "POST http://127.0.0.1:5003/login",
            "blueprints": {
                "rutas_bp":   "/rutas",
                "logicas_bp": "/logicas"
            },
            "endpoints": {
                "GET  /rutas":                       "Listar todas las rutas activas",
                "GET  /rutas/<id>":                  "Obtener ruta por ID",
                "GET  /rutas/buscar?zona=<kw>":      "Buscar rutas por zona",
                "POST /rutas":                       "Crear nueva ruta",
                "PUT  /rutas/<id>":                  "Actualizar ruta",
                "DELETE /rutas/<id>":                "Eliminar ruta",
                "GET  /logicas/viaje-directo":       "Planificar viaje directo (origin, destination)",
                "GET  /logicas/viaje-transbordo":    "Planificar viaje con transbordo",
                "GET  /logicas/congestion/<id>":     "Indice de congestion de ruta",
                "GET  /logicas/trafico/<id>":        "Simulador por franja horaria (?hora=HH:MM)",
                "GET  /logicas/comparar":            "Comparar eficiencia (?ruta1=ID&ruta2=ID)"
            }
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