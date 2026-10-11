from flask import Blueprint, request, jsonify
from auth import token_required
import repository

alertas_bp = Blueprint("alertas_bp", __name__)


def _alert_to_dict(alert: dict) -> dict:
    if not alert:
        return {}
    res = dict(alert)
    if "created_at" in res and res["created_at"]:
        res["created_at"] = str(res["created_at"])
    if "criticality_score" in res and res["criticality_score"] is not None:
        res["criticality_score"] = float(res["criticality_score"])
    return res


# ==============================================================================
# 1. CREAR / GENERAR ALERTA DE MONITOREO (POST)
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas", methods=["POST"])
@alertas_bp.route("/alertas", methods=["POST"])
@token_required
def create_alerta(current_user=None):
    """
    Registra una nueva alerta de seguridad o evento crítico en la ruta.
    JSON: {
        "route_id": 1,
        "bus_plate": "TPK-102",
        "alert_type": "BOTON_PANICO",
        "severity_level": "ALTA",
        "criticality_score": 85.0,
        "max_response_time_minutes": 10,
        "location_landmark": "Barrio Bolívar",
        "description": "Alerta de pánico activada por el conductor en paradero."
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        route_id = int(data.get("route_id", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "route_id debe ser un número entero"}), 400

    bus_plate = str(data.get("bus_plate", "")).strip().upper()
    alert_type = str(data.get("alert_type", "BOTON_PANICO")).strip().upper()
    severity_level = str(data.get("severity_level", "ALTA")).strip().upper()
    location_landmark = str(data.get("location_landmark", "Sector Urbano Popayán")).strip()
    description = str(data.get("description", "")).strip()

    try:
        criticality_score = float(data.get("criticality_score", 85.0))
        max_response_time_minutes = int(data.get("max_response_time_minutes", 10))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parámetros numéricos inválidos"}), 400

    if not route_id or not bus_plate or not description:
        return jsonify({
            "success": False,
            "error": "Campos requeridos: route_id, bus_plate y description"
        }), 400

    # Validar que la ruta exista en la base de datos
    ruta = repository.find_route_by_id(route_id)
    if not ruta:
        return jsonify({
            "success": False,
            "error": f"La ruta con ID {route_id} no existe en el sistema de transporte"
        }), 404

    try:
        nuevo_id = repository.save_emergency_alert(
            route_id=route_id,
            bus_plate=bus_plate,
            alert_type=alert_type,
            severity_level=severity_level,
            criticality_score=criticality_score,
            max_response_time_minutes=max_response_time_minutes,
            location_landmark=location_landmark,
            description=description
        )
        nueva_alerta = repository.find_emergency_alert_by_id(nuevo_id)
        return jsonify({
            "success": True,
            "mensaje": f"Alerta crítica #{nuevo_id} generada exitosamente",
            "data": _alert_to_dict(nueva_alerta)
        }), 201
    except Exception as ex:
        return jsonify({
            "success": False,
            "error": f"Error al registrar la alerta: {str(ex)}"
        }), 500


# ==============================================================================
# 2. LISTAR ALERTAS (GET)
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas", methods=["GET"])
@alertas_bp.route("/alertas", methods=["GET"])
@token_required
def get_all_alertas(current_user=None):
    """Retorna todas las alertas de seguridad y monitoreo registradas."""
    alertas = repository.get_all_emergency_alerts()
    data = [_alert_to_dict(a) for a in alertas]
    return jsonify({
        "success": True,
        "total": len(data),
        "data": data
    }), 200


# ==============================================================================
# 2. OBTENER ALERTA POR ID (GET)
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas/<int:alert_id>", methods=["GET"])
@alertas_bp.route("/alertas/<int:alert_id>", methods=["GET"])
@token_required
def get_alerta_by_id(alert_id: int, current_user=None):
    """Obtiene el detalle de una alerta de monitoreo por su identificador primario."""
    alerta = repository.find_emergency_alert_by_id(alert_id)
    if not alerta:
        return jsonify({
            "success": False,
            "error": f"Alerta con ID {alert_id} no encontrada"
        }), 404

    return jsonify({
        "success": True,
        "data": _alert_to_dict(alerta)
    }), 200


# ==============================================================================
# 3. ACTUALIZAR ALERTA DE MONITOREO (PUT / UPDATE)
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas/<int:alert_id>", methods=["PUT"])
@alertas_bp.route("/alertas/<int:alert_id>", methods=["PUT"])
@token_required
def update_alerta(alert_id: int, current_user=None):
    """
    Actualiza el estado o detalle de una alerta de monitoreo en tiempo real.
    JSON body:
    {
        "status": "RESUELTA",
        "description": "Novedad controlada por las autoridades viales en Popayán.",
        "severity_level": "BAJA",
        "location_landmark": "Barrio Bolívar"
    }
    """
    alerta_actual = repository.find_emergency_alert_by_id(alert_id)
    if not alerta_actual:
        return jsonify({
            "success": False,
            "error": f"No se encontró la alerta de monitoreo con ID {alert_id}"
        }), 404

    data = request.get_json(silent=True) or {}
    status            = data.get("status")
    description       = data.get("description")
    severity_level    = data.get("severity_level")
    location_landmark = data.get("location_landmark")

    if not any([status, description, severity_level, location_landmark]):
        return jsonify({
            "success": False,
            "error": "Debe enviar al menos un campo para actualizar: status, description, severity_level o location_landmark"
        }), 400

    repository.update_emergency_alert(
        alert_id=alert_id,
        status=status,
        description=description,
        severity_level=severity_level,
        location_landmark=location_landmark
    )

    alerta_actualizada = repository.find_emergency_alert_by_id(alert_id)
    return jsonify({
        "success": True,
        "mensaje": f"Alerta {alert_id} actualizada correctamente",
        "data": _alert_to_dict(alerta_actualizada)
    }), 200


# ==============================================================================
# 4. ELIMINAR ALERTA DE MONITOREO (DELETE)
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas/<int:alert_id>", methods=["DELETE"])
@alertas_bp.route("/alertas/<int:alert_id>", methods=["DELETE"])
@token_required
def delete_alerta(alert_id: int, current_user=None):
    """
    Elimina permanentemente una alerta de monitoreo (falsa alarma o registro cerrado).
    """
    alerta_existente = repository.find_emergency_alert_by_id(alert_id)
    if not alerta_existente:
        return jsonify({
            "success": False,
            "error": f"No se encontró la alerta de monitoreo con ID {alert_id}"
        }), 404

    eliminado = repository.delete_emergency_alert(alert_id)
    if eliminado:
        return jsonify({
            "success": True,
            "mensaje": f"Alerta de monitoreo #{alert_id} eliminada exitosamente",
            "alerta_eliminada": _alert_to_dict(alerta_existente)
        }), 200

    return jsonify({
        "success": False,
        "error": f"No se pudo eliminar la alerta {alert_id}"
    }), 500
