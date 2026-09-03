from spyne import ComplexModel, Integer, Unicode, Float, Boolean

NAMESPACE = 'popayan.transporte.rutas'

class Route(ComplexModel):
    """Representa una ruta de transporte público de Popayán."""
    __namespace__ = NAMESPACE

    id = Integer(doc="Identificador único de la ruta")
    code = Unicode(doc="Código comercial de la ruta (ej: RUTA-1, LINEA-2)")
    company = Unicode(doc="Empresa transportadora (ej: Sotracauca, Transpubenza)")
    origin = Unicode(doc="Punto de origen del recorrido")
    destination = Unicode(doc="Punto de destino final")
    fare = Float(doc="Tarifa oficial del pasaje en pesos colombianos")
    schedule = Unicode(doc="Horario de atención (ej: 05:30 - 21:00)")
    status = Unicode(doc="Estado de la ruta (ACTIVA, SUSPENDIDA)")


class TripPlanResult(ComplexModel):
    """Resultado detallado de la planificación de un viaje directo."""
    __namespace__ = NAMESPACE

    found = Boolean(doc="Indica si se encontró una ruta directa")
    origin_searched = Unicode(doc="Sector de origen ingresado")
    destination_searched = Unicode(doc="Sector de destino ingresado")
    recommended_route_code = Unicode(doc="Código de la ruta óptima sugerida")
    company = Unicode(doc="Empresa prestadora del servicio")
    boarding_stop = Unicode(doc="Paradero sugerido para abordar")
    alighting_stop = Unicode(doc="Paradero sugerido para descender")
    stops_count = Integer(doc="Cantidad de paradas en el trayecto")
    fare = Float(doc="Tarifa oficial a pagar")
    estimated_minutes = Integer(doc="Tiempo estimado de recorrido en minutos")
    trip_summary = Unicode(doc="Instrucción amigable para el usuario")


class TransferTripResult(ComplexModel):
    """Resultado de viaje multimodal con transbordo entre 2 rutas."""
    __namespace__ = NAMESPACE

    found = Boolean(doc="Indica si se encontró una combinación viable con transbordo")
    origin_searched = Unicode(doc="Sector de origen buscado")
    destination_searched = Unicode(doc="Sector de destino buscado")
    first_route_code = Unicode(doc="Código de la primera ruta a tomar")
    first_company = Unicode(doc="Empresa de la primera ruta")
    boarding_stop = Unicode(doc="Paradero para abordar el primer bus")
    transfer_stop = Unicode(doc="Paradero común donde se hace el transbordo")
    second_route_code = Unicode(doc="Código de la segunda ruta a tomar")
    second_company = Unicode(doc="Empresa de la segunda ruta")
    alighting_stop = Unicode(doc="Paradero de llegada final")
    total_fare = Float(doc="Costo total estimado sumando ambos pasajes")
    estimated_minutes = Integer(doc="Tiempo estimado total incluyendo espera de transbordo")
    trip_summary = Unicode(doc="Instrucciones paso a paso del viaje")


class RouteCongestionResult(ComplexModel):
    """Índice de afectación y congestión en tiempo real de una ruta."""
    __namespace__ = NAMESPACE

    route_id = Integer(doc="ID de la ruta evaluada")
    route_code = Unicode(doc="Código de la ruta")
    company = Unicode(doc="Empresa transportadora")
    active_incidents_count = Integer(doc="Número de incidentes viales activos reportados")
    congestion_level = Unicode(doc="Nivel de congestión: NORMAL, MODERADO, ALTO, CRÍTICO")
    delay_minutes = Integer(doc="Minutos de retraso proyectados")
    reliability_score = Float(doc="Puntaje de confiabilidad de la ruta (0 a 100%)")
    status_summary = Unicode(doc="Diagnóstico general del estado vial")


class TrafficSimulationResult(ComplexModel):
    """Simulación de tiempo de recorrido según franja horaria (Hora Pico vs Valle)."""
    __namespace__ = NAMESPACE

    route_id = Integer(doc="ID de la ruta evaluada")
    route_code = Unicode(doc="Código de la ruta")
    departure_hour = Unicode(doc="Hora de salida ingresada (HH:MM)")
    is_peak_hour = Boolean(doc="Indica si la hora de salida cae en hora pico de Popayán")
    traffic_factor = Float(doc="Factor multiplicador aplicado por tráfico")
    base_minutes = Integer(doc="Tiempo base en condiciones normales (minutos)")
    real_estimated_minutes = Integer(doc="Tiempo real estimado con tráfico (minutos)")
    estimated_arrival_time = Unicode(doc="Hora estimada de llegada al destino (HH:MM)")
    advice = Unicode(doc="Recomendación preventiva para el pasajero")


class RouteComparisonResult(ComplexModel):
    """Comparativa técnica de eficiencia entre dos rutas de transporte."""
    __namespace__ = NAMESPACE

    route_1_code = Unicode(doc="Código de la Ruta 1")
    route_2_code = Unicode(doc="Código de la Ruta 2")
    route_1_stops = Integer(doc="Cantidad de paraderos registrados en Ruta 1")
    route_2_stops = Integer(doc="Cantidad de paraderos registrados en Ruta 2")
    route_1_fare = Float(doc="Tarifa de la Ruta 1")
    route_2_fare = Float(doc="Tarifa de la Ruta 2")
    route_1_time_min = Integer(doc="Tiempo estimado de vuelta completa en Ruta 1 (min)")
    route_2_time_min = Integer(doc="Tiempo estimado de vuelta completa en Ruta 2 (min)")
    best_for_speed = Unicode(doc="Ruta recomendada por menor tiempo de recorrido")
    best_for_economy = Unicode(doc="Ruta recomendada por menor costo")
    verdict = Unicode(doc="Conclusión y análisis comparativo")
