# -*- coding: utf-8 -*-


from datetime import datetime
from wsgiref.simple_server import make_server
from spyne import (
    Application,
    ServiceBase,
    rpc,
    Integer,
    Unicode,
    Array,
    ComplexModel,
)

from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from base_de_datos.conexion_bd import get_db_connection


# ============================================================
# MODELO SOAP: Stop
# ============================================================

class Stop(ComplexModel):
    id = Integer
    route_id = Integer
    name = Unicode
    landmark_reference = Unicode
    stop_order = Integer


# ============================================================
# MODELO SOAP: Incident
# ============================================================

class Incident(ComplexModel):
    id = Integer
    route_id = Integer
    incident_type = Unicode
    description = Unicode
    reported_by = Unicode
    reported_at = Unicode
    status = Unicode


# ============================================================
# MODELO SOAP: BusTimeDifferenceResult
# ============================================================

class BusTimeDifferenceResult(ComplexModel):
    bus_plate_1 = Unicode
    bus_plate_2 = Unicode
    departure_time_1 = Unicode
    departure_time_2 = Unicode
    difference_minutes = Integer


# ============================================================
# MODELO SOAP: RouteStatus
# ============================================================

class RouteStatus(ComplexModel):
    route_id = Integer
    status = Unicode
    active_incidents_count = Integer


# ============================================================
# SERVICIO SOAP DE OPERACIONES
# ============================================================

