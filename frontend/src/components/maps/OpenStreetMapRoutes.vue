<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { OSM_POPAYAN_COORDINATES } from '@/data/popayanPlaces'

const coordenadasCache = new Map()
const viasPrincipalesCache = new Map()
const geometriaCache = new Map()
const coordenadasConocidas = new Map(OSM_POPAYAN_COORDINATES)
coordenadasConocidas.set('terminal de transporte', [2.4511705, -76.6079814])
coordenadasConocidas.set('cajete', [2.4781725, -76.6750103])
const centroPopayan = [2.4448, -76.6147]
const patronesRuta = [null, '10 6', '3 6', '12 5 2 5']

const props = defineProps({
  segments: {
    type: Array,
    default: () => [],
  },
  journey: {
    type: Object,
    default: null,
  },
  showInstructions: {
    type: Boolean,
    default: true,
  },
})

const transferencias = computed(() => [
  ...new Set(
    props.segments
      .filter((segment) => segment.legIndex < segment.legCount - 1)
      .map((segment) => (segment.journeyStops || segment.stops).at(-1)),
  ),
])

const container = ref(null)
const cargando = ref(false)
const estado = ref('Busca una ruta para verla en el mapa.')
let mapa
let capaRutas
let solicitudActual = 0
let controlador
let ultimaGeocodificacion = 0

function guardarCache(cache, clave, valor, limite) {
  cache.delete(clave)
  cache.set(clave, valor)
  if (cache.size > limite) cache.delete(cache.keys().next().value)
}

function obtenerPatronRuta(segmento) {
  const rutasEmpresa = [
    ...new Set(
      props.segments
        .filter((ruta) => ruta.empresa === segmento.empresa)
        .map((ruta) => ruta.codigo),
    ),
  ]
  const indice = rutasEmpresa.indexOf(segmento.codigo)
  return patronesRuta[(indice < 0 ? 0 : indice) % patronesRuta.length]
}

function contenidoPopup(texto) {
  const contenido = document.createElement('span')
  contenido.textContent = texto
  return contenido
}

async function geocodificar(lugar, signal) {
  const clave = lugar.trim().toLocaleLowerCase('es')
  if (coordenadasConocidas.has(clave)) return coordenadasConocidas.get(clave)
  if (coordenadasCache.has(clave)) return coordenadasCache.get(clave)
  const consulta = clave === 'centro' ? 'Parque Caldas' : lugar

  const parametros = new URLSearchParams({
    q: `${consulta}, Popayán, Cauca, Colombia`,
    format: 'jsonv2',
    limit: '1',
    countrycodes: 'co',
    viewbox: '-76.72,2.52,-76.54,2.35',
    bounded: '1',
  })
  const solicitud = (async () => {
    const espera = Math.max(0, 1100 - (Date.now() - ultimaGeocodificacion))
    if (espera) await new Promise((resolve) => setTimeout(resolve, espera))
    if (signal.aborted) throw new DOMException('La búsqueda fue cancelada.', 'AbortError')
    ultimaGeocodificacion = Date.now()

    const respuesta = await fetch(`https://nominatim.openstreetmap.org/search?${parametros}`, {
      signal,
    })
    if (!respuesta.ok) throw new Error('No fue posible buscar lugares en OpenStreetMap.')

    const datos = await respuesta.json()
    const lugarEncontrado = datos[0]
    if (!lugarEncontrado) {
      throw new Error(`No encontramos “${lugar}” en el mapa.`)
    }

    const punto = [Number(lugarEncontrado.lat), Number(lugarEncontrado.lon)]
    guardarCache(coordenadasCache, clave, punto, 100)
    return punto
  })()
  return solicitud
}

