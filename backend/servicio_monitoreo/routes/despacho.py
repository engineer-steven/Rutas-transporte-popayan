# ==============================================================================
# ARCHIVO: backend/servicio_monitoreo/routes/despacho.py
# RESPONSABILIDAD: Controlador REST para las 5 Lógicas No Lineales de Despacho Operativo.
# PREFIJO URL: /despacho
# ==============================================================================

# Importa utilidades de Flask para enrutamiento, lectura de peticiones y respuestas JSON.
from flask import Blueprint, request, jsonify

# Importa el decorador para requerir JWT y validar el rol.
from auth import role_required

# Importa la capa de servicio que contiene las reglas de negocio y modelos matemáticos.
from service import DespachoService

# Declara el Blueprint bajo el prefijo /despacho.
despacho_bp = Blueprint("despacho_bp", __name__, url_prefix="/despacho")


# ==============================================================================
# FUNCIONALIDAD 1: TABLA HORARIA DINÁMICA POR TIPO DE DÍA
# Endpoint: POST /despacho/horario
# ==============================================================================
@despacho_bp.route("/horario", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def generar_tabla_horaria(current_user=None):
    """
    Genera la tabla programada de despachos de cabecera según el tipo de día:
    HABIL (picos 8 min), SABADO (comercial 10 min), DOMINGO (15-30 min), FESTIVO (inicia 08:00).
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
        # Invoca a la lógica de negocio en DespachoService
        resultado = DespachoService.generar_tabla_horaria(route_id, tipo_dia, hora_inicio, hora_fin)
        return jsonify({"success": True, "data": resultado}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as ex:
        return jsonify({"success": False, "error": f"Error interno: {str(ex)}"}), 500


# ==============================================================================
# FUNCIONALIDAD 2: FRECUENCIAS MÍNIMAS Y FLOTA POR DEMANDA Y FACTOR UNICAUCA
# Endpoint: POST /despacho/frecuencias
# ==============================================================================
@despacho_bp.route("/frecuencias", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def calcular_frecuencias(current_user=None):
    """
    Calcula los colectivos por hora requeridos según la demanda horaria,
    el tipo de corredor vial y la afluencia de estudiantes universitarios (Factor Unicauca +20%).
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
# FUNCIONALIDAD 3: ASIGNACIÓN DE TIPO DE VEHÍCULO Y BALANCE DE RECAUDO
# Endpoint: POST /despacho/tipo-vehiculo
# ==============================================================================
@despacho_bp.route("/tipo-vehiculo", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def asignar_tipo_vehiculo(current_user=None):
    """
    Determina el tamaño del colectivo homologado en Popayán (19, 25 o 32 pasajeros)
    y liquida la tarifa oficial ($3.000 COP base o recargo por vereda lejana $3.400).
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
# FUNCIONALIDAD 4: CONTROL DE TIEMPOS DE DESCANSO EN TERMINAL DE CABECERA
# Endpoint: POST /despacho/descanso-terminal
# ==============================================================================
@despacho_bp.route("/descanso-terminal", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def calcular_descanso_terminal(current_user=None):
    """Calcula el descanso obligatorio en cabecera para prevenir accidentes por fatiga de conductores."""
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
# FUNCIONALIDAD 5: OPTIMIZADOR DE ROTACIÓN Y SCORE DE FATIGA DE CONDUCTORES
# Endpoint: POST /despacho/rotacion-conductor
# ==============================================================================
@despacho_bp.route("/rotacion-conductor", methods=["POST"])
@role_required("ADMIN", "SUPERVISOR", "OPERADOR")
def optimizar_rotacion_conductor(current_user=None):
    """
    Calcula un score de fatiga no lineal considerando horas acumuladas,
    kilometraje y cantidad de incidentes reportados, determinando si el conductor debe ser relevado.
    """
    data = request.get_json(silent=True) or {}
    try:
        conductor_id = data.get("conductor_id")
        nombre_conductor = str(data.get("nombre_conductor", "")).strip()
        empresa = str(data.get("empresa", "")).strip()

        # Si se suministró un ID de conductor, busca sus datos en la base de datos
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

        # Valores por defecto para pruebas
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
