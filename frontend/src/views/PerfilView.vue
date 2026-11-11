<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  BellRing,
  Clock3,
  Heart,
  LifeBuoy,
  LogOut,
  Mail,
  MapPinned,
  Settings,
  ShieldCheck,
  UserRound,
} from '@lucide/vue'
import { useAuthStore } from '@/stores/auth'
import { usePasajeroStore } from '@/stores/pasajero'

const auth = useAuthStore()
const pasajero = usePasajeroStore()
const router = useRouter()
const correo = ref(pasajero.preferences.email || '')
const notice = ref('')
const error = ref('')
const nombre = computed(() => {
  const username = auth.username || 'Pasajero'
  return username.charAt(0).toLocaleUpperCase('es') + username.slice(1)
})

function guardarPerfil() {
  error.value = ''
  try {
    pasajero.actualizarPreferencias({ email: correo.value.trim() })
    notice.value = 'Tu perfil se guardó en este dispositivo.'
  } catch (exception) {
    error.value = exception.message
  }
}

function cambiarAlertas(event) {
  try {
    pasajero.actualizarPreferencias({ alerts: event.target.checked })
    notice.value = event.target.checked
      ? 'Activaste las preferencias de alertas.'
      : 'Desactivaste las preferencias de alertas.'
    error.value = ''
  } catch (exception) {
    event.target.checked = pasajero.preferences.alerts
    error.value = exception.message
  }
}

function cerrarSesion() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <section class="passenger-screen passenger-profile-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">TU CUENTA</p>
        <h1>Perfil</h1>
      </div>
    </header>

    <section class="passenger-profile-card passenger-surface">
      <div class="passenger-profile-avatar"><UserRound :size="40" aria-hidden="true" /></div>
      <span class="passenger-profile-crown" aria-hidden="true">✦</span>
      <h2>{{ nombre }}</h2>
      <p>{{ correo || 'Añade tu correo para completar tu perfil' }}</p>
      <span class="passenger-profile-username">@{{ auth.username }}</span>
    </section>

    <section class="passenger-current-plan-card">
      <div class="passenger-current-plan-icon">
        <span>{{ pasajero.esPlus ? '✦' : 'B' }}</span>
      </div>
      <div>
        <strong>Plan {{ pasajero.esPlus ? 'Plus' : 'Básico' }}</strong>
        <small>{{ pasajero.esPlus ? 'Demo activada en este dispositivo' : 'Sin costo' }}</small>
      </div>
      <RouterLink :to="{ name: 'planes' }">
        {{ pasajero.esPlus ? 'Administrar' : 'Mejorar' }} <ArrowRight :size="15" />
      </RouterLink>
    </section>

    <form class="passenger-profile-settings passenger-surface" @submit.prevent="guardarPerfil">
      <label for="profile-email"><Mail :size="18" aria-hidden="true" /> Correo electrónico</label>
      <div class="passenger-profile-email-field">
        <input id="profile-email" v-model="correo" type="email" placeholder="tu@correo.com" required />
        <button class="passenger-secondary-button" type="submit">Guardar</button>
      </div>
      <p>Este dato queda guardado localmente; no se envía al servidor.</p>
    </form>

    <nav class="passenger-profile-links" aria-label="Opciones de perfil">
      <RouterLink :to="{ name: 'favoritos' }">
        <Heart aria-hidden="true" /><span>Mis rutas favoritas</span><ArrowRight aria-hidden="true" />
      </RouterLink>
      <RouterLink :to="{ name: 'historial' }">
        <Clock3 aria-hidden="true" /><span>Historial de viajes</span><ArrowRight aria-hidden="true" />
      </RouterLink>
      <label class="passenger-profile-toggle">
        <BellRing aria-hidden="true" /><span>Preferencias de alertas</span>
        <input
          type="checkbox"
          :checked="pasajero.preferences.alerts"
          @change="cambiarAlertas"
        />
      </label>
      <RouterLink :to="{ name: 'planes' }">
        <Settings aria-hidden="true" /><span>Configuración y planes</span><ArrowRight aria-hidden="true" />
      </RouterLink>
      <a href="mailto:soporte@popayanbus.co?subject=Ayuda%20EnRutate">
        <LifeBuoy aria-hidden="true" /><span>Ayuda y soporte</span><ArrowRight aria-hidden="true" />
      </a>
      <button class="passenger-logout-link" type="button" @click="cerrarSesion">
        <LogOut aria-hidden="true" /><span>Cerrar sesión</span><ArrowRight aria-hidden="true" />
      </button>
    </nav>

    <p class="passenger-profile-privacy">
      <ShieldCheck :size="15" aria-hidden="true" />
      Favoritos, historial y preferencias se almacenan en este dispositivo.
    </p>
    <p v-if="notice" class="passenger-inline-notice" role="status">{{ notice }}</p>
    <p v-if="error" class="passenger-inline-error" role="alert">{{ error }}</p>
  </section>
