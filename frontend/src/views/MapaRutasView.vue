<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@lucide/vue'
import PassengerRouteSchematic from '@/components/passenger/PassengerRouteSchematic.vue'
import OpenStreetMapRoutes from '@/components/maps/OpenStreetMapRoutes.vue'
import { buscarRutasLocales, PASSENGER_ROUTES } from '@/data/passengerRoutes'
import { usePasajeroStore } from '@/stores/pasajero'

const route = useRoute()
const pasajero = usePasajeroStore()
const origen = computed(() => String(route.query.origin || ''))
const destino = computed(() => String(route.query.destination || ''))
const routeId = computed(() => String(route.query.route || ''))
const journey = computed(() =>
  origen.value && destino.value
    ? { origin: origen.value, destination: destino.value }
    : null,
)

const alternatives = computed(() => {
  const routes = origen.value && destino.value
    ? buscarRutasLocales(origen.value, destino.value)
    : PASSENGER_ROUTES
  return routeId.value ? routes.filter((item) => item.id === routeId.value) : routes
})
const segments = computed(() =>
  alternatives.value.flatMap((item) => {
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
</script>

<template>
  <section class="passenger-screen passenger-map-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">TRANSPORTE URBANO · POPAYÁN</p>
        <h1>Guía de rutas</h1>
        <p>Consulta qué bus tomar y dónde hacer cada transbordo.</p>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'inicio' }">
        <ArrowLeft :size="17" aria-hidden="true" /> Inicio
      </RouterLink>
    </header>

    <section class="passenger-full-map">
      <OpenStreetMapRoutes
        :segments="segments"
        :journey="journey"
        :show-instructions="pasajero.esPlus"
      />
    </section>

    <section v-if="pasajero.esPlus" class="passenger-full-map">
      <PassengerRouteSchematic :segments="segments" :journey="journey" />
    </section>
    <RouterLink
      v-else
      class="passenger-plus-guide-prompt"
      :to="{ name: 'planes', query: { feature: 'guia-ruta' } }"
    >
      <strong>¿Quieres instrucciones paso a paso?</strong>
      <span>Consulta dónde subir y bajar y cómo hacer transbordo con Plus.</span>
      <span class="passenger-plus-guide-action">Conocer Plus <span aria-hidden="true">→</span></span>
    </RouterLink>

    <section v-if="!alternatives.length" class="passenger-surface passenger-map-empty" role="status">
      <strong>No encontramos esa ruta o recorrido.</strong>
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
          <span v-else-if="item.segmentRoutes">
            {{ item.segmentRoutes.map((leg) => leg.code).join(' → ') }}
          </span>
          <span v-else>{{ item.code }} · {{ item.company }} · Directo: {{ item.stops[0] }} → {{ item.stops.at(-1) }}</span>
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
  min-width: 0;
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

.passenger-map-route-copy > strong {
  color: #1b385b;
  font-size: 0.81rem;
}

.passenger-map-route-copy > span {
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
