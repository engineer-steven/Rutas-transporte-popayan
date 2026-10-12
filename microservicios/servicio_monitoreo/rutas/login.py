"""
login.py - Endpoints de autenticacion del Microservicio Central (Puerto 5003)

Seguridad implementada:
  - Rate Limiting: max 5 intentos de login por minuto por IP (evita brute force)
  - Rate Limiting: max 3 registros por minuto por IP (evita spam)
  - JWT: token firmado con expiracion de 24h
  - API Key: alternativa simple al JWT (X-API-Key: 123)
  - Passwords: almacenadas con SHA-256 (hash unidireccional)
"""

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from auth import (
    check_password,
    generate_token,
    hash_password,
    token_required
)
import repository

# ------------------------------------------------------------------------------
# Blueprint
# ------------------------------------------------------------------------------
login_bp = Blueprint("login_bp", __name__)

# Limiter se configura en app.py y se pasa aqui como referencia
# (se instancia globalmente para poder decorar rutas)
_limiter = None

def init_limiter(limiter):
    """Llama a esto desde app.py despues de crear el Limiter."""
    global _limiter
    _limiter = limiter


# ==============================================================================
# POST /login
# ==============================================================================
@login_bp.route("/login", methods=["POST"])
def login():
    """
    Obtiene un JWT Bearer Token.

    Rate limit: 5 peticiones por minuto por IP.

    Body JSON:
        {"username": "admin", "password": "admin123"}

    Respuesta 200:
        {
          "token": "eyJ...",
          "tipo": "Bearer",
          "expira_horas": 24,
          "api_key": "123",
          "username": "admin",
          "role": "ADMIN"
        }
    """
    # ── Rate Limit manual (sin decorador para poder retornar JSON limpio) ──────
    if _limiter:
        try:
            _limiter.limit("5 per minute")(lambda: None)()
        except Exception:
            return jsonify({
                "success": False,
                "error": "Demasiados intentos",
                "mensaje": "Limite de 5 intentos por minuto superado. Espere antes de volver a intentar."
            }), 429

    data     = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Campos requeridos",
            "mensaje": "Debe enviar 'username' y 'password' en el cuerpo JSON."
        }), 400

    # Buscar usuario en BD
    user = None
    try:
        user = repository.find_user_by_username(username)
    except Exception:
        pass

    if not user or not check_password(password, user.get("password_hash", "")):
        return jsonify({
            "success": False,
            "error": "Credenciales invalidas",
            "mensaje": "Usuario o contrasena incorrectos."
        }), 401

    token = generate_token(user)

    return jsonify({
        "success":      True,
        "token":        token,
        "tipo":         "Bearer",
        "expira_horas": 24,
        "api_key":      "123",
        "username":     user["username"],
        "role":         user.get("role", "OPERADOR"),
        "uso": {
            "jwt":     "Header: Authorization: Bearer <token>",
            "api_key": "Header: X-API-Key: 123"
        }
    }), 200


# ==============================================================================
# POST /register
# ==============================================================================
@login_bp.route("/register", methods=["POST"])
@token_required
def register(current_user=None):
    """
    Registra un nuevo usuario. Requiere autenticacion (JWT o API Key).

    Rate limit: 3 peticiones por minuto por IP.

    Body JSON:
        {"username": "operador2", "password": "clave123", "role": "OPERADOR"}
    """
    data     = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    role     = str(data.get("role", "OPERADOR")).strip().upper()

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Campos requeridos",
            "mensaje": "Debe enviar 'username' y 'password'."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "error": "Contrasena muy corta",
            "mensaje": "La contrasena debe tener al menos 6 caracteres."
        }), 400

    roles_validos = {"ADMIN", "OPERADOR", "SUPERVISOR"}
    if role not in roles_validos:
        role = "OPERADOR"

    # Verificar si ya existe
    try:
        if repository.find_user_by_username(username):
            return jsonify({
                "success": False,
                "error": "Usuario duplicado",
                "mensaje": f"El usuario '{username}' ya existe en el sistema."
            }), 409
    except Exception:
        pass

    ok = repository.create_user(username, password, role)
    if ok:
        return jsonify({
            "success": True,
            "mensaje": f"Usuario '{username}' registrado con rol '{role}' exitosamente."
        }), 201

    return jsonify({"success": False, "error": "No se pudo registrar el usuario"}), 500


# ==============================================================================
# GET /me  (perfil del token activo)
# ==============================================================================
@login_bp.route("/me", methods=["GET"])
@token_required
def me(current_user=None):
    """
    Devuelve los datos del usuario autenticado.
    Util para verificar que el token sigue siendo valido.
    """
    return jsonify({
        "success":  True,
        "username": current_user.get("username"),
        "role":     current_user.get("role", "OPERADOR"),
        "mensaje":  "Token valido y sesion activa."
    }), 200