async function trazarSegmento(segmento, paraderos, signal) {
  const coordenadas = paraderos.map(([latitud, longitud]) => `${longitud},${latitud}`).join(';')
  let trazado = geometriaCache.get(coordenadas)
  if (!trazado) {
    const ruta = new URL(`https://router.project-osrm.org/route/v1/driving/${coordenadas}`)
    ruta.searchParams.set('overview', 'full')
    ruta.searchParams.set('geometries', 'geojson')
    ruta.searchParams.set('steps', 'false')

    const respuesta = await fetch(ruta, { signal })
    if (!respuesta.ok) throw new Error('El servicio de trazado no respondió.')
    const datos = await respuesta.json()
    const puntos = datos.routes?.[0]?.geometry?.coordinates
    if (!Array.isArray(puntos) || puntos.length < 2) {
      throw new Error('No se pudo calcular el trazado por calles.')
    }
    trazado = puntos.map(([longitud, latitud]) => [latitud, longitud])
    guardarCache(geometriaCache, coordenadas, trazado, 30)
  }

  const color = /^#[\da-f]{6}$/i.test(segmento.color) ? segmento.color : '#2865d8'
  const dashArray = obtenerPatronRuta(segmento)
  L.polyline(trazado, {
    color: '#fff',
    weight: 11,
    opacity: 0.9,
    lineCap: 'round',
    lineJoin: 'round',
    dashArray,
  }).addTo(capaRutas)
  L.polyline(
    trazado,
    { color, weight: 7, opacity: 1, lineCap: 'round', lineJoin: 'round', dashArray },
  ).addTo(capaRutas)
  return trazado
}

function agregarMarcador(punto, letra, texto, clase) {
  const icon = L.divIcon({
    className: 'osm-waypoint-icon',
    html: `<span class="osm-waypoint-badge osm-waypoint-${clase}">${letra}</span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  })

  L.marker(punto, { icon, zIndexOffset: 1000 })
    .addTo(capaRutas)
    .bindPopup(contenidoPopup(texto))
}

function distanciaLocal(punto, origen) {
  const metrosPorGrado = 111320
  const escalaLongitud = Math.cos((origen[0] * Math.PI) / 180)
  return [
    (punto[1] - origen[1]) * metrosPorGrado * escalaLongitud,
    (punto[0] - origen[0]) * metrosPorGrado,
  ]
}

function distanciaPuntoASegmento(punto, inicio, fin, referencia) {
  const [puntoX, puntoY] = distanciaLocal(punto, referencia)
  const [inicioX, inicioY] = distanciaLocal(inicio, referencia)
  const [finX, finY] = distanciaLocal(fin, referencia)
  const deltaX = finX - inicioX
  const deltaY = finY - inicioY
  const longitudCuadrada = deltaX * deltaX + deltaY * deltaY
  if (!longitudCuadrada) return Math.hypot(puntoX - inicioX, puntoY - inicioY)

  const proporcion = Math.max(
    0,
    Math.min(
      1,
      ((puntoX - inicioX) * deltaX + (puntoY - inicioY) * deltaY) / longitudCuadrada,
    ),
  )
  return Math.hypot(puntoX - inicioX - proporcion * deltaX, puntoY - inicioY - proporcion * deltaY)
}

async function obtenerViasPrincipales(origen, signal) {
  const clave = `${origen[0].toFixed(4)},${origen[1].toFixed(4)}`
  if (viasPrincipalesCache.has(clave)) return viasPrincipalesCache.get(clave)

  const consulta = `[out:json][timeout:8];way(around:600,${origen[0]},${origen[1]})["highway"~"^(trunk|primary|secondary|tertiary)$"];out tags geom;`
  const parametros = new URLSearchParams({ data: consulta })
  const respuesta = await fetch(`https://overpass-api.de/api/interpreter?${parametros}`, {
    signal,
  })
  if (!respuesta.ok) throw new Error('No fue posible consultar las vías principales de OpenStreetMap.')

  const datos = await respuesta.json()
  const vias = (datos.elements || [])
    .filter((elemento) => Array.isArray(elemento.geometry) && elemento.geometry.length > 1)
    .map((elemento) => ({
      nombre: elemento.tags?.name || elemento.tags?.ref || '',
      puntos: elemento.geometry.map(({ lat, lon }) => [lat, lon]),
    }))
  guardarCache(viasPrincipalesCache, clave, vias, 20)
  return vias
}

