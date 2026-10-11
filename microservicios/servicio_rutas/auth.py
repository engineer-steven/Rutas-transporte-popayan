import os
import json
import datetime
import hashlib

try:
    import jwt
    _HAS_JWT = True
except ImportError:
    _HAS_JWT = False

API_KEY        = os.getenv("API_KEY",        "123")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "popayan_secreto_transporte_jwt_2026")
JWT_ALGORITHM  = "HS256"


def _validate_api_key(request) -> bool:
    key = (
        request.headers.get("X-API-KEY", "")
        or request.headers.get("X-Api-Key", "")
        or request.args.get("api_key", "")
    )
    return key.strip() == API_KEY


def _validate_jwt(request) -> bool:
    if not _HAS_JWT:
        return False
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ", 1)[1].strip()
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return True
    except Exception:
        return False


def token_required(f):
    """
    Decorador Flask que acepta:
      - Header X-API-KEY: 123
      - Header Authorization: Bearer <jwt_token>
    El token se obtiene en POST http://127.0.0.1:5003/api/v1/auth/login
    """
    import functools
    from flask import request, jsonify

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if _validate_api_key(request):
            return f(*args, **kwargs)
        if _validate_jwt(request):
            return f(*args, **kwargs)
        return jsonify({
            "success": False,
            "error": "No autorizado",
            "mensaje": (
                "Envie 'X-API-KEY: 123' "
                "o 'Authorization: Bearer <token>'. "
                "Token: POST http://127.0.0.1:5003/api/v1/auth/login"
            )
        }), 401

    return decorated


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
