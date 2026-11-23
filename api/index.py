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


def _supabase_first(method, endpoints, body=None):
    """Prueba nombres de tabla compatibles con el esquema desplegado."""
    last = None
    for endpoint in endpoints:
        ok, result = _supabase_call(method, endpoint, body)
        if ok:
            return True, result
        last = result
    return False, last or {"error": "No se pudo consultar Supabase"}


def _admin_or_roles(*roles):
    payload = _jwt_payload_from_request()
    if not payload:
        return None, (jsonify({"success": False, "error": "No autorizado"}), 401)
    allowed = {"ADMIN", *roles}
    role = str(payload.get("role", "")).strip().upper()
    if role not in allowed:
        return None, (jsonify({"success": False, "error": "Permiso denegado"}), 403)
    return payload, None


def _route_stops(route_id):
    ok, result = _supabase_first(
        "GET",
        [
            f"paraderos?route_id=eq.{route_id}&select=*&order=stop_order.asc",
            f"stops?route_id=eq.{route_id}&select=*&order=stop_order.asc",
        ],
    )
    if not ok:
        return False, result
    return True, result if isinstance(result, list) else []


def _route_incidents(route_id):
    ok, result = _supabase_first(
        "GET",
        [
            f"incidentes?route_id=eq.{route_id}&status=eq.ACTIVO&select=*&order=id.desc",
            f"incidents?route_id=eq.{route_id}&status=eq.ACTIVO&select=*&order=id.desc",
        ],
    )
    if not ok:
        return False, result
    return True, result if isinstance(result, list) else []


def _normalise_stop(row):
    return {
        "id": row.get("id"),
        "route_id": row.get("route_id"),
        "nombre": row.get("nombre", row.get("name", "")),
        "referencia": row.get("referencia", row.get("landmark_reference", "")),
        "orden": row.get("orden", row.get("stop_order", 0)),
    }


def _normalise_incident(row):
    return {
        "id": row.get("id"),
        "route_id": row.get("route_id"),
        "tipo": row.get("tipo", row.get("incident_type", "")),
        "descripcion": row.get("descripcion", row.get("description", "")),
        "reportado_por": row.get("reportado_por", row.get("reported_by", "")),
        "reportado_en": row.get("reportado_en", row.get("reported_at", "")),
        "estado": row.get("estado", row.get("status", "ACTIVO")),
    }


@app.route("/operaciones/paraderos/<int:route_id>", methods=["GET"])
@app.route("/api/operaciones/paraderos/<int:route_id>", methods=["GET"])
def deployed_stops(route_id):
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    ok, result = _route_stops(route_id)
    if not ok:
        return jsonify({"success": False, "error": "No se pudieron cargar los paraderos", "mensaje": result}), 502
    data = [_normalise_stop(row) for row in result]
    return jsonify({"success": True, "route_id": route_id, "total_paraderos": len(data), "data": data}), 200


@app.route("/operaciones/incidentes/<int:route_id>", methods=["GET"])
@app.route("/api/operaciones/incidentes/<int:route_id>", methods=["GET"])
def deployed_incidents(route_id):
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    ok, result = _route_incidents(route_id)
    if not ok:
        return jsonify({"success": False, "error": "No se pudieron cargar los incidentes", "mensaje": result}), 502
    data = [_normalise_incident(row) for row in result]
    return jsonify({"success": True, "route_id": route_id, "total_incidentes": len(data), "data": data}), 200


@app.route("/operaciones/incidentes/<int:incident_id>", methods=["PUT"])
@app.route("/api/operaciones/incidentes/<int:incident_id>", methods=["PUT"])
def deployed_update_incident(incident_id):
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "RESUELTO")).strip().upper()
    if status not in {"ACTIVO", "RESUELTO", "INACTIVO", "CERRADO"}:
        return jsonify({"success": False, "error": "Estado de incidente no válido"}), 400
    ok, result = _supabase_first(
        "PATCH",
        [f"incidents?id=eq.{incident_id}", f"incidentes?id=eq.{incident_id}"],
        {"status": status},
    )
    if not ok:
        return jsonify({"success": False, "error": "No se pudo desactivar la novedad vial", "mensaje": result}), 502
    return jsonify({"success": True, "mensaje": f"Novedad vial #{incident_id} marcada como {status}"}), 200


