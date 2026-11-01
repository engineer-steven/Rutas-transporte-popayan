# ==============================================================================
# ARCHIVO: backend/servicio_rutas/server.py
# RESPONSABILIDAD: Punto de entrada ejecutable para arrancar el Microservicio 1.
# PUERTO: 5001
# ==============================================================================

# Importa el módulo sys para configurar rutas del intérprete y codificación de consola.
import sys

# Importa el módulo os para resolver rutas de directorios absolutas.
import os

# Obtiene la ruta absoluta de la carpeta donde reside este archivo server.py.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Si el directorio actual no está en la lista de búsqueda de módulos de Python, lo inserta de primero.
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Importa la configuración de red y base de datos.
from config import Config

# Importa la aplicación Flask ensamblada con sus Blueprints.
from app import app


def main():
    """Función de arranque principal del servidor HTTP."""

    # Verifica si la salida estándar soporta reconfiguración de codificación UTF-8 (útil en Windows PowerShell).
    if hasattr(sys.stdout, "reconfigure"):
        try:
            # Fuerza a la terminal a escribir texto en UTF-8 para soportar tildes y caracteres especiales.
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            # Si falla la reconfiguración en la terminal, continúa sin detener el proceso.
            pass

    # Imprime el banner informativo en la consola con la lista de endpoints y documentación rápida.
    print("\n" + "=" * 76)
    print(" MS1: GESTION DE RUTAS - REST/Flask (Puerto 5001)")
    print("=" * 76)
    print(f" URL base:   http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    print(" Seguridad:  X-API-KEY: 123  o  Authorization: Bearer <token>")
    print(" Login:      POST http://127.0.0.1:5003/api/v1/auth/login")
    print(" CRUD:       GET/POST/PUT/DELETE /rutas")
    print(" Logicas:    GET /logicas/viaje-directo")
    print("             GET /logicas/viaje-transbordo")
    print("             GET /logicas/congestion/<id>")
    print("             GET /logicas/trafico/<id>?hora=HH:MM")
    print("             GET /logicas/comparar?ruta1=ID&ruta2=ID")
    print("=" * 76 + "\n")

    # Inicia el bucle de eventos del servidor HTTP en el host y puerto especificados.
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=False)


# Bloque de ejecución directa de Python: solo se ejecuta si se corre este script como programa principal.
if __name__ == "__main__":
    main()
