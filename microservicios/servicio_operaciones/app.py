import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from rutas.operaciones import operaciones_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Registro de Blueprints
    app.register_blueprint(operaciones_bp)

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "servicio": "MICROSERVICIO 2: OPERACIONES E INCIDENCIAS (REST)",
            "puerto": Config.SERVER_PORT,
            "seguridad": "X-API-KEY: 123  o  Authorization: Bearer <token>",
            "login_para_token": "POST http://127.0.0.1:5003/login",
            "blueprints": {
                "operaciones_bp": "/operaciones"
            },
            "endpoints": {
                "GET  /operaciones/diferencia-buses":     "Diferencia de tiempo entre dos buses (?route_id=&bus1=&bus2=)",
                "GET  /operaciones/diferencia-horas":     "Diferencia en minutos entre dos horas (?hora1=HH:MM&hora2=HH:MM)",
                "GET  /operaciones/paraderos/<route_id>": "Listar paraderos de una ruta",
                "POST /operaciones/incidente":            "Reportar incidente vial",
                "GET  /operaciones/incidentes/<route_id>":"Consultar incidentes activos"
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