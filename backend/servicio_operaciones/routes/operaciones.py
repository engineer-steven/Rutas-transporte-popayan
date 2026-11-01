# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/routes/operaciones.py
# RESPONSABILIDAD: Controlador REST para operaciones en vía, cálculo de intervalos e incidentes.
# PREFIJO URL: /operaciones
# ==============================================================================

# Importa clases datetime y timedelta para cálculo de brechas horarias.
from datetime import datetime, timedelta

# Importa utilidades de Flask para enrutamiento y respuestas HTTP.
from flask import Blueprint, request, jsonify

# Importa la capa de persistencia para operaciones e incidentes.
import repository

# Importa el decorador para protección de endpoints con token o API Key.
from auth import role_required

# Declara el Blueprint bajo el prefijo /operaciones.
operaciones_bp = Blueprint("operaciones_bp", __name__, url_prefix="/operaciones")


def _parse_time(time_val) -> datetime:
    """
    Función de interoperabilidad temporal defensiva:
    Parsea de forma homogénea valores que vengan como timedelta, datetime o strings con diferentes formatos.
    Resuelve incompatibilidades típicas entre MySQL y conectores de Python.
    """
    # Si MySQL entregó el campo horario como un objeto timedelta (duración desde medianoche):
    if isinstance(time_val, timedelta):
        total = int(time_val.total_seconds())
        # Reconstruye la cadena en formato HH:MM:SS y la parsea a datetime.
        return datetime.strptime(f"{total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}", "%H:%M:%S")

    # Si ya viene como instancia nativa de datetime, la retorna directamente.
    if isinstance(time_val, datetime):
        return time_val

    # Si es cadena de texto, limpia espacios en blanco.
    t = str(time_val).strip()
    # Prueba sucesivamente los formatos de hora más comunes.
    for fmt in ("%H:%M:%S", "%H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            continue

    # Si ningún formato coincidió, arroja un error explicativo.
    raise ValueError(f"Formato horario invalido: '{time_val}'")


# ==============================================================================
# OPERACIÓN 1: DIFERENCIA DE TIEMPO ENTRE DOS BUSES EN RUTA (HEADWAY)
# Endpoint: GET /operaciones/diferencia-buses?route_id=ID&bus1=PLACA1&bus2=PLACA2
# ==============================================================================
@operaciones_bp.route("/diferencia-buses", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def calculate_bus_time_difference(current_user=None):
    """Calcula los minutos de separación entre los despachos de dos colectivos de una misma ruta."""
    # Valida y convierte el identificador de ruta a entero.
    try:
        route_id = int(request.args.get("route_id", 0))
    except ValueError:
        return jsonify({"success": False, "error": "route_id debe ser entero"}), 400

    # Lee las placas de ambos vehículos.
    bus1 = request.args.get("bus1", "").strip()
    bus2 = request.args.get("bus2", "").strip()

    # Valida la presencia de todos los parámetros necesarios.
    if not route_id or not bus1 or not bus2:
        return jsonify({"success": False, "error": "Parametros requeridos: route_id, bus1, bus2"}), 400

    # Consulta el registro de despacho más reciente de cada vehículo.
    d1 = repository.find_dispatch(route_id, bus1)
    d2 = repository.find_dispatch(route_id, bus2)

    # Si alguno de los dos vehículos no tiene despacho registrado en esa ruta:
    if not d1 or not d2:
        no_hallado = bus1 if not d1 else bus2
        return jsonify({
            "success": False,
            "error": f"No se encontro despacho para la placa '{no_hallado}' en la ruta {route_id}"
        }), 404

    try:
        # Parsea los horarios de salida usando la función defensiva _parse_time.
        dt1 = _parse_time(d1["departure_time"])
        dt2 = _parse_time(d2["departure_time"])
        # Calcula la diferencia absoluta en minutos entre ambas salidas.
        diff_min = abs(int((dt2 - dt1).total_seconds() / 60))

        # Retorna el diagnóstico de separación horaria con HTTP 200 OK.
        return jsonify({
            "success": True,
            "route_id":  route_id,
            "bus_1":     {"placa": bus1, "hora_despacho": dt1.strftime("%H:%M:%S")},
            "bus_2":     {"placa": bus2, "hora_despacho": dt2.strftime("%H:%M:%S")},
            "diferencia_minutos": diff_min,
            "resumen": (
                f"El bus {bus1} (salida {dt1.strftime('%H:%M')}) y {bus2} "
                f"(salida {dt2.strftime('%H:%M')}) tienen {diff_min} min de diferencia."
            )
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al calcular: {str(e)}"}), 500


# ==============================================================================
# OPERACIÓN 2: CALCULADORA HORARIA DIRECTA
# Endpoint: GET /operaciones/diferencia-horas?hora1=HH:MM&hora2=HH:MM
# ==============================================================================
@operaciones_bp.route("/diferencia-horas", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def calculate_time_gap(current_user=None):
    """Calcula la brecha matemática exacta en minutos entre dos horas suministradas."""
    h1 = request.args.get("hora1", "").strip()
    h2 = request.args.get("hora2", "").strip()

    if not h1 or not h2:
        return jsonify({"success": False, "error": "Parametros requeridos: hora1, hora2 (formato HH:MM)"}), 400

    try:
        # Parsea ambas cadenas horarias.
        dt1 = _parse_time(h1)
        dt2 = _parse_time(h2)
        # Calcula la diferencia absoluta en minutos.
        diff = abs(int((dt2 - dt1).total_seconds() / 60))
        return jsonify({
            "success": True,
            "hora_1": h1,
            "hora_2": h2,
            "diferencia_minutos": diff
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Formato invalido: {str(e)}"}), 400


# ==============================================================================
# OPERACIÓN 3: LISTAR PARADEROS SECUENCIALES DE UNA RUTA
# Endpoint: GET /operaciones/paraderos/<route_id>
# ==============================================================================
@operaciones_bp.route("/paraderos/<int:route_id>", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def get_stops_by_route(route_id, current_user=None):
    """Retorna los paraderos georreferenciados de una ruta ordenados por su orden físico de parada."""
    paraderos = repository.find_stops_by_route(route_id)
    # Transforma los modelos Stop a diccionarios JSON.
    datos = [
        {
            "id":                 p.id,
            "route_id":           p.route_id,
            "nombre":             p.name,
            "referencia":         p.landmark_reference,
            "orden":              p.stop_order
        }
        for p in paraderos
    ]
    return jsonify({
        "success": True,
        "route_id": route_id,
        "total_paraderos": len(datos),
        "data": datos
    }), 200


# ==============================================================================
# OPERACIÓN 4: REPORTAR INCIDENTE O NOVEDAD VIAL
# Endpoint: POST /operaciones/incidente
# ==============================================================================
@operaciones_bp.route("/incidente", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def report_incident(current_user=None):
    """Registra una novedad vial (accidente, desvío, congestión) sobre una ruta específica."""
    data = request.get_json(silent=True) or {}

    # Valida el ID de la ruta afectada.
    try:
        route_id = int(data.get("route_id", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "route_id debe ser entero"}), 400

    incident_type = str(data.get("incident_type", "")).strip()
    description   = str(data.get("description", "")).strip()
    reported_by   = str(data.get("reported_by", "Sistema")).strip()

    # Verifica campos requeridos.
    if not route_id or not incident_type or not description:
        return jsonify({
            "success": False,
            "error": "Campos requeridos: route_id, incident_type, description"
        }), 400

    # Inserta el registro en la base de datos con commit.
    ok = repository.insert_incident(route_id, incident_type, description, reported_by)
    if ok:
        return jsonify({
            "success": True,
            "mensaje": f"Incidente '{incident_type}' registrado en ruta {route_id}."
        }), 201
    return jsonify({"success": False, "error": "No se pudo registrar el incidente"}), 500


# ==============================================================================
# OPERACIÓN 5: CONSULTAR INCIDENTES ACTIVOS DE UNA RUTA
# Endpoint: GET /operaciones/incidentes/<route_id>
# ==============================================================================
@operaciones_bp.route("/incidentes/<int:route_id>", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def get_incidents_by_route(route_id, current_user=None):
    """Retorna las novedades viales activas reportadas para una ruta."""
    incidentes = repository.find_incidents_by_route(route_id)
    datos = [
        {
            "id":            i.id,
            "route_id":      i.route_id,
            "tipo":          i.incident_type,
            "descripcion":   i.description,
            "reportado_por": i.reported_by,
            "reportado_en":  i.reported_at,
            "estado":        i.status
        }
        for i in incidentes
    ]
    return jsonify({
        "success": True,
        "route_id": route_id,
        "total_incidentes": len(datos),
        "data": datos
    }), 200
