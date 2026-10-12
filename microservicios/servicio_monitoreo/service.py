import math
from datetime import datetime, timedelta
import repository


class DespachoService:
    """
    Capa de Logica de Negocio del Microservicio de Programacion y Despacho Operativo.
    Implementa logicas para la gestion de horarios, vehiculos y conductores en Popayan.
    """

    # ==========================================================================
    # FUNCIONALIDAD 1: Generacion de tabla horaria por tipo de dia
    # ==========================================================================
    @staticmethod
    def generar_tabla_horaria(route_id: int, tipo_dia: str, hora_inicio: str = "05:00", hora_fin: str = "22:00") -> dict:
        """
        Genera la tabla de salidas de cabecera para una ruta segun el tipo de dia.
        La frecuencia NO es lineal: varia por franja horaria y tipo de dia.

        Tipos de dia: HABIL, SABADO, DOMINGO, FESTIVO
        """
        tipo_dia = tipo_dia.upper().strip()
        tipos_validos = {"HABIL", "SABADO", "DOMINGO", "FESTIVO"}
        if tipo_dia not in tipos_validos:
            raise ValueError(f"tipo_dia invalido. Use: {', '.join(sorted(tipos_validos))}")

        try:
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fin    = datetime.strptime(hora_fin,    "%H:%M")
        except ValueError:
            raise ValueError("Formato de hora invalido. Use HH:MM (ej: 05:30)")

        # Frecuencias base (minutos entre despachos) segun franja y tipo de dia
        def _frecuencia(hora: int, tipo: str) -> int:
            if tipo == "HABIL":
                if 5 <= hora < 7:   return 20
                if 7 <= hora < 9:   return 8   # pico manana
                if 9 <= hora < 11:  return 15
                if 11 <= hora < 14: return 10  # pico mediodia
                if 14 <= hora < 17: return 15
                if 17 <= hora < 20: return 8   # pico tarde
                return 20
            elif tipo == "SABADO":
                if 6 <= hora < 9:   return 12
                if 9 <= hora < 14:  return 10
                if 14 <= hora < 19: return 15
                return 25
            elif tipo == "DOMINGO":
                if 7 <= hora < 10:  return 20
                if 10 <= hora < 14: return 15
                if 14 <= hora < 18: return 20
                return 30
            else:  # FESTIVO
                if 8 <= hora < 12:  return 25  # festivos de Popayan inician tarde
                if 12 <= hora < 16: return 20
                if 16 <= hora < 20: return 25
                return 35

        salidas = []
        actual  = inicio
        while actual <= fin:
            frecuencia = _frecuencia(actual.hour, tipo_dia)
            salidas.append({
                "hora_salida":      actual.strftime("%H:%M"),
                "frecuencia_min":   frecuencia,
                "franja":           _nombre_franja(actual.hour)
            })
            actual += timedelta(minutes=frecuencia)

        total_salidas = len(salidas)
        frecuencia_promedio = round(sum(s["frecuencia_min"] for s in salidas) / max(total_salidas, 1), 1)

        return {
            "route_id":          route_id,
            "tipo_dia":          tipo_dia,
            "hora_inicio":       hora_inicio,
            "hora_fin":          hora_fin,
            "total_salidas":     total_salidas,
            "frecuencia_promedio_min": frecuencia_promedio,
            "tabla_horaria":     salidas,
            "nota": f"Horario generado con {total_salidas} despachos. Frecuencia variable por franja horaria de Popayan."
        }

    # ==========================================================================
    # FUNCIONALIDAD 2: Generador de frecuencias minimas por demanda horaria
    # ==========================================================================
    @staticmethod
    def calcular_frecuencias_minimas(route_id: int, hora: int, tipo_dia: str, capacidad_bus: int = 19) -> dict:
        """
        Calcula cuantos colectivos por hora se necesitan en una ruta especifica segun su demanda real en Popayan.
        - La demanda varia segun la RUTA (route_id): no es lo mismo una ruta troncal como la Ruta 1 (Campanario)
          que una ruta veredal como la Ruta 6 (Cajete/Pisojé) o un circuito urbano como la Ruta 5 (Calle 5).
        - Factor Unicauca: La Universidad del Cauca moviliza a mas de 18.000 estudiantes entre sus campus
          (Tulcan, Centro Historico, Facultad de Salud / Hospital San Jose, Los Naranjos).
          Solo las rutas que conectan con estos campus universitarios en dias habiles y horas de clase
          reciben el incremento de demanda estudiantil (+15% a +25%).
        """
        tipo_dia = tipo_dia.upper().strip()
        if not (0 <= hora <= 23):
            raise ValueError("La hora debe estar entre 0 y 23.")

        # 1. Obtener la ruta real desde la base de datos
        ruta_db = None
        stops_count = 0
        try:
            ruta_db = repository.find_route_by_id(route_id)
            stops_count = repository.get_stops_count(route_id)
        except Exception:
            pass

        codigo_ruta = f"RUTA-{route_id}"
        empresa = "Transporte Popayán"
        nombre_ruta = f"Ruta {route_id}"
        origen_dest = ""

        if ruta_db:
            codigo_ruta = ruta_db.get("code") or codigo_ruta
            empresa = ruta_db.get("company") or empresa
            orig = ruta_db.get("origin") or ""
            dest = ruta_db.get("destination") or ""
            nombre_ruta = f"{orig} -> {dest}"
            origen_dest = f"{orig} {dest}".lower()

        # 2. Factores de demanda base por franja horaria en Popayán
        demanda_base = {
            "HABIL":   {range(5, 7): 120, range(7, 9): 380, range(9, 11): 200,
                        range(11, 14): 320, range(14, 17): 210, range(17, 20): 390,
                        range(20, 23): 130},
            "SABADO":  {range(6, 9): 180, range(9, 14): 260, range(14, 19): 220, range(19, 23): 100},
            "DOMINGO": {range(7, 10): 140, range(10, 14): 200, range(14, 18): 180, range(18, 22): 90},
            "FESTIVO": {range(8, 12): 160, range(12, 16): 240, range(16, 20): 200, range(20, 23): 80},
        }

        pasajeros_hora_base = 100
        franjas = demanda_base.get(tipo_dia, demanda_base["HABIL"])
        for rango, valor in franjas.items():
            if hora in rango:
                pasajeros_hora_base = valor
                break

        # 3. Factor de Corredor según el destino y sector de la ruta en Popayán:
        # - Veredas (Cajete, Pisojé, La Venta, Santa Teresa): densidad poblacional reducida (~0.50x - 0.60x).
        # - Troncales principales (Terraplaza, Campanario, Variante, Bolívar, Terminal): alta concentración (~1.15x - 1.25x).
        # - Rutas intermedias urbanas (Calle 5, Lomas de Granada, Pandiguando, La Paz): demanda estándar (~0.85x - 1.00x).
        veredas = ["cajete", "pisoje", "pisojé", "santa teresa", "piendamo", "piendamó", "santa bárbara", "calibío", "la venta"]
        troncales = ["campanario", "terraplaza", "variante", "bolívar", "bolivar", "terminal", "loma de la virgen"]

        if any(v in origen_dest for v in veredas):
            factor_corredor = 0.55
            tipo_corredor = "RURAL_VEREDAL (Demanda reducida en zonas campesinas)"
        elif any(t in origen_dest for t in troncales):
            factor_corredor = 1.20
            tipo_corredor = "TRONCAL_ALTA_AFLUENCIA (Conecta centros comerciales, galerías y variantes)"
        else:
            factor_corredor = 0.90
            tipo_corredor = "URBANA_BARRIAL (Circuito interbarrial convencional)"

        # Ajuste adicional por número de paraderos (mayor cobertura = más pasajeros)
        factor_paradas = 0.9 + min(0.3, stops_count * 0.05) if stops_count > 0 else 1.0

        # 4. Factor Unicauca: ¿Pasa por zonas universitarias en horario de clases?
        # Zonas Unicauca: Tulcán (Ingeniería/Salud/FACA), Claustro Santo Domingo (Centro), Hospital San José, Los Naranjos.
        sectores_unicauca = ["tulcan", "tulcán", "hospital san josé", "hospital", "centro", "los naranjos", "campanario", "calle 5", "santo domingo"]
        pasa_por_unicauca = any(s in origen_dest for s in sectores_unicauca)
        es_hora_pico_universitaria = tipo_dia == "HABIL" and (7 <= hora <= 9 or 12 <= hora <= 14 or 17 <= hora <= 19)

        if pasa_por_unicauca and es_hora_pico_universitaria:
            factor_unicauca = 1.20
            explicacion_unicauca = (
                "ACTIVO (+20%): La ruta pasa por campus de Unicauca en hora pico de entrada/salida a clases."
            )
        elif pasa_por_unicauca:
            factor_unicauca = 1.05
            explicacion_unicauca = (
                "LEVE (+5%): La ruta pasa por campus universitarios en horario valle de clases."
            )
        else:
            factor_unicauca = 1.00
            explicacion_unicauca = (
                "INACTIVO (1.0x): La ruta no conecta con campus de Unicauca o es fin de semana/festivo."
            )

        # 5. Cálculo no lineal de la demanda real para esta ruta y hora
        demanda_real = round(pasajeros_hora_base * factor_corredor * factor_paradas * factor_unicauca)
        demanda_real = max(25, demanda_real)

        # Colectivos requeridos: demanda / (capacidad * ocupación objetivo 0.75)
        ocupacion_objetivo = 0.75
        capacidad = max(10, capacidad_bus)
        buses_necesarios = math.ceil(demanda_real / (capacidad * ocupacion_objetivo))
        buses_necesarios = max(1, buses_necesarios)

        intervalo_min = max(2, round(60 / buses_necesarios))

        if demanda_real >= 320:   nivel = "DEMANDA_ALTA_HORA_PICO"
        elif demanda_real >= 180: nivel = "DEMANDA_MEDIA"
        else:                     nivel = "DEMANDA_BAJA_HORA_VALLE"

        return {
            "route_id":                  route_id,
            "codigo_ruta":               codigo_ruta,
            "nombre_ruta":               nombre_ruta,
            "empresa":                   empresa,
            "hora":                      f"{hora:02d}:00",
            "tipo_dia":                  tipo_dia,
            "tipo_corredor":             tipo_corredor,
            "pasajeros_hora_estimados":  demanda_real,
            "capacidad_bus":             capacidad,
            "buses_requeridos":          buses_necesarios,
            "intervalo_minutos":         intervalo_min,
            "nivel_demanda":             nivel,
            "factor_unicauca":           factor_unicauca,
            "impacto_universitario":     explicacion_unicauca,
            "recomendacion": (
                f"Para la ruta {codigo_ruta} ({empresa}), despachar 1 colectivo cada {intervalo_min} min "
                f"({buses_necesarios} colectivos/hora). Demanda proyectada: {demanda_real} pasajeros/hora."
            )
        }

    # ==========================================================================
    # FUNCIONALIDAD 3: Asignacion de tamano de colectivo/buseta y control de asientos
    # ==========================================================================
    @staticmethod
    def asignar_tipo_vehiculo(route_id: int, hora: int, pasajeros_estimados: int,
                              longitud_ruta_km: float = 15.0, es_vereda: bool = None,
                              recargo_vereda: int = None) -> dict:
        """
        Determina el tamano del vehiculo y liquida el recaudo por asiento/pasajero en Popayan:
        1. En Popayan solo hay un tipo de bus: COLECTIVO / BUSETA (Sotracauca, Transpubenza, etc.).
           Solo varia el tamano:
             - Colectivo Pequeño (Microbús): 19 asientos
             - Colectivo Mediano (Buseta): 25 asientos
             - Colectivo Grande (Buseta extendida): 32 asientos
        2. Cada asiento representa un pasajero sentado y cada pasajero paga su tarifa reglamentaria:
             - Tarifa urbana oficial Popayán: $3.000 COP
             - A veredas: +$200 COP (cercana = $3.200) o +$400 COP (lejana = $3.400)
        """
        if pasajeros_estimados < 0:
            raise ValueError("pasajeros_estimados no puede ser negativo.")

        # Consultar contexto de la ruta en base de datos si existe
        ruta_db = None
        try:
            ruta_db = repository.find_route_by_id(route_id)
        except Exception:
            pass

        origen_dest = ""
        if ruta_db:
            origen_dest = f"{ruta_db.get('origin', '')} {ruta_db.get('destination', '')}".lower()

        veredas_lejanas = ["cajete", "pisoje", "pisojé", "santa teresa", "piendamo", "piendamó", "santa bárbara", "calibío", "calibio"]
        veredas_cercanas = ["la venta", "julumito", "puelenje", "figueroa", "el sendero", "santa rosa"]

        if es_vereda is None:
            if any(v in origen_dest for v in veredas_lejanas):
                es_vereda = True
                recargo_calculado = 400
                tipo_zona = "VEREDA_LEJANA"
            elif any(v in origen_dest for v in veredas_cercanas):
                es_vereda = True
                recargo_calculado = 200
                tipo_zona = "VEREDA_CERCANA"
            else:
                es_vereda = False
                recargo_calculado = 0
                tipo_zona = "URBANO"
        else:
            if es_vereda:
                recargo_calculado = int(recargo_vereda) if recargo_vereda in (200, 400) else 400
                tipo_zona = "VEREDA_LEJANA" if recargo_calculado == 400 else "VEREDA_CERCANA"
            else:
                recargo_calculado = 0
                tipo_zona = "URBANO"

        tarifa_base_urbana = 3000
        tarifa_pasaje = tarifa_base_urbana + recargo_calculado

        # Tipos de colectivo disponibles en Popayan (mismo bus, variando en tamano)
        tamanos_colectivo = [
            {
                "tipo_vehiculo": "COLECTIVO",
                "tamano": "PEQUEÑO (MICROBÚS)",
                "asientos": 19,
                "costo_km": 1200,
                "umbral_min": 0,
                "umbral_max": 22,
                "descripcion": "Microbús colectivo tradicional de Popayán (19 asientos)"
            },
            {
                "tipo_vehiculo": "COLECTIVO",
                "tamano": "MEDIANO (BUSETA)",
                "asientos": 25,
                "costo_km": 1500,
                "umbral_min": 23,
                "umbral_max": 30,
                "descripcion": "Buseta colectiva estándar de Popayán (25 asientos)"
            },
            {
                "tipo_vehiculo": "COLECTIVO",
                "tamano": "GRANDE (BUSETA EXTENDIDA)",
                "asientos": 32,
                "costo_km": 1800,
                "umbral_min": 31,
                "umbral_max": 9999,
                "descripcion": "Colectivo grande para horas pico o rutas veredales (32 asientos)"
            },
        ]

        vehiculo_asignado = tamanos_colectivo[0]
        for v in tamanos_colectivo:
            if v["umbral_min"] <= pasajeros_estimados <= v["umbral_max"]:
                vehiculo_asignado = v
                break

        asientos_totales = vehiculo_asignado["asientos"]
        asientos_ocupados = min(pasajeros_estimados, asientos_totales)
        asientos_libres = max(0, asientos_totales - pasajeros_estimados)
        pasajeros_de_pie_sobrecupo = max(0, pasajeros_estimados - asientos_totales)

        # Cada pasajero paga la tarifa de pasaje oficial ($3.000 COP urbana, o $3.200/$3.400 vereda)
        total_recaudo_pasajes = round(pasajeros_estimados * tarifa_pasaje)
        recaudo_asientos_llenos = round(asientos_totales * tarifa_pasaje)

        # Costo operativo de combustible y mantenimiento por kilometro
        factor_distancia = 1.0 + (longitud_ruta_km / 50.0) ** 2
        costo_operativo_ruta = round(vehiculo_asignado["costo_km"] * longitud_ruta_km * factor_distancia)
        balance_neto_vuelta  = round(total_recaudo_pasajes - costo_operativo_ruta)

        ocupacion_pct = round((pasajeros_estimados / asientos_totales) * 100, 1)

        if pasajeros_de_pie_sobrecupo > 0:
            alerta = (
                f"SOBRECUPO: {pasajeros_de_pie_sobrecupo} pasajeros van de pie superando los "
                f"{asientos_totales} asientos del colectivo ({ocupacion_pct}% ocupación). Despachar colectivo de refuerzo."
            )
        elif ocupacion_pct >= 85:
            alerta = f"CAPACIDAD_LIMITE: Colectivo casi lleno ({asientos_ocupados}/{asientos_totales} asientos ocupados, {asientos_libres} libres)."
        elif ocupacion_pct >= 50:
            alerta = f"CAPACIDAD_NORMAL: Colectivo operando con buena ocupación ({asientos_ocupados}/{asientos_totales} asientos)."
        else:
            alerta = f"SUBUTILIZADO: Hay {asientos_libres} asientos vacíos. Se recomienda colectivo pequeño de 19 asientos."

        return {
            "route_id":              route_id,
            "hora":                  f"{hora:02d}:00",
            "pasajeros_estimados":   pasajeros_estimados,
            "longitud_ruta_km":      longitud_ruta_km,
            "analisis_asientos_y_pasajes": {
                "principio":         "Cada asiento representa un pasajero y cada pasajero paga su tarifa reglamentaria.",
                "tarifa_por_pasajero": f"${tarifa_pasaje:,} COP",
                "tipo_trayecto":     tipo_zona,
                "es_vereda":         es_vereda,
                "recargo_vereda":    f"+${recargo_calculado:,} COP" if recargo_calculado > 0 else "$0 COP",
                "asientos_totales":  asientos_totales,
                "asientos_ocupados": asientos_ocupados,
                "asientos_libres":   asientos_libres,
                "pasajeros_de_pie_sobrecupo": pasajeros_de_pie_sobrecupo,
                "total_recaudo_pasajes": f"${total_recaudo_pasajes:,} COP",
                "recaudo_capacidad_maxima": f"${recaudo_asientos_llenos:,} COP",
                "costo_operativo_ruta": f"${costo_operativo_ruta:,} COP",
                "balance_neto_vuelta": f"${balance_neto_vuelta:,} COP"
            },
            "vehiculo_asignado": {
                "tipo":              "COLECTIVO",
                "tamano":            vehiculo_asignado["tamano"],
                "capacidad":         asientos_totales,
                "capacidad_asientos": asientos_totales,
                "tarifa_por_pasajero": f"${tarifa_pasaje:,} COP",
                "asientos_ocupados": asientos_ocupados,
                "asientos_libres":   asientos_libres,
                "pasajeros_de_pie":  pasajeros_de_pie_sobrecupo,
                "ocupacion_pct":     f"{ocupacion_pct}%",
                "total_recaudo_pasajes": f"${total_recaudo_pasajes:,} COP",
                "costo_operativo_ruta": f"${costo_operativo_ruta:,} COP",
                "descripcion":       vehiculo_asignado["descripcion"]
            },
            "factor_distancia":      round(factor_distancia, 3),
            "alerta":                alerta
        }

    # ==========================================================================
    # FUNCIONALIDAD 4: Control de tiempos de descanso en terminal
    # ==========================================================================
    @staticmethod
    def calcular_descanso_terminal(route_id: int, bus_plate: str, horas_en_ruta: float, km_recorridos: float, hora_llegada: str = None) -> dict:
        """
        Calcula los minutos de descanso reglamentarios que el conductor debe tomar
        en la terminal antes de reiniciar el viaje de vuelta.
        Penalizacion no lineal si las horas acumuladas superan umbrales criticos.
        """
        if horas_en_ruta < 0 or km_recorridos < 0:
            raise ValueError("horas_en_ruta y km_recorridos deben ser valores positivos.")

        # Descanso base reglamentario en Colombia (Res. 315 de 2013): 15 min cada 2h de conduccion continua
        descanso_base = 15.0

        # Factor no lineal por fatiga acumulada: crece cuadraticamente despues de 4h
        if horas_en_ruta <= 2.0:
            factor_fatiga  = 1.0
            nivel_fatiga   = "NORMAL"
        elif horas_en_ruta <= 4.0:
            factor_fatiga  = 1.0 + 0.15 * (horas_en_ruta - 2.0)
            nivel_fatiga   = "FATIGA_LEVE"
        elif horas_en_ruta <= 6.0:
            factor_fatiga  = 1.3 + 0.4 * ((horas_en_ruta - 4.0) ** 1.5)
            nivel_fatiga   = "FATIGA_MODERADA"
        else:
            factor_fatiga  = 1.3 + 0.4 * ((horas_en_ruta - 4.0) ** 1.5) + 0.6 * (horas_en_ruta - 6.0)
            nivel_fatiga   = "FATIGA_CRITICA"

        # Factor adicional por kilometros: ruta larga por la Variante o tramo Campanario-Terminal
        factor_km     = 1.0 + max(0, (km_recorridos - 30.0) / 100.0)
        descanso_total = round(descanso_base * factor_fatiga * factor_km)
        descanso_total = max(10, min(60, descanso_total))  # minimo 10, maximo 60 min

        # Calcular proxima hora de salida
        proxima_salida = None
        if hora_llegada:
            try:
                llegada_dt = datetime.strptime(hora_llegada, "%H:%M")
                salida_dt  = llegada_dt + timedelta(minutes=descanso_total)
                proxima_salida = salida_dt.strftime("%H:%M")
            except ValueError:
                proxima_salida = "Formato de hora invalido (use HH:MM)"

        cumple = horas_en_ruta <= 8.0  # Maximo legal 8h por turno en Colombia

        return {
            "route_id":            route_id,
            "bus_plate":           bus_plate,
            "horas_en_ruta":       horas_en_ruta,
            "km_recorridos":       km_recorridos,
            "nivel_fatiga":        nivel_fatiga,
            "factor_fatiga":       round(factor_fatiga, 3),
            "descanso_requerido_min": descanso_total,
            "hora_llegada":        hora_llegada,
            "proxima_salida":      proxima_salida,
            "cumple_reglamento":   cumple,
            "alerta": (
                "LIMITE_TURNO_SUPERADO: El conductor debe ser reemplazado. No puede continuar el turno."
                if not cumple else
                f"Descanso de {descanso_total} min requerido antes de iniciar el regreso."
            )
        }

    # ==========================================================================
    # FUNCIONALIDAD 5: Optimizador de rotacion de conductores
    # ==========================================================================
    @staticmethod
    def optimizar_rotacion_conductor(nombre_conductor: str, empresa: str, horas_acumuladas: float,
                                      km_acumulados: float, turnos_del_dia: int = 1,
                                      incidentes_reportados: int = 0, vueltas_completadas: int = None,
                                      conductor_id: int = None) -> dict:
        """
        Determina si un conductor debe ser rotado en su turno con score de fatiga no lineal.
        Soporta identificacion por conductor_id (base de datos) o nombre directo.
        Basado en normativa colombiana de transporte publico (Decreto 1079/2015).
        """
        LIMITE_HORAS_TURNO = 8.0
        LIMITE_KM_TURNO    = 200.0
        LIMITE_TURNOS_DIA  = 2

        score_fatiga = 0.0

        # Factor 1: horas acumuladas (penalizacion exponencial al superar 8h)
        if horas_acumuladas <= LIMITE_HORAS_TURNO:
            pct_horas = horas_acumuladas / LIMITE_HORAS_TURNO
            score_fatiga += 40.0 * (pct_horas ** 1.8)
        else:
            exceso_horas = horas_acumuladas - LIMITE_HORAS_TURNO
            score_fatiga += 40.0 + 20.0 * (math.exp(exceso_horas * 0.5) - 1)

        # Factor 2: kilometros acumulados
        if km_acumulados <= LIMITE_KM_TURNO:
            pct_km = km_acumulados / LIMITE_KM_TURNO
            score_fatiga += 30.0 * (pct_km ** 1.5)
        else:
            exceso_km = km_acumulados - LIMITE_KM_TURNO
            score_fatiga += 30.0 + 15.0 * math.log(1 + exceso_km / 10.0)

        # Factor 3: turnos en el dia
        if turnos_del_dia >= LIMITE_TURNOS_DIA:
            score_fatiga += 15.0 * turnos_del_dia

        # Factor 4: incidentes reportados (tension y fatiga psicologica del conductor)
        if incidentes_reportados > 0:
            score_fatiga += min(15.0, incidentes_reportados * 5.0)

        score_fatiga = round(min(100.0, score_fatiga), 2)

        necesita_relevo = (
            horas_acumuladas > LIMITE_HORAS_TURNO or
            km_acumulados > LIMITE_KM_TURNO or
            turnos_del_dia >= LIMITE_TURNOS_DIA or
            score_fatiga >= 80.0
        )

        if necesita_relevo:
            tiempo_max_adicional = 0
            medida = "RELEVO_INMEDIATO: Asignar conductor de reserva. Prohibido continuar segun Decreto 1079/2015."
        elif score_fatiga >= 60.0:
            tiempo_max_adicional = round((LIMITE_HORAS_TURNO - horas_acumuladas) * 60 * 0.5)
            medida = f"PRECAUCION: Conductor en zona amarilla. Maximo {tiempo_max_adicional} min adicionales antes de relevo obligatorio."
        else:
            tiempo_max_adicional = round((LIMITE_HORAS_TURNO - horas_acumuladas) * 60)
            medida = f"APTO: Conductor puede continuar hasta {tiempo_max_adicional} min mas antes de cumplir el limite de turno."

        if score_fatiga >= 80.0:   categoria = "CRITICO"
        elif score_fatiga >= 60.0: categoria = "ALTO"
        elif score_fatiga >= 40.0: categoria = "MODERADO"
        else:                      categoria = "NORMAL"

        return {
            "conductor_id":        conductor_id,
            "conductor":           nombre_conductor,
            "empresa":             empresa,
            "horas_acumuladas":    horas_acumuladas,
            "km_acumulados":       km_acumulados,
            "vueltas_completadas": vueltas_completadas,
            "incidentes_reportados": incidentes_reportados,
            "turnos_del_dia":      turnos_del_dia,
            "score_fatiga":        score_fatiga,
            "categoria_fatiga":    categoria,
            "necesita_relevo":     necesita_relevo,
            "tiempo_max_adicional_min": tiempo_max_adicional,
            "limites_normativos": {
                "horas_max_turno": LIMITE_HORAS_TURNO,
                "km_max_turno":    LIMITE_KM_TURNO,
                "turnos_max_dia":  LIMITE_TURNOS_DIA
            },
            "medida": medida
        }


# ==========================================================================
# HELPER COMPARTIDO
# ==========================================================================

def _nombre_franja(hora: int) -> str:
    if 5 <= hora < 7:   return "Madrugada"
    if 7 <= hora < 9:   return "Pico Manana"
    if 9 <= hora < 11:  return "Manana Media"
    if 11 <= hora < 14: return "Pico Mediodia"
    if 14 <= hora < 17: return "Tarde"
    if 17 <= hora < 20: return "Pico Tarde"
    if 20 <= hora < 23: return "Noche"
    return "Madrugada Nocturna"