class OperationsService(ServiceBase):

    # ========================================================
    # 1. CALCULAR DIFERENCIA ENTRE DOS BUSES
    # ========================================================

    @rpc(
        Integer,
        Unicode,
        Unicode,
        _returns=BusTimeDifferenceResult
    )
    def calculate_bus_time_difference(
        ctx,
        route_id,
        bus_plate_1,
        bus_plate_2
    ):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Buscar el primer bus
            cursor.execute(
                """
                SELECT departure_time
                FROM dispatches
                WHERE route_id = %s
                  AND bus_plate = %s
                ORDER BY departure_time DESC
                LIMIT 1
                """,
                (route_id, bus_plate_1)
            )

            resultado_1 = cursor.fetchone()

            # Buscar el segundo bus
            cursor.execute(
                """
                SELECT departure_time
                FROM dispatches
                WHERE route_id = %s
                  AND bus_plate = %s
                ORDER BY departure_time DESC
                LIMIT 1
                """,
                (route_id, bus_plate_2)
            )

            resultado_2 = cursor.fetchone()

            if not resultado_1:
                raise Exception(
                    f"No se encontró el bus {bus_plate_1} "
                    f"en la ruta {route_id}."
                )

            if not resultado_2:
                raise Exception(
                    f"No se encontró el bus {bus_plate_2} "
                    f"en la ruta {route_id}."
                )

            # DictCursor: acceder por nombre de columna
            hora_1 = resultado_1["departure_time"]
            hora_2 = resultado_2["departure_time"]

            # Diferencia absoluta en minutos
            diferencia = abs(
                (hora_1 - hora_2).total_seconds()
            ) / 60

            return BusTimeDifferenceResult(
                bus_plate_1=bus_plate_1,
                bus_plate_2=bus_plate_2,
                departure_time_1=str(hora_1),
                departure_time_2=str(hora_2),
                difference_minutes=int(diferencia)
            )

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 2. CALCULAR DIFERENCIA ENTRE DOS HORAS
    # ========================================================

    @rpc(
        Unicode,
        Unicode,
        _returns=Integer
    )
    def calculate_time_gap(ctx, time_1, time_2):

        try:
            formato = "%H:%M"

            hora_1 = datetime.strptime(
                time_1,
                formato
            )

            hora_2 = datetime.strptime(
                time_2,
                formato
            )

            diferencia = abs(
                (hora_1 - hora_2).total_seconds()
            ) / 60

            return int(diferencia)

        except ValueError:
            raise Exception(
                "Las horas deben tener el formato HH:MM."
            )


    # ========================================================
    # 3. OBTENER PARADEROS DE UNA RUTA
    # ========================================================

    @rpc(
        Integer,
        _returns=Array(Stop)
    )
    def get_stops_by_route(ctx, route_id):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que la ruta exista
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            ruta = cursor.fetchone()

            if not ruta:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            # Obtener paraderos ordenados por trayecto
            cursor.execute(
                """
                SELECT
                    id,
                    route_id,
                    name,
                    landmark_reference,
                    stop_order
                FROM stops
                WHERE route_id = %s
                ORDER BY stop_order ASC
                """,
                (route_id,)
            )

            resultados = cursor.fetchall()

            paraderos = []

            for fila in resultados:

                paradero = Stop(
                    id=fila["id"],
                    route_id=fila["route_id"],
                    name=fila["name"],
                    landmark_reference=fila["landmark_reference"],
                    stop_order=fila["stop_order"]
                )

                paraderos.append(paradero)

            return paraderos

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 4. REPORTAR INCIDENTE
    # ========================================================

    @rpc(
        Integer,
        Unicode,
        Unicode,
        Unicode,
        Unicode,
        _returns=Incident
    )
    def report_incident(
        ctx,
        route_id,
        incident_type,
        description,
        reported_by,
        status
    ):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que la ruta exista
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            ruta = cursor.fetchone()

            if not ruta:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            # Registrar el incidente
            cursor.execute(
                """
                INSERT INTO incidents (
                    route_id,
                    incident_type,
                    description,
                    reported_by,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    route_id,
                    incident_type,
                    description,
                    reported_by,
                    status
                )
            )

            conexion.commit()

            incidente_id = cursor.lastrowid

            # Obtener el incidente recién creado
            cursor.execute(
                """
                SELECT
                    id,
                    route_id,
                    incident_type,
                    description,
                    reported_by,
                    reported_at,
                    status
                FROM incidents
                WHERE id = %s
                """,
                (incidente_id,)
            )

            fila = cursor.fetchone()

            if not fila:
                raise Exception(
                    "No fue posible recuperar el incidente registrado."
                )

            return Incident(
                id=fila["id"],
                route_id=fila["route_id"],
                incident_type=fila["incident_type"],
                description=fila["description"],
                reported_by=fila["reported_by"],
                reported_at=str(fila["reported_at"]),
                status=fila["status"]
            )

        except Exception:
            if conexion:
                conexion.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 5. OBTENER INCIDENTES ACTIVOS DE UNA RUTA
    # ========================================================

    @rpc(
        Integer,
        _returns=Array(Incident)
    )
    def get_incidents_by_route(ctx, route_id):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que la ruta exista
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            ruta = cursor.fetchone()

            if not ruta:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            # Buscar únicamente incidentes activos
            cursor.execute(
                """
                SELECT
                    id,
                    route_id,
                    incident_type,
                    description,
                    reported_by,
                    reported_at,
                    status
                FROM incidents
                WHERE route_id = %s
                  AND status = 'ACTIVO'
                ORDER BY reported_at DESC
                """,
                (route_id,)
            )

            resultados = cursor.fetchall()

            incidentes = []

            for fila in resultados:

                incidente = Incident(
                    id=fila["id"],
                    route_id=fila["route_id"],
                    incident_type=fila["incident_type"],
                    description=fila["description"],
                    reported_by=fila["reported_by"],
                    reported_at=str(fila["reported_at"]),
                    status=fila["status"]
                )

                incidentes.append(incidente)

            return incidentes

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 6. ACTUALIZAR ESTADO DE UN INCIDENTE
    # ========================================================

    @rpc(
        Integer,
        Unicode,
        _returns=Incident
    )
    def update_incident_status(ctx, incident_id, new_status):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que el incidente exista
            cursor.execute(
                """
                SELECT id
                FROM incidents
                WHERE id = %s
                """,
                (incident_id,)
            )

            incidente_existente = cursor.fetchone()

            if not incidente_existente:
                raise Exception(
                    f"El incidente {incident_id} no existe."
                )

            # Actualizar el estado
            cursor.execute(
                """
                UPDATE incidents
                SET status = %s
                WHERE id = %s
                """,
                (new_status, incident_id)
            )

            conexion.commit()

            # Obtener el incidente ya actualizado
            cursor.execute(
                """
                SELECT
                    id,
                    route_id,
                    incident_type,
                    description,
                    reported_by,
                    reported_at,
                    status
                FROM incidents
                WHERE id = %s
                """,
                (incident_id,)
            )

            fila = cursor.fetchone()

            if not fila:
                raise Exception(
                    "No fue posible recuperar el incidente actualizado."
                )

            return Incident(
                id=fila["id"],
                route_id=fila["route_id"],
                incident_type=fila["incident_type"],
                description=fila["description"],
                reported_by=fila["reported_by"],
                reported_at=str(fila["reported_at"]),
                status=fila["status"]
            )

        except Exception:
            if conexion:
                conexion.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 7. OBTENER ESTADO DE UNA RUTA
    # ========================================================

    @rpc(
        Integer,
        _returns=RouteStatus
    )
    def get_route_status(ctx, route_id):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que la ruta exista
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            ruta = cursor.fetchone()

            if not ruta:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            # Contar incidentes activos de la ruta
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM incidents
                WHERE route_id = %s
                  AND status = 'ACTIVO'
                """,
                (route_id,)
            )

            fila = cursor.fetchone()

            total_incidentes = fila["total"] if fila else 0

            # Determinar el estado general de la ruta
            if total_incidentes > 0:
                estado = "CON_PROBLEMAS"
            else:
                estado = "ACTIVA"

            return RouteStatus(
                route_id=route_id,
                status=estado,
                active_incidents_count=total_incidentes
            )

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN SOAP
# ============================================================

application = Application(
    [OperationsService],
    tns="http://rutas.popayan/operations",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)


# ============================================================
# CONFIGURACIÓN WSGI
# ============================================================

wsgi_application = WsgiApplication(application)


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    host = "127.0.0.1"
    port = 8002

    print("=" * 60)
    print("MICROSERVICIO DE OPERACIONES")
    print("=" * 60)
    print(f"Servidor SOAP iniciado en http://{host}:{port}")
    print(f"WSDL disponible en http://{host}:{port}/?wsdl")
    print("=" * 60)

    servidor = make_server(
        host,
        port,
        wsgi_application
    )

    servidor.serve_forever()