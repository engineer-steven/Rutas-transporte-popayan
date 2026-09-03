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
    print(" 🚌 MICROSERVICIO 1: GESTIÓN DE RUTAS DE TRANSPORTE POPAYÁN (SOAP)")
    print("=" * 76)
    print(f" Servidor escuchando en: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/")
    print(f" WSDL disponible en:     http://{Config.SERVER_HOST}:{Config.SERVER_PORT}/?wsdl")
    print(" Espacio de nombres:     popayan.transporte.rutas")
    print(" Operaciones de Consulta y CRUD:")
    print("   1. get_all_routes()")
    print("   2. get_route_by_id(route_id)")
    print("   3. search_routes_by_zone(zone_keyword)")
    print("   4. add_route(code, company, origin, destination, fare, schedule)")
    print(" ⭐ 5 LÓGICAS NO PLANAS DISPONIBLES:")
    print("   1. plan_trip(origin_keyword, destination_keyword)")
    print("   2. suggest_transfer_trip(origin_keyword, destination_keyword)")
    print("   3. calculate_route_congestion_index(route_id)")
    print("   4. simulate_traffic_schedule(route_id, departure_hour)")
    print("   5. compare_routes_efficiency(route_id_1, route_id_2)")
    print("=" * 76)
    print(" Presione CTRL + C para detener el servidor.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor de rutas detenido por el usuario.")

if __name__ == "__main__":
    main()