function elegirPuntoDeEspera(origen, trazados, viasPrincipales) {
  let mejorOpcion = null
  const opciones = trazados.flatMap(({ segmento, puntos }) =>
    puntos.map((punto, indice) => ({
      punto,
      segmento,
      anterior: puntos[indice - 1],
      siguiente: puntos[indice + 1],
    })),
  )

  for (const opcion of opciones) {
    const distanciaAlOrigen = Math.hypot(...distanciaLocal(opcion.punto, origen))
    if (distanciaAlOrigen > 600) continue

    for (const via of viasPrincipales) {
      for (let indice = 1; indice < via.puntos.length; indice += 1) {
        const distanciaAVia = distanciaPuntoASegmento(
          opcion.punto,
          via.puntos[indice - 1],
          via.puntos[indice],
          origen,
        )
        if (distanciaAVia > 35) continue

        const puntuacion = distanciaAlOrigen + distanciaAVia * 3
        if (!mejorOpcion || puntuacion < mejorOpcion.puntuacion) {
          mejorOpcion = {
            ...opcion,
            nombreVia: via.nombre,
            puntuacion,
          }
        }
      }
    }
  }

  if (mejorOpcion) {
    return { ...mejorOpcion, sobreViaPrincipal: true }
  }

  return opciones.reduce((masCercana, opcion) => {
    const distancia = Math.hypot(...distanciaLocal(opcion.punto, origen))
    return !masCercana || distancia < masCercana.distancia
      ? { ...opcion, distancia, sobreViaPrincipal: false }
      : masCercana
  }, null)
}

function desplazarPuntoAlCostado(opcion, origen) {
  if (!opcion) return origen
  const anterior = opcion.anterior || opcion.punto
  const siguiente = opcion.siguiente || opcion.punto
  const [anteriorX, anteriorY] = distanciaLocal(anterior, opcion.punto)
  const [siguienteX, siguienteY] = distanciaLocal(siguiente, opcion.punto)
  const direccionX = siguienteX - anteriorX
  const direccionY = siguienteY - anteriorY
  const longitud = Math.hypot(direccionX, direccionY)
  if (!longitud) return opcion.punto

  const desplazamientoLateral = 8
  const lateralX = (-direccionY / longitud) * desplazamientoLateral
  const lateralY = (direccionX / longitud) * desplazamientoLateral
  const metrosPorGrado = 111320
  const escalaLongitud = Math.cos((opcion.punto[0] * Math.PI) / 180)
  return [
    opcion.punto[0] + lateralY / metrosPorGrado,
    opcion.punto[1] + lateralX / (metrosPorGrado * escalaLongitud),
  ]
}

async function dibujarPuntosDeViaje(puntos, trazados, viasPrincipalesPromesa, signal) {
  if (!props.journey) return ''

  const origen = puntos.get(props.journey.origin.trim().toLocaleLowerCase('es'))
  const destino = puntos.get(props.journey.destination.trim().toLocaleLowerCase('es'))
  let avisoPuntoEspera = ''
  if (origen) {
    let puntoElegido
    try {
      const resultadoVias = await viasPrincipalesPromesa
      if (resultadoVias.error) throw resultadoVias.error
      const viasPrincipales = resultadoVias.vias
      puntoElegido = elegirPuntoDeEspera(origen, trazados, viasPrincipales)
    } catch (error) {
      if (signal.aborted) return
      avisoPuntoEspera = error.message
      puntoElegido = elegirPuntoDeEspera(origen, trazados, [])
    }

    if (signal.aborted) return
    if (!puntoElegido) {
      avisoPuntoEspera = 'No se encontró un tramo cercano para ubicar la espera del bus.'
    } else if (!puntoElegido.sobreViaPrincipal && !avisoPuntoEspera) {
      avisoPuntoEspera = 'No encontramos una vía principal cercana; se marcó el tramo más próximo de la ruta.'
    } else if (puntoElegido.sobreViaPrincipal && puntoElegido.nombreVia) {
      avisoPuntoEspera = `Punto de espera sobre ${puntoElegido.nombreVia}, junto a la ruta.`
    } else if (puntoElegido.sobreViaPrincipal) {
      avisoPuntoEspera = 'Punto de espera ubicado junto a una vía principal.'
    }

    const icon = L.divIcon({
      className: 'osm-waypoint-icon',
      html: '<span class="osm-wait-point" aria-hidden="true"></span>',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    })
    if (puntoElegido) {
      const ubicacionEspera = desplazarPuntoAlCostado(puntoElegido, origen)
      const referenciaVia = puntoElegido.nombreVia ? ` en ${puntoElegido.nombreVia}` : ''
      L.marker(ubicacionEspera, { icon, zIndexOffset: 1100 })
        .addTo(capaRutas)
        .bindPopup(contenidoPopup(
          `Espera el bus${referenciaVia}, cerca de ${props.journey.origin}`,
        ))
    }
  }

  if (props.showInstructions) {
    for (const segmento of props.segments) {
      if (segmento.legIndex >= segmento.legCount - 1) continue
      const lugar = (segmento.journeyStops || segmento.stops).at(-1)
      const punto = puntos.get(lugar.trim().toLocaleLowerCase('es'))
      if (punto) agregarMarcador(punto, 'T', `Transbordo: ${lugar}`, 'transfer')
    }
  }

  if (destino) agregarMarcador(destino, 'B', `Destino: ${props.journey.destination}`, 'destination')
  return avisoPuntoEspera
}

