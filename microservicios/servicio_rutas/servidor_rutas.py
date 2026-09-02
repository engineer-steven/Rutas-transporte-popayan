# -*- coding: utf-8 -*-
"""
==============================================================================
MICROSERVICIO 1: GESTIÓN Y CONSULTA DE RUTAS DE TRANSPORTE PÚBLICO (SOAP)
==============================================================================
Responsable: Steven (feature/microservicio-rutas)
Puerto asignado: 8001
WSDL Endpoint: http://127.0.0.1:8001/?wsdl
Espacio de Nombres (Target Namespace): 'popayan.transporte.rutas'

DESCRIPCIÓN:
    Este microservicio expone operaciones web bajo el estándar SOAP 1.1 para
    la administración, consulta y búsqueda geo-referencial de rutas de transporte
    público colectivo en la ciudad de Popayán (Sotracauca, Transpubenza, Translibertad).

OPERACIONES DISPONIBLES:
    1. get_all_routes: Lista todas las rutas activas registradas.
    2. get_route_by_id: Consulta detallada de una ruta según su ID único.
    3. search_routes_by_zone: Búsqueda inteligente de rutas por palabras clave
       de sectores (ej: 'Campanario', 'Centro', 'Terminal', 'Bello Horizonte'),
       buscando tanto en origen/destino como en los paraderos asociados.
    4. add_route: Registra una nueva ruta en el sistema y base de datos.
==============================================================================
"""

import os
import sys
import logging
from wsgiref.simple_server import make_server

# ------------------------------------------------------------------------------
# 1. CONFIGURACIÓN DEL PATH DEL SISTEMA Y DEPENDENCIAS
# ------------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configuración de registro de eventos (Logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [Servicio-Rutas]: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('ServicioRutas')

# ------------------------------------------------------------------------------
# 2. GESTOR DE CONEXIÓN A BASE DE DATOS (CON FALLBACK RESILIENTE)
# ------------------------------------------------------------------------------
try:
    import pymysql
    import pymysql.cursors
except ImportError:
    logger.error("La librería 'pymysql' no está instalada. Ejecuta 'pip install pymysql'.")
    pymysql = None


