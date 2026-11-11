<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Check, Clock3, Crown, Footprints, Heart, MapPin, Repeat2 } from '@lucide/vue'
import OpenStreetMapRoutes from '@/components/maps/OpenStreetMapRoutes.vue'
import { buscarRutasLocales, PASSENGER_ROUTES } from '@/data/passengerRoutes'
import { usePasajeroStore } from '@/stores/pasajero'

const route = useRoute()
const router = useRouter()
const pasajero = usePasajeroStore()
const notice = ref('')
const error = ref('')

const origin = computed(() => String(route.query.origin || ''))
const destination = computed(() => String(route.query.destination || ''))
const selectedRoute = computed(() => {
  const foundBySearch = buscarRutasLocales(origin.value, destination.value).find(
    (item) => item.id === String(route.params.id),
  )
  return foundBySearch || PASSENGER_ROUTES.find((item) => item.id === String(route.params.id)) || null
})
const segments = computed(() => {
  if (!selectedRoute.value) return []
  const legs = selectedRoute.value.segmentRoutes || [selectedRoute.value]
  return legs.map((leg) => ({
    codigo: leg.code,
    empresa: leg.company,
    origen: leg.stops[0],
    destino: leg.stops.at(-1),
    stops: leg.stops,
    color: leg.color,
  }))
})

function guardarFavorito() {
  if (!pasajero.esPlus) {
    router.push({ name: 'planes', query: { feature: 'favoritos' } })
    return
  }
  if (!selectedRoute.value) return
  try {
    pasajero.agregarFavorito({
      routeId: selectedRoute.value.id,
      routeCode: selectedRoute.value.code,
      title: selectedRoute.value.name,
      address: selectedRoute.value.stops.join(' · '),
      company: selectedRoute.value.company,
    })
    notice.value = pasajero.esFavorito(selectedRoute.value.id)
      ? 'Ruta guardada en tus favoritos.'
      : 'Esta ruta ya estaba en tus favoritos.'
    error.value = ''
  } catch (exception) {
    error.value = exception.message
  }
}

function guardarEnHistorial() {
  if (!pasajero.esPlus) {
    router.push({ name: 'planes', query: { feature: 'historial' } })
    return
  }
  if (!selectedRoute.value) return
  try {
    const now = new Date()
    pasajero.agregarViaje({
      routeId: selectedRoute.value.id,
      routeCode: selectedRoute.value.code,
      routeName: selectedRoute.value.name,
      company: selectedRoute.value.company,
      origin: origin.value || selectedRoute.value.stops[0],
      destination: destination.value || selectedRoute.value.stops.at(-1),
      duration: selectedRoute.value.duration,
      transfers: selectedRoute.value.transfers,
      date: now.toISOString(),
    })
    notice.value = 'Viaje de demostración agregado a tu historial.'
    error.value = ''
  } catch (exception) {
    error.value = exception.message
  }
}
</script>

