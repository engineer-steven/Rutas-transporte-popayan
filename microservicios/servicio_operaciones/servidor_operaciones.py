# -*- coding: utf-8 -*-
"""
==============================================================================
MICROSERVICIO 2: OPERACIONES, INTERVALOS DE TIEMPO E INCIDENCIAS (SOAP)
==============================================================================
Puerto asignado: 8002
WSDL: http://127.0.0.1:8002/?wsdl
Espacio de nombres (Namespace): 'popayan.transporte.operaciones'

DESCRIPCIÓN:
    Este microservicio SOAP gestiona la lógica operativa del transporte:
    cálculo de intervalos de tiempo entre buses, consulta de paraderos
    y reporte/consulta de incidencias viales en Popayán.

OPERACIONES QUE DEBE IMPLEMENTAR:
    1. calculate_bus_time_difference(ctx, route_id, bus_plate_1, bus_plate_2):
       - Consulta en la tabla 'dispatches' las horas de salida de dos buses en una ruta.
       - Calcula los minutos exactos de diferencia entre ambos despachos.
       - Retorna un objeto 'BusTimeDifferenceResult' con las placas, horas y minutos calculados.
    
    2. calculate_time_gap(ctx, time_1, time_2):
       - Función calculadora directa: recibe dos horas en formato texto (ej: '10:00:00' y '10:18:00')
         y retorna el número entero de minutos de diferencia.
    
    3. get_stops_by_route(ctx, route_id):
       - Consulta los paraderos asociados a una ruta ordenados por su campo 'stop_order'.
       - Retorna un Iterable de objetos 'Stop'.
    
    4. report_incident(ctx, route_id, incident_type, description, reported_by):
       - Registra un reporte o alerta ciudadana/operativa en la tabla 'incidents'
         (ej: congestión en La Esmeralda, accidente en Campanario, etc.).
       - Retorna un booleano (True/False) indicando éxito.
    
    5. get_incidents_by_route(ctx, route_id):
       - Consulta las incidencias activas reportadas para una ruta específica.
       - Retorna un Iterable de objetos 'Incident'.

INSTRUCCIONES DE CONEXIÓN Y SERVIDOR:
    - Usar la función 'get_db_connection' de 'base_de_datos.conexion_bd'.
    - Configurar la aplicación Spyne usando Soap11 y empaquetarla con WsgiApplication.
    - Levantar el servidor WSGI con 'wsgiref.simple_server.make_server' en '127.0.0.1', puerto 8002.
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

# TODO: Importar librerías de Spyne y WSGI:
# from spyne import Application, rpc, ServiceBase, Integer, Unicode, Boolean, Iterable, ComplexModel
# from spyne.protocol.soap import Soap11
# from spyne.server.wsgi import WsgiApplication
# from wsgiref.simple_server import make_server


# ==============================================================================
# MODELOS DE DATOS SOAP
# ==============================================================================

# TODO: Definir el modelo 'Stop' (Paradero):
# class Stop(ComplexModel):
#     __namespace__ = 'popayan.transporte.operaciones'
#     id = Integer
#     route_id = Integer
#     name = Unicode
#     landmark_reference = Unicode
#     stop_order = Integer

# TODO: Definir el modelo 'Incident' (Incidencia o alerta vial):
# class Incident(ComplexModel):
#     __namespace__ = 'popayan.transporte.operaciones'
#     id = Integer
#     route_id = Integer
#     incident_type = Unicode
#     description = Unicode
#     reported_by = Unicode
#     reported_at = Unicode
#     status = Unicode

# TODO: Definir el modelo 'BusTimeDifferenceResult' (Resultado de diferencia de tiempos):
# class BusTimeDifferenceResult(ComplexModel):
#     __namespace__ = 'popayan.transporte.operaciones'
#     route_id = Integer
#     bus_plate_1 = Unicode
#     departure_time_1 = Unicode
#     bus_plate_2 = Unicode
#     departure_time_2 = Unicode
#     difference_minutes = Integer
#     summary_message = Unicode


# ==============================================================================
# SERVICIO SOAP: OperationsService
# ==============================================================================
# TODO: Definir la clase del servicio que hereda de ServiceBase:
# class OperationsService(ServiceBase):

    # --------------------------------------------------------------------------
    # OPERACIÓN 1: Diferencia de tiempo entre despachos de dos buses
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Integer, Unicode, Unicode, _returns=BusTimeDifferenceResult)
    # def calculate_bus_time_difference(ctx, route_id, bus_plate_1, bus_plate_2):
    #     """
    #     TODO: Consultar la hora de salida de bus_plate_1 y bus_plate_2 para la ruta dada.
    #     Calcular la diferencia absoluta en minutos y retornar el objeto BusTimeDifferenceResult.
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 2: Calculadora de diferencia entre dos horas en texto
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Unicode, Unicode, _returns=Integer)
    # def calculate_time_gap(ctx, time_1, time_2):
    #     """
    #     TODO: Parsear ambas cadenas de tiempo (ejemplo '10:00:00' y '10:25:00'),
    #     restar los segundos correspondientes y retornar la diferencia en minutos enteros.
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 3: Listar paraderos ordenados de una ruta
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Integer, _returns=Iterable(Stop))
    # def get_stops_by_route(ctx, route_id):
    #     """
    #     TODO: Consultar la tabla 'stops' donde route_id = %s ORDER BY stop_order ASC.
    #     Iterar los resultados y retornar instancias de Stop.
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 4: Reportar un incidente o alerta en la ruta
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Integer, Unicode, Unicode, Unicode, _returns=Boolean)
    # def report_incident(ctx, route_id, incident_type, description, reported_by):
    #     """
    #     TODO: Ejecutar INSERT INTO incidents (route_id, incident_type, description, reported_by)
    #     VALUES (...), confirmar con commit() y retornar True.
    #     """
    #     pass

    # --------------------------------------------------------------------------
    # OPERACIÓN 5: Consultar incidentes activos de una ruta
    # --------------------------------------------------------------------------
    # TODO: Decorar con @rpc(Integer, _returns=Iterable(Incident))
    # def get_incidents_by_route(ctx, route_id):
    #     """
    #     TODO: Consultar la tabla 'incidents' filtrando por route_id y status = 'ACTIVO'.
    #     Iterar y retornar objetos Incident.
    #     """
    #     pass


# ==============================================================================
# INICIALIZACIÓN DEL SERVIDOR WSGI (PUERTO 8002)
# ==============================================================================
if __name__ == '__main__':
    print("=" * 65)
    print(" MICROSERVICIO 2: OPERACIONES Y TIEMPOS DE TRANSPORTE (SOAP)")
    print(" Puerto: 8002 | WSDL: http://127.0.0.1:8002/?wsdl")
    print("=" * 65)

    # TODO: Crear la aplicación Spyne:
    # app = Application(
    #     [OperationsService],
    #     tns='popayan.transporte.operaciones',
    #     in_protocol=Soap11(validator='lxml'),
    #     out_protocol=Soap11()
    # )

    # TODO: Empaquetar con WSGI y levantar el servidor make_server en el puerto 8002:
    # wsgi_app = WsgiApplication(app)
    # server = make_server('127.0.0.1', 8002, wsgi_app)
    # print("Servidor de operaciones escuchando en http://127.0.0.1:8002/?wsdl")
    # server.serve_forever()
