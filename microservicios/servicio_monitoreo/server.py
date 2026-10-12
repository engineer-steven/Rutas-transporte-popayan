import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import Config
from app import app


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

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

    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=False)


if __name__ == "__main__":
    main()
