# ==============================================================================
# ARCHIVO: backend/servicio_monitoreo/routes/alertas.py
# RESPONSABILIDAD: Controlador REST para el ciclo de vida (CRUD) de Alertas de Emergencia.
# PREFIJO URL: /monitoreo/alertas y /alertas
# ==============================================================================

# Importa módulos de Flask para rutas, lectura de peticiones y respuestas JSON.
from flask import Blueprint, request, jsonify

# Importa el decorador para requerir JWT y validar el rol.
from auth import role_required

# Importa la capa de persistencia de alertas y usuarios.
import repository

# Declara el Blueprint de alertas.
alertas_bp = Blueprint("alertas_bp", __name__)


def _alert_to_dict(alert: dict) -> dict:
    """Normaliza y formatea los campos de fecha y números flotantes de una alerta para serialización JSON."""
    if not alert:
        return {}
    res = dict(alert)
    # Convierte objetos datetime a string legible
    if "created_at" in res and res["created_at"]:
        res["created_at"] = str(res["created_at"])
    # Convierte el score de criticidad a float nativo
    if "criticality_score" in res and res["criticality_score"] is not None:
        res["criticality_score"] = float(res["criticality_score"])
    return res


# ==============================================================================
# 1. CREAR / REGISTRAR NUEVA ALERTA DE EMERGENCIA (POST)
# Endpoints: POST /monitoreo/alertas y POST /alertas
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas", methods=["POST"])
@alertas_bp.route("/alertas", methods=["POST"])
@role_required("ADMIN")
def create_alerta(current_user=None):
    """Registra un evento crítico en vía (botón de pánico, falla mecánica, colisión)."""
    # Lee los datos del cuerpo JSON
    data = request.get_json(silent=True) or {}
    try:
        route_id = int(data.get("route_id", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "route_id debe ser un número entero"}), 400

    # Extrae y sanitiza atributos de la alerta
    bus_plate = str(data.get("bus_plate", "")).strip().upper()
    alert_type = str(data.get("alert_type", "BOTON_PANICO")).strip().upper()
    severity_level = str(data.get("severity_level", "ALTA")).strip().upper()
    location_landmark = str(data.get("location_landmark", "Sector Urbano Popayán")).strip()
    description = str(data.get("description", "")).strip()

    # Parsea los valores de criticidad y tiempo máximo de respuesta
    try:
        criticality_score = float(data.get("criticality_score", 85.0))
        max_response_time_minutes = int(data.get("max_response_time_minutes", 10))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parámetros numéricos inválidos"}), 400

    # Valida campos indispensables
    if not route_id or not bus_plate or not description:
        return jsonify({
            "success": False,
            "error": "Campos requeridos: route_id, bus_plate y description"
        }), 400

    # Valida que la ruta exista en la base de datos de transporte
    ruta = repository.find_route_by_id(route_id)
    if not ruta:
        return jsonify({
            "success": False,
            "error": f"La ruta con ID {route_id} no existe en el sistema de transporte"
        }), 404

    # Guarda el registro en la base de datos
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
        # Recupera la alerta recién creada y responde HTTP 201 Created
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
# 2. LISTAR TODAS LAS ALERTAS REGISTRADAS (GET)
# Endpoints: GET /monitoreo/alertas y GET /alertas
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas", methods=["GET"])
@alertas_bp.route("/alertas", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR")
def get_all_alertas(current_user=None):
    """Retorna el histórico y las alertas activas del sistema de monitoreo."""
    alertas = repository.get_all_emergency_alerts()
    data = [_alert_to_dict(a) for a in alertas]
    return jsonify({
        "success": True,
        "total": len(data),
        "data": data
    }), 200


# ==============================================================================
# 3. OBTENER DETALLE DE UNA ALERTA POR ID (GET)
# Endpoints: GET /monitoreo/alertas/<id> y GET /alertas/<id>
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas/<int:alert_id>", methods=["GET"])
@alertas_bp.route("/alertas/<int:alert_id>", methods=["GET"])
@role_required("ADMIN", "SUPERVISOR")
def get_alerta_by_id(alert_id: int, current_user=None):
    """Consulta una alerta específica mediante su identificador primario."""
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
# 4. ACTUALIZAR ESTADO O INFORMACIÓN DE UNA ALERTA (PUT)
# Endpoints: PUT /monitoreo/alertas/<id> y PUT /alertas/<id>
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas/<int:alert_id>", methods=["PUT"])
@alertas_bp.route("/alertas/<int:alert_id>", methods=["PUT"])
@role_required("ADMIN")
def update_alerta(alert_id: int, current_user=None):
    """Actualiza campos de una alerta existente (ej. marcar de ACTIVA a RESUELTA)."""
    # Verifica que la alerta exista
    alerta_actual = repository.find_emergency_alert_by_id(alert_id)
    if not alerta_actual:
        return jsonify({
            "success": False,
            "error": f"No se encontró la alerta de monitoreo con ID {alert_id}"
        }), 404

    # Lee los campos a modificar
    data = request.get_json(silent=True) or {}
    status            = data.get("status")
    description       = data.get("description")
    severity_level    = data.get("severity_level")
    location_landmark = data.get("location_landmark")

    # Verifica que al menos un campo haya sido suministrado
    if not any([status, description, severity_level, location_landmark]):
        return jsonify({
            "success": False,
            "error": "Debe enviar al menos un campo para actualizar: status, description, severity_level o location_landmark"
        }), 400

    # Aplica la actualización dinámica en base de datos
    repository.update_emergency_alert(
        alert_id=alert_id,
        status=status,
        description=description,
        severity_level=severity_level,
        location_landmark=location_landmark
    )

    # Consulta y devuelve el registro actualizado con HTTP 200 OK
    alerta_actualizada = repository.find_emergency_alert_by_id(alert_id)
    return jsonify({
        "success": True,
        "mensaje": f"Alerta {alert_id} actualizada correctamente",
        "data": _alert_to_dict(alerta_actualizada)
    }), 200


# ==============================================================================
# 5. ELIMINAR FÍSICAMENTE UNA ALERTA (DELETE)
# Endpoints: DELETE /monitoreo/alertas/<id> y DELETE /alertas/<id>
# ==============================================================================
@alertas_bp.route("/monitoreo/alertas/<int:alert_id>", methods=["DELETE"])
@alertas_bp.route("/alertas/<int:alert_id>", methods=["DELETE"])
@role_required("ADMIN")
def delete_alerta(alert_id: int, current_user=None):
    """Elimina permanentemente una alerta (falsa alarma o auditoría concluida)."""
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
