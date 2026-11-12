<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  Clock3,
  Heart,
  LocateFixed,
  Map,
  MapPin,
  Search,
} from '@lucide/vue'
import LocationAutocomplete from '@/components/passenger/LocationAutocomplete.vue'
import {
  PASSENGER_PLACE_DESCRIPTIONS,
  POPAYAN_LOCATIONS,
} from '@/data/passengerRoutes'
import { nearestPopayanNeighborhood } from '@/data/popayanPlaces'

const router = useRouter()
const origin = ref('')
const destination = ref('')
const locating = ref(false)
const locationError = ref('')

function buscar() {
  router.push({
    name: 'buscar',
    query: { origin: origin.value.trim(), destination: destination.value.trim() },
  })
}

function usarUbicacion() {
  locationError.value = ''
  if (!navigator.geolocation) {
    locationError.value = 'Tu navegador no permite consultar la ubicación.'
    return
  }

  locating.value = true
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      const nearest = nearestPopayanNeighborhood(coords.latitude, coords.longitude)
      if (!nearest) {
        locationError.value = 'Tu ubicación parece estar fuera de Popayán.'
      } else {
        origin.value = nearest
        locationError.value = `Punto de partida aproximado: ${nearest}`
      }
      locating.value = false
    },
    (error) => {
      locationError.value =
        error.code === error.PERMISSION_DENIED
          ? 'Permite el acceso a tu ubicación para usar esta opción.'
          : 'No se pudo obtener tu ubicación.'
      locating.value = false
    },
    { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 },
  )
}
</script>

<template>
  <section class="passenger-screen passenger-home">
    <header class="passenger-home-hero">
      <div class="passenger-home-copy">
        <p class="passenger-page-eyebrow">TU CIUDAD, MEJOR CONECTADA</p>
        <h1>Muévete por tu ciudad <span>de forma inteligente</span></h1>
        <p>Encuentra cómo llegar y descubre Popayán en cada recorrido.</p>
      </div>
      <div class="passenger-home-landmark" aria-hidden="true">
        <span class="home-landmark-cloud home-cloud-one"></span>
        <span class="home-landmark-cloud home-cloud-two"></span>
        <div class="home-clock-tower">
          <div class="clock-tower-dome"></div>
          <div class="clock-tower-top"><span></span></div>
          <div class="clock-tower-body">
            <span class="clock-face"></span>
            <span class="tower-window"></span>
            <span class="tower-window"></span>
            <span class="tower-window"></span>
            <span class="tower-window"></span>
          </div>
          <div class="clock-tower-base"></div>
        </div>
        <div class="home-landmark-hills"></div>
        <span class="home-landmark-caption">POPAYÁN · CAUCA</span>
      </div>
    </header>

    <section class="passenger-home-search passenger-surface">
      <form class="passenger-home-search-form" @submit.prevent="buscar">
        <LocationAutocomplete
          id="home-origin"
          v-model="origin"
          label="Origen"
          placeholder="Mi ubicación o un lugar"
          :suggestions="POPAYAN_LOCATIONS"
          :descriptions="PASSENGER_PLACE_DESCRIPTIONS"
        />
        <LocationAutocomplete
          id="home-destination"
          v-model="destination"
          label="Destino"
          placeholder="¿A dónde quieres ir?"
          :suggestions="POPAYAN_LOCATIONS"
          :descriptions="PASSENGER_PLACE_DESCRIPTIONS"
          destination
        />
        <button class="passenger-home-search-button" type="submit">
          <Search :size="22" aria-hidden="true" />
          Buscar rutas
        </button>
      </form>
      <button class="passenger-current-location" type="button" :disabled="locating" @click="usarUbicacion">
        <LocateFixed :size="18" aria-hidden="true" />
        {{ locating ? 'Buscando ubicación…' : 'Usar mi ubicación actual' }}
      </button>
      <p v-if="locationError" class="passenger-inline-error" role="alert">{{ locationError }}</p>
    </section>

    <nav class="passenger-home-shortcuts" aria-label="Accesos rápidos">
      <RouterLink class="passenger-home-shortcut" :to="{ name: 'mapa' }">
        <span class="shortcut-icon shortcut-map"><Map aria-hidden="true" /></span>
        <strong>Mapa</strong>
        <small>Explora las rutas</small>
        <span class="shortcut-arrow" aria-hidden="true">›</span>
      </RouterLink>
      <RouterLink class="passenger-home-shortcut" :to="{ name: 'favoritos' }">
        <span class="shortcut-icon shortcut-heart"><Heart aria-hidden="true" /></span>
        <strong>Mis favoritos</strong>
        <small>Guarda tus rutas</small>
        <span class="shortcut-arrow" aria-hidden="true">›</span>
      </RouterLink>
      <RouterLink class="passenger-home-shortcut" :to="{ name: 'historial' }">
        <span class="shortcut-icon shortcut-history"><Clock3 aria-hidden="true" /></span>
        <strong>Historial</strong>
        <small>Tus viajes</small>
        <span class="shortcut-arrow" aria-hidden="true">›</span>
      </RouterLink>
    </nav>

    <p class="passenger-home-map-note">
      <MapPin :size="14" aria-hidden="true" />
      Información de rutas de ejemplo para Popayán. Consulta el recorrido antes de viajar.
    </p>
  </section>
