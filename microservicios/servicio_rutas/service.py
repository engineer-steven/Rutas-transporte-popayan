import logging
from datetime import datetime, timedelta
from spyne import (
    Application,
    rpc,
    ServiceBase,
    Integer,
    Unicode,
    Float,
    Boolean,
    Iterable
)
from spyne.protocol.soap import Soap11

import repository
from models import (
    Route,
    TripPlanResult,
    TransferTripResult,
    RouteCongestionResult,
    TrafficSimulationResult,
    RouteComparisonResult,
    NAMESPACE
)

logger = logging.getLogger("RoutesService")
logger.setLevel(logging.INFO)


class RoutesService(ServiceBase):
    """
    Servicio SOAP para la administración, consulta y analítica
    inteligente de rutas de transporte público en Popayán.
    """

    # --------------------------------------------------------------------------
    # OPERACIÓN 1: Listar todas las rutas activas
    # --------------------------------------------------------------------------
    @rpc(_returns=Iterable(Route))
    def get_all_routes(ctx):
        """Retorna el listado completo de rutas activas."""
        logger.info("[get_all_routes] Consultando todas las rutas activas...")
        return repository.find_all_active()

    # --------------------------------------------------------------------------
    # OPERACIÓN 2: Consultar una ruta por su ID
    # --------------------------------------------------------------------------
    @rpc(Integer, _returns=Route)
    def get_route_by_id(ctx, route_id):
        """Consulta el detalle de una ruta específica por su ID."""
        logger.info(f"[get_route_by_id] Consultando ID: {route_id}")
        return repository.find_by_id(route_id)

    # --------------------------------------------------------------------------
    # OPERACIÓN 3: Búsqueda de rutas por zona o sector
    # --------------------------------------------------------------------------
    @rpc(Unicode, _returns=Iterable(Route))
    def search_routes_by_zone(ctx, zone_keyword):
        """Busca rutas que conecten con un sector de Popayán."""
        termino = str(zone_keyword or "").strip()
        logger.info(f"[search_routes_by_zone] Búsqueda por sector: '{termino}'")
        if not termino:
            return []
        return repository.search_by_zone(termino)

    # --------------------------------------------------------------------------
    # OPERACIÓN 4: Registrar una nueva ruta (add_route / create_route)
    # --------------------------------------------------------------------------
    @rpc(Unicode, Unicode, Unicode, Unicode, Float, Unicode, _returns=Boolean)
    def add_route(ctx, code, company, origin, destination, fare, schedule):
        """Inserta una nueva ruta de transporte en MySQL."""
        logger.info(f"[add_route] Registrando ruta {code} ({company})")
        return repository.insert_route(code, company, origin, destination, fare, schedule)

    @rpc(Unicode, Unicode, Unicode, Unicode, Float, Unicode, Unicode, _returns=Route)
    def create_route(ctx, code, company, origin, destination, fare, schedule, status):
        """Crea una nueva ruta y retorna la entidad Route creada."""
        logger.info(f"[create_route] Creando ruta {code} ({company})")
        repository.insert_route(code, company, origin, destination, fare, schedule, status)
        rutas = repository.search_by_zone(code)
        return rutas[0] if rutas else None

    @rpc(Integer, Unicode, Unicode, Unicode, Unicode, Float, Unicode, Unicode, _returns=Route)
    def update_route(ctx, route_id, code, company, origin, destination, fare, schedule, status):
        """Actualiza los datos de una ruta existente."""
        logger.info(f"[update_route] Actualizando ruta ID {route_id}")
        repository.update_route(route_id, code, company, origin, destination, fare, schedule, status)
        return repository.find_by_id(route_id)

    @rpc(Integer, _returns=Unicode)
    def delete_route(ctx, route_id):
        """Elimina una ruta por su ID."""
        logger.info(f"[delete_route] Eliminando ruta ID {route_id}")
        if repository.delete_route(route_id):
            return f"La ruta {route_id} fue eliminada correctamente."
        return f"La ruta {route_id} no existe."

    # --------------------------------------------------------------------------
    # ⭐ LÓGICA NO PLANA 1: Planificador Directo de Viajes
    # --------------------------------------------------------------------------
    @rpc(Unicode, Unicode, _returns=TripPlanResult)
    def plan_trip(ctx, origin_keyword, destination_keyword):
        """
        Algoritmo de planificación de viaje directo:
        1. Valida secuencia direccional de paraderos (s1.stop_order < s2.stop_order).
        2. Calcula número de paradas intermedias.
        3. Estima tiempo de recorrido (~4 min por paradero en Popayán).
        """
        orig = str(origin_keyword or "").strip()
        dest = str(destination_keyword or "").strip()
        logger.info(f"[plan_trip] Calculando viaje directo: '{orig}' -> '{dest}'")

        if not orig or not dest:
            return TripPlanResult(
                found=False,
                origin_searched=orig,
                destination_searched=dest,
                trip_summary="Debes ingresar tanto el punto de origen como el de destino."
            )

        mejor = repository.find_direct_trip(orig, dest)
        if not mejor:
            return TripPlanResult(
                found=False,
                origin_searched=orig,
                destination_searched=dest,
                trip_summary=f"No hay ruta directa entre '{orig}' y '{dest}'. Prueba con 'suggest_transfer_trip'."
            )

        paradas = int(mejor.get("stops_between") or 1)
        minutos = max(10, paradas * 4)
        tarifa = float(mejor.get("fare") or 2800.0)
        codigo = str(mejor.get("route_code") or "RUTA")
        empresa = str(mejor.get("company") or "Transporte Popayán")
        subida = str(mejor.get("origin_stop_name") or orig)
        bajada = str(mejor.get("destination_stop_name") or dest)

        resumen = (
            f"Toma la ruta {codigo} ({empresa}) en '{subida}' y baja en '{bajada}'. "
            f"Trayecto de {paradas} paradas (~{minutos} min). Tarifa oficial: ${tarifa:,.0f} COP."
        )

        return TripPlanResult(
            found=True,
            origin_searched=orig,
            destination_searched=dest,
            recommended_route_code=codigo,
            company=empresa,
            boarding_stop=subida,
            alighting_stop=bajada,
            stops_count=paradas,
            fare=tarifa,
            estimated_minutes=minutos,
            trip_summary=resumen
        )

    # --------------------------------------------------------------------------
    # ⭐ LÓGICA NO PLANA 2: Planificador de Viajes con Transbordo (2 Rutas)
    # --------------------------------------------------------------------------
    @rpc(Unicode, Unicode, _returns=TransferTripResult)
    def suggest_transfer_trip(ctx, origin_keyword, destination_keyword):
        """
        Algoritmo de viaje multimodal con transbordo:
        Cruza dos rutas distintas que coincidan en un paradero común de conexión,
        calculando costo total y tiempo de traslado + espera estimada de transbordo.
        """
        orig = str(origin_keyword or "").strip()
        dest = str(destination_keyword or "").strip()
        logger.info(f"[suggest_transfer_trip] Buscando viaje con transbordo: '{orig}' -> '{dest}'")

        if not orig or not dest:
            return TransferTripResult(
                found=False,
                origin_searched=orig,
                destination_searched=dest,
                trip_summary="Debes ingresar origen y destino para calcular el transbordo."
            )

        trans = repository.find_transfer_trip(orig, dest)
        if not trans:
            return TransferTripResult(
                found=False,
                origin_searched=orig,
                destination_searched=dest,
                trip_summary=(
                    f"No se encontró un transbordo automático entre '{orig}' y '{dest}'. "
                    f"Te sugerimos dirigirte al Centro Histórico o Terminal de Transportes para conectar."
                )
            )

        paradas_totales = int(trans.get("total_stops") or 4)
        # Tiempo de recorrido (~4 min por parada) + 12 min de espera promedio para transbordo
        tiempo_total = max(20, (paradas_totales * 4) + 12)
        tarifa_total = float(trans.get("r1_fare") or 2800.0) + float(trans.get("r2_fare") or 2800.0)

        r1_code = str(trans.get("r1_code") or "Ruta 1")
        r1_comp = str(trans.get("r1_company") or "")
        r2_code = str(trans.get("r2_code") or "Ruta 2")
        r2_comp = str(trans.get("r2_company") or "")
        subida = str(trans.get("boarding_stop") or orig)
        transbordo = str(trans.get("transfer_stop") or "Centro")
        llegada = str(trans.get("alighting_stop") or dest)

        resumen = (
            f"Paso 1: Toma la ruta {r1_code} ({r1_comp}) en '{subida}' hasta '{transbordo}'. "
            f"Paso 2: En '{transbordo}', haz transbordo a la ruta {r2_code} ({r2_comp}) hasta '{llegada}'. "
            f"Tiempo estimado: {tiempo_total} min (incluye ~12 min de transbordo). Tarifa total: ${tarifa_total:,.0f} COP."
        )

        return TransferTripResult(
            found=True,
            origin_searched=orig,
            destination_searched=dest,
            first_route_code=r1_code,
            first_company=r1_comp,
            boarding_stop=subida,
            transfer_stop=transbordo,
            second_route_code=r2_code,
            second_company=r2_comp,
            alighting_stop=llegada,
            total_fare=tarifa_total,
            estimated_minutes=tiempo_total,
            trip_summary=resumen
        )

    # --------------------------------------------------------------------------
    # ⭐ LÓGICA NO PLANA 3: Índice de Afectación y Congestión en Tiempo Real
    # --------------------------------------------------------------------------
    @rpc(Integer, _returns=RouteCongestionResult)
    def calculate_route_congestion_index(ctx, route_id):
        """
        Calcula el impacto de incidentes viales activos en la ruta:
        Aplica penalizaciones por tipo de incidente y estima retrasos y confiabilidad.
        """
        logger.info(f"[calculate_route_congestion_index] Evaluando congestión para ruta ID: {route_id}")
        ruta = repository.find_by_id(route_id)
        if not ruta:
            return RouteCongestionResult(
                route_id=route_id,
                route_code="DESCONOCIDA",
                company="",
                active_incidents_count=0,
                congestion_level="DESCONOCIDO",
                delay_minutes=0,
                reliability_score=0.0,
                status_summary=f"No se encontró ninguna ruta con el ID {route_id}."
            )

        incidentes = repository.get_active_incidents(route_id)
        num_inc = len(incidentes)

        demora = 0
        penalizacion_confiabilidad = 0.0

        for inc in incidentes:
            tipo = str(inc.get("incident_type") or "").upper()
            if "ACCIDENTE" in tipo:
                demora += 20
                penalizacion_confiabilidad += 30.0
            elif "DESVIO" in tipo or "CIERRE" in tipo:
                demora += 15
                penalizacion_confiabilidad += 20.0
            elif "CONGESTION" in tipo or "TRAFICO" in tipo:
                demora += 10
                penalizacion_confiabilidad += 15.0
            else:
                demora += 8
                penalizacion_confiabilidad += 10.0

        confiabilidad = max(10.0, 100.0 - penalizacion_confiabilidad)

        if num_inc == 0:
            nivel = "NORMAL"
            diagnostico = f"Ruta {ruta.code} operando con normalidad. Sin reportes de congestión vial."
        elif num_inc == 1:
            nivel = "MODERADO"
            diagnostico = f"Afectación moderada por 1 incidente reportado. Retraso estimado de ~{demora} min."
        elif num_inc == 2:
            nivel = "ALTO"
            diagnostico = f"Afectación alta por 2 incidentes activos. Retraso estimado de ~{demora} min."
        else:
            nivel = "CRÍTICO"
            diagnostico = f"Estado crítico: {num_inc} novedades viales activas. Retraso severo de ~{demora}+ min."

        return RouteCongestionResult(
            route_id=ruta.id,
            route_code=ruta.code,
            company=ruta.company,
            active_incidents_count=num_inc,
            congestion_level=nivel,
            delay_minutes=demora,
            reliability_score=confiabilidad,
            status_summary=diagnostico
        )

    # --------------------------------------------------------------------------
    # ⭐ LÓGICA NO PLANA 4: Simulador de Recorrido según Franja Horaria
    # --------------------------------------------------------------------------
    @rpc(Integer, Unicode, _returns=TrafficSimulationResult)
    def simulate_traffic_schedule(ctx, route_id, departure_hour):
        """
        Simula el tiempo de viaje considerando si la hora de salida coincide
        con horas pico urbanas de Popayán, aplicando factor de congestión.
        """
        hora_str = str(departure_hour or "").strip()
        logger.info(f"[simulate_traffic_schedule] Ruta {route_id} a las {hora_str}")

        ruta = repository.find_by_id(route_id)
        if not ruta:
            return TrafficSimulationResult(
                route_id=route_id,
                route_code="DESCONOCIDA",
                departure_hour=hora_str,
                is_peak_hour=False,
                traffic_factor=1.0,
                base_minutes=0,
                real_estimated_minutes=0,
                estimated_arrival_time="--:--",
                advice=f"Ruta con ID {route_id} no encontrada."
            )

        # Validación y parsing de hora
        try:
            hora_dt = datetime.strptime(hora_str, "%H:%M")
        except ValueError:
            hora_dt = datetime.strptime("08:00", "%H:%M")
            hora_str = "08:00"

        hora_num = hora_dt.hour + (hora_dt.minute / 60.0)

        # Franjas pico en Popayán: 06:30-08:30 (Mañana), 11:45-13:45 (Mediodía), 17:30-19:30 (Tarde)
        es_pico = (
            (6.5 <= hora_num <= 8.5) or
            (11.75 <= hora_num <= 13.75) or
            (17.5 <= hora_num <= 19.5)
        )

        factor_trafico = 1.45 if es_pico else 1.0
        paraderos = repository.get_route_stops_count(route_id)
        base_minutos = max(15, paradas_min := (paraderos * 3 if paraderos > 0 else 25))
        minutos_reales = int(round(base_minutos * factor_trafico))

        llegada_dt = hora_dt + timedelta(minutes=minutos_reales)
        llegada_str = llegada_dt.strftime("%H:%M")

        if es_pico:
            consejo = (
                f"⚠️ Franja de Hora Pico en Popayán (+45% tráfico). Salida {hora_str} -> "
                f"Llegada estimada a las {llegada_str} ({minutos_reales} min). Te sugerimos salir 15 min antes."
            )
        else:
            consejo = (
                f"✅ Franja de Hora Valle con tráfico fluido. Salida {hora_str} -> "
                f"Llegada estimada a las {llegada_str} ({minutos_reales} min)."
            )

        return TrafficSimulationResult(
            route_id=ruta.id,
            route_code=ruta.code,
            departure_hour=hora_str,
            is_peak_hour=es_pico,
            traffic_factor=factor_trafico,
            base_minutes=base_minutos,
            real_estimated_minutes=minutos_reales,
            estimated_arrival_time=llegada_str,
            advice=consejo
        )

    # --------------------------------------------------------------------------
    # ⭐ LÓGICA NO PLANA 5: Comparador de Eficiencia entre Dos Rutas
    # --------------------------------------------------------------------------
    @rpc(Integer, Integer, _returns=RouteComparisonResult)
    def compare_routes_efficiency(ctx, route_id_1, route_id_2):
        """
        Evalúa y compara dos rutas en términos de densidad de paraderos,
        tarifa oficial y tiempo de ciclo completo, emitiendo un veredicto técnico.
        """
        logger.info(f"[compare_routes_efficiency] Comparando rutas {route_id_1} vs {route_id_2}")

        r1 = repository.find_by_id(route_id_1)
        r2 = repository.find_by_id(route_id_2)

        if not r1 or not r2:
            return RouteComparisonResult(
                route_1_code="N/A",
                route_2_code="N/A",
                route_1_stops=0,
                route_2_stops=0,
                route_1_fare=0.0,
                route_2_fare=0.0,
                route_1_time_min=0,
                route_2_time_min=0,
                best_for_speed="N/A",
                best_for_economy="N/A",
                verdict="Una o ambas rutas no existen en la base de datos."
            )

        stops_1 = max(1, repository.get_route_stops_count(r1.id) or 6)
        stops_2 = max(1, repository.get_route_stops_count(r2.id) or 6)

        time_1 = stops_1 * 4
        time_2 = stops_2 * 4

        # Mejor por velocidad
        if time_1 < time_2:
            mejor_vel = f"{r1.code} ({time_1} min vs {time_2} min)"
        elif time_2 < time_1:
            mejor_vel = f"{r2.code} ({time_2} min vs {time_1} min)"
        else:
            mejor_vel = "Empate en tiempo estimado"

        # Mejor por economía
        if r1.fare < r2.fare:
            mejor_eco = f"{r1.code} (${r1.fare:,.0f} COP)"
        elif r2.fare < r1.fare:
            mejor_eco = f"{r2.code} (${r2.fare:,.0f} COP)"
        else:
            mejor_eco = f"Misma tarifa (${r1.fare:,.0f} COP)"

        veredicto = (
            f"Comparativa entre {r1.code} ({r1.company}) y {r2.code} ({r2.company}): "
            f"{r1.code} cuenta con {stops_1} paradas (~{time_1} min, ${r1.fare:,.0f} COP). "
            f"{r2.code} cuenta con {stops_2} paradas (~{time_2} min, ${r2.fare:,.0f} COP). "
            f"Veredicto: Si priorizas rapidez elige '{mejor_vel}', si priorizas economía elige '{mejor_eco}'."
        )

        return RouteComparisonResult(
            route_1_code=r1.code,
            route_2_code=r2.code,
            route_1_stops=stops_1,
            route_2_stops=stops_2,
            route_1_fare=r1.fare,
            route_2_fare=r2.fare,
            route_1_time_min=time_1,
            route_2_time_min=time_2,
            best_for_speed=mejor_vel,
            best_for_economy=mejor_eco,
            verdict=veredicto
        )


# Aplicación Spyne SOAP 1.1
application = Application(
    [RoutesService],
    tns=NAMESPACE,
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)
