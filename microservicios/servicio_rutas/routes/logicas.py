from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
import repository
from auth import token_required

logicas_bp = Blueprint("logicas_bp", __name__, url_prefix="/logicas")


# ==============================================================================
# LOGICA NO PLANA 1: Planificador de Viaje Directo
# ==============================================================================
@logicas_bp.route("/viaje-directo", methods=["GET"])
@token_required
def plan_trip(current_user=None):
    """
    Busca la ruta mas directa entre dos sectores.
    Params: ?origin=<keyword>&destination=<keyword>
    """
    orig = request.args.get("origin", "").strip()
    dest = request.args.get("destination", "").strip()

    if not orig or not dest:
        return jsonify({"success": False, "error": "Parametros requeridos: origin, destination"}), 400

    mejor = repository.find_direct_trip(orig, dest)
    if not mejor:
        return jsonify({
            "success": False,
            "encontrado": False,
            "origin": orig,
            "destination": dest,
            "mensaje": f"No hay ruta directa entre '{orig}' y '{dest}'. Use /logicas/viaje-transbordo"
        }), 200

    paradas = int(mejor.get("stops_between") or 1)
    minutos = max(10, paradas * 4)
    tarifa  = float(mejor.get("fare") or 3000.0)

    return jsonify({
        "success": True,
        "encontrado": True,
        "origin": orig,
        "destination": dest,
        "ruta_recomendada": {
            "codigo":      str(mejor.get("route_code") or ""),
            "empresa":     str(mejor.get("company") or ""),
            "paradero_subida":  str(mejor.get("origin_stop_name") or orig),
            "paradero_bajada":  str(mejor.get("destination_stop_name") or dest),
            "paradas":     paradas,
            "tarifa_cop":  tarifa,
            "minutos_estimados": minutos
        },
        "resumen": (
            f"Tome la ruta {mejor.get('route_code')} en '{mejor.get('origin_stop_name', orig)}' "
            f"y baje en '{mejor.get('destination_stop_name', dest)}'. "
            f"~{paradas} paradas / {minutos} min / ${tarifa:,.0f} COP"
        )
    }), 200


# ==============================================================================
# LOGICA NO PLANA 2: Viaje con Transbordo
# ==============================================================================
@logicas_bp.route("/viaje-transbordo", methods=["GET"])
@token_required
def suggest_transfer_trip(current_user=None):
    """
    Busca combinacion de 2 rutas con transbordo en paradero comun.
    Params: ?origin=<keyword>&destination=<keyword>
    """
    orig = request.args.get("origin", "").strip()
    dest = request.args.get("destination", "").strip()

    if not orig or not dest:
        return jsonify({"success": False, "error": "Parametros requeridos: origin, destination"}), 400

    trans = repository.find_transfer_trip(orig, dest)
    if not trans:
        return jsonify({
            "success": False,
            "encontrado": False,
            "origin": orig,
            "destination": dest,
            "mensaje": "No se encontro un transbordo automatico. Dirigirse al Centro o Terminal de Transportes."
        }), 200

    paradas_totales = int(trans.get("total_stops") or 4)
    tiempo_total    = max(20, (paradas_totales * 4) + 12)
    tarifa_total    = float(trans.get("r1_fare") or 3000.0) + float(trans.get("r2_fare") or 3000.0)

    return jsonify({
        "success": True,
        "encontrado": True,
        "origin": orig,
        "destination": dest,
        "paso_1": {
            "ruta":     str(trans.get("r1_code") or ""),
            "empresa":  str(trans.get("r1_company") or ""),
            "subida":   str(trans.get("boarding_stop") or orig),
            "bajada_transbordo": str(trans.get("transfer_stop") or "Centro")
        },
        "paso_2": {
            "ruta":    str(trans.get("r2_code") or ""),
            "empresa": str(trans.get("r2_company") or ""),
            "llegada": str(trans.get("alighting_stop") or dest)
        },
        "tarifa_total_cop":    tarifa_total,
        "minutos_estimados":   tiempo_total,
        "resumen": (
            f"Paso 1: Tome ruta {trans.get('r1_code')} en '{trans.get('boarding_stop', orig)}' "
            f"hasta '{trans.get('transfer_stop', 'Centro')}'. "
            f"Paso 2: Cambie a ruta {trans.get('r2_code')} hasta '{trans.get('alighting_stop', dest)}'. "
            f"Total: ~{tiempo_total} min / ${tarifa_total:,.0f} COP"
        )
    }), 200


