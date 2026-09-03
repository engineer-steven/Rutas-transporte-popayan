from database import get_cursor
from models import Stop, Incident

def _row_to_stop(row: dict) -> Stop:
    """Mapeo de fila MySQL a modelo Stop."""
    return Stop(
        id=int(row["id"]),
        route_id=int(row["route_id"]),
        name=str(row.get("name") or ""),
        landmark_reference=str(row.get("landmark_reference") or ""),
        stop_order=int(row.get("stop_order") or 0)
    )

def _row_to_incident(row: dict) -> Incident:
    """Mapeo de fila MySQL a modelo Incident."""
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
    """Retorna los paraderos de una ruta ordenados por stop_order."""
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
    """Busca el despacho más reciente de un bus por placa en una ruta."""
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
    """Registra una novedad vial en la tabla incidents."""
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
    """Retorna las incidencias activas reportadas para una ruta."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, route_id, incident_type, description, reported_by, reported_at, status
            FROM incidents
            WHERE route_id = %s AND (status = 'ACTIVO' OR status IS NULL)
            ORDER BY id DESC
        """
        cursor.execute(sql, (route_id,))
        return [_row_to_incident(row) for row in cursor.fetchall()]
