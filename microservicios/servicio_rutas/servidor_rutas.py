# -*- coding: utf-8 -*-
"""
==============================================================================
MICROSERVICIO 1: GESTIÓN Y CONSULTA DE RUTAS (SOAP)
==============================================================================
Puerto asignado: 8001
WSDL: http://127.0.0.1:8001/?wsdl
Espacio de nombres (Namespace): 'popayan.transporte.rutas'

DESCRIPCIÓN:
    Este microservicio SOAP expone operaciones CRUD y de búsqueda para las
    rutas de transporte público de la ciudad de Popayán.

OPERACIONES QUE DEBE IMPLEMENTAR:
    1. get_all_routes(ctx):
       - Consulta todas las rutas registradas en la base de datos.
       - Retorna una lista o Iterable de objetos 'Route'.
    
    2. get_route_by_id(ctx, route_id):
       - Busca una ruta específica por su identificador primario (ID).
       - Retorna el objeto 'Route' si existe, o None si no se encuentra.
    
    3. search_routes_by_zone(ctx, zone_keyword):
       - Busca rutas cuyo origen, destino o paraderos coincidan con una palabra clave
         (ejemplo: 'Campanario', 'Centro', 'Terminal', 'Bello Horizonte').
       - Retorna la lista de rutas coincidentes.
    
    4. add_route(ctx, code, company, origin, destination, fare, schedule):
       - Inserta una nueva ruta en la tabla 'routes'.
       - Retorna un booleano (True/False) o mensaje indicando si el registro fue exitoso.

INSTRUCCIONES DE CONEXIÓN Y SERVIDOR:
    - Usar la función 'get_db_connection' de 'base_de_datos.conexion_bd'.
    - Configurar la aplicación Spyne usando Soap11 y empaquetarla con WsgiApplication.
    - Levantar el servidor WSGI con 'wsgiref.simple_server.make_server' en '127.0.0.1', puerto 8001.
==============================================================================
"""

import os
import sys

# Asegurar importación de módulos del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# TODO: Importar la conexión a la base de datos
# from base_de_datos.conexion_bd import get_db_connection

# TODO: Importar los módulos de Spyne necesarios:
# from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float, Boolean, Iterable, ComplexModel
# from spyne.protocol.soap import Soap11
# from spyne.server.wsgi import WsgiApplication
# from wsgiref.simple_server import make_server


# ==============================================================================
# MODELO DE DATOS SOAP: Route
# ==============================================================================
# TODO: Definir el modelo complejo 'Route' que herede de ComplexModel.
# Debe tener el namespace 'popayan.transporte.rutas' y los siguientes atributos:
#   - id (Integer)
#   - code (Unicode)
#   - company (Unicode)
#   - origin (Unicode)
#   - destination (Unicode)
#   - fare (Float)
#   - schedule (Unicode)
#   - status (Unicode)

# class Route(ComplexModel):
#     __namespace__ = 'popayan.transporte.rutas'
#     # Definir los campos aquí
#     pass


# ==============================================================================
# SERVICIO SOAP: RoutesService
# ==============================================================================
# TODO: Definir la clase del servicio que hereda de ServiceBase:
# class RoutesService(ServiceBase):

    # --------------------------------------------------------------------------
    # OPERACIÓN 1: Obtener todas las rutas
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(_returns=Iterable(Route))
    # def get_all_routes(ctx):
    #     """
    #     TODO: Conectar a MySQL, ejecutar SELECT sobre 'routes',
    #     iterar los resultados y hacer yield o return de objetos Route.
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 2: Obtener ruta por ID
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Integer, _returns=Route)
    # def get_route_by_id(ctx, route_id):
    #     """
    #     TODO: Consultar la tabla 'routes' filtrando por WHERE id = %s.
    #     Si existe, retornar la instancia de Route con sus datos.
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 3: Buscar rutas por sector / zona clave
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Unicode, _returns=Iterable(Route))
    # def search_routes_by_zone(ctx, zone_keyword):
    #     """
    #     TODO: Buscar rutas donde origin, destination o sus paraderos asociados
    #     contengan la palabra clave recibida (usando LIKE %keyword%).
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 4: Registrar una nueva ruta
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Unicode, Unicode, Unicode, Unicode, Float, Unicode, _returns=Boolean)
    # def add_route(ctx, code, company, origin, destination, fare, schedule):
    #     """
    #     TODO: Ejecutar INSERT INTO routes (...) VALUES (...).
    #     Hacer commit de la transacción y retornar True si se insertó correctamente.
    #     """
    #     pass


# ==============================================================================
# INICIALIZACIÓN DEL SERVIDOR WSGI (PUERTO 8001)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 65)
    print(" MICROSERVICIO 1: RUTAS DE TRANSPORTE POPAYÁN (SOAP)")
    print(" Puerto: 8001 | WSDL: http://127.0.0.1:8001/?wsdl")
    print("=" * 65)

    # TODO: Crear la aplicación Spyne:
    # app = Application(
    #     [RoutesService],
    #     tns='popayan.transporte.rutas',
    #     in_protocol=Soap11(validator='lxml'),
    #     out_protocol=Soap11()
    # )

    # TODO: Empaquetar con WSGI y levantar el servidor make_server en el puerto 8001:
    # wsgi_app = WsgiApplication(app)
    # server = make_server('127.0.0.1', 8001, wsgi_app)
    # print("Servidor de rutas escuchando en http://127.0.0.1:8001/?wsdl")
    # server.serve_forever()
