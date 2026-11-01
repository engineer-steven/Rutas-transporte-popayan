# ==============================================================================
# ARCHIVO: backend/servicio_operaciones/models.py
# RESPONSABILIDAD: Modelos de datos de entidades operativas (Paraderos e Incidentes).
# PATRÓN: Data Transfer Objects (DTO) usando @dataclass con slots=True.
# ==============================================================================

# Importa el decorador dataclass de la biblioteca estándar de Python.
from dataclasses import dataclass


@dataclass(slots=True)
class Stop:
    """Representa un paradero físico o punto de control georreferenciado en la ruta."""

    id: int                     # Clave primaria única del paradero en la tabla 'stops'
    route_id: int               # Clave foránea asociada a la ruta de transporte
    name: str                   # Nombre representativo del paradero (ej. 'Campanario', 'Hospital')
    landmark_reference: str     # Referencia física o hito urbano (ej. 'Frente a entrada principal')
    stop_order: int             # Número secuencial de parada en el sentido de ida (1, 2, 3...)


@dataclass(slots=True)
class Incident:
    """Representa un reporte o novedad vial que afecta el tráfico en la ruta."""

    id: int                     # Identificador único de la novedad en la tabla 'incidents'
    route_id: int               # Ruta sobre la cual se presentó la afectación
    incident_type: str          # Tipo tipificado (ej. 'ACCIDENTE', 'DESVIO', 'CONGESTION')
    description: str            # Detalle descriptivo de lo ocurrido en vía
    reported_by: str            # Entidad o persona que emitió la alerta (ej. 'Policía', 'Operador')
    reported_at: str            # Fecha y hora exacta de registro del evento
    status: str                 # Estado actual de la novedad ('ACTIVO' o 'RESUELTO')


@dataclass(slots=True)
class BusTimeDifferenceResult:
    """Estructura de respuesta para el cálculo de intervalos de salida entre buses (Headway)."""

    route_id: int = 0           # Identificador de la ruta monitoreada
    bus_plate_1: str = ""       # Placa del primer colectivo evaluado
    departure_time_1: str = ""  # Hora en que fue despachado el primer bus
    bus_plate_2: str = ""       # Placa del segundo colectivo evaluado
    departure_time_2: str = ""  # Hora en que fue despachado el segundo bus
    difference_minutes: int = 0 # Brecha de tiempo calculada en minutos
    summary_message: str = ""   # Diagnóstico operativo para control de despacho