<template>
  <section v-if="selectedRoute" class="passenger-screen passenger-detail-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">RECORRIDO DE TRANSPORTE</p>
        <h1>Detalle de ruta</h1>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'buscar', query: { origin, destination } }">
        <ArrowLeft :size="17" aria-hidden="true" /> Volver
      </RouterLink>
    </header>

    <article class="passenger-detail-route-header passenger-surface">
      <span class="passenger-detail-route-badge" :style="{ '--route-color': selectedRoute.color }">
        {{ selectedRoute.code }}
      </span>
      <div>
        <h2>{{ selectedRoute.name }}</h2>
        <p>{{ selectedRoute.company }} · {{ selectedRoute.via }}</p>
      </div>
      <RouterLink class="passenger-detail-map-link" :to="{ name: 'mapa', query: { route: selectedRoute.id } }">
        Ver mapa
      </RouterLink>
    </article>

    <section v-if="pasajero.esPlus" class="passenger-detail-metrics passenger-surface">
      <div><Footprints aria-hidden="true" /><span>Caminar<strong>{{ selectedRoute.walkingMinutes }} min</strong></span></div>
      <div><Clock3 aria-hidden="true" /><span>Tiempo estimado<strong>{{ selectedRoute.duration }} min</strong></span></div>
      <div><Repeat2 aria-hidden="true" /><span>Transbordos<strong>{{ selectedRoute.transfers }}</strong></span></div>
    </section>
    <RouterLink
      v-else
      class="passenger-detail-plus-prompt passenger-surface"
      :to="{ name: 'planes', query: { feature: 'tiempos' } }"
    >
      <Crown :size="19" aria-hidden="true" />
      <span><strong>Conoce el tiempo y los transbordos</strong><small>Información adicional disponible con Plus</small></span>
      <span aria-hidden="true">→</span>
    </RouterLink>

    <section class="passenger-detail-map passenger-surface">
      <OpenStreetMapRoutes :segments="segments" />
    </section>

    <section class="passenger-detail-stops passenger-surface">
      <h2>Paraderos principales</h2>
      <ol>
        <li v-for="(stop, index) in selectedRoute.stops" :key="stop">
          <span :class="{ 'passenger-stop-final': index === selectedRoute.stops.length - 1 }">
            <MapPin :size="16" aria-hidden="true" />
          </span>
          <strong>{{ stop }}</strong>
        </li>
      </ol>
    </section>

    <div class="passenger-detail-actions">
      <button class="passenger-primary-button" type="button" @click="guardarFavorito">
        <Heart :size="17" aria-hidden="true" />
        {{ pasajero.esFavorito(selectedRoute.id) ? 'Guardada en favoritos' : 'Guardar en favoritos' }}
      </button>
      <button class="passenger-secondary-button" type="button" @click="guardarEnHistorial">
        <Check :size="17" aria-hidden="true" /> Registrar viaje de prueba
      </button>
    </div>
    <p v-if="notice" class="passenger-inline-notice" role="status">{{ notice }}</p>
    <p v-if="error" class="passenger-inline-error" role="alert">{{ error }}</p>
  </section>
  <section v-else class="passenger-screen passenger-empty-state">
    <h1>No encontramos esa ruta</h1>
    <p>Vuelve a buscar un recorrido para ver sus detalles.</p>
    <RouterLink class="passenger-primary-button" :to="{ name: 'buscar' }">Buscar rutas</RouterLink>
  </section>
</template>

<style>
.passenger-detail-plus-prompt {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.9rem 1rem;
  color: #098774;
  text-decoration: none;
}

.passenger-detail-plus-prompt > span:nth-child(2) {
  display: grid;
  flex: 1;
  gap: 0.2rem;
}

.passenger-detail-plus-prompt strong {
  color: #244463;
  font-size: 0.78rem;
}

.passenger-detail-plus-prompt small {
  color: #72839a;
  font-size: 0.68rem;
}

.passenger-detail-route-header {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.7rem;
  padding: 0.9rem;
}

.passenger-detail-route-badge {
  padding: 0.43rem 0.62rem;
  border-radius: 9px;
  background: color-mix(in srgb, var(--route-color) 12%, white);
  color: var(--route-color);
  font-size: 0.78rem;
  font-weight: 850;
}

.passenger-detail-route-header h2 {
  color: #193958;
  font-size: 0.88rem;
}

.passenger-detail-route-header p {
  margin-top: 0.15rem;
  color: #76869a;
  font-size: 0.66rem;
}

.passenger-detail-map-link {
  color: #17669b;
  font-size: 0.7rem;
  font-weight: 750;
  text-decoration: none;
}

.passenger-detail-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.65rem;
  padding: 0.75rem 0.4rem;
}

.passenger-detail-metrics > div {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  min-width: 0;
  color: #2471a5;
}

.passenger-detail-metrics > div > svg {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
}

.passenger-detail-metrics > div span {
  display: grid;
  color: #728198;
  font-size: 0.57rem;
  line-height: 1.4;
}

.passenger-detail-metrics strong {
  color: #234465;
  font-size: 0.68rem;
}

.passenger-detail-map {
  margin-top: 0.65rem;
  padding: 0.3rem;
}

.passenger-detail-map .osm-card {
  border: 0;
  box-shadow: none;
}

.passenger-detail-map .osm-map {
  height: 245px;
}

.passenger-detail-stops {
  margin-top: 0.7rem;
  padding: 1rem;
}

.passenger-detail-stops h2 {
  color: #173a5d;
  font-size: 0.9rem;
}

.passenger-detail-stops ol {
  display: grid;
  gap: 0.65rem;
  margin-top: 0.8rem;
  list-style: none;
}

.passenger-detail-stops li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #435976;
  font-size: 0.75rem;
}

.passenger-detail-stops li > span {
  display: grid;
  width: 20px;
  height: 20px;
  place-items: center;
  border: 2px solid #126cc2;
  border-radius: 50%;
  color: #126cc2;
}

.passenger-detail-stops li > span.passenger-stop-final {
  border-color: #e35d42;
  color: #e35d42;
}

.passenger-detail-actions {
  display: grid;
  gap: 0.55rem;
  margin-top: 0.8rem;
}

@media (min-width: 640px) {
  .passenger-detail-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