async function dibujarRutas() {
  if (!mapa) return

  const solicitud = ++solicitudActual
  controlador?.abort()
  controlador = new AbortController()
  const { signal } = controlador
  capaRutas.clearLayers()

  if (!props.segments.length) {
    cargando.value = false
    estado.value = 'Busca una ruta para verla en el mapa.'
    mapa.setView(centroPopayan, 13)
    return
  }

  cargando.value = true
  estado.value = 'Trazando las rutas sobre el mapa…'
  const puntos = new Map()
  const trazados = []
  const fallidos = []
  let avisoPuntoEspera = ''

  try {
    for (const segmento of props.segments) {
      for (const lugar of segmento.stops || [segmento.origen, segmento.destino]) {
        const clave = lugar.trim().toLocaleLowerCase('es')
        if (puntos.has(clave)) continue
        try {
          puntos.set(clave, await geocodificar(lugar, signal))
        } catch (error) {
          if (signal.aborted) return
          fallidos.push(error.message)
        }
      }
    }

    const origen = props.journey
      ? puntos.get(props.journey.origin.trim().toLocaleLowerCase('es'))
      : null
    const viasPrincipalesPromesa = origen
      ? obtenerViasPrincipales(origen, signal)
          .then((vias) => ({ vias }))
          .catch((error) => ({ error }))
      : Promise.resolve({ vias: [] })
    const segmentosListos = props.segments.map((segmento) => {
      const paraderos = segmento.stops || [segmento.origen, segmento.destino]
      const puntosRuta = paraderos
        .map((lugar) => puntos.get(lugar.trim().toLocaleLowerCase('es')))
        .filter(Boolean)
      return puntosRuta.length >= 2 ? { segmento, puntosRuta } : null
    }).filter(Boolean)
    let siguienteSegmento = 0
    const trabajadores = Array.from(
      { length: Math.min(3, segmentosListos.length) },
      async () => {
        while (siguienteSegmento < segmentosListos.length) {
          if (solicitud !== solicitudActual) return
          const indice = siguienteSegmento
          siguienteSegmento += 1
          const { segmento, puntosRuta } = segmentosListos[indice]

          try {
            const puntosTrazados = await trazarSegmento(segmento, puntosRuta, signal)
            trazados[indice] = { segmento, puntos: puntosTrazados }
          } catch (error) {
            if (signal.aborted) return
            fallidos.push(error.message)
          }
        }
      },
    )
    await Promise.all(trabajadores)

    if (solicitud !== solicitudActual) return
    if (props.journey) {
      avisoPuntoEspera = await dibujarPuntosDeViaje(
        puntos,
        trazados.filter(Boolean),
        viasPrincipalesPromesa,
        signal,
      )
      if (solicitud !== solicitudActual) return
    }

    const limites = capaRutas.getBounds()
    if (limites.isValid()) {
      const origen = props.journey
        ? puntos.get(props.journey.origin.trim().toLocaleLowerCase('es'))
        : null
      const destino = props.journey
        ? puntos.get(props.journey.destination.trim().toLocaleLowerCase('es'))
        : null

      if (origen && destino) {
        mapa.fitBounds(L.latLngBounds(origen, destino).pad(0.3), { maxZoom: 17 })
      } else {
        mapa.fitBounds(limites.pad(0.18), { maxZoom: 15 })
      }
      estado.value = avisoPuntoEspera || (fallidos.length
        ? 'Algunos puntos no se ubicaron correctamente.'
        : 'Recorridos aproximados calculados con OpenStreetMap.')
    } else {
      estado.value = fallidos[0] || 'No se encontraron los puntos de este recorrido.'
    }
  } finally {
    if (solicitud === solicitudActual) cargando.value = false
  }
}