# ==============================================================================
# LOGICA NO PLANA 3: Indice de Congestion
# ==============================================================================
@logicas_bp.route("/congestion/<int:route_id>", methods=["GET"])
@token_required
def calculate_route_congestion_index(route_id, current_user=None):
    """Calcula el indice de congestion y confiabilidad de una ruta."""
    ruta = repository.find_by_id(route_id)
    if not ruta:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404

    incidentes = repository.get_active_incidents(route_id)
    num_inc = len(incidentes)
    demora = 0
    penalizacion = 0.0

    for inc in incidentes:
        tipo = str(inc.get("incident_type") or "").upper()
        if "ACCIDENTE" in tipo:
            demora += 20; penalizacion += 30.0
        elif "DESVIO" in tipo or "CIERRE" in tipo:
            demora += 15; penalizacion += 20.0
        elif "CONGESTION" in tipo or "TRAFICO" in tipo:
            demora += 10; penalizacion += 15.0
        else:
            demora += 8;  penalizacion += 10.0

    confiabilidad = round(max(10.0, 100.0 - penalizacion), 1)

    if num_inc == 0:   nivel = "NORMAL"
    elif num_inc == 1: nivel = "MODERADO"
    elif num_inc == 2: nivel = "ALTO"
    else:              nivel = "CRITICO"

    return jsonify({
        "success": True,
        "route_id":            ruta.id,
        "route_code":          ruta.code,
        "company":             ruta.company,
        "incidentes_activos":  num_inc,
        "nivel_congestion":    nivel,
        "demora_minutos":      demora,
        "confiabilidad":       f"{confiabilidad}%",
        "diagnostico": (
            f"Ruta {ruta.code} operando con normalidad." if num_inc == 0
            else f"{num_inc} incidente(s) activo(s). Retraso estimado ~{demora} min."
        )
    }), 200


# ==============================================================================
# LOGICA NO PLANA 4: Simulador de Trafico por Franja Horaria
# ==============================================================================
@logicas_bp.route("/trafico/<int:route_id>", methods=["GET"])
@token_required
def simulate_traffic_schedule(route_id, current_user=None):
    """
    Simula tiempos de viaje segun hora pico o valle.
    Param: ?hora=HH:MM  (default: 08:00)
    """
    hora_str = request.args.get("hora", "08:00").strip()
    ruta = repository.find_by_id(route_id)
    if not ruta:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404

    try:
        hora_dt = datetime.strptime(hora_str, "%H:%M")
    except ValueError:
        hora_dt = datetime.strptime("08:00", "%H:%M")
        hora_str = "08:00"

    hora_num = hora_dt.hour + (hora_dt.minute / 60.0)
    es_pico  = (6.5 <= hora_num <= 8.5) or (11.75 <= hora_num <= 13.75) or (17.5 <= hora_num <= 19.5)
    factor   = 1.45 if es_pico else 1.0

    paraderos    = repository.get_route_stops_count(route_id)
    base_min     = max(15, paraderos * 3 if paraderos > 0 else 25)
    real_min     = int(round(base_min * factor))
    llegada_str  = (hora_dt + timedelta(minutes=real_min)).strftime("%H:%M")

    return jsonify({
        "success": True,
        "route_id":           ruta.id,
        "route_code":         ruta.code,
        "hora_salida":        hora_str,
        "es_hora_pico":       es_pico,
        "factor_trafico":     factor,
        "minutos_base":       base_min,
        "minutos_reales":     real_min,
        "hora_llegada_estimada": llegada_str,
        "consejo": (
            f"Hora pico en Popayan (+45% trafico). Salida {hora_str} -> Llegada ~{llegada_str} ({real_min} min). "
            "Salga 15 min antes." if es_pico
            else f"Trafico fluido. Salida {hora_str} -> Llegada ~{llegada_str} ({real_min} min)."
        )
    }), 200


# ==============================================================================
# LOGICA NO PLANA 5: Comparador de Eficiencia entre Dos Rutas
# ==============================================================================
@logicas_bp.route("/comparar", methods=["GET"])
@token_required
def compare_routes_efficiency(current_user=None):
    """
    Compara dos rutas en velocidad, tarifa y paradas.
    Params: ?ruta1=<id>&ruta2=<id>
    """
    try:
        id1 = int(request.args.get("ruta1", 0))
        id2 = int(request.args.get("ruta2", 0))
    except ValueError:
        return jsonify({"success": False, "error": "Parametros 'ruta1' y 'ruta2' deben ser enteros"}), 400

    r1 = repository.find_by_id(id1)
    r2 = repository.find_by_id(id2)

    if not r1 or not r2:
        return jsonify({"success": False, "error": "Una o ambas rutas no existen"}), 404

    stops_1 = max(1, repository.get_route_stops_count(r1.id) or 6)
    stops_2 = max(1, repository.get_route_stops_count(r2.id) or 6)
    time_1  = stops_1 * 4
    time_2  = stops_2 * 4

    mejor_vel = (r1.code if time_1 < time_2 else r2.code) if time_1 != time_2 else "Empate"
    mejor_eco = (r1.code if r1.fare < r2.fare else r2.code) if r1.fare != r2.fare else "Misma tarifa"

    return jsonify({
        "success": True,
        f"ruta_{r1.code}": {
            "id": r1.id, "empresa": r1.company,
            "paradas": stops_1, "tiempo_min": time_1, "tarifa_cop": r1.fare
        },
        f"ruta_{r2.code}": {
            "id": r2.id, "empresa": r2.company,
            "paradas": stops_2, "tiempo_min": time_2, "tarifa_cop": r2.fare
        },
        "mejor_por_velocidad": mejor_vel,
        "mejor_por_economia":  mejor_eco,
        "veredicto": (
            f"Comparativa {r1.code} vs {r2.code}: "
            f"{r1.code} = {stops_1} paradas/{time_1} min/${r1.fare:,.0f}. "
            f"{r2.code} = {stops_2} paradas/{time_2} min/${r2.fare:,.0f}. "
            f"Rapidez: {mejor_vel}. Economia: {mejor_eco}."
        )
    }), 200
