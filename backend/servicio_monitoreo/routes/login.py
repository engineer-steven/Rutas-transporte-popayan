import re

from flask import Blueprint, jsonify, request

from auth import check_password, generate_token, token_required
import repository

login_bp = Blueprint("login_bp", __name__)
USERNAME_PATTERN = re.compile(r"[a-zA-Z0-9._-]{3,40}")


def _read_credentials():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return None, None, jsonify({
            "success": False,
            "error": "Campos requeridos",
            "mensaje": "Debe enviar 'username' y 'password'.",
        }), 400

    username = username.strip().lower()
    if not USERNAME_PATTERN.fullmatch(username):
        return None, None, jsonify({
            "success": False,
            "error": "Usuario inválido",
            "mensaje": "El usuario debe tener entre 3 y 40 caracteres: letras, números, punto, guion o guion bajo.",
        }), 400

    if not password.strip() or len(password) > 128:
        return None, None, jsonify({
            "success": False,
            "error": "Contraseña inválida",
            "mensaje": "La contraseña es obligatoria y no puede superar 128 caracteres.",
        }), 400

    return username, password, None, None


@login_bp.route("/login", methods=["POST"])
def login():
    username, password, error_response, error_status = _read_credentials()
    if error_response:
        return error_response, error_status

    user = repository.find_user_by_username(username)
    if not user or not check_password(password, user.get("password_hash", "")):
        return jsonify({
            "success": False,
            "error": "Credenciales inválidas",
            "mensaje": "Usuario o contraseña incorrectos.",
        }), 401

    return jsonify({
        "success": True,
        "token": generate_token(user),
        "tipo": "Bearer",
        "expira_horas": 24,
        "username": user["username"],
        "role": user.get("role", "USUARIO"),
    }), 200


@login_bp.route("/register", methods=["POST"])
def register():
    username, password, error_response, error_status = _read_credentials()
    if error_response:
        return error_response, error_status

    if (
        len(password) < 8
        or not any(char.isalpha() for char in password)
        or not any(char.isdigit() for char in password)
    ):
        return jsonify({
            "success": False,
            "error": "Contraseña inválida",
            "mensaje": "Usa entre 8 y 128 caracteres e incluye al menos una letra y un número.",
        }), 400

    if repository.find_user_by_username(username):
        return jsonify({
            "success": False,
            "error": "Usuario duplicado",
            "mensaje": f"El usuario '{username}' ya existe en el sistema.",
        }), 409

    if repository.create_user(username, password, "USUARIO"):
        return jsonify({
            "success": True,
            "mensaje": f"Cuenta de usuario '{username}' creada correctamente.",
        }), 201

    return jsonify({
        "success": False,
        "error": "No se pudo registrar el usuario",
    }), 500


@login_bp.route("/me", methods=["GET"])
@token_required
def me(current_user=None):
    return jsonify({
        "success": True,
        "username": current_user.get("username"),
        "role": current_user.get("role", "USUARIO"),
        "mensaje": "Token válido y sesión activa.",
    }), 200
