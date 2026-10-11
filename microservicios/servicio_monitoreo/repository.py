from database import get_cursor

# ------------------------------------------------------------------------------
# CONSULTAS DE USUARIOS Y AUTENTICACIÓN
# ------------------------------------------------------------------------------

def find_user_by_username(username: str):
    """Busca un usuario por su nombre de usuario."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT id, username, password_hash, full_name, role, api_key, created_at FROM users WHERE username = %s LIMIT 1",
            (username,)
        )
        return cursor.fetchone()

def find_user_by_id(user_id: int):
    """Busca un usuario por su ID primario."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT id, username, full_name, role, api_key, created_at FROM users WHERE id = %s LIMIT 1",
            (user_id,)
        )
        return cursor.fetchone()

def find_user_by_api_key(api_key: str):
    """Busca un usuario activo mediante su API Key asignada."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT id, username, full_name, role, api_key, created_at FROM users WHERE api_key = %s LIMIT 1",
            (api_key,)
        )
        return cursor.fetchone()

def create_user(username: str, password: str, role: str = "OPERADOR") -> bool:
    """Registra un nuevo usuario con contrasena hasheada en SHA-256."""
    import hashlib
    import secrets
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    api_key = f"popayan-{username.strip().lower()}-{secrets.token_hex(4)}"
    full_name = f"Usuario {username.strip().capitalize()}"
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role, api_key) VALUES (%s, %s, %s, %s, %s)",
            (username.strip(), password_hash, full_name, role, api_key)
        )
        return cursor.rowcount > 0

# ------------------------------------------------------------------------------
# CONSULTAS DE APOYO A RUTAS Y PARADEROS
# ------------------------------------------------------------------------------

def find_route_by_id(route_id: int):
    """Obtiene los datos base de una ruta de transporte de Popayán."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT id, code, company, origin, destination, fare, schedule, status FROM routes WHERE id = %s",
            (route_id,)
        )
        return cursor.fetchone()

def get_stops_count(route_id: int) -> int:
    """Retorna la cantidad de paraderos registrados para una ruta."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM stops WHERE route_id = %s",
            (route_id,)
        )
        row = cursor.fetchone()
        return int(row["total"]) if row else 0

def get_active_incidents_count(route_id: int) -> int:
    """Cuenta los incidentes activos actualmente en una ruta."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM incidents WHERE route_id = %s AND status = 'ACTIVO'",
            (route_id,)
        )
        row = cursor.fetchone()
        return int(row["total"]) if row else 0

def get_intersecting_routes_by_landmark(landmark: str, exclude_route_id: int = None):
    """Encuentra otras rutas que pasan cerca o por el mismo hito o paradero en Popayán."""
    with get_cursor() as cursor:
        query = """
            SELECT DISTINCT r.id, r.code, r.company, r.origin, r.destination, s.name AS stop_name
            FROM routes r
            JOIN stops s ON r.id = s.route_id
            WHERE (s.name LIKE %s OR s.landmark_reference LIKE %s)
        """
        params = [f"%{landmark}%", f"%{landmark}%"]
        if exclude_route_id:
            query += " AND r.id != %s"
            params.append(exclude_route_id)
        query += " LIMIT 5"
        cursor.execute(query, tuple(params))
        return cursor.fetchall() or []

# ------------------------------------------------------------------------------
# CONSULTAS Y PERSISTENCIA DE VALORACIONES Y CALIDAD
# ------------------------------------------------------------------------------

