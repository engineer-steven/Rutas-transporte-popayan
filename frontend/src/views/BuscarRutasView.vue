<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowDownUp,
  ArrowLeft,
  ArrowRight,
  Clock3,
  Footprints,
  LocateFixed,
  MapPinned,
  Search,
} from '@lucide/vue'
import LocationAutocomplete from '@/components/passenger/LocationAutocomplete.vue'
import PassengerRouteSchematic from '@/components/passenger/PassengerRouteSchematic.vue'
import OpenStreetMapRoutes from '@/components/maps/OpenStreetMapRoutes.vue'
import {
  buscarRutasLocales,
  PASSENGER_PLACE_DESCRIPTIONS,
  POPAYAN_LOCATIONS,
} from '@/data/passengerRoutes'
import { nearestPopayanNeighborhood } from '@/data/popayanPlaces'
import { usePasajeroStore } from '@/stores/pasajero'

const route = useRoute()
const router = useRouter()
const pasajero = usePasajeroStore()
const origin = ref('')
const destination = ref('')
const searched = ref(false)
const results = ref([])
const error = ref('')
const locating = ref(false)

const queryLabel = computed(() =>
  origin.value && destination.value ? `${origin.value} → ${destination.value}` : '',
)
const journey = computed(() =>
  origin.value && destination.value
    ? { origin: origin.value, destination: destination.value }
    : null,
)
const routeSegments = computed(() =>
  results.value.flatMap((item) => {
    const legs = item.segmentRoutes || [item]
    return legs.map((leg, legIndex) => ({
      routeId: item.id,
      routeCode: item.code,
      codigo: item.segmentRoutes ? leg.code : item.code,
      empresa: leg.company,
      origen: (leg.fullStops || item.fullStops || leg.stops)[0],
      destino: (leg.fullStops || item.fullStops || leg.stops).at(-1),
      stops: leg.fullStops || item.fullStops || leg.stops,
      journeyStops: leg.stops,
      color: leg.color,
      legIndex,
      legCount: legs.length,
    }))
  }),
)

function buscar() {
  error.value = ''
  if (!origin.value.trim() || !destination.value.trim()) {
    error.value = 'Escribe el origen y el destino para buscar rutas.'
    return
  }
  if (origin.value.trim().toLocaleLowerCase('es') === destination.value.trim().toLocaleLowerCase('es')) {
    error.value = 'El origen y el destino deben ser diferentes.'
    return
  }
  results.value = buscarRutasLocales(origin.value, destination.value)
  searched.value = true
  if (!results.value.length) {
    error.value = 'No encontramos una ruta de ejemplo. Prueba con un punto de referencia cercano.'
  }
}

function intercambiar() {
  const previousOrigin = origin.value
  origin.value = destination.value
  destination.value = previousOrigin
  if (origin.value && destination.value) buscar()
}

function usarUbicacionActual() {
  error.value = ''
  if (!navigator.geolocation) {
    error.value = 'Tu navegador no admite la ubicación actual.'
    return
  }

  locating.value = true
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      const nearest = nearestPopayanNeighborhood(coords.latitude, coords.longitude)
      if (!nearest) {
        error.value = 'Tu ubicación parece estar fuera de Popayán.'
        locating.value = false
        return
      }

      origin.value = nearest
      error.value = `Punto de partida aproximado: ${origin.value}`
      locating.value = false
    },
    (locationError) => {
      error.value = locationError.code === locationError.PERMISSION_DENIED
        ? 'Permite el acceso a tu ubicación para usar esta opción.'
        : 'No se pudo obtener tu ubicación.'
      locating.value = false
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
  )
}

function verDetalle(routeOption) {
  router.push({
    name: 'detalle',
    params: { id: routeOption.id },
    query: { origin: origin.value, destination: destination.value },
  })
}

onMounted(() => {
  origin.value = typeof route.query.origin === 'string' ? route.query.origin : ''
  destination.value = typeof route.query.destination === 'string' ? route.query.destination : ''
  if (origin.value && destination.value) buscar()
})
</script>

