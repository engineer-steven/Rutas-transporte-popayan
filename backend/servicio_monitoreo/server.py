# ==============================================================================
# ARCHIVO: backend/servicio_monitoreo/server.py
# RESPONSABILIDAD: Punto de entrada ejecutable para arrancar el Microservicio 3.
# PUERTO: 5003
# ==============================================================================

# Importa sys para gestión de entorno y consola.
import sys

# Importa os para rutas del sistema de archivos.
import os

# Obtiene la ruta del directorio del servicio actual.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegura que el directorio actual esté en sys.path para importaciones locales.
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Importa la configuración del microservicio (puerto 5003).
from config import Config

# Importa la aplicación Flask ensamblada con Rate Limiting y Blueprints.
from app import app


def main():
    """Función de arranque principal del servidor HTTP de Monitoreo y Despacho."""

    # Ajusta la codificación a UTF-8 si la consola de Windows lo admite.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Imprime en la consola el banner informativo con todos los endpoints disponibles.
    print("\n" + "=" * 76)
    print(" MS4: PROGRAMACION Y DESPACHO OPERATIVO - REST/Flask (Puerto 5003)")
    print("=" * 76)
    print(f" URL base:   http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    print(" Seguridad:  X-API-Key: 123  o  Authorization: Bearer <token>")
    print(" Login:      POST http://{}:{}/login".format(Config.SERVER_HOST, Config.SERVER_PORT))
    print(" Funcionalidades:")
    print("   POST /despacho/horario           -> Tabla horaria por tipo de dia")
    print("   POST /despacho/frecuencias       -> Frecuencias minimas por demanda")
    print("   POST /despacho/tipo-vehiculo     -> Asignacion de vehiculo")
    print("   POST /despacho/descanso-terminal -> Descanso reglamentario")
    print("   POST /despacho/rotacion-conductor-> Optimizador de rotacion")
    print(" Alertas y Monitoreo:")
    print("   POST   /monitoreo/alertas        -> Generar nueva alerta de emergencia")
    print("   GET    /monitoreo/alertas        -> Listar todas las alertas")
    print("   GET    /monitoreo/alertas/<id>   -> Detalle de alerta por ID")
    print("   PUT    /monitoreo/alertas/<id>   -> Actualizar alerta (estado, descripcion)")
    print("   DELETE /monitoreo/alertas/<id>   -> Eliminar alerta de emergencia")
    print("=" * 76 + "\n")

    # Inicia el servidor web Flask en el puerto 5003.
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=False)


# Bloque de ejecución principal.
if __name__ == "__main__":
    main()
