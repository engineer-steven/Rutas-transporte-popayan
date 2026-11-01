import functools
import os

try:
    import jwt
except ImportError:
    jwt = None

from config import Config

API_KEY = os.getenv("API_KEY", "").strip()
if API_KEY == "123":
    API_KEY = ""

JWT_SECRET_KEY = Config.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"
ROLE_ALIASES = {"PASAJERO": "USUARIO", "CONDUCTOR": "OPERADOR"}


def _jwt_payload(request):
    if jwt is None:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None


def _validate_api_key(request) -> bool:
    if not API_KEY:
        return False

    key = (
        request.headers.get("X-API-KEY", "")
        or request.headers.get("X-Api-Key", "")
        or request.args.get("api_key", "")
    )
    return key.strip() == API_KEY


def token_required(f):
    from flask import jsonify, request

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        payload = _jwt_payload(request)
        if payload:
            kwargs["current_user"] = payload
            return f(*args, **kwargs)

        if _validate_api_key(request):
            return f(*args, **kwargs)

        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": "Inicia sesión para acceder a este recurso.",
        }), 401

    return decorated


def role_required(*allowed_roles):
    from flask import jsonify, request

    allowed = {ROLE_ALIASES.get(role, role) for role in allowed_roles}

    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            payload = _jwt_payload(request)
            if not payload:
                return jsonify({
                    "success": False,
                    "error": "No autorizado",
                    "mensaje": "Se requiere una sesión válida para esta operación.",
                }), 401

            role = str(payload.get("role", "")).strip().upper()
            role = ROLE_ALIASES.get(role, role)
            if role not in allowed:
                return jsonify({
                    "success": False,
                    "error": "Permiso denegado",
                    "mensaje": "Tu rol no tiene permiso para realizar esta operación.",
                }), 403

            kwargs["current_user"] = payload
            return f(*args, **kwargs)

        return decorated

    return decorator
