<script setup>
import { ref } from 'vue'
import { Check, Crown } from '@lucide/vue'
import { usePasajeroStore } from '@/stores/pasajero'

const pasajero = usePasajeroStore()
const notice = ref('')

function seleccionar(plan) {
  if (pasajero.plan === plan) return
  pasajero.seleccionarPlan(plan)
  notice.value =
    plan === 'plus'
      ? 'Plus quedó activado como una simulación local. No se realizará ningún cobro.'
      : 'Cambiaste al plan Básico. Puedes volver a activar Plus cuando quieras.'
}
</script>

<template>
  <section class="passenger-plans">
    <header class="passenger-plans-heading">
      <div>
        <p>ELIGE CÓMO MOVERTE</p>
        <h2>Nuestros planes</h2>
      </div>
      <span class="passenger-plans-heading-note">Sin permanencia</span>
    </header>

    <div class="passenger-plans-grid">
      <article class="passenger-plan-card passenger-plan-basic">
        <span class="passenger-plan-badge">BÁSICO</span>
        <h3>Gratis</h3>
        <p>Lo esencial para encontrar cómo llegar.</p>
        <ul>
          <li><Check aria-hidden="true" /> Consultar rutas</li>
          <li><Check aria-hidden="true" /> Mapa interactivo</li>
        </ul>
        <button
          class="passenger-plan-button passenger-plan-button-basic"
          type="button"
          :disabled="!pasajero.esPlus"
          :aria-pressed="!pasajero.esPlus"
          @click="seleccionar('basic')"
        >
          {{ pasajero.esPlus ? 'Usar plan básico' : 'Tu plan actual' }}
        </button>
      </article>

      <article class="passenger-plan-card passenger-plan-plus">
        <span class="passenger-plan-ornament" aria-hidden="true">✦</span>
        <span class="passenger-plan-badge"><Crown :size="15" aria-hidden="true" /> PLUS</span>
        <h3>$9.900 <small>/ mes</small></h3>
        <p>Más beneficios para planear con confianza.</p>
        <ul>
          <li><Check aria-hidden="true" /> Tiempo estimado de viaje</li>
          <li><Check aria-hidden="true" /> Alternativas con menos transbordos</li>
          <li><Check aria-hidden="true" /> Rutas alternativas</li>
          <li><Check aria-hidden="true" /> Alertas de cambios</li>
        </ul>
        <button
          class="passenger-plan-button passenger-plan-button-plus"
          type="button"
          :disabled="pasajero.esPlus"
          :aria-pressed="pasajero.esPlus"
          @click="seleccionar('plus')"
        >
          {{ pasajero.esPlus ? 'Plan Plus activo' : 'Obtener Plus' }}
          <Check v-if="pasajero.esPlus" :size="17" aria-hidden="true" />
          <span v-else aria-hidden="true">→</span>
        </button>
        <span class="passenger-plan-reassurance">Compra simulada · Sin cobros reales</span>
      </article>
    </div>

    <p v-if="notice" class="passenger-inline-notice" role="status" aria-live="polite">
      {{ notice }}
    </p>
    <p class="passenger-plan-disclaimer">
      Precio de referencia para la propuesta. Activar Plus en esta versión es solo una simulación;
      no se procesa ningún pago.
    </p>
  </section>
</template>

<style>
.passenger-plans {
  margin-top: 1.65rem;
  scroll-margin-top: 1rem;
}

.passenger-plans-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
  padding: 0 0.15rem;
}

.passenger-plans-heading > div > p {
  color: #7887a2;
  font-size: 0.63rem;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.passenger-plans-heading h2 {
  margin-top: 0.15rem;
  color: #152f53;
  font-size: clamp(1.35rem, 3vw, 1.8rem);
  letter-spacing: -0.035em;
}

.passenger-plans-heading-note {
  color: #1b6593;
  font-size: 0.72rem;
  font-weight: 730;
}

.passenger-plans-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: stretch;
  gap: 1rem;
}

.passenger-plan-card {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  align-items: center;
  padding: clamp(1rem, 2.5vw, 1.6rem);
  border: 1px solid #e1e8f1;
  border-radius: 21px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(22, 50, 82, 0.07);
  text-align: center;
}

