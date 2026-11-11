<script setup>
import { RouterLink, useRoute } from 'vue-router'
import {
  ArrowLeft,
  BellRing,
  Clock3,
  Map,
  MapPinned,
  Search,
  SlidersHorizontal,
  Sparkles,
} from '@lucide/vue'
import PassengerPlans from '@/components/passenger/PassengerPlans.vue'

const route = useRoute()
const featureNames = {
  favoritos: 'Favoritos',
  historial: 'Historial de viajes',
  tiempos: 'Tiempos estimados y transbordos',
}
</script>

<template>
  <section class="passenger-screen passenger-plans-screen">
    <header class="passenger-page-heading">
      <div>
        <p class="passenger-page-eyebrow">ENRUTATE · PLANES</p>
        <h1>Elige el plan ideal para ti</h1>
        <p>Mejora tu experiencia y personaliza cómo te mueves por la ciudad.</p>
      </div>
      <RouterLink class="passenger-back-link" :to="{ name: 'inicio' }">
        <ArrowLeft :size="17" aria-hidden="true" /> Inicio
      </RouterLink>
    </header>

    <p v-if="featureNames[String(route.query.feature)]" class="passenger-inline-notice">
      {{ featureNames[String(route.query.feature)] }} y otras herramientas están incluidas en Plus.
      Puedes probar el plan sin cobros.
    </p>

    <div class="passenger-plan-intro passenger-surface">
      <Sparkles :size="25" aria-hidden="true" />
      <p>Comienza gratis y activa Plus cuando quieras. Tu elección se guarda en este dispositivo.</p>
    </div>
    <PassengerPlans />

    <section class="passenger-plan-feature-grid" aria-label="Beneficios de cada plan">
      <article><Search aria-hidden="true" /><strong>Consultar rutas</strong><span>Básico</span></article>
      <article><Map aria-hidden="true" /><strong>Mapa interactivo</strong><span>Básico</span></article>
      <article><Clock3 aria-hidden="true" /><strong>Tiempo estimado</strong><span>Plus</span></article>
      <article><MapPinned aria-hidden="true" /><strong>Menos transbordos</strong><span>Plus</span></article>
      <article><BellRing aria-hidden="true" /><strong>Alertas de cambios</strong><span>Plus</span></article>
    </section>

    <p class="passenger-plan-disclaimer">
      La compra de Plus es simulada en esta versión. El valor de $9.900 COP/mes es referencial y no
      se realizará ningún cobro.
    </p>
  </section>
</template>

<style>
.passenger-plan-intro {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.85rem 1rem;
  color: #2478a8;
}

.passenger-plan-intro p {
  color: #536b84;
  font-size: 0.76rem;
  line-height: 1.5;
}

.passenger-plan-feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 1rem;
}

.passenger-plan-feature-grid article {
  display: grid;
  justify-items: center;
  gap: 0.35rem;
  padding: 0.8rem 0.5rem;
  border: 1px solid #e5ebf3;
  border-radius: 13px;
  background: #fff;
  color: #2273a8;
  text-align: center;
}

.passenger-plan-feature-grid strong {
  color: #2f4965;
  font-size: 0.67rem;
}

.passenger-plan-feature-grid span {
  color: #118b7d;
  font-size: 0.61rem;
  font-weight: 780;
}

.passenger-plans-screen > .passenger-plan-disclaimer {
  margin-top: 0.9rem;
  color: #8290a4;
  font-size: 0.68rem;
  line-height: 1.55;
}

@media (max-width: 560px) {
  .passenger-plan-feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
