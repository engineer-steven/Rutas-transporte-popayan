import os
import sys
import json
import base64
import binascii
import hashlib
import hmac
import datetime
import traceback
import requests
from urllib.parse import quote
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ------------------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "enrutate_jwt_secret_popayan_2026_default")

# Auto-detección si falta SUPABASE_URL
if not SUPABASE_URL:
    if SUPABASE_KEY and SUPABASE_KEY.startswith("eyJ"):
        try:
            parts = SUPABASE_KEY.split(".")
            if len(parts) >= 2:
                pad = len(parts[1]) % 4
                padded = parts[1] + ("=" * (4 - pad) if pad else "")
                p_json = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
                p_ref = p_json.get("ref")
                if p_ref:
                    SUPABASE_URL = f"https://{p_ref}.supabase.co"
        except Exception:
            pass

    if not SUPABASE_URL:
        SUPABASE_URL = "https://ppnonvpaqxmmnvayjuaw.supabase.co"


@app.errorhandler(Exception)
def handle_error(e):
    traceback.print_exc()
    res = jsonify({
        "success": False,
        "error": "Error interno del servidor",
        "mensaje": str(e)
    })
    res.headers["Access-Control-Allow-Origin"] = "*"
    return res, 500


def _supabase_call(method, endpoint, body=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, {"error": "Credenciales SUPABASE_URL o SUPABASE_KEY no configuradas en Vercel."}

    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        r = requests.request(method, url, headers=headers, json=body, timeout=8)
        if r.status_code in (200, 201, 204):
            return True, r.json() if r.text else {}
        return False, {"status": r.status_code, "message": r.text}
    except Exception as e:
        return False, {"error": str(e)}


def _check_pw(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    if plain == hashed:
        return True
    if hashed.startswith("pbkdf2:sha256:"):
        try:
            parts = hashed.split("$")
            salt = parts[1]
            target_hex = parts[2]
            dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), 100000)
            return hmac.compare_digest(dk.hex(), target_hex)
        except Exception:
            pass
    if len(hashed) == 64:
        legacy = hashlib.sha256(plain.encode("utf-8")).hexdigest()
        return hmac.compare_digest(legacy, hashed)
    return False


def _hash_pw(plain: str) -> str:
    salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2:sha256:100000${salt}${dk.hex()}"


def _get_user(username: str):
    for table in ["usuarios_api", "users"]:
        ok, res = _supabase_call("GET", f"{table}?username=eq.{username}&select=*")
        if ok and isinstance(res, list) and len(res) > 0:
            return res[0]
    return None


def _create_jwt(user: dict) -> str:
    exp = int((datetime.datetime.utcnow() + datetime.timedelta(hours=24)).timestamp())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user.get("id", 1)),
        "username": user.get("username", ""),
        "role": user.get("role", "USUARIO"),
        "full_name": user.get("full_name", user.get("username", "")),
        "exp": exp
    }
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    msg = f"{h_b64}.{p_b64}".encode()
    sig = hmac.new(JWT_SECRET.encode(), msg, hashlib.sha256).digest()
    s_b64 = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()
    return f"{h_b64}.{p_b64}.{s_b64}"