</template>

<style>
.passenger-profile-card {
  position: relative;
  display: grid;
  justify-items: center;
  padding: 1.4rem 1rem 1.15rem;
  background: linear-gradient(180deg, #eff6ff, #fff 58%);
  text-align: center;
}

.passenger-profile-avatar {
  display: grid;
  width: 76px;
  height: 76px;
  place-items: center;
  border: 3px solid #fff;
  border-radius: 50%;
  background: linear-gradient(145deg, #a9d8f1, #d7edfa);
  color: #174f84;
  box-shadow: 0 5px 16px rgba(27, 86, 132, 0.15);
}

.passenger-profile-crown {
  position: absolute;
  top: 1.25rem;
  left: calc(50% + 28px);
  color: #e6aa23;
  font-size: 1.1rem;
}

.passenger-profile-card h2 {
  margin-top: 0.55rem;
  color: #18395d;
  font-size: 0.98rem;
}

.passenger-profile-card > p {
  margin-top: 0.12rem;
  color: #627891;
  font-size: 0.72rem;
}

.passenger-profile-username {
  margin-top: 0.35rem;
  color: #8290a4;
  font-size: 0.66rem;
}

.passenger-current-plan-card {
  display: flex;
  min-height: 65px;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.7rem;
  padding: 0.65rem 0.85rem;
  border-radius: 13px;
  background: linear-gradient(110deg, #104575, #16558b);
  color: #fff;
  box-shadow: 0 8px 18px rgba(15, 65, 110, 0.18);
}

.passenger-current-plan-icon {
  display: grid;
  width: 37px;
  height: 37px;
  place-items: center;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.14);
  color: #ffe294;
  font-size: 1.1rem;
  font-weight: 850;
}

.passenger-current-plan-card > div:nth-child(2) {
  display: grid;
  gap: 0.08rem;
}

.passenger-current-plan-card strong {
  font-size: 0.77rem;
}

.passenger-current-plan-card small {
  color: #d3e2f4;
  font-size: 0.61rem;
}

.passenger-current-plan-card > a {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  margin-left: auto;
  padding: 0.35rem 0.55rem;
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 999px;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 750;
  text-decoration: none;
}

.passenger-profile-settings {
  margin-top: 0.7rem;
  padding: 0.85rem;
}

.passenger-profile-settings > label {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #294866;
  font-size: 0.74rem;
  font-weight: 750;
}

.passenger-profile-email-field {
  display: flex;
  gap: 0.45rem;
  margin-top: 0.55rem;
}

.passenger-profile-email-field input {
  min-width: 0;
  flex: 1;
  padding: 0.6rem 0.7rem;
  border: 1px solid #e1e8f1;
  border-radius: 9px;
  background: #f9fbfd;
  font-size: 0.76rem;
}

.passenger-profile-email-field button {
  min-height: 38px;
  padding: 0.4rem 0.7rem;
  font-size: 0.68rem;
}

.passenger-profile-settings > p {
  margin-top: 0.4rem;
  color: #8290a4;
  font-size: 0.61rem;
}

.passenger-profile-links {
  display: grid;
  gap: 0.1rem;
  margin-top: 0.75rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid #e4eaf3;
  border-radius: 15px;
  background: #fff;
  box-shadow: 0 8px 22px rgba(25, 55, 87, 0.05);
}

.passenger-profile-links > a,
.passenger-profile-toggle,
.passenger-logout-link {
  display: grid;
  min-height: 45px;
  grid-template-columns: 22px minmax(0, 1fr) 18px;
  align-items: center;
  gap: 0.5rem;
  border: 0;
  border-bottom: 1px solid #edf0f5;
  background: transparent;
  color: #36506a;
  font: inherit;
  font-size: 0.72rem;
  text-align: left;
  text-decoration: none;
}

.passenger-profile-links > a > svg:first-child,
.passenger-profile-toggle > svg {
  width: 17px;
  height: 17px;
  color: #1668a2;
}

.passenger-profile-links > a > svg:last-child,
.passenger-logout-link > svg:last-child {
  width: 16px;
  height: 16px;
  color: #427298;
}

.passenger-profile-toggle {
  cursor: pointer;
}

.passenger-profile-toggle input {
  width: 36px;
  height: 20px;
  justify-self: end;
  accent-color: #0c9b83;
}

.passenger-logout-link {
  grid-template-columns: 22px minmax(0, 1fr) 18px;
  border-bottom: 0;
  cursor: pointer;
}

.passenger-logout-link > svg:first-child {
  width: 17px;
  color: #3174a4;
}

.passenger-profile-privacy {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  margin: 0.75rem 0;
  color: #8290a4;
  font-size: 0.65rem;
  line-height: 1.45;
}

.passenger-profile-privacy svg {
  flex: 0 0 auto;
  color: #159181;
}
</style>