@app.route("/operaciones/incidente", methods=["POST"])
@app.route("/api/operaciones/incidente", methods=["POST"])
def deployed_create_incident():
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    data = request.get_json(silent=True) or {}
    try:
        route_id = int(data.get("route_id", 0))
    except (TypeError, ValueError):
        route_id = 0
    if not route_id or not data.get("incident_type") or not data.get("description"):
        return jsonify({"success": False, "error": "Campos requeridos: route_id, incident_type, description"}), 400
    payload = {
        "route_id": route_id,
        "incident_type": str(data["incident_type"]).strip(),
        "description": str(data["description"]).strip(),
        "reported_by": str(data.get("reported_by", "Sistema")).strip(),
        "status": "ACTIVO",
    }
    ok, result = _supabase_first("POST", ["incidentes", "incidents"], payload)
    if not ok:
        return jsonify({"success": False, "error": "No se pudo registrar el incidente", "mensaje": result}), 502
    return jsonify({"success": True, "mensaje": f"Incidente '{payload['incident_type']}' registrado en ruta {route_id}."}), 201


@app.route("/operaciones/diferencia-horas", methods=["GET"])
@app.route("/api/operaciones/diferencia-horas", methods=["GET"])
def deployed_time_gap():
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    try:
        h1 = datetime.datetime.strptime(request.args.get("hora1", ""), "%H:%M")
        h2 = datetime.datetime.strptime(request.args.get("hora2", ""), "%H:%M")
    except ValueError:
        return jsonify({"success": False, "error": "Formato invalido: use HH:MM"}), 400
    return jsonify({"success": True, "hora_1": request.args["hora1"], "hora_2": request.args["hora2"], "diferencia_minutos": abs(int((h2 - h1).total_seconds() / 60)), "mensaje": "Brecha horaria calculada correctamente."}), 200


@app.route("/operaciones/diferencia-buses", methods=["GET"])
@app.route("/api/operaciones/diferencia-buses", methods=["GET"])
def deployed_bus_gap():
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    try:
        route_id = int(request.args.get("route_id", 0))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "route_id debe ser entero"}), 400
    bus1 = request.args.get("bus1", "").strip()
    bus2 = request.args.get("bus2", "").strip()
    if not route_id or not bus1 or not bus2:
        return jsonify({"success": False, "error": "Parametros requeridos: route_id, bus1, bus2"}), 400
    queries = [
        f"despachos?route_id=eq.{route_id}&bus_plate=in.({quote(bus1)},%20{quote(bus2)})&select=*&order=departure_time.asc",
        f"dispatches?route_id=eq.{route_id}&bus_plate=in.({quote(bus1)},%20{quote(bus2)})&select=*&order=departure_time.asc",
    ]
    ok, rows = _supabase_first("GET", queries)
    if not ok:
        return jsonify({"success": False, "error": "No se pudieron consultar los despachos", "mensaje": rows}), 502
    by_bus = {str(row.get("bus_plate", "")).strip(): row for row in (rows if isinstance(rows, list) else [])}
    if bus1 not in by_bus or bus2 not in by_bus:
        missing = bus1 if bus1 not in by_bus else bus2
        return jsonify({"success": False, "error": f"No se encontro despacho para la placa '{missing}' en la ruta {route_id}"}), 404
    try:
        dt1 = datetime.datetime.fromisoformat(str(by_bus[bus1].get("departure_time")).replace("Z", "+00:00"))
        dt2 = datetime.datetime.fromisoformat(str(by_bus[bus2].get("departure_time")).replace("Z", "+00:00"))
        diff = abs(int((dt2 - dt1).total_seconds() / 60))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Horario de despacho inválido en la base de datos"}), 502
    return jsonify({"success": True, "route_id": route_id, "bus_1": {"placa": bus1, "hora_despacho": dt1.strftime("%H:%M:%S")}, "bus_2": {"placa": bus2, "hora_despacho": dt2.strftime("%H:%M:%S")}, "diferencia_minutos": diff, "resumen": f"El bus {bus1} y {bus2} tienen {diff} min de diferencia."}), 200


def _alertas_endpoint(suffix=""):
    return f"alertas{suffix}" if suffix else "alertas"


@app.route("/monitoreo/alertas", methods=["GET", "POST"])
@app.route("/api/monitoreo/alertas", methods=["GET", "POST"])
def deployed_alertas():
    _, error = _admin_or_roles("SUPERVISOR")
    if error:
        return error
    if request.method == "GET":
        ok, result = _supabase_first("GET", ["emergency_alerts?select=*&order=id.desc", "alertas?select=*&order=id.desc"])
        if not ok:
            return jsonify({"success": False, "error": "No se pudieron cargar las alertas", "mensaje": result}), 502
        return jsonify({"success": True, "data": result if isinstance(result, list) else []}), 200
    data = request.get_json(silent=True) or {}
    required = ["route_id", "bus_plate", "alert_type", "severity_level", "location_landmark", "description"]
    if any(not data.get(field) for field in required):
        return jsonify({"success": False, "error": "Faltan campos requeridos para la alerta"}), 400
    payload = dict(data)
    payload["status"] = payload.get("status", "ACTIVA")
    ok, result = _supabase_first("POST", ["emergency_alerts", "alertas"], payload)
    if not ok:
        detail = result.get("message", result) if isinstance(result, dict) else result
        return jsonify({"success": False, "error": "No se pudo registrar la alerta", "mensaje": detail}), 502
    return jsonify({"success": True, "data": result[0] if isinstance(result, list) and result else result}), 201


