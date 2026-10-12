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
    print(" MS2: OPERACIONES E INCIDENCIAS - REST/Flask (Puerto 8002)")
    print("=" * 76)
    print(f" URL base:   http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    print(" Seguridad:  X-API-KEY: 123  o  Authorization: Bearer <token>")
    print(" Login:      POST http://127.0.0.1:5003/api/v1/auth/login")
    print(" Endpoints:")
    print("   GET  /operaciones/diferencia-buses  ?route_id=&bus1=&bus2=")
    print("   GET  /operaciones/diferencia-horas  ?hora1=HH:MM&hora2=HH:MM")
    print("   GET  /operaciones/paraderos/<id>")
    print("   POST /operaciones/incidente")
    print("   GET  /operaciones/incidentes/<id>")
    print("=" * 76 + "\n")

    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=False)

if __name__ == "__main__":
    main()