<template>
  <section class="passenger-screen passenger-search-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">POPAYÁN · ENCUENTRA TU RECORRIDO</p>
        <h1>Buscar rutas</h1>
        <p>Indica desde dónde sales y a dónde quieres llegar.</p>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'inicio' }">
        <ArrowLeft :size="17" aria-hidden="true" /> Inicio
      </RouterLink>
    </header>

    <section class="passenger-route-search passenger-surface">
      <form @submit.prevent="buscar">
        <LocationAutocomplete
          id="search-origin"
          v-model="origin"
          label="Origen"
          placeholder="Barrio o punto de referencia"
          :suggestions="POPAYAN_LOCATIONS"
          :descriptions="PASSENGER_PLACE_DESCRIPTIONS"
        />
        <button
          class="passenger-swap-button"
          type="button"
          aria-label="Intercambiar origen y destino"
          @click="intercambiar"
        >
          <ArrowDownUp :size="18" aria-hidden="true" />
        </button>
        <LocationAutocomplete
          id="search-destination"
          v-model="destination"
          label="Destino"
          placeholder="Barrio o punto de referencia"
          :suggestions="POPAYAN_LOCATIONS"
          :descriptions="PASSENGER_PLACE_DESCRIPTIONS"
          destination
        />
        <button class="passenger-primary-button passenger-search-submit" type="submit">
          <Search :size="18" aria-hidden="true" /> Buscar rutas
        </button>
      </form>
      <button
        class="passenger-search-location"
        type="button"
        :disabled="locating"
        @click="usarUbicacionActual"
      >
        <LocateFixed :size="16" aria-hidden="true" />
        {{ locating ? 'Buscando ubicación…' : 'Usar mi ubicación actual' }}
      </button>
    </section>

    <p v-if="error" :class="['passenger-inline-notice', { 'passenger-inline-error': results.length === 0 && searched }]" role="status">
      {{ error }}
    </p>

    <section v-if="results.length" class="passenger-search-results" aria-live="polite">
      <header class="passenger-search-results-heading">
        <div>
          <p>RUTAS DISPONIBLES</p>
          <h2>{{ queryLabel }}</h2>
        </div>
        <span>{{ results.length }} {{ results.length === 1 ? 'opción' : 'opciones' }}</span>
      </header>

      <section class="passenger-search-map" aria-label="Mapa de las rutas">
        <OpenStreetMapRoutes
          :segments="routeSegments"
          :journey="journey"
          :show-instructions="pasajero.esPlus"
        />
      </section>

      <section v-if="pasajero.esPlus" class="passenger-search-map" aria-label="Pasos para tomar cada ruta">
        <PassengerRouteSchematic :segments="routeSegments" :journey="journey" />
      </section>
      <RouterLink
        v-else
        class="passenger-plus-guide-prompt"
        :to="{ name: 'planes', query: { feature: 'guia-ruta' } }"
      >
        <strong>¿Quieres instrucciones paso a paso?</strong>
        <span>Consulta dónde subir y bajar y cómo hacer transbordo con Plus.</span>
        <span class="passenger-plus-guide-action">Conocer Plus <ArrowRight :size="15" aria-hidden="true" /></span>
      </RouterLink>

      <article v-for="item in results" :key="item.id" class="passenger-search-result passenger-surface">
        <div class="passenger-result-route-mark" :style="{ '--route-color': item.color }">
          <span>{{ item.code }}</span>
          <small>{{ item.company }}</small>
        </div>
        <div v-if="pasajero.esPlus" class="passenger-result-facts">
          <span><Clock3 :size="15" aria-hidden="true" /> ~{{ item.duration }} min</span>
          <span><Footprints :size="15" aria-hidden="true" /> {{ item.transfers }} transbordos</span>
        </div>
        <RouterLink
          v-else
          class="passenger-result-plus-hint"
          :to="{ name: 'planes', query: { feature: 'tiempos' } }"
        >
          Activa Plus para ver tiempos y transbordos
        </RouterLink>
        <div v-if="item.segmentRoutes && pasajero.esPlus" class="passenger-route-legs" aria-label="Pasos del recorrido">
          <template v-for="(leg, index) in item.segmentRoutes" :key="leg.code">
            <div class="passenger-route-leg" :style="{ '--route-color': leg.color }">
            <span>Tramo {{ index + 1 }}</span>
              <strong>{{ leg.code }} · {{ leg.company }}</strong>
            <small>Sube en: {{ leg.stops[0] }}</small>
            <small>Bájate en: {{ leg.stops.at(-1) }}</small>
            </div>
            <p v-if="index < item.segmentRoutes.length - 1" class="passenger-route-transfer">
            Cambia de bus aquí: <strong>{{ item.interchange }}</strong>
            </p>
          </template>
        </div>
        <p v-else-if="item.segmentRoutes" class="passenger-result-stops">
          {{ item.segmentRoutes.map((leg) => leg.code).join(' → ') }}
        </p>
        <p v-else class="passenger-result-stops">
          <MapPinned :size="15" aria-hidden="true" />
          Directo · {{ item.stops[0] }} → {{ item.stops.at(-1) }} · Sin transbordos
        </p>
        <div class="passenger-result-actions">
          <RouterLink
            class="passenger-secondary-button"
            :to="{ name: 'mapa', query: { route: item.id, origin: origin, destination: destination } }"
          >
            Ver en el mapa
          </RouterLink>
          <button class="passenger-primary-button" type="button" @click="verDetalle(item)">
            Ver detalles de la ruta <ArrowRight :size="16" aria-hidden="true" />
          </button>
        </div>
      </article>
    </section>

    <section v-else-if="searched && !results.length" class="passenger-surface passenger-search-empty">
      <p>Elige otro punto de referencia o barrio cercano.</p>
    </section>

    <p class="passenger-demo-disclaimer">
      Recorridos de demostración, no rutas oficiales. Confirma la información antes de viajar.
    </p>
  </section>