</template>

<style>
.passenger-home-hero {
  position: relative;
  display: grid;
  min-height: 278px;
  grid-template-columns: 1.05fr 0.95fr;
  align-items: center;
  overflow: hidden;
  padding: clamp(1.3rem, 4vw, 3.2rem);
  border: 1px solid #dfeaf5;
  border-radius: 25px;
  background: linear-gradient(120deg, #eef5ff, #f4fbfb);
  box-shadow: 0 14px 36px rgba(23, 59, 93, 0.08);
}

.passenger-home-copy {
  position: relative;
  z-index: 2;
}

.passenger-home-copy h1 {
  max-width: 580px;
  margin-top: 0.75rem;
  color: #102d54;
  font-size: clamp(2rem, 4.7vw, 3.2rem);
  font-weight: 820;
  letter-spacing: -0.06em;
  line-height: 1.03;
}

.passenger-home-copy h1 span {
  display: block;
  margin-top: 0.2rem;
  color: #0b9686;
  font-style: italic;
}

.passenger-home-copy > p:last-child {
  max-width: 40ch;
  margin-top: 0.8rem;
  color: #687a91;
  font-size: 0.87rem;
  line-height: 1.6;
}

.passenger-home-landmark {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 56%;
  overflow: hidden;
  background: linear-gradient(112deg, rgba(242, 249, 253, 0.98), rgba(235, 248, 247, 0.28));
}

.home-landmark-cloud {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  filter: blur(1px);
}

.home-cloud-one {
  top: 20%;
  right: 19%;
  width: 120px;
  height: 28px;
}

.home-cloud-two {
  top: 31%;
  right: 3%;
  width: 85px;
  height: 23px;
}

.home-landmark-hills {
  position: absolute;
  right: -5%;
  bottom: 8%;
  width: 112%;
  height: 56%;
  border-radius: 50% 50% 0 0;
  background: linear-gradient(145deg, #aed9d5, #78b9b1);
  clip-path: polygon(0 60%, 15% 50%, 31% 57%, 49% 20%, 62% 40%, 78% 12%, 100% 40%, 100% 100%, 0 100%);
  opacity: 0.67;
}

.home-clock-tower {
  position: absolute;
  z-index: 1;
  right: 29%;
  bottom: 12%;
  width: 112px;
  height: 190px;
}

.clock-tower-dome {
  position: absolute;
  top: 0;
  left: 36px;
  width: 40px;
  height: 30px;
  border: 3px solid #587b91;
  border-bottom: 0;
  border-radius: 50% 50% 0 0;
  background: #dce8e7;
}

.clock-tower-dome::before {
  position: absolute;
  top: -9px;
  left: 17px;
  width: 3px;
  height: 12px;
  background: #536f83;
  content: '';
}

.clock-tower-top {
  position: absolute;
  top: 26px;
  left: 27px;
  width: 58px;
  height: 45px;
  border: 3px solid #6f8796;
  background: #e8eeee;
}

.clock-tower-top::before,
.clock-tower-top::after {
  position: absolute;
  top: 8px;
  width: 10px;
  height: 21px;
  border: 2px solid #718795;
  border-radius: 7px 7px 0 0;
  background: #b6d2d1;
  content: '';
}

.clock-tower-top::before {
  left: 7px;
}

.clock-tower-top::after {
  right: 7px;
}

.clock-tower-body {
  position: absolute;
  top: 69px;
  left: 18px;
  display: grid;
  width: 76px;
  height: 92px;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px 8px;
  padding: 12px 12px 8px;
  border: 3px solid #7d8f97;
  background: linear-gradient(90deg, #f5f2e8, #e8e5d9);
}

.clock-face {
  position: absolute;
  top: -49px;
  left: 17px;
  width: 30px;
  height: 30px;
  border: 3px solid #657e8d;
  border-radius: 50%;
  background: #fcfbf4;
}

.clock-face::after {
  position: absolute;
  top: 5px;
  left: 12px;
  width: 2px;
  height: 9px;
  background: #214f70;
  transform: rotate(-35deg);
  transform-origin: bottom;
  content: '';
}

.tower-window {
  width: 14px;
  height: 26px;
  border: 2px solid #748a94;
  border-radius: 9px 9px 0 0;
  background: #aacdcd;
}

.clock-tower-base {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 27px;
  border: 3px solid #89999c;
  background: repeating-linear-gradient(90deg, #e8e4d7 0 17px, #d6d3c7 17px 20px);
}

.home-landmark-caption {
  position: absolute;
  right: 0.9rem;
  bottom: 0.65rem;
  z-index: 2;
  color: #486d85;
  font-size: 0.55rem;
  font-weight: 850;
  letter-spacing: 0.15em;
}

.passenger-home-search {
  position: relative;
  z-index: 4;
  width: min(100% - 2rem, 800px);
  margin: 1.1rem auto 0;
  padding: 0.85rem;
  border-radius: 20px;
  box-shadow: 0 18px 42px rgba(27, 55, 87, 0.14);
}

.passenger-home-search-form {
  display: grid;
  gap: 0.45rem;
  overflow: visible;
  border: 0;
  background: transparent;
}

.passenger-home-search-button {
  display: inline-flex;
  min-height: 49px;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  margin: 0.65rem 0 0;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(110deg, #104575, #16558b);
  box-shadow: 0 7px 16px rgba(16, 73, 123, 0.2);
  color: #fff;
  font: inherit;
  font-size: 0.86rem;
  font-weight: 800;
  cursor: pointer;
}

.passenger-current-location {
  display: flex;
  min-height: 38px;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  margin: 0.65rem auto 0;
  padding: 0.45rem 0.9rem;
  border: 0;
  border-radius: 999px;
  background: #e8f2ff;
  color: #17649d;
  font: inherit;
  font-size: 0.73rem;
  font-weight: 750;
  cursor: pointer;
}

.passenger-current-location:disabled {
  cursor: wait;
  opacity: 0.7;
}

.passenger-home-shortcuts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
  margin: 1.2rem 0 1.5rem;
}

.passenger-home-shortcut {
  position: relative;
  display: grid;
  min-width: 0;
  min-height: 150px;
  align-content: center;
  justify-items: start;
  gap: 0.35rem;
  padding: 1rem;
  border: 1px solid #e5ebf4;
  border-radius: 17px;
  background: #fff;
  box-shadow: 0 9px 22px rgba(26, 58, 91, 0.06);
  color: inherit;
  text-decoration: none;
  transition:
    transform 150ms ease,
    box-shadow 150ms ease;
}

.passenger-home-shortcut:hover {
  transform: translateY(-2px);
  box-shadow: 0 13px 25px rgba(26, 58, 91, 0.1);
}

.shortcut-icon {
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  margin-bottom: 0.1rem;
  border-radius: 14px;
  background: #e8f4fc;
  color: #137ab4;
}

.shortcut-icon svg {
  width: 26px;
  height: 26px;
  stroke-width: 2.2;
}

.shortcut-heart {
  background: #f0edff;
  color: #315d9f;
}

.shortcut-heart svg {
  fill: currentColor;
}

.shortcut-history {
  background: #e9f7f3;
  color: #118e7c;
}

.passenger-home-shortcut strong {
  color: #18395d;
  font-size: 0.82rem;
}

.passenger-home-shortcut small {
  color: #77869b;
  font-size: 0.7rem;
}

.shortcut-arrow {
  position: absolute;
  right: 0.8rem;
  bottom: 1rem;
  color: #1b6593;
  font-size: 1.35rem;
}

.passenger-home-map-note {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  margin: 0.9rem 0;
  color: #8390a4;
  font-size: 0.68rem;
  line-height: 1.5;
}

.passenger-home-map-note svg {
  flex: 0 0 auto;
  color: #38819e;
}

@media (max-width: 700px) {
  .passenger-home-hero {
    min-height: 272px;
    grid-template-columns: minmax(0, 1fr) 0.3fr;
    padding: 1.2rem 1rem 2.35rem;
    border-radius: 20px;
  }

  .passenger-home-copy h1 {
    font-size: clamp(1.8rem, 7vw, 2.3rem);
  }

  .passenger-home-copy > p:last-child {
    max-width: 32ch;
    font-size: 0.74rem;
  }

  .passenger-home-landmark {
    width: 48%;
    background: linear-gradient(105deg, rgba(242, 249, 253, 0.98), rgba(235, 248, 247, 0.48));
  }

  .home-clock-tower {
    right: 17%;
    transform: scale(0.78);
    transform-origin: bottom center;
  }

  .home-landmark-caption {
    right: 0.45rem;
    bottom: 0.45rem;
    font-size: 0.45rem;
  }

  .passenger-home-search {
    width: 100%;
    margin-top: 0.85rem;
    padding: 0.65rem;
    border-radius: 17px;
  }

  .passenger-home-shortcuts {
    gap: 0.45rem;
    margin: 0.9rem 0 1.25rem;
  }

  .passenger-home-shortcut {
    min-height: 120px;
    gap: 0.22rem;
    padding: 0.65rem;
    border-radius: 13px;
  }

  .shortcut-icon {
    width: 38px;
    height: 38px;
    border-radius: 11px;
  }

  .shortcut-icon svg {
    width: 22px;
    height: 22px;
  }

  .passenger-home-shortcut strong {
    max-width: 100%;
    font-size: 0.62rem;
  }

  .passenger-home-shortcut small {
    font-size: 0.56rem;
  }

  .shortcut-arrow {
    top: 0.45rem;
    right: 0.45rem;
    bottom: auto;
    font-size: 1rem;
  }
}
</style>
