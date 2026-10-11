from flask import Blueprint, request, jsonify
from auth import token_required
from service import DespachoService

# Solo el blueprint de funcionalidades de despacho
# El login/register/me estan en login.py
despacho_bp = Blueprint("despacho_bp", __name__, url_prefix="/despacho")





# ==============================================================================
# FUNCIONALIDAD 1: Tabla horaria por tipo de dia
# ==============================================================================

@despacho_bp.route("/horario", methods=["POST"])
@token_required
def generar_tabla_horaria(current_user=None):
    """
    Genera la tabla de salidas de cabecera para una ruta segun tipo de dia.
    JSON: {
      "route_id": 1,
      "tipo_dia": "HABIL",        (HABIL | SABADO | DOMINGO | FESTIVO)
      "hora_inicio": "05:00",
      "hora_fin": "22:00"
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        route_id    = int(data.get("route_id", 0))
        tipo_dia    = str(data.get("tipo_dia", "HABIL"))
        hora_inicio = str(data.get("hora_inicio", "05:00"))
        hora_fin    = str(data.get("hora_fin",    "22:00"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parametros invalidos"}), 400

    if not route_id:
        return jsonify({"success": False, "error": "route_id es requerido"}), 400

    try:
        resultado = DespachoService.generar_tabla_horaria(route_id, tipo_dia, hora_inicio, hora_fin)
        return jsonify({"success": True, "data": resultado}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": f"Error interno: {str(ex)}"}), 500


# ==============================================================================
# FUNCIONALIDAD 2: Frecuencias minimas por demanda horaria
# ==============================================================================

@despacho_bp.route("/frecuencias", methods=["POST"])
@token_required
def calcular_frecuencias(current_user=None):
    """
    Calcula los buses minimos requeridos por hora segun demanda.
    JSON: {
      "route_id": 1,
      "hora": 7,
      "tipo_dia": "HABIL",
      "capacidad_bus": 45
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        route_id      = int(data.get("route_id", 0))
        hora          = int(data.get("hora", 7))
        tipo_dia      = str(data.get("tipo_dia", "HABIL"))
        capacidad_bus = int(data.get("capacidad_bus", 45))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parametros invalidos"}), 400

    try:
        resultado = DespachoService.calcular_frecuencias_minimas(route_id, hora, tipo_dia, capacidad_bus)
        return jsonify({"success": True, "data": resultado}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": f"Error interno: {str(ex)}"}), 500


# ==============================================================================
# FUNCIONALIDAD 3: Asignacion de tipo de vehiculo por demanda
# ==============================================================================

@despacho_bp.route("/tipo-vehiculo", methods=["POST"])
@token_required
def asignar_tipo_vehiculo(current_user=None):
    """
    Determina el tamano de colectivo/buseta y calcula la tarifa para Popayan.
    En Popayan solo hay un tipo de bus (colectivo), variando solo el tamano:
      - Pequeño (19 pax), Mediano (25 pax), Grande (32 pax)
    Tarifa: Base urbana $3.000 COP (+ $200 o + $400 si es vereda).
    JSON: {
      "route_id": 1,
      "hora": 8,
      "pasajeros_estimados": 24,
      "longitud_ruta_km": 15.0,
      "es_vereda": false,        (opcional, se deduce de la ruta si no se envia)
      "recargo_vereda": 200      (opcional: 200 o 400 COP)
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        route_id             = int(data.get("route_id", 0))
        hora                 = int(data.get("hora", 8))
        pasajeros_estimados  = int(data.get("pasajeros_estimados", 0))
        longitud_ruta_km     = float(data.get("longitud_ruta_km", 15.0))
        es_vereda            = data.get("es_vereda", None)
        recargo_vereda       = data.get("recargo_vereda", None)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parametros invalidos"}), 400

    try:
        resultado = DespachoService.asignar_tipo_vehiculo(
            route_id=route_id,
            hora=hora,
            pasajeros_estimados=pasajeros_estimados,
            longitud_ruta_km=longitud_ruta_km,
            es_vereda=es_vereda,
            recargo_vereda=recargo_vereda
        )
        return jsonify({"success": True, "data": resultado}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": f"Error interno: {str(ex)}"}), 500


# ==============================================================================
# FUNCIONALIDAD 4: Control de tiempos de descanso en terminal
# ==============================================================================

@despacho_bp.route("/descanso-terminal", methods=["POST"])
@token_required
def calcular_descanso_terminal(current_user=None):
    """
    Calcula el descanso reglamentario del conductor antes de retornar.
    JSON: {
      "route_id": 1,
      "bus_plate": "TPK-102",
      "horas_en_ruta": 3.5,
      "km_recorridos": 85.0,
      "hora_llegada": "14:30"
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        route_id      = int(data.get("route_id", 0))
        bus_plate     = str(data.get("bus_plate", "")).strip()
        horas_en_ruta = float(data.get("horas_en_ruta", 0))
        km_recorridos = float(data.get("km_recorridos", 0))
        hora_llegada  = data.get("hora_llegada", None)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parametros invalidos"}), 400

    if not bus_plate:
        return jsonify({"success": False, "error": "El campo 'bus_plate' es requerido"}), 400

    try:
        resultado = DespachoService.calcular_descanso_terminal(route_id, bus_plate, horas_en_ruta, km_recorridos, hora_llegada)
        return jsonify({"success": True, "data": resultado}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": f"Error interno: {str(ex)}"}), 500


# ==============================================================================
# FUNCIONALIDAD 5: Optimizador de rotacion de conductores
# ==============================================================================

@despacho_bp.route("/rotacion-conductor", methods=["POST"])
@token_required
def optimizar_rotacion_conductor(current_user=None):
    """
    Decide si el conductor debe ser relevado con score de fatiga no lineal.
    Soporta formato por ID de conductor o por nombre directo.
    JSON: {
      "conductor_id": 3,
      "horas_conducidas_hoy": 6.5,
      "vueltas_completadas": 4,
      "incidentes_reportados": 1
    }
    O tambien: {
      "nombre_conductor": "Jairo Ordonez",
      "empresa": "Sotracauca",
      "horas_acumuladas": 7.5,
      "km_acumulados": 190.0,
      "turnos_del_dia": 2
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        conductor_id = data.get("conductor_id")
        nombre_conductor = str(data.get("nombre_conductor", "")).strip()
        empresa = str(data.get("empresa", "")).strip()

        # Si viene conductor_id, buscar datos del conductor en la base de datos
        if conductor_id:
            try:
                import repository
                user = repository.find_user_by_id(int(conductor_id))
                if user:
                    if not nombre_conductor:
                        nombre_conductor = user.get("full_name") or user.get("username")
                    if not empresa:
                        empresa = "Sotracauca" if "sotra" in user.get("username", "").lower() else "Transpubenza"
            except Exception:
                pass

        if not nombre_conductor:
            nombre_conductor = "Jairo Ordóñez (Conductor Colectivo)"
        if not empresa:
            empresa = "Sotracauca"

        horas_acumuladas = float(data.get("horas_acumuladas") or data.get("horas_conducidas_hoy") or 0)
        vueltas = int(data.get("vueltas_completadas") or 0)
        km_acumulados = float(data.get("km_acumulados") or (vueltas * 25.0 if vueltas else 0))
        turnos_del_dia = int(data.get("turnos_del_dia") or max(1, vueltas // 3 if vueltas else 1))
        incidentes_reportados = int(data.get("incidentes_reportados") or 0)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Parametros invalidos"}), 400

    try:
        resultado = DespachoService.optimizar_rotacion_conductor(
            nombre_conductor=nombre_conductor,
            empresa=empresa,
            horas_acumuladas=horas_acumuladas,
            km_acumulados=km_acumulados,
            turnos_del_dia=turnos_del_dia,
            incidentes_reportados=incidentes_reportados,
            vueltas_completadas=vueltas if vueltas else None,
            conductor_id=int(conductor_id) if conductor_id else None
        )
        return jsonify({"success": True, "data": resultado}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": f"Error interno: {str(ex)}"}), 500