def _jwt_payload_from_request():
    """Lee y valida el JWT emitido por este mismo gateway."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
        padding = "=" * (-len(signature_b64) % 4)
        received = base64.urlsafe_b64decode((signature_b64 + padding).encode("ascii"))
        if not hmac.compare_digest(expected, received):
            return None

        payload_padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode((payload_b64 + payload_padding).encode("ascii")).decode("utf-8")
        )
        if int(payload.get("exp", 0)) < int(datetime.datetime.utcnow().timestamp()):
            return None
        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, binascii.Error):
        return None


def _require_admin():
    payload = _jwt_payload_from_request()
    if not payload:
        return None, (jsonify({"success": False, "error": "No autorizado"}), 401)
    if str(payload.get("role", "")).strip().upper() != "ADMIN":
        return None, (jsonify({"success": False, "error": "Permiso denegado"}), 403)
    return payload, None


def _require_authenticated():
    payload = _jwt_payload_from_request()
    if not payload:
        return None, (jsonify({"success": False, "error": "No autorizado"}), 401)
    return payload, None


def _route_payload(data):
    """Normaliza los campos que comparte el frontend con la tabla routes."""
    return {
        "code": str(data.get("code", "")).strip(),
        "company": str(data.get("company", "")).strip(),
        "origin": str(data.get("origin", "")).strip(),
        "destination": str(data.get("destination", "")).strip(),
        "fare": float(data.get("fare", 0) or 0),
        "schedule": str(data.get("schedule", "")).strip(),
        "status": str(data.get("status", "ACTIVA")).strip().upper(),
    }


def _routes_response(routes):
    return jsonify({"success": True, "total": len(routes), "data": routes}), 200


@app.route("/rutas", methods=["GET"])
@app.route("/api/rutas", methods=["GET"])
def get_routes():
    _, error = _require_authenticated()
    if error:
        return error
    ok, result = _supabase_call("GET", "routes?select=*&status=eq.ACTIVA&order=id.asc")
    if not ok:
        return jsonify({"success": False, "error": "No se pudieron cargar las rutas", "mensaje": result}), 502
    return _routes_response(result if isinstance(result, list) else [])


@app.route("/rutas/buscar", methods=["GET"])
@app.route("/api/rutas/buscar", methods=["GET"])
def search_routes():
    _, error = _require_authenticated()
    if error:
        return error
    zona = request.args.get("zona", "").strip()
    if not zona:
        return jsonify({"success": False, "error": "Parametro 'zona' requerido"}), 400

    termino = quote(f"*{zona}*", safe="*")
    endpoint = (
        "routes?select=*&status=eq.ACTIVA&or="
        f"(origin.ilike.{termino},destination.ilike.{termino},company.ilike.{termino},code.ilike.{termino})&order=id.asc"
    )
    ok, result = _supabase_call("GET", endpoint)
    if not ok:
        return jsonify({"success": False, "error": "No se pudo buscar la ruta", "mensaje": result}), 502
    return _routes_response(result if isinstance(result, list) else [])


@app.route("/rutas", methods=["POST"])
@app.route("/api/rutas", methods=["POST"])
def create_route():
    _, error = _require_admin()
    if error:
        return error
    try:
        payload = _route_payload(request.get_json(silent=True) or {})
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "La tarifa debe ser numérica"}), 400
    if not all([payload["code"], payload["company"], payload["origin"], payload["destination"]]):
        return jsonify({"success": False, "error": "Campos requeridos: code, company, origin, destination"}), 400

    ok, result = _supabase_call("POST", "routes", payload)
    if not ok:
        return jsonify({"success": False, "error": "No se pudo insertar la ruta", "mensaje": result}), 502
    return jsonify({"success": True, "data": result}), 201


@app.route("/rutas/<int:route_id>", methods=["PUT"])
@app.route("/api/rutas/<int:route_id>", methods=["PUT"])
def update_route(route_id):
    _, error = _require_admin()
    if error:
        return error
    try:
        payload = _route_payload(request.get_json(silent=True) or {})
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "La tarifa debe ser numérica"}), 400

    ok, result = _supabase_call("PATCH", f"routes?id=eq.{route_id}", payload)
    if not ok:
        return jsonify({"success": False, "error": "No se pudo actualizar la ruta", "mensaje": result}), 502
    if not result:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404
    return jsonify({"success": True, "data": result[0] if isinstance(result, list) else result}), 200


@app.route("/rutas/<int:route_id>", methods=["DELETE"])
@app.route("/api/rutas/<int:route_id>", methods=["DELETE"])
def delete_route(route_id):
    _, error = _require_admin()
    if error:
        return error

    ok, result = _supabase_call("DELETE", f"routes?id=eq.{route_id}")
    if not ok:
        return jsonify({"success": False, "error": "No se pudo eliminar la ruta", "mensaje": result}), 502
    if not result:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404
    return jsonify({"success": True, "mensaje": f"Ruta {route_id} eliminada correctamente"}), 200


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET"])
def health(path):
    ok, test_res = _supabase_call("GET", "usuarios_api?select=id&limit=1")
    return jsonify({
        "servicio": "EnRutate Popayán API Gateway",
        "status": "online",
        "supabase_url": SUPABASE_URL,
        "supabase_conectado": ok,
        "supabase_respuesta": test_res if not ok else "OK",
        "key_presente": bool(SUPABASE_KEY),
        "key_tipo": "JWT" if SUPABASE_KEY.startswith("eyJ") else ("Secret" if SUPABASE_KEY.startswith("sb_") else "Otro")
    }), 200


@app.route("/login", methods=["POST"])
@app.route("/api/login", methods=["POST"])
@app.route("/api/servicio_monitoreo/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Campos requeridos",
            "mensaje": "Debe ingresar usuario y contraseña."
        }), 400

    user = _get_user(username)
    if not user or not _check_pw(password, user.get("password_hash", "")):
        return jsonify({
            "success": False,
            "error": "Credenciales inválidas",
            "mensaje": "Usuario o contraseña incorrectos."
        }), 401

    token = _create_jwt(user)
    return jsonify({
        "success": True,
        "token": token,
        "tipo": "Bearer",
        "username": user.get("username"),
        "role": user.get("role", "USUARIO"),
        "full_name": user.get("full_name", user.get("username")),
        "api_key": user.get("api_key", "")
    }), 200


@app.route("/register", methods=["POST"])
@app.route("/api/register", methods=["POST"])
@app.route("/api/servicio_monitoreo/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Campos requeridos",
            "mensaje": "Debe enviar usuario y contraseña."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "error": "Contraseña muy corta",
            "mensaje": "La contraseña debe tener al menos 6 caracteres."
        }), 400

    if _get_user(username):
        return jsonify({
            "success": False,
            "error": "Usuario duplicado",
            "mensaje": f"El usuario '{username}' ya está registrado."
        }), 409

    hashed = _hash_pw(password)
    user_payload = {
        "username": username,
        "password_hash": hashed,
        "full_name": f"Usuario {username.capitalize()}",
        "role": "USUARIO"
    }

    ok, res = _supabase_call("POST", "usuarios_api", user_payload)
    if not ok:
        ok, res = _supabase_call("POST", "users", user_payload)

    if not ok:
        msg = res.get("message") if isinstance(res, dict) else str(res)
        return jsonify({
            "success": False,
            "error": "Error al registrar en Supabase",
            "mensaje": f"Supabase rechazó la inserción: {msg}"
        }), 500

    created_user = res[0] if isinstance(res, list) and len(res) > 0 else user_payload
    token = _create_jwt(created_user)

    return jsonify({
        "success": True,
        "token": token,
        "username": username,
        "role": "USUARIO",
        "mensaje": "Usuario registrado exitosamente."
    }), 201


@app.route("/me", methods=["GET"])
@app.route("/api/me", methods=["GET"])
@app.route("/api/servicio_monitoreo/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "No autorizado"}), 401

    token = auth_header.split(" ", 1)[1].strip()
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            pad = len(parts[1]) % 4
            padded = parts[1] + ("=" * (4 - pad) if pad else "")
            payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
            return jsonify({
                "success": True,
                "username": payload.get("username"),
                "role": payload.get("role"),
                "full_name": payload.get("full_name")
            }), 200
    except Exception:
        pass

    return jsonify({"error": "Token inválido o expirado"}), 401


handler = app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
