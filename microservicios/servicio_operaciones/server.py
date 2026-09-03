import sys
import os
from wsgiref.simple_server import make_server
from spyne.server.wsgi import WsgiApplication

# Asegurar path local para importaciones directas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import Config
from service import application

def main():
    wsgi_app = WsgiApplication(application)
    server = make_server(Config.SERVER_HOST, Config.SERVER_PORT, wsgi_app)

    print("\n" + "=" * 76)
    print(" ⏱️  MICROSERVICIO 2: OPERACIONES, INTERVALOS E INCIDENCIAS (SOAP)")
    print("=" * 76)
    print(f" Servidor escuchando en: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    print(f" WSDL disponible en:     http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/?wsdl")
    print(" Espacio de nombres:     popayan.transporte.operaciones")
    print(" Operaciones Disponibles:")
    print("   1. calculate_bus_time_difference(route_id, bus_plate_1, bus_plate_2)")
    print("   2. calculate_time_gap(time_1, time_2)")
    print("   3. get_stops_by_route(route_id)")
    print("   4. report_incident(route_id, incident_type, description, reported_by)")
    print("   5. get_incidents_by_route(route_id)")
    print("=" * 76)
    print(" Presione CTRL + C para detener el servidor.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor de operaciones detenido por el usuario.")

if __name__ == "__main__":
    main()