def get_recent_ratings_by_route(route_id: int):
    """Obtiene el historial de calificaciones registradas para una ruta."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT final_score, punctuality_score, comfort_score, driver_score, safety_score, category "
            "FROM service_ratings WHERE route_id = %s ORDER BY created_at DESC LIMIT 30",
            (route_id,)
        )
        return cursor.fetchall() or []

def save_service_rating(route_id: int, company: str, user_id: int, punctuality_score: int,
                        comfort_score: int, driver_score: int, safety_score: int,
                        final_score: float, category: str, comment: str) -> int:
    """Inserta una nueva evaluación ciudadana de servicio de transporte."""
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO service_ratings 
            (route_id, company, user_id, punctuality_score, comfort_score, driver_score, 
             safety_score, final_score, category, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (route_id, company, user_id, punctuality_score, comfort_score, driver_score,
             safety_score, final_score, category, comment)
        )
        return cursor.lastrowid

# ------------------------------------------------------------------------------
# PERSISTENCIA DE TELEMETRÍA Y SOBRECUPO
# ------------------------------------------------------------------------------

def save_bus_telemetry(route_id: int, bus_plate: str, current_passengers: int, max_capacity: int,
                       occupancy_ratio: float, current_speed: float, risk_level: str,
                       reinforcement_needed: bool) -> int:
    """Registra la lectura de telemetría de aforo y velocidad en tiempo real."""
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO bus_telemetry 
            (route_id, bus_plate, current_passengers, max_capacity, occupancy_ratio, 
             current_speed, risk_level, reinforcement_needed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (route_id, bus_plate, current_passengers, max_capacity, occupancy_ratio,
             current_speed, risk_level, 1 if reinforcement_needed else 0)
        )
        return cursor.lastrowid

# ------------------------------------------------------------------------------
# PERSISTENCIA DE ALERTAS DE SEGURIDAD
# ------------------------------------------------------------------------------

def save_emergency_alert(route_id: int, bus_plate: str, alert_type: str, severity_level: str,
                         criticality_score: float, max_response_time_minutes: int,
                         location_landmark: str, description: str) -> int:
    """Inserta una novedad o alerta crítica de seguridad en Popayán."""
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO emergency_alerts 
            (route_id, bus_plate, alert_type, severity_level, criticality_score, 
             max_response_time_minutes, location_landmark, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (route_id, bus_plate, alert_type, severity_level, criticality_score,
             max_response_time_minutes, location_landmark, description)
        )
        return cursor.lastrowid

# ------------------------------------------------------------------------------
# AGREGACIONES PARA RANKING DE EMPRESAS DE POPAYÁN
# ------------------------------------------------------------------------------

def get_all_companies_names():
    """Obtiene la lista de todas las empresas prestadoras de transporte registradas."""
    with get_cursor() as cursor:
        cursor.execute("SELECT DISTINCT company FROM routes WHERE company IS NOT NULL AND company != ''")
        rows = cursor.fetchall()
        return [r["company"] for r in rows]

def get_company_stats(company: str):
    """Recopila estadísticas cruzadas para auditoría de una empresa de Popayán."""
    with get_cursor() as cursor:
        # Rutas de la empresa
        cursor.execute("SELECT COUNT(*) AS total_routes FROM routes WHERE company = %s", (company,))
        total_routes = int(cursor.fetchone()["total_routes"])

        # Despachos totales y en ruta
        cursor.execute("""
            SELECT COUNT(*) AS total_dispatches,
                   SUM(CASE WHEN d.status = 'EN_RUTA' THEN 1 ELSE 0 END) AS active_dispatches,
                   SUM(CASE WHEN d.status = 'FINALIZADO' THEN 1 ELSE 0 END) AS completed_dispatches
            FROM dispatches d
            JOIN routes r ON d.route_id = r.id
            WHERE r.company = %s
        """, (company,))
        dispatch_stats = cursor.fetchone() or {}

        # Incidentes registrados en rutas de la empresa
        cursor.execute("""
            SELECT COUNT(*) AS total_incidents,
                   SUM(CASE WHEN i.incident_type = 'ACCIDENTE' THEN 1 ELSE 0 END) AS accidents,
                   SUM(CASE WHEN i.incident_type = 'CONGESTION' THEN 1 ELSE 0 END) AS congestions
            FROM incidents i
            JOIN routes r ON i.route_id = r.id
            WHERE r.company = %s
        """, (company,))
        incident_stats = cursor.fetchone() or {}

        # Promedio de satisfacción de usuarios
        cursor.execute("""
            SELECT COUNT(*) AS total_reviews,
                   AVG(final_score) AS avg_score,
                   AVG(punctuality_score) AS avg_punctuality,
                   AVG(safety_score) AS avg_safety
            FROM service_ratings
            WHERE company = %s
        """, (company,))
        rating_stats = cursor.fetchone() or {}

        # Alertas de emergencia críticas
        cursor.execute("""
            SELECT COUNT(*) AS total_alerts,
                   SUM(CASE WHEN ea.severity_level IN ('ALTA', 'CRITICA') THEN 1 ELSE 0 END) AS high_alerts
            FROM emergency_alerts ea
            JOIN routes r ON ea.route_id = r.id
            WHERE r.company = %s
        """, (company,))
        alert_stats = cursor.fetchone() or {}

        return {
            "company": company,
            "total_routes": total_routes,
            "total_dispatches": int(dispatch_stats.get("total_dispatches") or 0),
            "active_dispatches": int(dispatch_stats.get("active_dispatches") or 0),
            "completed_dispatches": int(dispatch_stats.get("completed_dispatches") or 0),
            "total_incidents": int(incident_stats.get("total_incidents") or 0),
            "accidents": int(incident_stats.get("accidents") or 0),
            "congestions": int(incident_stats.get("congestions") or 0),
            "total_reviews": int(rating_stats.get("total_reviews") or 0),
            "avg_score": float(rating_stats.get("avg_score") or 75.0),
            "avg_punctuality": float(rating_stats.get("avg_punctuality") or 3.5),
            "avg_safety": float(rating_stats.get("avg_safety") or 3.8),
            "total_alerts": int(alert_stats.get("total_alerts") or 0),
            "high_alerts": int(alert_stats.get("high_alerts") or 0)
        }


# ------------------------------------------------------------------------------
# CRUD / GESTIÓN DE ALERTAS DE EMERGENCIA Y MONITOREO
# ------------------------------------------------------------------------------

def find_emergency_alert_by_id(alert_id: int):
    """Busca una alerta de emergencia por su ID."""
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, route_id, bus_plate, alert_type, severity_level, criticality_score,
                   max_response_time_minutes, location_landmark, description, status, created_at
            FROM emergency_alerts
            WHERE id = %s
            """,
            (alert_id,)
        )
        return cursor.fetchone()