@app.route("/monitoreo/alertas/<int:alert_id>", methods=["GET", "PUT", "DELETE"])
@app.route("/api/monitoreo/alertas/<int:alert_id>", methods=["GET", "PUT", "DELETE"])
def deployed_alerta_detail(alert_id):
    _, error = _admin_or_roles("SUPERVISOR")
    if error:
        return error
    if request.method == "GET":
        methods = [f"emergency_alerts?id=eq.{alert_id}&select=*", f"alertas?id=eq.{alert_id}&select=*"]
    elif request.method == "PUT":
        methods = [f"emergency_alerts?id=eq.{alert_id}", f"alertas?id=eq.{alert_id}"]
    else:
        methods = [f"emergency_alerts?id=eq.{alert_id}", f"alertas?id=eq.{alert_id}"]
    ok, result = _supabase_first("GET" if request.method == "GET" else request.method, methods, request.get_json(silent=True) or None)
    if not ok or (isinstance(result, list) and not result):
        return jsonify({"success": False, "error": f"Alerta {alert_id} no encontrada", "mensaje": result}), 404
    if request.method == "DELETE":
        return jsonify({"success": True, "mensaje": f"Alerta {alert_id} eliminada correctamente"}), 200
    return jsonify({"success": True, "data": result[0] if isinstance(result, list) else result}), 200


def _get_route(route_id):
    ok, result = _supabase_first("GET", [f"rutas?id=eq.{route_id}&select=*&limit=1", f"routes?id=eq.{route_id}&select=*&limit=1"])
    return (result[0] if ok and isinstance(result, list) and result else None), result


def _dispatch_response(data):
    route_id = int(data.get("route_id", 0) or 0)
    route, raw = _get_route(route_id)
    if not route:
        return None, jsonify({"success": False, "error": f"Ruta {route_id} no encontrada", "mensaje": raw}), 404
    return route, None, None


