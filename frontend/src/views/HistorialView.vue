<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { ArrowLeft, ChartNoAxesColumn, Clock3, Trash2 } from '@lucide/vue'
import { usePasajeroStore } from '@/stores/pasajero'

const pasajero = usePasajeroStore()
const router = useRouter()

function borrarHistorial() {
  if (!pasajero.history.length) return
  if (!window.confirm('¿Quieres borrar todo el historial de viajes de este dispositivo?')) return
  pasajero.borrarHistorial()
}

function verViaje(trip) {
  router.push({
    name: 'detalle',
    params: { id: trip.routeId },
    query: { origin: trip.origin, destination: trip.destination },
  })
}

function fechaViaje(value) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}
</script>

<template>
  <section class="passenger-screen passenger-list-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">TUS RECORRIDOS RECIENTES</p>
        <h1>Historial de viajes</h1>
        <p>Consulta los viajes que registraste en esta demostración.</p>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'perfil' }">
        <ArrowLeft :size="17" aria-hidden="true" /> Perfil
      </RouterLink>
    </header>

    <template v-if="pasajero.esPlus">
      <div v-if="pasajero.history.length" class="passenger-history-list">
        <article
          v-for="trip in pasajero.history"
          :key="trip.id"
          class="passenger-history-row passenger-surface"
        >
          <span class="passenger-history-pin" aria-hidden="true"></span>
          <button class="passenger-history-copy" type="button" @click="verViaje(trip)">
            <strong>{{ trip.origin }} <span>→</span> {{ trip.destination }}</strong>
            <small>{{ fechaViaje(trip.date) }} · {{ trip.routeCode }}</small>
          </button>
          <span class="passenger-history-duration"><Clock3 :size="14" /> {{ trip.duration }} min</span>
          <button
            class="passenger-icon-button"
            type="button"
            :aria-label="`Ver viaje ${trip.origin} a ${trip.destination}`"
            @click="verViaje(trip)"
          >
            <span aria-hidden="true">›</span>
          </button>
        </article>
        <div class="passenger-history-info">
          <ChartNoAxesColumn :size="21" aria-hidden="true" />
          <p>Tu historial te ayuda a encontrar los recorridos que más utilizas.</p>
          <button class="passenger-danger-button" type="button" @click="borrarHistorial">
            <Trash2 :size="16" aria-hidden="true" /> Borrar historial
          </button>
        </div>
      </div>
      <section v-else class="passenger-surface passenger-empty-state">
        <Clock3 :size="40" aria-hidden="true" />
        <h2>Aún no hay viajes en tu historial</h2>
        <p>Registra un viaje desde el detalle de una ruta para encontrarlo aquí.</p>
        <RouterLink class="passenger-primary-button" :to="{ name: 'buscar' }">Buscar una ruta</RouterLink>
      </section>
    </template>

    <section v-else class="passenger-surface passenger-feature-lock">
      <Clock3 :size="34" aria-hidden="true" />
      <h2>Tu historial está incluido en Plus</h2>
      <p>Activa la demo Plus para registrar y volver a consultar tus viajes.</p>
      <RouterLink class="passenger-primary-button" :to="{ name: 'planes' }">Conocer los planes</RouterLink>
    </section>
  </section>
</template>

<style>
.passenger-history-list {
  display: grid;
  gap: 0.55rem;
}

.passenger-history-row {
  display: grid;
  grid-template-columns: 19px minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.55rem;
  padding: 0.75rem;
}

.passenger-history-pin {
  width: 12px;
  height: 12px;
  border: 3px solid #126fc1;
  border-radius: 50%;
}

.passenger-history-copy {
  display: grid;
  min-width: 0;
  gap: 0.16rem;
  border: 0;
  background: none;
  text-align: left;
  cursor: pointer;
}

.passenger-history-copy strong {
  overflow: hidden;
  color: #203958;
  font-size: 0.73rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.passenger-history-copy strong span {
  color: #7d8ca0;
}

.passenger-history-copy small {
  color: #7c899d;
  font-size: 0.62rem;
}

.passenger-history-duration {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #556b85;
  font-size: 0.64rem;
  white-space: nowrap;
}

.passenger-history-info {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.35rem;
  padding: 0.85rem;
  border: 1px solid #dfeafa;
  border-radius: 13px;
  background: #eef5ff;
  color: #2874a9;
}

.passenger-history-info p {
  color: #486580;
  font-size: 0.68rem;
  line-height: 1.45;
}

.passenger-history-info .passenger-danger-button {
  min-height: 35px;
  padding: 0.35rem 0.55rem;
  font-size: 0.64rem;
}

@media (max-width: 540px) {
  .passenger-history-info {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .passenger-history-info .passenger-danger-button {
    grid-column: 1 / -1;
    justify-self: end;
  }
}
</style>
