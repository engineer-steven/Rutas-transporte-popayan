# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/repository.py
# RESPONSABILIDAD: Capa DAO (Data Access Object) para operaciones, paraderos e incidentes.
# SEGURIDAD: Consultas parametrizadas contra Inyección SQL (CWE-89).
# ==============================================================================

# Importa el administrador de conexiones y transacciones.
from database import get_cursor

# Importa los modelos de datos tipados del servicio.
from models import Stop, Incident


def _row_to_stop(row: dict) -> Stop:
    """Mapea una fila devuelta por MySQL a una instancia del modelo tipado Stop."""
    return Stop(
        id=int(row["id"]),
        route_id=int(row["route_id"]),
        name=str(row.get("name") or ""),
        landmark_reference=str(row.get("landmark_reference") or ""),
        stop_order=int(row.get("stop_order") or 0)
    )


def _row_to_incident(row: dict) -> Incident:
    """Mapea una fila de incidentes devuelta por MySQL a una instancia del modelo tipado Incident."""
    return Incident(
        id=int(row["id"]),
        route_id=int(row["route_id"]),
        incident_type=str(row.get("incident_type") or ""),
        description=str(row.get("description") or ""),
        reported_by=str(row.get("reported_by") or ""),
        reported_at=str(row.get("reported_at") or ""),
        status=str(row.get("status") or "ACTIVO")
    )


def find_stops_by_route(route_id: int) -> list[Stop]:
    """Retorna la lista de paraderos pertenecientes a una ruta, ordenados secuencialmente por stop_order."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, route_id, name, landmark_reference, stop_order
            FROM stops
            WHERE route_id = %s
            ORDER BY stop_order ASC
        """
        cursor.execute(sql, (route_id,))
        return [_row_to_stop(row) for row in cursor.fetchall()]


def find_dispatch(route_id: int, bus_plate: str) -> dict | None:
    """Busca y retorna el registro de despacho más reciente de un colectivo según su placa y ruta."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, route_id, bus_plate, departure_time, status
            FROM dispatches
            WHERE route_id = %s AND bus_plate = %s
            ORDER BY id DESC
            LIMIT 1
        """
        cursor.execute(sql, (route_id, bus_plate.strip()))
        return cursor.fetchone()


def insert_incident(route_id: int, incident_type: str, description: str, reported_by: str) -> bool:
    """Inserta un nuevo incidente vial en la tabla 'incidents' ejecutando confirmación de transacción."""
    with get_cursor(commit=True) as cursor:
        sql = """
            INSERT INTO incidents (route_id, incident_type, description, reported_by, status)
            VALUES (%s, %s, %s, %s, 'ACTIVO')
        """
        cursor.execute(sql, (
            route_id,
            incident_type.strip(),
            description.strip(),
            reported_by.strip()
        ))
        return cursor.rowcount > 0


def find_incidents_by_route(route_id: int) -> list[Incident]:
    """Retorna todos los incidentes que se encuentran en estado 'ACTIVO' para una ruta determinada."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, route_id, incident_type, description, reported_by, reported_at, status
            FROM incidents
            WHERE route_id = %s AND (status = 'ACTIVO' OR status IS NULL)
            ORDER BY id DESC
        """
        cursor.execute(sql, (route_id,))
        return [_row_to_incident(row) for row in cursor.fetchall()]