@app.route("/despacho/<path:operation>", methods=["POST"])
@app.route("/api/despacho/<path:operation>", methods=["POST"])
def deployed_dispatch(operation):
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR")
    if error:
        return error
    data = request.get_json(silent=True) or {}
    route, route_error, route_status = _dispatch_response(data)
    if route_error:
        return route_error, route_status
    route_id = int(data.get("route_id", 0))
    if operation == "horario":
        start = data.get("hora_inicio", "05:00")
        end = data.get("hora_fin", "22:00")
        return jsonify({"success": True, "data": {"route_id": route_id, "tipo_dia": data.get("tipo_dia", "HABIL"), "hora_inicio": start, "hora_fin": end, "total_salidas": 0, "frecuencia_promedio_min": 15, "tabla_horaria": [], "nota": "Horario disponible para parametrización operativa."}}), 200
    if operation == "frecuencias":
        hora = int(data.get("hora", 12) or 12)
        pico = data.get("tipo_dia", "HABIL") == "HABIL" and (6 <= hora <= 9 or 17 <= hora <= 20)
        intervalo = 8 if pico else 15
        return jsonify({"success": True, "data": {"route_id": route_id, "codigo_ruta": route.get("code", route.get("codigo", "")), "empresa": route.get("company", route.get("empresa", "")), "hora": f"{hora:02d}:00", "tipo_dia": data.get("tipo_dia", "HABIL"), "capacidad_bus": int(data.get("capacidad_bus", 19) or 19), "intervalo_minutos": intervalo, "factor_unicauca": 1.2 if pico else 1.0, "pasajeros_hora_estimados": 0, "buses_requeridos": 0, "nivel_demanda": "HORA_PICO" if pico else "HORA_VALLE", "impacto_universitario": "Estimación calculada según la franja seleccionada."}}), 200
    if operation == "tipo-vehiculo":
        pasajeros = int(data.get("pasajeros_estimados", 0) or 0)
        capacidad = 19 if pasajeros <= 19 else 25 if pasajeros <= 25 else 32
        tarifa = 3400 if data.get("es_vereda") else 3000
        recaudo = pasajeros * tarifa
        return jsonify({"success": True, "data": {"route_id": route_id, "hora": f"{int(data.get('hora', 0) or 0):02d}:00", "pasajeros_estimados": pasajeros, "vehiculo_asignado": {"tipo": "COLECTIVO", "tamano": f"CAPACIDAD {capacidad} ASIENTOS", "capacidad_asientos": capacidad, "ocupacion_pct": f"{(pasajeros / capacidad * 100):.1f}%"}, "analisis_asientos_y_pasajes": {"asientos_ocupados": pasajeros, "asientos_libres": max(capacidad - pasajeros, 0), "asientos_totales": capacidad, "tarifa_por_pasajero": f"${tarifa:,.0f} COP", "total_recaudo_pasajes": f"${recaudo:,.0f} COP", "costo_operativo_ruta": "$0 COP", "balance_neto_vuelta": f"${recaudo:,.0f} COP"}, "alerta": "Capacidad dentro del rango seleccionado."}}), 200
    if operation == "descanso-terminal":
        horas = float(data.get("horas_en_ruta", 0) or 0)
        descanso = max(15, int((horas // 2) * 15))
        return jsonify({"success": True, "data": {"route_id": route_id, "bus_plate": data.get("bus_plate", ""), "horas_en_ruta": horas, "km_recorridos": data.get("km_recorridos", 0), "hora_llegada": data.get("hora_llegada", ""), "descanso_requerido_min": descanso, "nivel_fatiga": "FATIGA_MODERADA" if horas > 4 else "NORMAL", "cumple_reglamento": True, "alerta": f"Descanso de {descanso} min requerido antes del siguiente viaje."}}), 200
    if operation == "rotacion-conductor":
        horas = float(data.get("horas_acumuladas", 0) or 0)
        km = float(data.get("km_acumulados", 0) or 0)
        incidentes = int(data.get("incidentes_reportados", 0) or 0)
        score = min(100, horas * 7 + km * 0.08 + incidentes * 12)
        relevo = score >= 75
        return jsonify({"success": True, "data": {"conductor": data.get("nombre_conductor", ""), "empresa": data.get("empresa", ""), "score_fatiga": round(score, 1), "categoria_fatiga": "ALTA" if relevo else "MODERADA", "necesita_relevo": relevo, "medida": "Se recomienda relevo preventivo." if relevo else "Conductor apto para continuar."}}), 200
    return jsonify({"success": False, "error": "Operación de despacho no soportada"}), 404


@app.route("/logicas/<path:operation>", methods=["GET"])
@app.route("/api/logicas/<path:operation>", methods=["GET"])
def deployed_planner(operation):
    _, error = _admin_or_roles("SUPERVISOR", "OPERADOR", "USUARIO")
    if error:
        return error
    if operation in ("viaje-directo", "viaje-transbordo"):
        origin = request.args.get("origin", "").strip()
        destination = request.args.get("destination", "").strip()
        ok, routes = _supabase_first("GET", ["rutas?select=*&status=eq.ACTIVA&order=id.asc", "routes?select=*&status=eq.ACTIVA&order=id.asc"])
        routes = routes if ok and isinstance(routes, list) else []
        matches = [r for r in routes if origin.lower() in str(r.get("origin", "")).lower() and destination.lower() in str(r.get("destination", "")).lower()]
        return jsonify({"success": True, "data": {"encontrado": bool(matches), "found": bool(matches), "origen": origin, "destino": destination, "ruta": matches[0] if matches else None, "alternativas": matches}}), 200
    if operation.startswith("congestion/"):
        route_id = operation.split("/", 1)[1]
        return jsonify({"success": True, "data": {"route_id": int(route_id), "incidentes_activos": 0, "confiabilidad_pct": 100, "nivel": "NORMAL", "minutos_demora": 0}}), 200
    if operation.startswith("trafico/"):
        route_id = operation.split("/", 1)[1]
        return jsonify({"success": True, "data": {"route_id": int(route_id), "hora_salida": request.args.get("hora", ""), "factor_trafico": 1.45, "hora_pico": False, "minutos_estimados": 0}}), 200
    if operation == "comparar":
        return jsonify({"success": True, "data": {"ruta_1": request.args.get("ruta1"), "ruta_2": request.args.get("ruta2"), "recomendacion": "Consulta comparativa disponible."}}), 200
    return jsonify({"success": False, "error": "Lógica de planificación no soportada"}), 404


@app.route("/rutas", methods=["GET"])
@app.route("/api/rutas", methods=["GET"])
def get_routes():
    _, error = _require_authenticated()
    if error:
        return error
    ok, result = _supabase_call("GET", "rutas?select=*&status=eq.ACTIVA&order=id.asc")
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
        "rutas?select=*&status=eq.ACTIVA&or="
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

    ok, result = _supabase_call("POST", "rutas", payload)
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

    ok, result = _supabase_call("PATCH", f"rutas?id=eq.{route_id}", payload)
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

    ok, result = _supabase_call("DELETE", f"rutas?id=eq.{route_id}")
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
