from flask import Blueprint, request, jsonify
import repository
from auth import token_required

rutas_bp = Blueprint("rutas_bp", __name__, url_prefix="/rutas")


def _route_to_dict(r) -> dict:
    return {
        "id":          r.id,
        "code":        r.code,
        "company":     r.company,
        "origin":      r.origin,
        "destination": r.destination,
        "fare":        r.fare,
        "schedule":    r.schedule,
        "status":      r.status
    }


# ==============================================================================
# CRUD: RUTAS
# ==============================================================================

@rutas_bp.route("", methods=["GET"], strict_slashes=False)
@token_required
def get_all_routes(current_user=None):
    """Lista todas las rutas activas."""
    rutas = repository.find_all_active()
    datos = [_route_to_dict(r) for r in rutas]
    return jsonify({"success": True, "total": len(datos), "data": datos}), 200


@rutas_bp.route("/<int:route_id>", methods=["GET"])
@token_required
def get_route_by_id(route_id, current_user=None):
    """Retorna una ruta por su ID."""
    ruta = repository.find_by_id(route_id)
    if not ruta:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404
    return jsonify({"success": True, "data": _route_to_dict(ruta)}), 200


@rutas_bp.route("/buscar", methods=["GET"])
@token_required
def search_routes_by_zone(current_user=None):
    """Busca rutas por zona/sector. Parametro: ?zona=<keyword>"""
    zona = request.args.get("zona", "").strip()
    if not zona:
        return jsonify({"success": False, "error": "Parametro 'zona' requerido"}), 400
    rutas = repository.search_by_zone(zona)
    return jsonify({"success": True, "total": len(rutas), "data": [_route_to_dict(r) for r in rutas]}), 200


@rutas_bp.route("", methods=["POST"], strict_slashes=False)
@token_required
def add_route(current_user=None):
    """Registra una nueva ruta. JSON: {code, company, origin, destination, fare, schedule}"""
    data = request.get_json(silent=True) or {}
    code        = str(data.get("code", "")).strip()
    company     = str(data.get("company", "")).strip()
    origin      = str(data.get("origin", "")).strip()
    destination = str(data.get("destination", "")).strip()
    fare        = data.get("fare", 0)
    schedule    = str(data.get("schedule", "")).strip()

    if not all([code, company, origin, destination]):
        return jsonify({"success": False, "error": "Campos requeridos: code, company, origin, destination"}), 400

    ok = repository.insert_route(code, company, origin, destination, float(fare), schedule)
    if ok:
        return jsonify({"success": True, "mensaje": f"Ruta '{code}' registrada correctamente"}), 201
    return jsonify({"success": False, "error": "No se pudo insertar la ruta"}), 500


@rutas_bp.route("/<int:route_id>", methods=["PUT"])
@token_required
def update_route(route_id, current_user=None):
    """Actualiza una ruta existente."""
    data = request.get_json(silent=True) or {}
    code        = str(data.get("code", "")).strip()
    company     = str(data.get("company", "")).strip()
    origin      = str(data.get("origin", "")).strip()
    destination = str(data.get("destination", "")).strip()
    fare        = data.get("fare", 0)
    schedule    = str(data.get("schedule", "")).strip()
    status      = str(data.get("status", "ACTIVA")).strip()

    ok = repository.update_route(route_id, code, company, origin, destination, float(fare), schedule, status)
    if ok:
        ruta = repository.find_by_id(route_id)
        return jsonify({"success": True, "data": _route_to_dict(ruta)}), 200
    return jsonify({"success": False, "error": f"No se pudo actualizar la ruta {route_id}"}), 404


@rutas_bp.route("/<int:route_id>", methods=["DELETE"])
@token_required
def delete_route(route_id, current_user=None):
    """Elimina una ruta por su ID."""
    ok = repository.delete_route(route_id)
    if ok:
        return jsonify({"success": True, "mensaje": f"Ruta {route_id} eliminada correctamente"}), 200
    return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404
