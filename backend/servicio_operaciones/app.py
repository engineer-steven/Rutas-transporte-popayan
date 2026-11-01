# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/app.py
# RESPONSABILIDAD: Ensamblar la aplicación Flask para operaciones en vía y registrar errores.
# PATRÓN: Application Factory Pattern (create_app).
# ==============================================================================

# Importa sys para configuración de rutas del intérprete.
import sys

# Importa os para manipulación del sistema de archivos.
import os

# Obtiene la ruta de este directorio.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Agrega el directorio a la lista de módulos de Python.
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Importa Flask y jsonify para construir la API REST.
from flask import Flask, jsonify

# Importa CORS para permitir peticiones HTTP desde orígenes cruzados.
from flask_cors import CORS

# Importa la configuración de puertos y credenciales.
from config import Config

# Importa el Blueprint de operaciones e incidentes viales.
from routes.operaciones import operaciones_bp


def create_app():
    """Fábrica de aplicación Flask: inicializa middlewares y monta rutas de operaciones."""

    # Crea la instancia principal de Flask.
    app = Flask(__name__)

    # Activa soporte para CORS en todas las rutas.
    CORS(app)

    # Registra el módulo de operaciones bajo el prefijo /operaciones.
    app.register_blueprint(operaciones_bp)

    # Ruta raíz que provee el catálogo descriptivo del servicio de operaciones.
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "servicio": "MICROSERVICIO 2: OPERACIONES EN VIA E INCIDENTES (REST)",
            "puerto": Config.SERVER_PORT,
            "seguridad": "X-API-KEY: 123  o  Authorization: Bearer <token>",
            "login_para_token": "POST http://127.0.0.1:5003/login",
            "blueprint": "/operaciones",
            "endpoints": {
                "GET  /operaciones/diferencia-buses": "Calcular intervalo entre 2 buses (?route_id=ID&bus1=P1&bus2=P2)",
                "GET  /operaciones/diferencia-horas": "Calcular brecha horaria (?hora1=HH:MM&hora2=HH:MM)",
                "GET  /operaciones/paraderos/<id>":   "Listar paraderos secuenciales de una ruta",
                "POST /operaciones/incidente":        "Reportar nuevo incidente vial",
                "GET  /operaciones/incidentes/<id>":  "Listar incidentes activos de una ruta"
            }
        }), 200

    # Manejo centralizado del código de error HTTP 404 (Endpoint o recurso no encontrado).
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Ruta no encontrada"}), 404

    # Manejo centralizado del código de error HTTP 500 (Error interno del servidor).
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

    # Retorna la aplicación configurada.
    return app


# Crea la instancia exportable de la aplicación.
app = create_app()
