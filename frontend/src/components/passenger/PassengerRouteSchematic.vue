<script setup>
import { computed } from 'vue'

const props = defineProps({
  segments: {
    type: Array,
    default: () => [],
  },
  journey: {
    type: Object,
    default: null,
  },
})

const alternatives = computed(() => {
  const grouped = new Map()

  props.segments.forEach((segment, index) => {
    const key = segment.routeId || `route-${index}`
    if (!grouped.has(key)) {
      grouped.set(key, {
        id: key,
        code: segment.routeCode || segment.codigo,
        segments: [],
      })
    }
    grouped.get(key).segments.push(segment)
  })

  return [...grouped.values()]
})

function stopName(segment, first) {
  const stops = segment.stops || [segment.origen, segment.destino]
  return first ? stops[0] : stops.at(-1)
}

function startName(alternative) {
  return props.journey?.origin || stopName(alternative.segments[0], true)
}

function endName(alternative) {
  return props.journey?.destination || stopName(alternative.segments.at(-1), false)
}

function routeSummary(alternative) {
  return alternative.segments.map((segment) => segment.codigo).join(' + ')
}
</script>

<template>
  <section class="passenger-schematic" aria-label="Esquema de las rutas y pasos para abordar">
    <header class="passenger-schematic-heading">
      <div>
        <p>GUÍA ESQUEMÁTICA · POPAYÁN</p>
        <h3>Qué bus tomar y dónde subirte</h3>
      </div>
      <span v-if="journey" class="passenger-schematic-trip">
        {{ journey.origin }} <span aria-hidden="true">→</span> {{ journey.destination }}
      </span>
    </header>

    <p v-if="!alternatives.length" class="passenger-schematic-empty">
      {{
        journey
          ? 'No encontramos una conexión de ejemplo para este recorrido.'
          : 'Busca un origen y un destino para ver cómo hacer el recorrido.'
      }}
    </p>

    <article
      v-for="(alternative, alternativeIndex) in alternatives"
      :key="alternative.id"
      class="passenger-schematic-option"
    >
      <h4 v-if="alternatives.length > 1">
        Opción {{ alternativeIndex + 1 }} · {{ routeSummary(alternative) }}
      </h4>

      <div class="passenger-schematic-endpoint">
        <span class="passenger-schematic-node node-start">A</span>
        <div>
          <small>PUNTO DE PARTIDA</small>
          <strong>{{ startName(alternative) }}</strong>
        </div>
      </div>

      <template v-for="(segment, index) in alternative.segments" :key="`${alternative.id}-${segment.codigo}-${index}`">
        <div class="passenger-schematic-leg" :style="{ '--route-color': segment.color }">
          <span class="passenger-schematic-route-pill">{{ segment.codigo }}</span>
          <div class="passenger-schematic-leg-copy">
            <strong>Toma el {{ segment.codigo }} · {{ segment.empresa }}</strong>
            <span>Sube en la zona de <b>{{ stopName(segment, true) }}</b></span>
            <span>Bájate en la zona de <b>{{ stopName(segment, false) }}</b></span>
          </div>
        </div>

        <div v-if="index < alternative.segments.length - 1" class="passenger-schematic-transfer">
          <span class="passenger-schematic-node node-transfer">T</span>
          <span>Cambia de bus en <strong>{{ stopName(segment, false) }}</strong></span>
        </div>
      </template>

      <div class="passenger-schematic-endpoint">
        <span class="passenger-schematic-node node-end">B</span>
        <div>
          <small>DESTINO</small>
          <strong>{{ endName(alternative) }}</strong>
        </div>
      </div>
    </article>

    <p v-if="segments.length" class="passenger-schematic-note">
      A, T y B indican inicio, transbordo y destino. Los puntos de subida y bajada son referencias
      aproximadas de los recorridos de demostración, no paraderos oficiales verificados.
    </p>
  </section>
</template>

