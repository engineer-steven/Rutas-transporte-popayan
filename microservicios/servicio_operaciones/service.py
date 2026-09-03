import logging
from datetime import datetime, timedelta
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Boolean, Iterable
from spyne.protocol.soap import Soap11

import repository
from models import Stop, Incident, BusTimeDifferenceResult, NAMESPACE

logger = logging.getLogger("OperationsService")
logger.setLevel(logging.INFO)

def parse_time_str(time_val) -> datetime:
    """Convierte cadenas u objetos de tiempo (TIME / DATETIME / timedelta) a datetime."""
    if isinstance(time_val, timedelta):
        total_seconds = int(time_val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return datetime.strptime(f"{hours:02d}:{minutes:02d}:{seconds:02d}", "%H:%M:%S")
    
    if isinstance(time_val, datetime):
        return time_val

    t_str = str(time_val).strip()
    for fmt in ("%H:%M:%S", "%H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(t_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato horario inválido: '{time_val}'")


class OperationsService(ServiceBase):
    """
    Servicio SOAP para operaciones de campo, intervalos de salida entre buses,
    gestión de paraderos e incidencias viales en Popayán.
    """

    # --------------------------------------------------------------------------
    # OPERACIÓN 1: Diferencia de tiempo entre dos buses de una ruta
    # --------------------------------------------------------------------------
    @rpc(Integer, Unicode, Unicode, _returns=BusTimeDifferenceResult)
    def calculate_bus_time_difference(ctx, route_id, bus_plate_1, bus_plate_2):
        """Calcula los minutos de diferencia entre los despachos de dos buses."""
        p1 = str(bus_plate_1 or "").strip()
        p2 = str(bus_plate_2 or "").strip()
        logger.info(f"[calculate_bus_time_difference] Ruta {route_id}: Bus {p1} vs Bus {p2}")

        d1 = repository.find_dispatch(route_id, p1)
        d2 = repository.find_dispatch(route_id, p2)

        if not d1 or not d2:
            no_hallado = p1 if not d1 else p2
            return BusTimeDifferenceResult(
                route_id=route_id,
                bus_plate_1=p1,
                departure_time_1=str(d1.get("departure_time") if d1 else "--:--"),
                bus_plate_2=p2,
                departure_time_2=str(d2.get("departure_time") if d2 else "--:--"),
                difference_minutes=-1,
                summary_message=f"No se encontró registro de despacho para el vehículo con placa '{no_hallado}'."
            )

        t1_val = d1["departure_time"]
        t2_val = d2["departure_time"]

        try:
            dt1 = parse_time_str(t1_val)
            dt2 = parse_time_str(t2_val)
            diff_min = abs(int((dt2 - dt1).total_seconds() / 60))
            msg = (
                f"El bus {p1} (salida {dt1.strftime('%H:%M:%S')}) y el bus {p2} "
                f"(salida {dt2.strftime('%H:%M:%S')}) tienen un intervalo de {diff_min} minutos entre sí."
            )
        except Exception as e:
            logger.error(f"Error al calcular diferencia horaria: {e}")
            diff_min = 0
            msg = f"Error al procesar formatos horarios: {e}"

        return BusTimeDifferenceResult(
            route_id=route_id,
            bus_plate_1=p1,
            departure_time_1=str(t1_val),
            bus_plate_2=p2,
            departure_time_2=str(t2_val),
            difference_minutes=diff_min,
            summary_message=msg
        )

    # --------------------------------------------------------------------------
    # OPERACIÓN 2: Calculadora de minutos entre dos horas en texto
    # --------------------------------------------------------------------------
    @rpc(Unicode, Unicode, _returns=Integer)
    def calculate_time_gap(ctx, time_1, time_2):
        """Calcula directamente la diferencia en minutos entre dos horas recibidas como texto."""
        try:
            dt1 = parse_time_str(time_1)
            dt2 = parse_time_str(time_2)
            return abs(int((dt2 - dt1).total_seconds() / 60))
        except Exception as e:
            logger.error(f"[calculate_time_gap] Error: {e}")
            return -1

    # --------------------------------------------------------------------------
    # OPERACIÓN 3: Listar paraderos ordenados por trayecto
    # --------------------------------------------------------------------------
    @rpc(Integer, _returns=Iterable(Stop))
    def get_stops_by_route(ctx, route_id):
        """Retorna todos los paraderos de la ruta ordenados por su secuencia."""
        logger.info(f"[get_stops_by_route] Consultando paraderos para ruta ID: {route_id}")
        return repository.find_stops_by_route(route_id)

    # --------------------------------------------------------------------------
    # OPERACIÓN 4: Registrar un reporte de incidente vial
    # --------------------------------------------------------------------------
    @rpc(Integer, Unicode, Unicode, Unicode, _returns=Boolean)
    def report_incident(ctx, route_id, incident_type, description, reported_by):
        """Registra un evento o incidente vial en la ruta."""
        logger.info(f"[report_incident] Reportando incidente en ruta {route_id}: {incident_type}")
        return repository.insert_incident(route_id, incident_type, description, reported_by)

    # --------------------------------------------------------------------------
    # OPERACIÓN 5: Consultar incidentes activos de una ruta
    # --------------------------------------------------------------------------
    @rpc(Integer, _returns=Iterable(Incident))
    def get_incidents_by_route(ctx, route_id):
        """Retorna las incidencias viales activas de una ruta."""
        logger.info(f"[get_incidents_by_route] Consultando incidencias para ruta ID: {route_id}")
        return repository.find_incidents_by_route(route_id)


# Aplicación Spyne SOAP 1.1
application = Application(
    [OperationsService],
    tns=NAMESPACE,
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)
