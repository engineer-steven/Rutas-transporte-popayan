from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
import repository
from auth import token_required

operaciones_bp = Blueprint("operaciones_bp", __name__, url_prefix="/operaciones")


def _parse_time(time_val) -> datetime:
    if isinstance(time_val, timedelta):
        total = int(time_val.total_seconds())
        return datetime.strptime(f"{total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}", "%H:%M:%S")
    if isinstance(time_val, datetime):
        return time_val
    t = str(time_val).strip()
    for fmt in ("%H:%M:%S", "%H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato horario invalido: '{time_val}'")


# ==============================================================================
# OPERACION 1: Diferencia de tiempo entre dos buses
# ==============================================================================
@operaciones_bp.route("/diferencia-buses", methods=["GET"])
@token_required
def calculate_bus_time_difference(current_user=None):
    """
    Calcula los minutos de diferencia entre los despachos de dos buses.
    Params: ?route_id=<id>&bus1=<placa>&bus2=<placa>
    """
    try:
        route_id = int(request.args.get("route_id", 0))
    except ValueError:
        return jsonify({"success": False, "error": "route_id debe ser entero"}), 400

    bus1 = request.args.get("bus1", "").strip()
    bus2 = request.args.get("bus2", "").strip()

    if not route_id or not bus1 or not bus2:
        return jsonify({"success": False, "error": "Parametros requeridos: route_id, bus1, bus2"}), 400

    d1 = repository.find_dispatch(route_id, bus1)
    d2 = repository.find_dispatch(route_id, bus2)

    if not d1 or not d2:
        no_hallado = bus1 if not d1 else bus2
        return jsonify({
            "success": False,
            "error": f"No se encontro despacho para la placa '{no_hallado}' en la ruta {route_id}"
        }), 404

    try:
        dt1 = _parse_time(d1["departure_time"])
        dt2 = _parse_time(d2["departure_time"])
        diff_min = abs(int((dt2 - dt1).total_seconds() / 60))
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
# OPERACION 2: Diferencia directa entre dos horas
# ==============================================================================
@operaciones_bp.route("/diferencia-horas", methods=["GET"])
@token_required
def calculate_time_gap(current_user=None):
    """
    Calcula directamente la diferencia en minutos entre dos horas.
    Params: ?hora1=HH:MM&hora2=HH:MM
    """
    h1 = request.args.get("hora1", "").strip()
    h2 = request.args.get("hora2", "").strip()

    if not h1 or not h2:
        return jsonify({"success": False, "error": "Parametros requeridos: hora1, hora2 (formato HH:MM)"}), 400

    try:
        dt1 = _parse_time(h1)
        dt2 = _parse_time(h2)
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
# OPERACION 3: Listar paraderos de una ruta
# ==============================================================================
@operaciones_bp.route("/paraderos/<int:route_id>", methods=["GET"])
@token_required
def get_stops_by_route(route_id, current_user=None):
    """Retorna los paraderos de una ruta ordenados por su secuencia."""
    paraderos = repository.find_stops_by_route(route_id)
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
# OPERACION 4: Reportar incidente vial
# ==============================================================================
@operaciones_bp.route("/incidente", methods=["POST"])
@token_required
def report_incident(current_user=None):
    """
    Registra un incidente vial.
    JSON: {route_id, incident_type, description, reported_by}
    """
    data = request.get_json(silent=True) or {}

    try:
        route_id = int(data.get("route_id", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "route_id debe ser entero"}), 400

    incident_type = str(data.get("incident_type", "")).strip()
    description   = str(data.get("description", "")).strip()
    reported_by   = str(data.get("reported_by", "Sistema")).strip()

    if not route_id or not incident_type or not description:
        return jsonify({
            "success": False,
            "error": "Campos requeridos: route_id, incident_type, description"
        }), 400

    ok = repository.insert_incident(route_id, incident_type, description, reported_by)
    if ok:
        return jsonify({
            "success": True,
            "mensaje": f"Incidente '{incident_type}' registrado en ruta {route_id}."
        }), 201
    return jsonify({"success": False, "error": "No se pudo registrar el incidente"}), 500


# ==============================================================================
# OPERACION 5: Consultar incidentes activos de una ruta
# ==============================================================================
@operaciones_bp.route("/incidentes/<int:route_id>", methods=["GET"])
@token_required
def get_incidents_by_route(route_id, current_user=None):
    """Retorna las incidencias viales activas de una ruta."""
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
