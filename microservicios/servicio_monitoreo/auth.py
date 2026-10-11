import datetime
import functools
import hashlib
import jwt
from flask import request, jsonify
from config import Config
import repository

def hash_password(password: str) -> str:
    """Calcula el hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def check_password(password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    return hash_password(password) == hashed_password

def generate_token(user: dict) -> str:
    """Genera un JSON Web Token (JWT) firmado con expiración configurada."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "role": user.get("role", "OPERADOR"),
        "iat": datetime.datetime.utcnow(),
        "exp": expiration
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    """Decodifica y valida un JWT. Lanza excepciones de pyjwt si falla o expira."""
    return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])

def token_required(f):
    """
    Decorador de seguridad para proteger endpoints REST.
    Permite autenticación flexible mediante:
      1. Header HTTP 'Authorization: Bearer <JWT_TOKEN>'
      2. Header HTTP 'X-API-Key: <API_KEY>'
      3. Parámetro query '?api_key=<API_KEY>'
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        current_user = None

        # 1. Verificar si viene header Authorization Bearer
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = decode_token(token)
                user_id = int(payload.get("sub", 0))
                current_user = repository.find_user_by_id(user_id)
                if not current_user:
                    return jsonify({
                        "success": False,
                        "status": 401,
                        "error": "Usuario no encontrado",
                        "message": "El token es válido pero el usuario ya no existe en el sistema."
                    }), 401
            except jwt.ExpiredSignatureError:
                return jsonify({
                    "success": False,
                    "status": 401,
                    "error": "Token expirado",
                    "message": "La sesión ha expirado. Realice login nuevamente para obtener un nuevo token."
                }), 401
            except (jwt.InvalidTokenError, Exception) as e:
                return jsonify({
                    "success": False,
                    "status": 401,
                    "error": "Token inválido",
                    "message": f"El token JWT proporcionado no es válido: {str(e)}"
                }), 401

        # 2. Si no hay Bearer token, verificar X-API-Key o query param api_key
        if not current_user:
            api_key = (
                request.headers.get("X-API-Key")
                or request.headers.get("x-api-key")
                or request.headers.get("X-API-KEY")
                or request.args.get("api_key")
            )
            if api_key:
                key_clean = api_key.strip()
                if key_clean == "123":
                    # Clave maestra de desarrollo (123)
                    current_user = repository.find_user_by_username("admin") or {
                        "id": 1, "username": "admin", "role": "ADMIN", "api_key": "123"
                    }
                else:
                    current_user = repository.find_user_by_api_key(key_clean)

                if not current_user:
                    return jsonify({
                        "success": False,
                        "status": 401,
                        "error": "API Key inválida",
                        "message": "La API Key suministrada no coincide con ningún usuario registrado."
                    }), 401

        # 3. Si no pasó ninguna credencial válida
        if not current_user:
            return jsonify({
                "success": False,
                "status": 401,
                "error": "No autorizado",
                "message": "Acceso protegido. Envíe el header 'Authorization: Bearer <token>' o el header 'X-API-Key: <key>'."
            }), 401

        # Inyectar el usuario actual en los argumentos del endpoint si lo recibe, o permitir acceso
        kwargs["current_user"] = current_user
        return f(*args, **kwargs)

    return decorated