.passenger-plan-plus {
  overflow: hidden;
  border-color: #9cddd3;
  background:
    radial-gradient(ellipse at 100% 0%, rgba(136, 221, 204, 0.23), transparent 40%),
    linear-gradient(145deg, #f2fffc, #e8f8f5);
  box-shadow: 0 12px 30px rgba(16, 130, 113, 0.1);
}

.passenger-plan-badge {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  padding: 0.35rem 1.25rem;
  border-radius: 999px;
  background: #176eac;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 850;
  letter-spacing: 0.06em;
}

.passenger-plan-plus .passenger-plan-badge {
  background: #078e79;
}

.passenger-plan-card h3 {
  margin-top: 0.65rem;
  color: #142f53;
  font-size: clamp(1.35rem, 3vw, 1.9rem);
  letter-spacing: -0.045em;
  line-height: 1.18;
}

.passenger-plan-card h3 small {
  color: #63758c;
  font-size: 0.75rem;
  font-weight: 650;
  letter-spacing: 0;
}

.passenger-plan-card > p {
  min-height: 2.6em;
  margin-top: 0.45rem;
  color: #64758e;
  font-size: 0.79rem;
  line-height: 1.5;
}

.passenger-plan-card ul {
  display: grid;
  width: min(100%, 340px);
  gap: 0.58rem;
  margin: 1rem 0 1.15rem;
  padding: 0;
  color: #43536b;
  font-size: 0.77rem;
  list-style: none;
  text-align: left;
}

.passenger-plan-card li {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.passenger-plan-card li svg {
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
  color: #1687c0;
  stroke-width: 3;
}

.passenger-plan-plus li svg {
  color: #0c9d83;
}

.passenger-plan-button {
  display: inline-flex;
  width: 100%;
  min-height: 46px;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: auto;
  padding: 0.55rem 0.8rem;
  border: 1.5px solid #3786bd;
  border-radius: 999px;
  background: #fff;
  color: #17649d;
  font: inherit;
  font-size: 0.78rem;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease;
}

.passenger-plan-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 7px 15px rgba(30, 101, 151, 0.13);
}

.passenger-plan-button:disabled {
  cursor: default;
  opacity: 0.82;
}

.passenger-plan-button-plus {
  border-color: #078e79;
  background: linear-gradient(105deg, #078e79, #0b9e85);
  color: #fff;
}

.passenger-plan-button-plus:hover:not(:disabled) {
  background: linear-gradient(105deg, #087b6b, #078e79);
  box-shadow: 0 8px 18px rgba(8, 142, 121, 0.24);
}

.passenger-plan-reassurance,
.passenger-plan-disclaimer {
  margin-top: 0.55rem;
  color: #618478;
  font-size: 0.64rem;
}

.passenger-plan-ornament {
  position: absolute;
  top: 0.65rem;
  right: 0.85rem;
  color: #079985;
  font-size: 1.6rem;
  transform: rotate(12deg);
}

.passenger-plan-disclaimer {
  color: #8390a4;
  font-size: 0.66rem;
  line-height: 1.55;
}

@media (max-width: 700px) {
  .passenger-plans {
    margin-top: 1.5rem;
  }

  .passenger-plans-grid {
    gap: 0.6rem;
  }

  .passenger-plan-card {
    padding: 0.85rem 0.7rem;
    border-radius: 17px;
  }

  .passenger-plan-card > p {
    min-height: 3.2em;
    font-size: 0.68rem;
  }

  .passenger-plan-card ul {
    gap: 0.55rem;
    margin: 0.8rem 0 1rem;
    font-size: 0.65rem;
  }

  .passenger-plan-card li {
    gap: 0.35rem;
  }

  .passenger-plan-badge {
    min-height: 27px;
    padding: 0.3rem 0.8rem;
    font-size: 0.62rem;
  }

  .passenger-plan-button {
    min-height: 42px;
    gap: 0.25rem;
    padding: 0.4rem 0.45rem;
    font-size: 0.67rem;
  }

  .passenger-plan-reassurance {
    font-size: 0.56rem;
  }
}
</style>