</template>

<style>
.passenger-route-search {
  padding: 0.85rem;
}

.passenger-route-search form {
  position: relative;
  display: grid;
  gap: 0.5rem;
  overflow: visible;
}

.passenger-swap-button {
  position: absolute;
  z-index: 3;
  top: 56px;
  right: 0.65rem;
  display: grid;
  width: 35px;
  height: 35px;
  place-items: center;
  border: 1px solid #dfe8f3;
  border-radius: 50%;
  background: #fff;
  color: #28618c;
  box-shadow: 0 3px 8px rgba(24, 55, 84, 0.08);
  cursor: pointer;
}

.passenger-search-submit {
  margin-top: 0.45rem;
}

.passenger-search-location {
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  gap: 0.4rem;
  margin: 0.65rem 0.1rem 0;
  padding: 0.35rem 0.6rem;
  border: 0;
  border-radius: 9px;
  background: #f0f7fc;
  color: #17649d;
  font: inherit;
  font-size: 0.7rem;
  font-weight: 750;
  cursor: pointer;
}

.passenger-search-location:disabled {
  opacity: 0.65;
  cursor: wait;
}

.passenger-search-results {
  display: grid;
  gap: 0.75rem;
  margin-top: 1.4rem;
}

.passenger-search-results-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.8rem;
  margin-bottom: 0.1rem;
}

.passenger-search-results-heading > div > p {
  color: #7587a0;
  font-size: 0.63rem;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.passenger-search-results-heading h2 {
  margin-top: 0.2rem;
  color: #17385c;
  font-size: clamp(1.05rem, 3vw, 1.35rem);
}

.passenger-search-results-heading > span {
  color: #77869b;
  font-size: 0.7rem;
}

.passenger-search-result {
  padding: 1rem;
}

.passenger-result-route-mark {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.passenger-result-route-mark > span {
  padding: 0.34rem 0.52rem;
  border-radius: 8px;
  background: color-mix(in srgb, var(--route-color) 12%, white);
  color: var(--route-color);
  font-size: 0.75rem;
  font-weight: 850;
}

.passenger-result-route-mark small {
  color: #6d7d93;
  font-size: 0.74rem;
}

.passenger-result-facts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  margin-top: 0.85rem;
}

.passenger-result-facts span {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: #435976;
  font-size: 0.72rem;
}

.passenger-result-facts svg {
  color: #2874a9;
}

.passenger-result-plus-hint {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  margin-top: 0.75rem;
  padding: 0.42rem 0.65rem;
  border: 1px solid #d6eee7;
  border-radius: 999px;
  background: #f0faf7;
  color: #147c6c;
  font-size: 0.68rem;
  font-weight: 750;
  text-decoration: none;
}

.passenger-result-plus-hint:hover {
  border-color: #9ed8ca;
  background: #e7f7f2;
}

.passenger-result-stops {
  display: flex;
  align-items: flex-start;
  gap: 0.35rem;
  margin-top: 0.65rem;
  color: #77869b;
  font-size: 0.7rem;
  line-height: 1.55;
}

.passenger-result-stops svg {
  flex: 0 0 auto;
  color: #138c82;
}

.passenger-result-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.85rem;
}

.passenger-result-actions > * {
  flex: 1 1 170px;
}

.passenger-search-empty {
  margin-top: 1rem;
  padding: 1rem;
  color: #687a91;
  font-size: 0.78rem;
}

.passenger-demo-disclaimer {
  margin-top: 1rem;
  color: #8793a4;
  font-size: 0.67rem;
  line-height: 1.5;
}

</style>
