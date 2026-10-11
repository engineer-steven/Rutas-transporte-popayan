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
    print(" MS1: GESTION DE RUTAS - REST/Flask (Puerto 8001)")
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

    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT, debug=False)

if __name__ == "__main__":
    main()