<style>
.passenger-schematic {
  min-width: 0;
  overflow: hidden;
  border: 1px solid #e3eaf2;
  border-radius: 17px;
  background: #fff;
  box-shadow: 0 12px 30px rgba(24, 42, 75, 0.07);
}

.passenger-schematic-heading {
  display: grid;
  gap: 0.35rem;
  padding: 1rem 1.1rem 0.8rem;
  border-bottom: 1px solid #edf1f6;
}

.passenger-schematic-heading p {
  color: #7887a2;
  font-size: 0.62rem;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.passenger-schematic-heading h3 {
  margin-top: 0.2rem;
  color: #1d2b48;
  font-size: 0.98rem;
}

.passenger-schematic-trip {
  color: #52677e;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1.45;
}

.passenger-schematic-option {
  position: relative;
  display: grid;
  gap: 0.65rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #edf1f6;
}

.passenger-schematic-option::before {
  position: absolute;
  top: 2.3rem;
  bottom: 2.3rem;
  left: calc(1rem + 12px);
  border-left: 2px dashed #d2dce7;
  content: '';
}

.passenger-schematic-option > * {
  position: relative;
}

.passenger-schematic-option:last-of-type {
  border-bottom: 0;
}

.passenger-schematic-option h4 {
  color: #203d59;
  font-size: 0.8rem;
}

.passenger-schematic-endpoint {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.65rem;
}

.passenger-schematic-endpoint > div {
  display: grid;
  min-width: 0;
  gap: 0.12rem;
}

.passenger-schematic-endpoint small {
  color: #74849a;
  font-size: 0.59rem;
  font-weight: 850;
  letter-spacing: 0.08em;
}

.passenger-schematic-endpoint strong {
  overflow-wrap: anywhere;
  color: #24425e;
  font-size: 0.78rem;
}

.passenger-schematic-node {
  display: grid;
  width: 27px;
  height: 27px;
  flex: 0 0 27px;
  place-items: center;
  border: 2px solid #fff;
  border-radius: 50%;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 900;
  box-shadow: 0 1px 5px rgba(15, 23, 42, 0.22);
}

.node-start {
  background: #15803d;
}

.node-transfer {
  background: #d97706;
}

.node-end {
  background: #dc2626;
}

.passenger-schematic-leg {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  gap: 0.65rem;
  margin-left: 0.75rem;
  padding: 0.7rem 0.75rem;
  border-left: 4px solid var(--route-color, #2865d8);
  border-radius: 0 11px 11px 0;
  background: #f7f9fc;
}

.passenger-schematic-route-pill {
  display: inline-grid;
  min-width: 40px;
  min-height: 30px;
  place-items: center;
  padding: 0.25rem 0.4rem;
  border-radius: 8px;
  background: color-mix(in srgb, var(--route-color, #2865d8) 12%, white);
  color: var(--route-color, #2865d8);
  font-size: 0.72rem;
  font-weight: 900;
}

.passenger-schematic-leg-copy {
  display: grid;
  min-width: 0;
  gap: 0.25rem;
}

.passenger-schematic-leg-copy strong {
  color: #23425f;
  font-size: 0.75rem;
  line-height: 1.4;
}

.passenger-schematic-leg-copy span {
  color: #64788e;
  font-size: 0.69rem;
  line-height: 1.45;
}

.passenger-schematic-leg-copy b {
  color: #344f68;
}

.passenger-schematic-transfer {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  margin-left: 0.75rem;
  color: #79500e;
  font-size: 0.7rem;
}

.passenger-schematic-note,
.passenger-schematic-empty {
  padding: 0.75rem 1rem;
  color: #78879a;
  font-size: 0.66rem;
  line-height: 1.5;
}

@media (max-width: 480px) {
  .passenger-schematic-heading,
  .passenger-schematic-option {
    padding-right: 0.75rem;
    padding-left: 0.75rem;
  }
}
</style>
