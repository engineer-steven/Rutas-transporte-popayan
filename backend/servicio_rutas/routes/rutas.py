# ==============================================================================
# ARCHIVO: backend/servicio_rutas/routes/rutas.py
# RESPONSABILIDAD: Controlador REST para operaciones CRUD de la entidad Ruta.
# PREFIJO URL: /rutas
# ==============================================================================

# Importa utilidades de Flask para enrutamiento, lectura de peticiones y respuestas JSON.
from flask import Blueprint, request, jsonify

# Importa la capa de acceso a datos de rutas.
import repository

# Importa el decorador de seguridad para proteger los endpoints.
from auth import role_required, token_required

# Declara el Blueprint de rutas con el prefijo /rutas.
rutas_bp = Blueprint("rutas_bp", __name__, url_prefix="/rutas")


def _route_to_dict(r) -> dict:
    """Función auxiliar de serialización para normalizar el objeto ruta a formato JSON plano."""
    return {
        "id":          r["id"],
        "code":        r["code"],
        "company":     r["company"],
        "origin":      r["origin"],
        "destination": r["destination"],
        "fare":        r["fare"],
        "schedule":    r["schedule"],
        "status":      r["status"]
    }


# ==============================================================================
# 1. LISTAR TODAS LAS RUTAS ACTIVAS (GET /rutas)
# ==============================================================================
@rutas_bp.route("", methods=["GET"], strict_slashes=False)
@token_required
def get_all_routes(current_user=None):
    """Retorna el listado completo de rutas activas en formato JSON."""
    # Consulta la base de datos a través del repositorio.
    rutas = repository.find_all_active()
    # Transforma cada registro a diccionario limpio.
    datos = [_route_to_dict(r) for r in rutas]
    # Retorna HTTP 200 OK con el total de registros y los datos.
    return jsonify({"success": True, "total": len(datos), "data": datos}), 200


# ==============================================================================
# 2. OBTENER RUTA POR SU ID (GET /rutas/<id>)
# ==============================================================================
@rutas_bp.route("/<int:route_id>", methods=["GET"])
@token_required
def get_route_by_id(route_id, current_user=None):
    """Busca y retorna una ruta específica por su identificador primario."""
    # Consulta la ruta por ID.
    ruta = repository.find_by_id(route_id)
    # Si no existe en la base de datos, retorna HTTP 404 Not Found.
    if not ruta:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404
    # Si existe, retorna HTTP 200 OK con la información de la ruta.
    return jsonify({"success": True, "data": _route_to_dict(ruta)}), 200


# ==============================================================================
# 3. BUSCAR RUTAS POR ZONA O SECTOR (GET /rutas/buscar?zona=...)
# ==============================================================================
@rutas_bp.route("/buscar", methods=["GET"])
@token_required
def search_routes_by_zone(current_user=None):
    """Filtra rutas que conecten con un sector de Popayán (ej: Campanario, Centro)."""
    # Lee el parámetro de consulta 'zona' enviado en la URL (?zona=...).
    zona = request.args.get("zona", "").strip()
    # Si el cliente no envió el parámetro, retorna HTTP 400 Bad Request.
    if not zona:
        return jsonify({"success": False, "error": "Parametro 'zona' requerido"}), 400
    # Ejecuta la búsqueda relacional sobre orígenes, destinos y nombres de paraderos.
    rutas = repository.search_by_zone(zona)
    # Retorna HTTP 200 OK con las coincidencias encontradas.
    return jsonify({"success": True, "total": len(rutas), "data": [_route_to_dict(r) for r in rutas]}), 200


# ==============================================================================
# 4. REGISTRAR UNA NUEVA RUTA (POST /rutas)
# ==============================================================================
@rutas_bp.route("", methods=["POST"], strict_slashes=False)
@role_required("ADMIN")
def add_route(current_user=None):
    """Registra una nueva ruta de transporte público urbano."""
    # Lee el cuerpo de la petición en formato JSON de forma segura.
    data = request.get_json(silent=True) or {}
    # Extrae y sanitiza cada uno de los campos enviados.
    code        = str(data.get("code", "")).strip()
    company     = str(data.get("company", "")).strip()
    origin      = str(data.get("origin", "")).strip()
    destination = str(data.get("destination", "")).strip()
    fare        = data.get("fare", 0)
    schedule    = str(data.get("schedule", "")).strip()
    status      = str(data.get("status", "ACTIVA")).strip().upper()

    # Valida la presencia de campos estrictamente requeridos.
    if not all([code, company, origin, destination]):
        return jsonify({"success": False, "error": "Campos requeridos: code, company, origin, destination"}), 400

    # Invoca al repositorio para insertar el registro en la base de datos.
    ok = repository.insert_route(code, company, origin, destination, float(fare), schedule, status)
    # Si la inserción afectó filas, retorna HTTP 201 Created.
    if ok:
        return jsonify({"success": True, "mensaje": f"Ruta '{code}' registrada correctamente"}), 201
    # Si falló la inserción, retorna HTTP 500 Internal Server Error.
    return jsonify({"success": False, "error": "No se pudo insertar la ruta"}), 500


# ==============================================================================
# 5. ACTUALIZAR RUTA EXISTENTE (PUT /rutas/<id>)
# ==============================================================================
@rutas_bp.route("/<int:route_id>", methods=["PUT"])
@role_required("ADMIN")
def update_route(route_id, current_user=None):
    """Actualiza la información completa de una ruta existente (operación idempotente)."""
    # Lee el cuerpo JSON de la actualización.
    data = request.get_json(silent=True) or {}
    # Extrae los valores actualizados.
    code        = str(data.get("code", "")).strip()
    company     = str(data.get("company", "")).strip()
    origin      = str(data.get("origin", "")).strip()
    destination = str(data.get("destination", "")).strip()
    fare        = data.get("fare", 0)
    schedule    = str(data.get("schedule", "")).strip()
    status      = str(data.get("status", "ACTIVA")).strip()

    # Ejecuta el UPDATE parametrizado en la base de datos.
    ok = repository.update_route(route_id, code, company, origin, destination, float(fare), schedule, status)
    # Si la actualización fue exitosa, consulta y retorna el recurso modificado con HTTP 200 OK.
    if ok:
        ruta = repository.find_by_id(route_id)
        return jsonify({"success": True, "data": _route_to_dict(ruta)}), 200
    # Si no existía la ruta para actualizar, retorna HTTP 404 Not Found.
    return jsonify({"success": False, "error": f"No se pudo actualizar la ruta {route_id}"}), 404


# ==============================================================================
# 6. ELIMINAR UNA RUTA (DELETE /rutas/<id>)
# ==============================================================================
@rutas_bp.route("/<int:route_id>", methods=["DELETE"])
@role_required("ADMIN")
def delete_route(route_id, current_user=None):
    """Elimina físicamente una ruta por su ID."""
    # Ejecuta la sentencia DELETE en el repositorio.
    ok = repository.delete_route(route_id)
    # Si se eliminó correctamente, retorna HTTP 200 OK.
    if ok:
        return jsonify({"success": True, "mensaje": f"Ruta {route_id} eliminada correctamente"}), 200
    # Si la ruta no existía, retorna HTTP 404 Not Found.
    return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404
