# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/server.py
# RESPONSABILIDAD: Punto de entrada ejecutable para arrancar el Microservicio 2.
# PUERTO: 5002
# ==============================================================================

# Importa el módulo sys para controlar el PYTHONPATH y la salida estándar.
import sys

# Importa os para manipulación de rutas en el sistema de archivos.
import os

# Obtiene la ruta del directorio del servicio actual.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Añade el directorio al PYTHONPATH para resolver módulos internos.
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Importa los parámetros de configuración de red.
from config import Config

# Importa la aplicación Flask ensamblada con sus endpoints de operaciones.
from app import app


def main():
    """Función de arranque del servidor HTTP de Operaciones."""

    # Reconfigura la salida estándar de terminal a UTF-8 si es compatible.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Imprime el menú informativo en la consola con los endpoints disponibles en el puerto 5002.
    print("\n" + "=" * 76)
    print(" MS2: OPERACIONES EN VIA E INCIDENTES - REST/Flask (Puerto 5002)")
    print("=" * 76)
    print(f" URL base:   http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    print(" Seguridad:  X-API-KEY: 123  o  Authorization: Bearer <token>")
    print(" Login:      POST http://127.0.0.1:5003/api/v1/auth/login")
    print(" Operaciones:GET  /operaciones/diferencia-buses?route_id=ID&bus1=P1&bus2=P2")
    print("             GET  /operaciones/diferencia-horas?hora1=HH:MM&hora2=HH:MM")
    print("             GET  /operaciones/paraderos/<route_id>")
    print("             POST /operaciones/incidente")
    print("             GET  /operaciones/incidentes/<route_id>")
    print("=" * 76 + "\n")

    # Inicia el servidor Flask en el host y puerto 5002.
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=False)


# Punto de entrada directo del script.
if __name__ == "__main__":
    main()
