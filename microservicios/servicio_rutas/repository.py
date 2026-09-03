from database import get_cursor
from models import Route

def _row_to_route(row: dict) -> Route:
    """Conversión centralizada de fila MySQL a objeto Route de Spyne."""
    return Route(
        id=int(row["id"]),
        code=str(row.get("code") or ""),
        company=str(row.get("company") or ""),
        origin=str(row.get("origin") or ""),
        destination=str(row.get("destination") or ""),
        fare=float(row["fare"]) if row.get("fare") is not None else 0.0,
        schedule=str(row.get("schedule") or ""),
        status=str(row.get("status") or "ACTIVA")
    )

def find_all_active() -> list[Route]:
    """Retorna todas las rutas con estado ACTIVA."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, code, company, origin, destination, fare, schedule, status
            FROM routes
            WHERE status = 'ACTIVA' OR status IS NULL
            ORDER BY id ASC
        """
        cursor.execute(sql)
        return [_row_to_route(row) for row in cursor.fetchall()]

def find_by_id(route_id: int) -> Route | None:
    """Busca y retorna una ruta por su ID primario."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, code, company, origin, destination, fare, schedule, status
            FROM routes
            WHERE id = %s
            LIMIT 1
        """
        cursor.execute(sql, (route_id,))
        row = cursor.fetchone()
        return _row_to_route(row) if row else None

def search_by_zone(zone_keyword: str) -> list[Route]:
    """Busca rutas que coincidan con un sector en origen, destino o paraderos."""
    patron = f"%{zone_keyword.strip()}%"
    with get_cursor() as cursor:
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
        return [_row_to_route(row) for row in cursor.fetchall()]

def insert_route(code: str, company: str, origin: str, destination: str, fare: float, schedule: str) -> bool:
    """Inserta una nueva ruta en la base de datos."""
    with get_cursor(commit=True) as cursor:
        sql = """
            INSERT INTO routes (code, company, origin, destination, fare, schedule, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVA')
        """
        cursor.execute(sql, (
            code.strip(),
            company.strip(),
            origin.strip(),
            destination.strip(),
            float(fare) if fare is not None else 0.0,
            schedule.strip()
        ))
        return cursor.rowcount > 0

def find_direct_trip(orig: str, dest: str) -> dict | None:
    """Busca la mejor ruta directa entre dos paraderos con validación de secuencia."""
    patron_orig = f"%{orig.strip()}%"
    patron_dest = f"%{dest.strip()}%"

    with get_cursor() as cursor:
        # 1. Búsqueda por paraderos con dirección s1.stop_order < s2.stop_order
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
        resultado = cursor.fetchone()
        if resultado:
            return resultado

        # 2. Búsqueda alternativa por origen/destino general de la ruta
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
        return cursor.fetchone()

def find_transfer_trip(orig: str, dest: str) -> dict | None:
    """Busca combinación de 2 rutas conectadas por un paradero de transbordo en común."""
    patron_orig = f"%{orig.strip()}%"
    patron_dest = f"%{dest.strip()}%"

    with get_cursor() as cursor:
        sql = """
            SELECT 
                r1.id AS r1_id, r1.code AS r1_code, r1.company AS r1_company, r1.fare AS r1_fare,
                s_orig.name AS boarding_stop,
                s_trans1.name AS transfer_stop,
                r2.id AS r2_id, r2.code AS r2_code, r2.company AS r2_company, r2.fare AS r2_fare,
                s_dest.name AS alighting_stop,
                ((s_trans1.stop_order - s_orig.stop_order) + (s_dest.stop_order - s_trans2.stop_order)) AS total_stops
            FROM routes r1
            INNER JOIN stops s_orig ON r1.id = s_orig.route_id
            INNER JOIN stops s_trans1 ON r1.id = s_trans1.route_id
            INNER JOIN routes r2 ON r1.id <> r2.id
            INNER JOIN stops s_trans2 ON r2.id = s_trans2.route_id
            INNER JOIN stops s_dest ON r2.id = s_dest.route_id
            WHERE (s_orig.name LIKE %s OR s_orig.landmark_reference LIKE %s)
              AND (s_dest.name LIKE %s OR s_dest.landmark_reference LIKE %s)
              AND s_trans1.stop_order > s_orig.stop_order
              AND s_dest.stop_order > s_trans2.stop_order
              AND (s_trans1.name = s_trans2.name OR s_trans1.landmark_reference = s_trans2.landmark_reference)
              AND (r1.status = 'ACTIVA' OR r1.status IS NULL)
              AND (r2.status = 'ACTIVA' OR r2.status IS NULL)
            ORDER BY total_stops ASC
            LIMIT 1
        """
        cursor.execute(sql, (patron_orig, patron_orig, patron_dest, patron_dest))
        return cursor.fetchone()

def get_active_incidents(route_id: int) -> list[dict]:
    """Obtiene los incidentes viales activos reportados para una ruta."""
    with get_cursor() as cursor:
        sql = """
            SELECT id, incident_type, description, reported_by, reported_at, status
            FROM incidents
            WHERE route_id = %s AND (status = 'ACTIVO' OR status IS NULL)
            ORDER BY id DESC
        """
        cursor.execute(sql, (route_id,))
        return cursor.fetchall()

def get_route_stops_count(route_id: int) -> int:
    """Cuenta la cantidad de paraderos registrados para una ruta."""
    with get_cursor() as cursor:
        sql = "SELECT COUNT(*) AS total FROM stops WHERE route_id = %s"
        cursor.execute(sql, (route_id,))
        res = cursor.fetchone()
        return int(res["total"]) if res and res.get("total") else 0
