# ==============================================================================
# ARCHIVO: backend/servicio_rutas/routes/logicas.py
# RESPONSABILIDAD: Los 5 Algoritmos y Modelos de Lógica No Lineal del Microservicio 1.
# PREFIJO URL: /logicas
# ==============================================================================

# Importa utilidades para manipulación de horas, minutos y diferencias temporales.
from datetime import datetime, timedelta

# Importa componentes de Flask para peticiones y respuestas.
from flask import Blueprint, request, jsonify

# Importa la capa de acceso a datos de rutas e incidentes.
import repository

# Importa el middleware de validación de seguridad por token o API Key.
from auth import token_required

# Declara el Blueprint de lógicas complejas bajo el prefijo /logicas.
logicas_bp = Blueprint("logicas_bp", __name__, url_prefix="/logicas")


# ==============================================================================
# LÓGICA NO PLANA 1: PLANIFICADOR DE VIAJE DIRECTO (GET /logicas/viaje-directo)
# Algoritmo: Valida secuencia direccional (Order_orig < Order_dest) y densidad de paradas.
# ==============================================================================
@logicas_bp.route("/viaje-directo", methods=["GET"])
@token_required
def plan_trip(current_user=None):
    """Calcula la mejor ruta directa entre dos paraderos respetando el sentido del recorrido."""
    # Obtiene los términos de búsqueda desde los query parameters.
    orig = request.args.get("origin", "").strip()
    dest = request.args.get("destination", "").strip()

    # Valida que ambos parámetros hayan sido suministrados.
    if not orig or not dest:
        return jsonify({"success": False, "error": "Parametros requeridos: origin, destination"}), 400

    # Busca en el grafo relacional una ruta donde el paradero de origen preceda al de destino.
    mejor = repository.find_direct_trip(orig, dest)
    # Si no hay ruta directa, sugiere utilizar el servicio de transbordo.
    if not mejor:
        return jsonify({
            "success": False,
            "encontrado": False,
            "origin": orig,
            "destination": dest,
            "mensaje": f"No hay ruta directa entre '{orig}' y '{dest}'. Use /logicas/viaje-transbordo"
        }), 200

    # Calcula la cantidad de paraderos intermedios.
    paradas = int(mejor.get("stops_between") or 1)
    # Aplica cálculo no lineal de tiempo (~4 min por parada en Popayán con un piso mínimo de 10 min).
    minutos = max(10, paradas * 4)
    # Extrae la tarifa oficial registrada para dicha ruta.
    tarifa = float(mejor.get("fare") or 3000.0)

    # Retorna el itinerario detallado con HTTP 200 OK.
    return jsonify({
        "success": True,
        "encontrado": True,
        "origin": orig,
        "destination": dest,
        "ruta_recomendada": {
            "codigo":           str(mejor.get("route_code") or ""),
            "empresa":          str(mejor.get("company") or ""),
            "paradero_subida":  str(mejor.get("origin_stop_name") or orig),
            "paradero_bajada":  str(mejor.get("destination_stop_name") or dest),
            "paradas":          paradas,
            "tarifa_cop":       tarifa,
            "minutos_estimados": minutos
        },
        "resumen": (
            f"Tome la ruta {mejor.get('route_code')} en '{mejor.get('origin_stop_name', orig)}' "
            f"y baje en '{mejor.get('destination_stop_name', dest)}'. "
            f"~{paradas} paradas / {minutos} min / ${tarifa:,.0f} COP"
        )
    }), 200