def obtener_conexion_mysql():
    """
    Intenta importar y usar get_db_connection de base_de_datos.conexion_bd.
    Si el módulo no ha sido completado por el compañero de BD, utiliza una
    conexión directa resiliente con parámetros de entorno y valores por defecto.
    """
    # 1. Intentar usar el módulo del compañero
    try:
        from base_de_datos.conexion_bd import get_db_connection
        conn = get_db_connection()
        if conn is not None:
            return conn
    except Exception as err:
        logger.debug(f"Aviso al importar get_db_connection: {err}")

    # 2. Fallback de conexión directa si get_db_connection aún no retorna conexión
    if pymysql is None:
        raise RuntimeError("No se puede conectar a MySQL: falta librería 'pymysql'.")

    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', '19971020'),
        database=os.environ.get('DB_NAME', 'movi_popayan_db'),
        port=int(os.environ.get('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4',
        autocommit=False
    )


# ------------------------------------------------------------------------------
# 3. IMPORTACIÓN DE SPYNE PARA SERVICIO WEB SOAP
# ------------------------------------------------------------------------------
from spyne import (
    Application,
    rpc,
    ServiceBase,
    Integer,
    Unicode,
    Float,
    Boolean,
    Iterable,
    ComplexModel
)
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


# ------------------------------------------------------------------------------
# 4. MODELO DE DATOS SOAP (ComplexModel)
# ------------------------------------------------------------------------------
class Route(ComplexModel):
    """
    Representa una ruta de transporte público de Popayán en el contrato WSDL.
    """
    __namespace__ = 'popayan.transporte.rutas'

    id = Integer(doc="Identificador único de la ruta en la base de datos")
    code = Unicode(doc="Código comercial de la ruta (ej: RUTA-1, LINEA-2)")
    company = Unicode(doc="Empresa transportadora (ej: Sotracauca, Transpubenza)")
    origin = Unicode(doc="Punto de origen o despacho de la ruta")
    destination = Unicode(doc="Punto de destino final")
    fare = Float(doc="Tarifa oficial del pasaje en pesos colombianos")
    schedule = Unicode(doc="Horario de atención (ej: 05:30 - 21:00)")
    status = Unicode(doc="Estado de la ruta (ACTIVA, SUSPENDIDA)")


class TripPlanResult(ComplexModel):
    """
    Resultado detallado de la planificación de un viaje entre dos sectores de Popayán.
    """
    __namespace__ = 'popayan.transporte.rutas'

    found = Boolean(doc="Indica si se encontró una ruta directa disponible")
    origin_searched = Unicode(doc="Sector de origen ingresado")
    destination_searched = Unicode(doc="Sector de destino ingresado")
    recommended_route_code = Unicode(doc="Código de la ruta óptima sugerida (ej: RUTA-1)")
    company = Unicode(doc="Empresa de transporte prestadora (ej: Sotracauca)")
    boarding_stop = Unicode(doc="Paradero sugerido para abordar el bus")
    alighting_stop = Unicode(doc="Paradero sugerido para bajarse del bus")
    stops_count = Integer(doc="Cantidad de paradas intermedias en el trayecto")
    fare = Float(doc="Tarifa oficial a pagar en pesos colombianos")
    estimated_minutes = Integer(doc="Tiempo estimado de recorrido en minutos")
    trip_summary = Unicode(doc="Instrucción y resumen amigable para el pasajero")


# ------------------------------------------------------------------------------
# 5. DEFINICIÓN DEL SERVICIO SOAP Y OPERACIONES
# ------------------------------------------------------------------------------
class RoutesService(ServiceBase):
    """
    Servicio SOAP con las operaciones de consulta y administración de rutas.
    """

    # --------------------------------------------------------------------------
    # OPERACIÓN 1: Obtener todas las rutas activas
    # --------------------------------------------------------------------------
    @rpc(_returns=Iterable(Route))
    def get_all_routes(ctx):
        """
        Retorna la lista completa de rutas de transporte público en Popayán.
        """
        logger.info("[get_all_routes] Solicitud recibida.")
        conn = None
        try:
            conn = obtener_conexion_mysql()
            with conn.cursor() as cursor:
                sql = """
                    SELECT id, code, company, origin, destination, fare, schedule, status
                    FROM routes
                    WHERE status = 'ACTIVA' OR status IS NULL
                    ORDER BY id ASC
                """
                cursor.execute(sql)
                registros = cursor.fetchall()
                logger.info(f"[get_all_routes] Se encontraron {len(registros)} rutas.")

                for reg in registros:
                    yield Route(
                        id=int(reg['id']),
                        code=str(reg.get('code') or ''),
                        company=str(reg.get('company') or ''),
                        origin=str(reg.get('origin') or ''),
                        destination=str(reg.get('destination') or ''),
                        fare=float(reg['fare']) if reg.get('fare') is not None else 0.0,
                        schedule=str(reg.get('schedule') or ''),
                        status=str(reg.get('status') or 'ACTIVA')
                    )
        except Exception as e:
            logger.error(f"[get_all_routes] Error al consultar rutas: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    # --------------------------------------------------------------------------
    # OPERACIÓN 2: Obtener una ruta por su ID
    # --------------------------------------------------------------------------
    @rpc(Integer, _returns=Route)
    def get_route_by_id(ctx, route_id):
        """
        Busca y retorna una ruta específica según su identificador (ID).
        """
        logger.info(f"[get_route_by_id] Buscando ruta ID: {route_id}")
        conn = None
        try:
            conn = obtener_conexion_mysql()
            with conn.cursor() as cursor:
                sql = """
                    SELECT id, code, company, origin, destination, fare, schedule, status
                    FROM routes
                    WHERE id = %s
                    LIMIT 1
                """
                cursor.execute(sql, (route_id,))
                reg = cursor.fetchone()

                if not reg:
                    logger.warning(f"[get_route_by_id] Ruta ID {route_id} no encontrada.")
                    return None

                logger.info(f"[get_route_by_id] Ruta encontrada: {reg.get('code')} ({reg.get('company')})")
                return Route(
                    id=int(reg['id']),
                    code=str(reg.get('code') or ''),
                    company=str(reg.get('company') or ''),
                    origin=str(reg.get('origin') or ''),
                    destination=str(reg.get('destination') or ''),
                    fare=float(reg['fare']) if reg.get('fare') is not None else 0.0,
                    schedule=str(reg.get('schedule') or ''),
                    status=str(reg.get('status') or 'ACTIVA')
                )
        except Exception as e:
            logger.error(f"[get_route_by_id] Error en la consulta: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    # --------------------------------------------------------------------------
    # OPERACIÓN 3: Búsqueda de rutas por zona o punto de interés de Popayán
    # --------------------------------------------------------------------------
    @rpc(Unicode, _returns=Iterable(Route))
    def search_routes_by_zone(ctx, zone_keyword):
        """
        Busca rutas que pasen o conecten con un sector de Popayán
        (ej: Campanario, Centro, Terminal, Hospital San José, La Esmeralda).
        Busca en el origen, destino y también en paraderos de la ruta.
        """
        termino = str(zone_keyword or '').strip()
        logger.info(f"[search_routes_by_zone] Búsqueda por sector: '{termino}'")

        if not termino:
            return

        conn = None
        try:
            conn = obtener_conexion_mysql()
            with conn.cursor() as cursor:
                patron = f"%{termino}%"
                sql = """
                    SELECT DISTINCT r.id, r.code, r.company, r.origin, r.destination, 
                                    r.fare, r.schedule, r.status
                    FROM routes r
                    LEFT JOIN stops s ON r.id = s.route_id
                    WHERE r.origin LIKE %s 
                       OR r.destination LIKE %s 
                       OR s.name LIKE %s 
                       OR s.landmark_reference LIKE %s
                    ORDER BY r.id ASC
                """
                cursor.execute(sql, (patron, patron, patron, patron))
                filas = cursor.fetchall()
                logger.info(f"[search_routes_by_zone] Coincidencias encontradas: {len(filas)}")

                for reg in filas:
                    yield Route(
                        id=int(reg['id']),
                        code=str(reg.get('code') or ''),
                        company=str(reg.get('company') or ''),
                        origin=str(reg.get('origin') or ''),
                        destination=str(reg.get('destination') or ''),
                        fare=float(reg['fare']) if reg.get('fare') is not None else 0.0,
                        schedule=str(reg.get('schedule') or ''),
                        status=str(reg.get('status') or 'ACTIVA')
                    )
        except Exception as e:
            logger.error(f"[search_routes_by_zone] Error en la búsqueda: {e}")
            raise e
        finally:
            if conn:
                conn.close()

    # --------------------------------------------------------------------------
    # OPERACIÓN 4: Registrar una nueva ruta de transporte
    # --------------------------------------------------------------------------
    @rpc(Unicode, Unicode, Unicode, Unicode, Float, Unicode, _returns=Boolean)
    def add_route(ctx, code, company, origin, destination, fare, schedule):
        """
        Inserta una nueva ruta de transporte público en la base de datos MySQL.
        Retorna True si el registro fue exitoso, o False si falló.
        """
        logger.info(f"[add_route] Registrando nueva ruta: {code} | {company}")
        conn = None
        try:
            conn = obtener_conexion_mysql()
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO routes (code, company, origin, destination, fare, schedule, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVA')
                """
                cursor.execute(sql, (
                    str(code).strip(),
                    str(company).strip(),
                    str(origin).strip(),
                    str(destination).strip(),
                    float(fare) if fare is not None else 0.0,
                    str(schedule).strip()
                ))
            conn.commit()
            logger.info(f"[add_route] Ruta {code} registrada exitosamente en MySQL.")
            return True
        except Exception as e:
            logger.error(f"[add_route] Error al registrar ruta: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    # --------------------------------------------------------------------------
    # OPERACIÓN 5 (LÓGICA NO PLANA): Planificador Inteligente de Viajes
    # --------------------------------------------------------------------------
    @rpc(Unicode, Unicode, _returns=TripPlanResult)
    def plan_trip(ctx, origin_keyword, destination_keyword):
        """
        Algoritmo de planificación de viajes entre dos sectores de Popayán:
        1. Cruza los paraderos de las rutas para identificar trayectos directos.
        2. Valida la orientación del viaje: el bus debe pasar PRIMERO por el origen
           y DESPUÉS por el destino (s1.stop_order < s2.stop_order).
        3. Calcula la cantidad de paraderos intermedios entre ambos puntos.
        4. Estima el tiempo real de viaje (~4 min por paradero en tráfico de Popayán).
        5. Genera una recomendación detallada con tarifa, paradas y tiempo estimado.
        """
        orig = str(origin_keyword or '').strip()
        dest = str(destination_keyword or '').strip()
        logger.info(f"[plan_trip] Calculando viaje desde '{orig}' hacia '{dest}'...")

        if not orig or not dest:
            return TripPlanResult(
                found=False,
                origin_searched=orig,
                destination_searched=dest,
                trip_summary="Debes ingresar tanto el punto de origen como el punto de destino."
            )

        conn = None
        try:
            conn = obtener_conexion_mysql()
            with conn.cursor() as cursor:
                patron_orig = f"%{orig}%"
                patron_dest = f"%{dest}%"

                # 1. Búsqueda principal: Cruce de paraderos con orden direccional
                sql_paraderos = """
                    SELECT 
                        r.id AS route_id,
                        r.code AS route_code,
                        r.company,
                        r.fare,
                        s1.name AS origin_stop_name,
                        s1.stop_order AS origin_order,
                        s2.name AS destination_stop_name,
                        s2.stop_order AS destination_order,
                        (s2.stop_order - s1.stop_order) AS stops_between
                    FROM routes r
                    INNER JOIN stops s1 ON r.id = s1.route_id
                    INNER JOIN stops s2 ON r.id = s2.route_id
                    WHERE (s1.name LIKE %s OR s1.landmark_reference LIKE %s)
                      AND (s2.name LIKE %s OR s2.landmark_reference LIKE %s)
                      AND s1.stop_order < s2.stop_order
                      AND (r.status = 'ACTIVA' OR r.status IS NULL)
                    ORDER BY stops_between ASC, r.fare ASC
                    LIMIT 1
                """
                cursor.execute(sql_paraderos, (patron_orig, patron_orig, patron_dest, patron_dest))
                mejor_opcion = cursor.fetchone()

                # 2. Si no hay coincidencia en paraderos específicos, buscar por origen/destino de la ruta
                if not mejor_opcion:
                    sql_general = """
                        SELECT 
                            r.id AS route_id,
                            r.code AS route_code,
                            r.company,
                            r.fare,
                            r.origin AS origin_stop_name,
                            1 AS origin_order,
                            r.destination AS destination_stop_name,
                            6 AS destination_order,
                            5 AS stops_between
                        FROM routes r
                        WHERE r.origin LIKE %s
                          AND r.destination LIKE %s
                          AND (r.status = 'ACTIVA' OR r.status IS NULL)
                        LIMIT 1
                    """
                    cursor.execute(sql_general, (patron_orig, patron_dest))
                    mejor_opcion = cursor.fetchone()

                if mejor_opcion:
                    paradas = int(mejor_opcion.get('stops_between') or 1)
                    # Estimación de tráfico en Popayán: ~4 minutos por paradero (mínimo 10 min)
                    minutos_est = max(10, paradas * 4)
                    tarifa = float(mejor_opcion.get('fare') or 2800.0)
                    cod_ruta = str(mejor_opcion.get('route_code') or 'RUTA')
                    empresa = str(mejor_opcion.get('company') or 'Transporte Popayán')
                    parada_subida = str(mejor_opcion.get('origin_stop_name') or orig)
                    parada_bajada = str(mejor_opcion.get('destination_stop_name') or dest)

                    resumen = (
                        f"Toma la ruta {cod_ruta} ({empresa}) abordando en '{parada_subida}' "
                        f"y descendiendo en '{parada_bajada}'. El trayecto comprende {paradas} paradas "
                        f"con un tiempo estimado de {minutos_est} minutos. Tarifa oficial: ${tarifa:,.0f} COP."
                    )
                    logger.info(f"[plan_trip] Ruta óptima recomendada: {cod_ruta} ({empresa})")

                    return TripPlanResult(
                        found=True,
                        origin_searched=orig,
                        destination_searched=dest,
                        recommended_route_code=cod_ruta,
                        company=empresa,
                        boarding_stop=parada_subida,
                        alighting_stop=parada_bajada,
                        stops_count=paradas,
                        fare=tarifa,
                        estimated_minutes=minutos_est,
                        trip_summary=resumen
                    )
                else:
                    logger.warning(f"[plan_trip] No se halló ruta directa entre '{orig}' y '{dest}'.")
                    return TripPlanResult(
                        found=False,
                        origin_searched=orig,
                        destination_searched=dest,
                        trip_summary=(
                            f"No se encontró una ruta directa entre '{orig}' y '{dest}'. "
                            f"Te sugerimos tomar una ruta hacia el Centro o el Parque Caldas de Popayán "
                            f"para realizar un transbordo."
                        )
                    )
        except Exception as e:
            logger.error(f"[plan_trip] Error al planificar viaje: {e}")
            raise e
        finally:
            if conn:
                conn.close()


# ------------------------------------------------------------------------------
# 6. CONFIGURACIÓN Y PUESTA EN MARCHA DEL SERVIDOR WSGI (PUERTO 8001)
# ------------------------------------------------------------------------------
# Creación de la aplicación Spyne compatible con SOAP 1.1
application = Application(
    services=[RoutesService],
    tns='popayan.transporte.rutas',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# Empaquetado WSGI estándar de Python
wsgi_app = WsgiApplication(application)


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8001

    print("\n" + "=" * 75)
    print(" 🚌 MICROSERVICIO 1: GESTIÓN DE RUTAS DE TRANSPORTE POPAYÁN (SOAP)")
    print("=" * 75)
    print(f" Servidor escuchando en: http://{HOST}:{PORT}/")
    print(f" WSDL disponible en:     http://{HOST}:{PORT}/?wsdl")
    print(" Espacio de nombres:     popayan.transporte.rutas")
    print(" Operaciones activas:")
    print("   1. get_all_routes()")
    print("   2. get_route_by_id(route_id)")
    print("   3. search_routes_by_zone(zone_keyword)")
    print("   4. add_route(code, company, origin, destination, fare, schedule)")
    print("   5. plan_trip(origin_keyword, destination_keyword)  [⭐ Lógica No Plana]")
    print("=" * 75)
    print(" Presione CTRL + C para detener el servidor.\n")

    try:
        server = make_server(HOST, PORT, wsgi_app)
        logger.info(f"Iniciando servidor WSGI en puerto {PORT}...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor detenido por el usuario.")
    except Exception as e:
        logger.critical(f"[!] Error crítico en el servidor: {e}")