def get_all_emergency_alerts():
    """Retorna el listado completo de alertas de monitoreo y seguridad."""
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, route_id, bus_plate, alert_type, severity_level, criticality_score,
                   max_response_time_minutes, location_landmark, description, status, created_at
            FROM emergency_alerts
            ORDER BY id DESC
            """
        )
        return cursor.fetchall() or []


def update_emergency_alert(alert_id: int, status: str = None, description: str = None,
                           severity_level: str = None, location_landmark: str = None) -> bool:
    """Actualiza los campos de una alerta de emergencia existente."""
    fields = []
    params = []
    if status is not None:
        fields.append("status = %s")
        params.append(status.strip())
    if description is not None:
        fields.append("description = %s")
        params.append(description.strip())
    if severity_level is not None:
        fields.append("severity_level = %s")
        params.append(severity_level.strip())
    if location_landmark is not None:
        fields.append("location_landmark = %s")
        params.append(location_landmark.strip())

    if not fields:
        return False

    params.append(alert_id)
    query = f"UPDATE emergency_alerts SET {', '.join(fields)} WHERE id = %s"
    with get_cursor(commit=True) as cursor:
        cursor.execute(query, tuple(params))
        return cursor.rowcount > 0


def delete_emergency_alert(alert_id: int) -> bool:
    """Elimina permanentemente una alerta de emergencia por su ID."""
    with get_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM emergency_alerts WHERE id = %s", (alert_id,))
        return cursor.rowcount > 0

