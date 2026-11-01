# ==============================================================================
# ARCHIVO: backend/servicio_rutas/models.py
# RESPONSABILIDAD: Modelos de datos del dominio y estructuras de respuesta.
# PATRÓN: Data Transfer Objects (DTO) usando @dataclass con slots=True para rendimiento.
# ==============================================================================

# Importa el decorador dataclass de la biblioteca estándar de Python.
from dataclasses import dataclass


@dataclass(slots=True)
class Route:
    """Representa una ruta física de transporte público urbano en Popayán."""

    id: int              # Identificador numérico único de la ruta en la base de datos
    code: str            # Código visible de la ruta (ej. 'RUTA 1', 'RUTA 2')
    company: str         # Empresa prestadora del servicio (ej. 'Sotracauca', 'Transpubenza')
    origin: str          # Sector de inicio del recorrido (ej. 'Lomas de Granada')
    destination: str     # Sector final o terminal de retorno (ej. 'Campanario')
    fare: float          # Tarifa oficial en pesos colombianos (COP)
    schedule: str        # Horario de operación habilitado (ej. '05:30 - 21:30')
    status: str          # Estado operativo actual (ej. 'ACTIVA', 'SUSPENDIDA')


@dataclass(slots=True)
class TripPlanResult:
    """Estructura de respuesta para la planificación algorítmica de un viaje directo."""

    found: bool = False                   # Indica si se encontró una ruta que conecte ambos paraderos
    origin_searched: str = ""             # Criterio de búsqueda original para el origen
    destination_searched: str = ""        # Criterio de búsqueda original para el destino
    recommended_route_code: str = ""      # Código de la ruta directa seleccionada
    company: str = ""                     # Empresa operadora de dicha ruta
    boarding_stop: str = ""               # Nombre del paradero exacto de abordaje
    alighting_stop: str = ""              # Nombre del paradero exacto de desembarque
    stops_count: int = 0                  # Cantidad de paraderos intermedios entre origen y destino
    fare: float = 0.0                     # Tarifa total liquidada
    estimated_minutes: int = 0            # Tiempo estimado de trayecto calculado dinámicamente
    trip_summary: str = ""                # Resumen textual descriptivo para el usuario


@dataclass(slots=True)
class TransferTripResult:
    """Estructura de respuesta para planificación multimodal con transbordo entre 2 rutas."""

    found: bool = False                   # Indica si existe combinación con transbordo viable
    origin_searched: str = ""             # Término de búsqueda de origen
    destination_searched: str = ""        # Término de búsqueda de destino
    first_route_code: str = ""            # Código de la primera ruta a tomar
    first_company: str = ""               # Empresa de la primera ruta
    boarding_stop: str = ""               # Paradero donde sube el pasajero inicialmente
    transfer_stop: str = ""               # Paradero intermedio común donde se realiza el cambio de colectivo
    second_route_code: str = ""           # Código de la segunda ruta a tomar
    second_company: str = ""              # Empresa de la segunda ruta
    alighting_stop: str = ""              # Paradero final de destino
    total_fare: float = 0.0               # Sumatoria de ambas tarifas de pasaje
    estimated_minutes: int = 0            # Tiempo total (incluyendo margen de espera en el nodo común)
    trip_summary: str = ""                # Instrucciones paso a paso para el viajero


@dataclass(slots=True)
class RouteCongestionResult:
    """Estructura que reporta el índice de afectación y confiabilidad en tiempo real de una ruta."""

    route_id: int = 0                     # ID primario de la ruta analizada
    route_code: str = ""                  # Código de la ruta
    company: str = ""                     # Empresa operadora
    active_incidents_count: int = 0       # Total de incidentes viales activos no resueltos
    congestion_level: str = ""            # Nivel cualitativo: NORMAL, MODERADO, ALTO, CRITICO
    delay_minutes: int = 0                # Minutos acumulados de retraso estimados
    reliability_score: float = 0.0        # Porcentaje de confiabilidad del servicio (0% a 100%)
    status_summary: str = ""              # Diagnóstico técnico descriptivo


@dataclass(slots=True)
class TrafficSimulationResult:
    """Estructura que simula el tiempo de viaje según la hora del día y congestión histórica."""

    route_id: int = 0                     # ID de la ruta evaluada
    route_code: str = ""                  # Código de la ruta
    departure_hour: str = ""              # Hora programada de salida (HH:MM)
    is_peak_hour: bool = False            # Bandera que indica si cae en una de las 3 horas pico de Popayán
    traffic_factor: float = 0.0           # Factor multiplicador de fricción (1.45x en hora pico)
    base_minutes: int = 0                 # Tiempo estimado en condiciones ideales de tráfico fluido
    real_estimated_minutes: int = 0       # Tiempo real estimado aplicando el factor de fricción
    estimated_arrival_time: str = ""      # Hora proyectada de llegada al destino
    advice: str = ""                      # Recomendación preventiva al pasajero


@dataclass(slots=True)
class RouteComparisonResult:
    """Estructura de comparación técnica de eficiencia entre dos rutas de transporte."""

    route_1_code: str = ""                # Código de la primera ruta evaluada
    route_2_code: str = ""                # Código de la segunda ruta evaluada
    route_1_stops: int = 0                # Paraderos totales de la ruta 1
    route_2_stops: int = 0                # Paraderos totales de la ruta 2
    route_1_fare: float = 0.0             # Tarifa de la ruta 1
    route_2_fare: float = 0.0             # Tarifa de la ruta 2
    route_1_time_min: int = 0             # Tiempo de ciclo de la ruta 1
    route_2_time_min: int = 0             # Tiempo de ciclo de la ruta 2
    best_for_speed: str = ""              # Ruta ganadora en velocidad
    best_for_economy: str = ""            # Ruta ganadora en costo
    verdict: str = ""                     # Veredicto técnico comparativo