function encuadrarRecorridos() {
  const limites = capaRutas?.getBounds()
  if (limites?.isValid()) mapa.fitBounds(limites.pad(0.12), { maxZoom: 15 })
}

function centrarEnUbicacion(latitud, longitud) {
  if (!mapa || !capaRutas) return
  const punto = [latitud, longitud]
  mapa.setView(punto, 15)
  L.circleMarker(punto, {
    radius: 8,
    color: '#fff',
    weight: 3,
    fillColor: '#1878cf',
    fillOpacity: 1,
  })
    .bindPopup('Tu ubicación')
    .addTo(capaRutas)
    .openPopup()
}

defineExpose({ centrarEnUbicacion })

onMounted(() => {
  mapa = L.map(container.value, {
    zoomControl: true,
    scrollWheelZoom: true,
    touchZoom: true,
    doubleClickZoom: true,
    zoomSnap: 0.5,
    minZoom: 12,
    maxZoom: 19,
  }).setView(centroPopayan, 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    maxNativeZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa)
  capaRutas = L.featureGroup().addTo(mapa)
  dibujarRutas()
  requestAnimationFrame(() => mapa?.invalidateSize())
})

watch([() => props.segments, () => props.journey], dibujarRutas, { deep: true })

onBeforeUnmount(() => {
  solicitudActual += 1
  controlador?.abort()
  mapa?.remove()
})
</script>

<template>
  <section class="osm-card" aria-label="Mapa de alternativas">
    <div class="osm-heading">
      <div>
        <p>MAPA DE RECORRIDOS · POPAYÁN</p>
        <h3>{{ journey ? 'Ruta completa y tu destino' : 'Rutas disponibles' }}</h3>
      </div>
      <span class="osm-live-dot" aria-label="Mapa OpenStreetMap"></span>
    </div>
    <div class="osm-map-frame">
      <div ref="container" class="osm-map" role="application" aria-label="Mapa interactivo de OpenStreetMap"></div>
      <button
        v-if="journey && segments.length"
        class="osm-fit-control"
        type="button"
        @click="encuadrarRecorridos"
      >
        Ver recorridos completos
      </button>
    </div>
    <p v-if="journey" class="osm-trip-summary">
      <span class="osm-wait-point osm-wait-point-summary" aria-hidden="true"></span>
      <strong>Espera el bus cerca de:</strong> {{ journey.origin }}
      <span class="osm-trip-arrow" aria-hidden="true">→</span>
      <span class="osm-waypoint-badge osm-waypoint-destination" aria-hidden="true">B</span>
      <strong>Bájate en:</strong> {{ journey.destination }}
      <span v-if="showInstructions && transferencias.length" class="osm-trip-transfer">
        <span class="osm-waypoint-badge osm-waypoint-transfer" aria-hidden="true">T</span>
        Cambia de bus en {{ transferencias.join(', ') }}
      </span>
    </p>
    <p v-if="journey" class="osm-map-key">
      <template v-if="showInstructions">Punto negro = espera el bus · T = transbordo · B = destino</template>
      <template v-else>Punto negro = espera el bus · B = destino</template>
    </p>
    <p class="osm-status" role="status" aria-live="polite">
      <span v-if="cargando" class="osm-spinner" aria-hidden="true"></span>
      {{ estado }}
    </p>
    <ul v-if="segments.length" class="osm-legend" aria-label="Rutas y empresas de transporte">
      <li v-for="segment in segments" :key="`${segment.routeId}-${segment.legIndex}-${segment.codigo}`">
        <span
          :class="['osm-legend-line', { 'osm-legend-line-dashed': obtenerPatronRuta(segment) }]"
          :style="{ '--route-color': segment.color }"
          aria-hidden="true"
        ></span>
        <span class="osm-legend-copy">
          <strong>{{ segment.codigo }} · {{ segment.empresa }}</strong>
          <small>{{ segment.origen }} → {{ segment.destino }}</small>
        </span>
      </li>
    </ul>
    <p class="osm-attribution">
      Trazado estimado, no ruta oficial · © OpenStreetMap contributors
    </p>
  </section>
