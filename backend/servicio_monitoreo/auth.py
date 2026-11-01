from datetime import datetime, timedelta, timezone
from functools import wraps
import hashlib
import hmac

import jwt
from flask import jsonify, request
from werkzeug.security import check_password_hash

from config import Config
import repository

ROLE_ALIASES = {"PASAJERO": "USUARIO", "CONDUCTOR": "OPERADOR"}


def check_password(password, password_hash):
    if not password_hash:
        return False
    if password_hash.startswith(("scrypt:", "pbkdf2:")):
        return check_password_hash(password_hash, password)
    candidate_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(candidate_hash, password_hash)


def generate_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user.get("role", "USUARIO"),
        "iat": now,
        "exp": now + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, separator, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not separator or not token.strip():
            return jsonify({
                "success": False,
                "error": "Autenticación requerida",
                "mensaje": "Debe iniciar sesión para acceder a este recurso.",
            }), 401

        try:
            payload = decode_token(token.strip())
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token expirado",
                "mensaje": "Inicie sesión nuevamente.",
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": "Token inválido",
                "mensaje": "Inicie sesión nuevamente.",
            }), 401

        try:
            user_id = int(payload.get("user_id"))
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "error": "Token inválido",
                "mensaje": "Inicie sesión nuevamente.",
            }), 401

        current_user = repository.find_user_by_id(user_id)
        if not current_user:
            return jsonify({
                "success": False,
                "error": "Usuario no encontrado",
                "mensaje": "Inicie sesión nuevamente.",
            }), 401

        kwargs["current_user"] = current_user
        return function(*args, **kwargs)

    return decorated


def role_required(*allowed_roles):
    allowed = {ROLE_ALIASES.get(role, role) for role in allowed_roles}

    def decorator(function):
        @wraps(function)
        def decorated(*args, **kwargs):
            current_user = kwargs.get("current_user")
            role = None
            if current_user:
                stored_role = str(current_user.get("role", "")).strip().upper()
                role = ROLE_ALIASES.get(stored_role, stored_role)
            if not current_user or role not in allowed:
                return jsonify({
                    "success": False,
                    "error": "Acceso denegado",
                    "mensaje": "No tiene permisos para realizar esta acción.",
                }), 403
            return function(*args, **kwargs)

        return token_required(decorated)

    return decorator