# ==============================================================================
# LÓGICA NO PLANA 2: PLANIFICACIÓN MULTIMODAL CON TRANSBORDO (GET /logicas/viaje-transbordo)
# Algoritmo: Intersección relacional para hallar el nodo común de intercambio de pasajeros.
# ==============================================================================
@logicas_bp.route("/viaje-transbordo", methods=["GET"])
@token_required
def suggest_transfer_trip(current_user=None):
    """Encuentra la mejor combinación de 2 rutas diferentes conectadas por un paradero común."""
    orig = request.args.get("origin", "").strip()
    dest = request.args.get("destination", "").strip()

    if not orig or not dest:
        return jsonify({"success": False, "error": "Parametros requeridos: origin, destination"}), 400

    # Ejecuta el cruce de grafos relacionales en MySQL para ubicar el paradero de trasbordo.
    trans = repository.find_transfer_trip(orig, dest)
    if not trans:
        return jsonify({
            "success": False,
            "encontrado": False,
            "origin": orig,
            "destination": dest,
            "mensaje": "No se encontro un transbordo automatico. Dirigirse al Centro o Terminal de Transportes."
        }), 200

    # Total de paradas sumando ambos tramos de viaje.
    paradas_totales = int(trans.get("total_stops") or 4)
    # Tiempo total: paradas * 4 min + 12 minutos fijos estimados de espera en el paradero de conexión.
    tiempo_total = max(20, (paradas_totales * 4) + 12)
    # Liquidación acumulada de ambas tarifas oficiales.
    tarifa_total = float(trans.get("r1_fare") or 3000.0) + float(trans.get("r2_fare") or 3000.0)

    # Retorna las instrucciones completas divididas en Paso 1 y Paso 2.
    return jsonify({
        "success": True,
        "encontrado": True,
        "origin": orig,
        "destination": dest,
        "paso_1": {
            "ruta":              str(trans.get("r1_code") or ""),
            "empresa":           str(trans.get("r1_company") or ""),
            "subida":            str(trans.get("boarding_stop") or orig),
            "bajada_transbordo": str(trans.get("transfer_stop") or "Centro")
        },
        "paso_2": {
            "ruta":              str(trans.get("r2_code") or ""),
            "empresa":           str(trans.get("r2_company") or ""),
            "llegada":           str(trans.get("alighting_stop") or dest)
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
# LÓGICA NO PLANA 3: ÍNDICE DE CONGESTIÓN Y CONFIABILIDAD (GET /logicas/congestion/<id>)
# Algoritmo: Modelo de decaimiento con penalizaciones ponderadas por tipo de novedad vial.
# ==============================================================================
@logicas_bp.route("/congestion/<int:route_id>", methods=["GET"])
@token_required
def calculate_route_congestion_index(route_id, current_user=None):
    """Cruza los incidentes activos de la ruta para calcular su índice de confiabilidad porcentual."""
    # Verifica la existencia de la ruta.
    ruta = repository.find_by_id(route_id)
    if not ruta:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404

    # Consulta las novedades viales reportadas y no resueltas.
    incidentes = repository.get_active_incidents(route_id)
    num_inc = len(incidentes)
    demora = 0
    penalizacion = 0.0

    # Aplica ponderaciones técnicas según la gravedad de cada evento.
    for inc in incidentes:
        tipo = str(inc.get("incident_type") or "").upper()
        if "ACCIDENTE" in tipo:
            demora += 20         # Un accidente añade 20 minutos de espera
            penalizacion += 30.0 # Reduce 30% la confiabilidad de la ruta
        elif "DESVIO" in tipo or "CIERRE" in tipo:
            demora += 15         # Un desvío añade 15 minutos
            penalizacion += 20.0 # Reduce 20% la confiabilidad
        elif "CONGESTION" in tipo or "TRAFICO" in tipo:
            demora += 10         # Congestión pesada añade 10 minutos
            penalizacion += 15.0 # Reduce 15% la confiabilidad
        else:
            demora += 8
            penalizacion += 10.0

    # La confiabilidad inicia en 100% y tiene un piso mínimo no nulo del 10%.
    confiabilidad = round(max(10.0, 100.0 - penalizacion), 1)

    # Clasifica el nivel de congestión.
    if num_inc == 0:   nivel = "NORMAL"
    elif num_inc == 1: nivel = "MODERADO"
    elif num_inc == 2: nivel = "ALTO"
    else:              nivel = "CRITICO"

    return jsonify({
        "success": True,
        "route_id":            ruta["id"],
        "route_code":          ruta["code"],
        "company":             ruta["company"],
        "incidentes_activos":  num_inc,
        "nivel_congestion":    nivel,
        "demora_minutos":      demora,
        "confiabilidad":       f"{confiabilidad}%",
        "diagnostico": (
            f"Ruta {ruta['code']} operando con normalidad." if num_inc == 0
            else f"{num_inc} incidente(s) activo(s). Retraso estimado ~{demora} min."
        )
    }), 200


# ==============================================================================
# LÓGICA NO PLANA 4: SIMULADOR DE TRÁFICO POR FRANJA HORARIA (GET /logicas/trafico/<id>)
# Algoritmo: Aplica factor de fricción de 1.45x (+45% de tiempo) en horas pico de Popayán.
# ==============================================================================
@logicas_bp.route("/trafico/<int:route_id>", methods=["GET"])
@token_required
def simulate_traffic_schedule(route_id, current_user=None):
    """Predice el tiempo de llegada evaluando si la salida coincide con horas pico locales."""
    hora_str = request.args.get("hora", "08:00").strip()
    ruta = repository.find_by_id(route_id)
    if not ruta:
        return jsonify({"success": False, "error": f"Ruta {route_id} no encontrada"}), 404

    # Parsea la hora de salida de forma segura.
    try:
        hora_dt = datetime.strptime(hora_str, "%H:%M")
    except ValueError:
        hora_dt = datetime.strptime("08:00", "%H:%M")
        hora_str = "08:00"

    # Convierte la hora a valor decimal para comparar rangos continuos (ej. 06:30 -> 6.5).
    hora_num = hora_dt.hour + (hora_dt.minute / 60.0)

    # Franjas pico de Popayán: 06:30-08:30 (mañana), 11:45-13:45 (mediodía), 17:30-19:30 (tarde).
    es_pico = (6.5 <= hora_num <= 8.5) or (11.75 <= hora_num <= 13.75) or (17.5 <= hora_num <= 19.5)
    # Aplica factor multiplicador del 1.45x en hora pico o 1.0x en tráfico fluido.
    factor = 1.45 if es_pico else 1.0

    # Calcula el tiempo base por cantidad de paraderos.
    paraderos = repository.get_route_stops_count(route_id)
    base_min = max(15, paraderos * 3 if paraderos > 0 else 25)
    # Calcula el tiempo real proyectado.
    real_min = int(round(base_min * factor))
    # Calcula la hora estimada de llegada sumando los minutos al horario de partida.
    llegada_str = (hora_dt + timedelta(minutes=real_min)).strftime("%H:%M")

    return jsonify({
        "success": True,
        "route_id":               ruta["id"],
        "route_code":             ruta["code"],
        "hora_salida":            hora_str,
        "es_hora_pico":           es_pico,
        "factor_trafico":         factor,
        "minutos_base":           base_min,
        "minutos_reales":         real_min,
        "hora_llegada_estimada":  llegada_str,
        "consejo": (
            f"Hora pico en Popayan (+45% trafico). Salida {hora_str} -> Llegada ~{llegada_str} ({real_min} min). "
            "Salga 15 min antes." if es_pico
            else f"Trafico fluido. Salida {hora_str} -> Llegada ~{llegada_str} ({real_min} min)."
        )
    }), 200


# ==============================================================================
# LÓGICA NO PLANA 5: COMPARADOR DE EFICIENCIA ENTRE DOS RUTAS (GET /logicas/comparar)
# Algoritmo: Evaluación multicriterio de densidad de paradas, costo y tiempo de ciclo.
# ==============================================================================
@logicas_bp.route("/comparar", methods=["GET"])
@token_required
def compare_routes_efficiency(current_user=None):
    """Compara 2 rutas y emite un dictamen técnico recomendando cuál es superior según rapidez o costo."""
    try:
        id1 = int(request.args.get("ruta1", 0))
        id2 = int(request.args.get("ruta2", 0))
    except ValueError:
        return jsonify({"success": False, "error": "Parametros 'ruta1' y 'ruta2' deben ser enteros"}), 400

    r1 = repository.find_by_id(id1)
    r2 = repository.find_by_id(id2)

    if not r1 or not r2:
        return jsonify({"success": False, "error": "Una o ambas rutas no existen"}), 404

    # Obtiene la densidad de paraderos de cada alternativa.
    stops_1 = max(1, repository.get_route_stops_count(r1["id"]) or 6)
    stops_2 = max(1, repository.get_route_stops_count(r2["id"]) or 6)
    # Estima el tiempo promedio de recorrido de cada ruta.
    time_1 = stops_1 * 4
    time_2 = stops_2 * 4

    # Evalúa cuál es mejor en velocidad (menor tiempo).
    mejor_vel = (r1["code"] if time_1 < time_2 else r2["code"]) if time_1 != time_2 else "Empate"
    # Evalúa cuál es mejor en economía (menor tarifa).
    mejor_eco = (r1["code"] if r1["fare"] < r2["fare"] else r2["code"]) if r1["fare"] != r2["fare"] else "Misma tarifa"

    return jsonify({
        "success": True,
        f"ruta_{r1['code']}": {
            "id": r1["id"], "empresa": r1["company"],
            "paradas": stops_1, "tiempo_min": time_1, "tarifa_cop": r1["fare"]
        },
        f"ruta_{r2['code']}": {
            "id": r2["id"], "empresa": r2["company"],
            "paradas": stops_2, "tiempo_min": time_2, "tarifa_cop": r2["fare"]
        },
        "mejor_por_velocidad": mejor_vel,
        "mejor_por_economia":  mejor_eco,
        "veredicto": (
            f"Comparativa {r1['code']} vs {r2['code']}: "
            f"{r1['code']} = {stops_1} paradas/{time_1} min/${r1['fare']:,.0f}. "
            f"{r2['code']} = {stops_2} paradas/{time_2} min/${r2['fare']:,.0f}. "
            f"Rapidez: {mejor_vel}. Economia: {mejor_eco}."
        )
    }), 200
