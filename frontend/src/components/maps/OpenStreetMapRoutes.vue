<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { OSM_POPAYAN_COORDINATES } from '@/data/popayanPlaces'

const props = defineProps({
  segments: {
    type: Array,
    default: () => [],
  },
})

const container = ref(null)
const cargando = ref(false)
const estado = ref('Busca un recorrido para ver las alternativas en el mapa.')
let mapa
let capaRutas
let solicitudActual = 0
let controlador
let ultimaGeocodificacion = 0

const coordenadasCache = new Map()
const coordenadasConocidas = new Map(OSM_POPAYAN_COORDINATES)
coordenadasConocidas.set('terminal de transporte', [2.4511705, -76.6079814])
coordenadasConocidas.set('cajete', [2.4781725, -76.6750103])
const centroPopayan = [2.4448, -76.6147]

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
  coordenadasCache.set(clave, punto)
  return punto
}

async function trazarSegmento(segmento, paraderos, signal) {
  const coordenadas = paraderos.map(([latitud, longitud]) => `${longitud},${latitud}`).join(';')
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

  const color = /^#[\da-f]{6}$/i.test(segmento.color) ? segmento.color : '#2865d8'
  L.polyline(
    puntos.map(([longitud, latitud]) => [latitud, longitud]),
    { color, weight: 5, opacity: 0.88, lineCap: 'round', lineJoin: 'round' },
  ).addTo(capaRutas)

  L.circleMarker(paraderos[0], {
    radius: 6,
    color: '#fff',
    weight: 2,
    fillColor: color,
    fillOpacity: 1,
  }).addTo(capaRutas)

  L.circleMarker(paraderos[paraderos.length - 1], {
    radius: 6,
    color: '#fff',
    weight: 2,
    fillColor: color,
    fillOpacity: 1,
  }).addTo(capaRutas)
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
    estado.value = 'Busca un recorrido para ver las alternativas en el mapa.'
    mapa.setView(centroPopayan, 13)
    return
  }

  cargando.value = true
  estado.value = 'Ubicando paraderos y trazando alternativas sobre OpenStreetMap…'
  const puntos = new Map()
  const fallidos = []

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

    for (const segmento of props.segments) {
      if (solicitud !== solicitudActual) return
      const paraderos = segmento.stops || [segmento.origen, segmento.destino]
      const puntosRuta = paraderos
        .map((lugar) => puntos.get(lugar.trim().toLocaleLowerCase('es')))
        .filter(Boolean)
      if (puntosRuta.length < 2) continue

      try {
        await trazarSegmento(segmento, puntosRuta, signal)
      } catch (error) {
        if (signal.aborted) return
        fallidos.push(error.message)
      }
    }

    if (solicitud !== solicitudActual) return
    const limites = capaRutas.getBounds()
    if (limites.isValid()) {
      mapa.fitBounds(limites.pad(0.18), { maxZoom: 15 })
      estado.value = fallidos.length
        ? 'Se muestran los trazos disponibles; algunos lugares no pudieron ubicarse.'
        : 'Alternativas aproximadas calculadas sobre calles de OpenStreetMap.'
    } else {
      estado.value = fallidos[0] || 'No pudimos ubicar los puntos de este recorrido.'
    }
  } finally {
    if (solicitud === solicitudActual) cargando.value = false
  }
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
  mapa = L.map(container.value, { scrollWheelZoom: false }).setView(centroPopayan, 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapa)
  capaRutas = L.featureGroup().addTo(mapa)
  dibujarRutas()
  requestAnimationFrame(() => mapa?.invalidateSize())
})

watch(() => props.segments, dibujarRutas, { deep: true })

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
        <p>MAPA DE RECORRIDOS</p>
        <h3>Alternativas en Popayán</h3>
      </div>
      <span class="osm-live-dot" aria-label="Mapa OpenStreetMap"></span>
    </div>
    <div ref="container" class="osm-map" role="application" aria-label="Mapa interactivo de OpenStreetMap"></div>
    <p class="osm-status" role="status" aria-live="polite">
      <span v-if="cargando" class="osm-spinner" aria-hidden="true"></span>
      {{ estado }}
    </p>
    <ul v-if="segments.length" class="osm-legend" aria-label="Empresas por color">
      <li v-for="segment in segments" :key="`${segment.codigo}-${segment.origen}-${segment.destino}`">
        <span :style="{ backgroundColor: segment.color }" aria-hidden="true"></span>
        {{ segment.codigo }} · {{ segment.empresa }}
      </li>
    </ul>
    <p class="osm-attribution">
      Trazado vial estimado · Datos cartográficos © OpenStreetMap contributors
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
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 0.85rem;
  margin: 0;
  padding: 0.6rem 1rem 0.25rem;
  list-style: none;
}

.osm-legend li {
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  color: #53627a;
  font-size: 0.67rem;
}

.osm-legend li span {
  width: 9px;
  height: 9px;
  flex: 0 0 9px;
  border-radius: 50%;
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