</template>

<style>
.osm-card {
  min-width: 0;
  overflow: hidden;
  border: 1px solid #e6eaf1;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 12px 30px rgba(24, 42, 75, 0.07);
}

.osm-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.1rem 0.75rem;
}

.osm-heading p {
  color: #7887a2;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.osm-heading h3 {
  margin-top: 0.2rem;
  color: #1d2b48;
  font-size: 0.95rem;
}

.osm-live-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #51ad83;
  box-shadow: 0 0 0 4px #eaf7f0;
}

.osm-map {
  z-index: 0;
  width: 100%;
  height: 390px;
  background: #edf2f7;
}

.osm-map-frame {
  position: relative;
}

.osm-fit-control {
  position: absolute;
  z-index: 500;
  top: 0.65rem;
  right: 0.65rem;
  min-height: 36px;
  padding: 0.45rem 0.7rem;
  border: 1px solid #dce5ef;
  border-radius: 9px;
  background: #fff;
  color: #17385c;
  font: inherit;
  font-size: 0.68rem;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.16);
  cursor: pointer;
}

.osm-waypoint-icon {
  border: 0;
  background: transparent;
}

.osm-waypoint-badge {
  display: inline-grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border: 3px solid #fff;
  border-radius: 50%;
  color: #fff;
  font-size: 0.78rem;
  font-weight: 900;
  box-shadow: 0 2px 9px rgba(15, 23, 42, 0.35);
}

.osm-waypoint-origin {
  background: #15803d;
}

.osm-wait-point {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 3px solid #fff;
  border-radius: 50%;
  background: #111827;
  box-shadow: 0 2px 9px rgba(15, 23, 42, 0.45);
}

.osm-wait-point-summary {
  flex: 0 0 18px;
}

.osm-waypoint-transfer {
  background: #d97706;
}

.osm-waypoint-destination {
  background: #dc2626;
}

.osm-waypoint-tooltip {
  padding: 0.28rem 0.48rem;
  border: 0;
  border-radius: 7px;
  color: #18395d;
  font-size: 0.7rem;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.2);
}

.osm-waypoint-tooltip::before {
  display: none;
}

.osm-trip-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  padding: 0.7rem 1rem 0.15rem;
  color: #334155;
  font-size: 0.72rem;
}

.osm-trip-summary .osm-waypoint-badge {
  width: 21px;
  height: 21px;
  border: 0;
  font-size: 0.65rem;
  box-shadow: none;
}

.osm-trip-arrow {
  color: #8a98ab;
  font-weight: 900;
}

.osm-trip-transfer {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-left: 0.35rem;
  color: #79500e;
  font-weight: 750;
}

.osm-map-key {
  padding: 0.15rem 1rem 0;
  color: #74849a;
  font-size: 0.65rem;
  line-height: 1.45;
}

.osm-status {
  display: flex;
  min-height: 36px;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem 0;
  color: #697891;
  font-size: 0.72rem;
  line-height: 1.45;
}

.osm-spinner {
  flex: 0 0 14px;
  width: 14px;
  height: 14px;
  border: 2px solid #dfe7f6;
  border-top-color: #3764ca;
  border-radius: 50%;
  animation: osm-spin 0.8s linear infinite;
}

.osm-legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.45rem 0.85rem;
  margin: 0;
  padding: 0.6rem 1rem 0.25rem;
  list-style: none;
}

.osm-legend li {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: #53627a;
  font-size: 0.67rem;
}

.osm-legend-line {
  width: 27px;
  height: 0;
  flex: 0 0 27px;
  border-top: 5px solid var(--route-color);
  border-radius: 99px;
}

.osm-legend-line-dashed {
  border-top-style: dashed;
}

.osm-legend-copy {
  display: grid;
  min-width: 0;
  gap: 0.1rem;
}

.osm-legend-copy strong {
  color: #40546c;
  font-size: 0.67rem;
}

.osm-legend-copy small {
  overflow: hidden;
  color: #8390a0;
  font-size: 0.62rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.osm-attribution {
  padding: 0.5rem 1rem 0.75rem;
  color: #8b95a6;
  font-size: 0.61rem;
}

@keyframes osm-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 620px) {
  .osm-map {
    height: 320px;
  }
}
</style>
