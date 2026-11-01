# ==============================================================================
# ARCHIVO: backend/servicio_rutas/app.py
# RESPONSABILIDAD: Ensamblar la aplicación Flask, registrar Blueprints y errores HTTP.
# PATRÓN: Application Factory Pattern (create_app).
# ==============================================================================

# Importa el módulo sys para controlar el PYTHONPATH en tiempo de ejecución.
import sys

# Importa el módulo os para localizar directorios de trabajo.
import os

# Obtiene la ruta del directorio del servicio actual.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegura que las importaciones relativas (config, routes, etc.) funcionen sin importar desde dónde se invoque.
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Importa la clase principal del framework web Flask y la utilidad jsonify.
from flask import Flask, jsonify

# Importa CORS para permitir peticiones HTTP desde clientes web en otros orígenes o puertos.
from flask_cors import CORS

# Importa la clase de configuración de puertos y credenciales.
from config import Config

# Importa el Blueprint encargado de las operaciones CRUD de rutas.
from routes.rutas import rutas_bp

# Importa el Blueprint encargado de los 5 algoritmos de lógica no lineal.
from routes.logicas import logicas_bp


def create_app():
    """Fábrica de aplicación: instancia, configura y conecta componentes de Flask."""

    # Inicializa la instancia principal de la aplicación web Flask.
    app = Flask(__name__)

    # Habilita el intercambio de recursos de origen cruzado (Cross-Origin Resource Sharing).
    CORS(app)

    # Registra el módulo de rutas bajo el prefijo /rutas.
    app.register_blueprint(rutas_bp)

    # Registra el módulo de algoritmos bajo el prefijo /logicas.
    app.register_blueprint(logicas_bp)

    # Define el endpoint raíz '/' para verificación de estado y catálogo de servicios (Service Discovery).
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
                "GET  /logicas/comparar":             "Comparar eficiencia (?ruta1=ID&ruta2=ID)"
            }
        }), 200

    # Manejador global para el error HTTP 404 (Recurso no encontrado).
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Ruta no encontrada"}), 404

    # Manejador global para el error HTTP 500 (Fallo no controlado en el servidor).
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500

    # Retorna la aplicación configurada y lista para escuchar peticiones.
    return app


# Crea la instancia singleton de la aplicación para que server.py o gunicorn puedan servirla.
app = create_app()
