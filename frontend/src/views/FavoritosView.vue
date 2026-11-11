<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft, Heart, MapPin, Trash2 } from '@lucide/vue'
import { PASSENGER_ROUTES } from '@/data/passengerRoutes'
import { usePasajeroStore } from '@/stores/pasajero'

const pasajero = usePasajeroStore()
const router = useRouter()

function quitar(routeId) {
  pasajero.eliminarFavorito(routeId)
}

function verRuta(favorite) {
  const found = PASSENGER_ROUTES.find((route) => route.id === favorite.routeId)
  if (!found) return
  router.push({ name: 'detalle', params: { id: found.id } })
}
</script>

<template>
  <section class="passenger-screen passenger-list-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">TUS LUGARES GUARDADOS</p>
        <h1>Mis favoritos</h1>
        <p>Ten tus recorridos preferidos siempre a mano.</p>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'perfil' }">
        <ArrowLeft :size="17" aria-hidden="true" /> Perfil
      </RouterLink>
    </header>

    <template v-if="pasajero.esPlus">
      <div v-if="pasajero.favorites.length" class="passenger-saved-list">
        <article
          v-for="favorite in pasajero.favorites"
          :key="favorite.routeId"
          class="passenger-favorite-row passenger-surface"
        >
          <span class="passenger-favorite-pin"><MapPin :size="19" aria-hidden="true" /></span>
          <button class="passenger-favorite-copy" type="button" @click="verRuta(favorite)">
            <strong>{{ favorite.title }}</strong>
            <span>{{ favorite.address }}</span>
            <small>{{ favorite.routeCode }} · {{ favorite.company }}</small>
          </button>
          <button
            class="passenger-icon-button passenger-delete-favorite"
            type="button"
            :aria-label="`Eliminar ${favorite.title} de favoritos`"
            @click="quitar(favorite.routeId)"
          >
            <Trash2 :size="18" aria-hidden="true" />
          </button>
        </article>
      </div>
      <section v-else class="passenger-surface passenger-empty-state">
        <Heart :size="40" aria-hidden="true" />
        <h2>Guarda tus rutas favoritas</h2>
        <p>En el detalle de una ruta, toca “Guardar en favoritos” para encontrarla más rápido después.</p>
        <RouterLink class="passenger-primary-button" :to="{ name: 'buscar' }">Buscar rutas</RouterLink>
      </section>
    </template>

    <section v-else class="passenger-surface passenger-feature-lock">
      <Heart :size="34" aria-hidden="true" />
      <h2>Favoritos es parte de Plus</h2>
      <p>Activa la demo Plus para guardar recorridos y consultarlos cuando quieras.</p>
      <RouterLink class="passenger-primary-button" :to="{ name: 'planes' }">Conocer los planes</RouterLink>
    </section>
  </section>
</template>

<style>
.passenger-saved-list {
  display: grid;
  gap: 0.6rem;
}

.passenger-favorite-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 0.8rem;
}

.passenger-favorite-pin {
  display: grid;
  width: 37px;
  height: 37px;
  place-items: center;
  border-radius: 12px;
  background: #fff0e8;
  color: #ee762e;
}

.passenger-favorite-copy {
  display: grid;
  min-width: 0;
  gap: 0.14rem;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.passenger-favorite-copy strong {
  overflow: hidden;
  color: #203958;
  font-size: 0.77rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.passenger-favorite-copy span,
.passenger-favorite-copy small {
  overflow: hidden;
  color: #78879b;
  font-size: 0.64rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.passenger-icon-button {
  display: grid;
  width: 37px;
  height: 37px;
  place-items: center;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #396d9b;
  cursor: pointer;
}

.passenger-icon-button:hover {
  background: #fff0ef;
  color: #c1494e;
}

.passenger-feature-lock {
  display: grid;
  justify-items: center;
  gap: 0.55rem;
  padding: 2rem 1rem;
  text-align: center;
}

.passenger-feature-lock > svg {
  color: #2679b8;
}

.passenger-feature-lock h2 {
  color: #193958;
  font-size: 1.05rem;
}

.passenger-feature-lock p {
  max-width: 40ch;
  color: #78879b;
  font-size: 0.77rem;
  line-height: 1.55;
}
</style>
