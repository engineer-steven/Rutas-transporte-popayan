<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, LocateFixed } from '@lucide/vue'
import OpenStreetMapRoutes from '@/components/maps/OpenStreetMapRoutes.vue'
import { buscarRutasLocales, PASSENGER_ROUTES } from '@/data/passengerRoutes'
import { usePasajeroStore } from '@/stores/pasajero'

const route = useRoute()
const pasajero = usePasajeroStore()
const map = ref(null)
const locationError = ref('')
const origen = computed(() => String(route.query.origin || ''))
const destino = computed(() => String(route.query.destination || ''))

const alternatives = computed(() =>
  origen.value && destino.value
    ? buscarRutasLocales(origen.value, destino.value)
    : PASSENGER_ROUTES,
)
const segments = computed(() =>
  alternatives.value.flatMap((item) => {
    const legs = item.segmentRoutes || [item]
    return legs.map((leg) => ({
      codigo: item.segmentRoutes ? leg.code : item.code,
      empresa: leg.company,
      origen: leg.stops[0],
      destino: leg.stops.at(-1),
      stops: leg.stops,
      color: leg.color,
    }))
  }),
)

function usarUbicacion() {
  locationError.value = ''
  if (!navigator.geolocation) {
    locationError.value = 'Tu navegador no admite ubicación.'
    return
  }
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => map.value?.centrarEnUbicacion(coords.latitude, coords.longitude),
    () => {
      locationError.value = 'No pudimos obtener tu ubicación. Revisa los permisos del navegador.'
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
  )
}
</script>

<template>
  <section class="passenger-screen passenger-map-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">TRANSPORTE URBANO · POPAYÁN</p>
        <h1>Mapa de rutas</h1>
        <p>Explora recorridos y paraderos de referencia.</p>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'inicio' }">
        <ArrowLeft :size="17" aria-hidden="true" /> Inicio
      </RouterLink>
    </header>

    <section class="passenger-full-map passenger-surface">
      <OpenStreetMapRoutes ref="map" :segments="segments" />
      <button
        class="passenger-map-location-button"
        type="button"
        aria-label="Centrar mapa en mi ubicación"
        @click="usarUbicacion"
      >
        <LocateFixed :size="19" aria-hidden="true" />
      </button>
    </section>
    <p v-if="locationError" class="passenger-inline-error" role="alert">{{ locationError }}</p>

    <section v-if="!alternatives.length" class="passenger-surface passenger-map-empty" role="status">
      <strong>No encontramos rutas para ese recorrido.</strong>
      <RouterLink :to="{ name: 'buscar', query: { origin: origen, destination: destino } }">
        Cambiar origen o destino
      </RouterLink>
    </section>

    <section v-else class="passenger-map-alternatives" aria-label="Rutas alternativas">
      <h2>{{ origen && destino ? `${origen} → ${destino}` : 'Rutas disponibles en Popayán' }}</h2>
      <article
        v-for="item in alternatives"
        :key="item.id"
        class="passenger-map-route-preview passenger-surface"
      >
        <div class="passenger-map-route-symbol" :style="{ '--route-color': item.color }">
          {{ item.code }}
        </div>
        <div class="passenger-map-route-copy">
          <strong>{{ item.name }}</strong>
          <span>{{ item.company }} · {{ item.stops.join(' · ') }}</span>
        </div>
        <span v-if="pasajero.esPlus" class="passenger-map-route-duration">
          ~{{ item.duration }} min · {{ item.transfers }} transbordos
        </span>
        <RouterLink
          v-else
          class="passenger-map-route-duration passenger-map-plus-link"
          :to="{ name: 'planes', query: { feature: 'tiempos' } }"
        >
          Ver tiempos con Plus
        </RouterLink>
        <RouterLink
          class="passenger-primary-button"
          :to="{
            name: 'detalle',
            params: { id: item.id },
            query: { origin: origen || undefined, destination: destino || undefined },
          }"
        >
          Ver detalles <span aria-hidden="true">→</span>
        </RouterLink>
      </article>
    </section>
    <p class="passenger-demo-disclaimer">
      Barrios y ubicaciones basados en OpenStreetMap. Los recorridos son de demostración y no
      representan rutas oficiales de buses.
    </p>
  </section>
</template>

<style>
.passenger-full-map {
  position: relative;
  padding: 0.35rem;
}

.passenger-full-map .osm-card {
  border: 0;
  box-shadow: none;
}

.passenger-full-map .osm-map {
  height: min(57vh, 500px);
  min-height: 310px;
}

.passenger-map-location-button {
  position: absolute;
  z-index: 450;
  right: 1rem;
  bottom: 4.8rem;
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid #d9e3ed;
  border-radius: 12px;
  background: #fff;
  color: #2469a1;
  box-shadow: 0 3px 12px rgba(21, 51, 79, 0.16);
  cursor: pointer;
}

.passenger-map-route-preview {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.8rem;
  padding: 0.9rem;
}

.passenger-map-alternatives {
  display: grid;
  gap: 0.7rem;
  margin-top: 1rem;
}

.passenger-map-alternatives h2 {
  color: #18395d;
  font-size: 1rem;
}

.passenger-map-empty {
  display: grid;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 1rem;
  color: #536b84;
}

.passenger-map-empty a {
  color: #17649d;
  font-size: 0.8rem;
  font-weight: 750;
}

.passenger-map-route-symbol {
  padding: 0.45rem 0.62rem;
  border-radius: 9px;
  background: color-mix(in srgb, var(--route-color) 12%, white);
  color: var(--route-color);
  font-size: 0.75rem;
  font-weight: 850;
}

.passenger-map-route-copy {
  display: grid;
  min-width: 0;
  gap: 0.15rem;
}

.passenger-map-route-copy strong {
  color: #1b385b;
  font-size: 0.81rem;
}

.passenger-map-route-copy span {
  color: #73829a;
  font-size: 0.68rem;
}

.passenger-map-route-duration {
  color: #405975;
  font-size: 0.73rem;
  font-weight: 800;
}

.passenger-map-plus-link {
  text-decoration: none;
}

.passenger-map-plus-link:hover {
  color: #17649d;
  text-decoration: underline;
}

.passenger-map-route-preview .passenger-primary-button {
  grid-column: 1 / -1;
}

@media (max-width: 600px) {
  .passenger-map-route-preview {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .passenger-map-route-duration,
  .passenger-map-route-preview .passenger-primary-button {
    grid-column: 1 / -1;
  }
}
</style>
