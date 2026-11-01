<script setup>
import { computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRutasStore } from '@/stores/rutas'
import planificadorService from '@/services/planificadorService'

const route = useRoute()
const auth = useAuthStore()
const rutasStore = useRutasStore()

const cargando = reactive({
  rutas: false,
  viaje: false,
  congestion: false,
  trafico: false,
  comparativa: false,
})

const errores = reactive({
  rutas: '',
  viaje: '',
  congestion: '',
  trafico: '',
  comparativa: '',
})

const viaje = reactive({
  origin: '',
  destination: '',
  tipo: 'directo',
  resultado: null,
})

const congestion = reactive({
  route_id: null,
  resultado: null,
})

const trafico = reactive({
  route_id: null,
  hora: '07:30',
  resultado: null,
})

const comparativa = reactive({
  ruta1: null,
  ruta2: null,
  resultado: null,
})

const resultadosComparacion = computed(() => {
  if (!comparativa.resultado) return []

  return Object.entries(comparativa.resultado).filter(
    ([, valor]) => valor && typeof valor === 'object' && !Array.isArray(valor),
  )
})

const formatoCOP = (valor) =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(valor) || 0)

function mensajeError(e, fallback) {
  if (e.code === 'ECONNABORTED') {
    return 'El microservicio de rutas no respondió en 10 segundos. Revisa que el backend esté encendido e inténtalo de nuevo.'
  }
  if (!e.response && e.request) {
    return 'No se pudo conectar con el microservicio de rutas. Revisa la conexión e inténtalo de nuevo.'
  }
  return (
    e.response?.data?.mensaje || e.response?.data?.error || e.response?.data?.message || fallback
  )
}

function urlGoogleMaps(origen, destino) {
  const query = new URLSearchParams({
    api: '1',
    origin: `${origen}, Popayán, Cauca, Colombia`,
    destination: `${destino}, Popayán, Cauca, Colombia`,
    travelmode: 'transit',
  })
  return `https://www.google.com/maps/dir/?${query.toString()}`
}

async function cargarRutas() {
  cargando.rutas = true
  errores.rutas = ''
  try {
    if (rutasStore.filtroZona) {
      await rutasStore.limpiarFiltro()
    } else {
      await rutasStore.cargar()
    }
    if (rutasStore.lista.length > 0) {
      const primeraRuta = rutasStore.lista[0]
      const segundaRuta = rutasStore.lista.find((ruta) => ruta.id !== primeraRuta.id)
      congestion.route_id ??= primeraRuta.id
      trafico.route_id ??= primeraRuta.id
      comparativa.ruta1 ??= primeraRuta.id
      comparativa.ruta2 ??= segundaRuta?.id ?? primeraRuta.id
    }
  } catch (e) {
    errores.rutas = mensajeError(
      e,
      'No se pudieron cargar las rutas. Verifica que el microservicio esté disponible.',
    )
  } finally {
    cargando.rutas = false
  }
}

async function solicitar(clave, limpiarResultado, guardarResultado, solicitud, fallback) {
  errores[clave] = ''
  limpiarResultado()
  cargando[clave] = true

  try {
    const respuesta = await solicitud()
    guardarResultado(respuesta.data)
  } catch (e) {
    errores[clave] = mensajeError(e, fallback)
  } finally {
    cargando[clave] = false
  }
}

function planificarViaje() {
  const origen = viaje.origin.trim()
  const destino = viaje.destination.trim()

  if (origen.toLocaleLowerCase('es') === destino.toLocaleLowerCase('es')) {
    errores.viaje = 'El origen y el destino deben ser diferentes.'
    viaje.resultado = null
    return
  }

  return solicitar(
    'viaje',
    () => {
      viaje.resultado = null
    },
    (resultado) => {
      viaje.resultado = resultado
    },
    () =>
      viaje.tipo === 'directo'
        ? planificadorService.planificarViajeDirecto(origen, destino)
        : planificadorService.planificarViajeTransbordo(origen, destino),
    'No se pudo planificar el viaje. Inténtalo nuevamente.',
  )
}

function consultarCongestion() {
  return solicitar(
    'congestion',
    () => {
      congestion.resultado = null
    },
    (resultado) => {
      congestion.resultado = resultado
    },
    () => planificadorService.calcularCongestion(congestion.route_id),
    'No se pudo consultar la congestión de esta ruta.',
  )
}

function simularTrafico() {
  return solicitar(
    'trafico',
    () => {
      trafico.resultado = null
    },
    (resultado) => {
      trafico.resultado = resultado
    },
    () => planificadorService.simularTrafico(trafico.route_id, trafico.hora),
    'No se pudo simular el tráfico para esta ruta.',
  )
}

function compararRutas() {
  if (comparativa.ruta1 === comparativa.ruta2) {
    errores.comparativa = 'Selecciona dos rutas distintas para compararlas.'
    comparativa.resultado = null
    return
  }

  return solicitar(
    'comparativa',
    () => {
      comparativa.resultado = null
    },
    (resultado) => {
      comparativa.resultado = resultado
    },
    () => planificadorService.compararRutas(comparativa.ruta1, comparativa.ruta2),
    'No se pudo comparar las rutas seleccionadas.',
  )
}

onMounted(() => {
  if (typeof route.query.origin === 'string') {
    viaje.origin = route.query.origin.slice(0, 120)
  }
  if (typeof route.query.destination === 'string') {
    viaje.destination = route.query.destination.slice(0, 120)
  }
  cargarRutas()
})
</script>

<template>
  <section class="page planner-page">
    <header class="planner-heading">
      <div>
        <p class="planner-eyebrow">
          {{
            auth.role === 'USUARIO'
              ? 'TU MOVILIDAD • POPAYÁN'
              : 'MICROSERVICIO 01 • ASISTENTE DE MOVILIDAD'
          }}
        </p>
        <h1 class="page-title">
          {{ auth.role === 'USUARIO' ? 'Muévete por Popayán' : 'Planificador inteligente' }}
        </h1>
        <p class="page-subtitle">
          {{
            auth.role === 'USUARIO'
              ? 'Encuentra cómo llegar, cuánto cuesta y qué ruta te conviene.'
              : 'Encuentra recorridos y consulta información operativa de la red de Popayán.'
          }}
        </p>
      </div>
      <span class="planner-live">
        <span></span>{{ auth.role === 'USUARIO' ? 'Rutas y viajes' : 'Análisis de rutas' }}
      </span>
    </header>

    <p v-if="errores.rutas" class="alert alert-error" role="alert">{{ errores.rutas }}</p>
    <div v-if="cargando.rutas" class="planner-loading" role="status">
      <span class="planner-spinner" aria-hidden="true"></span>
      Cargando rutas disponibles…
    </div>
    <div v-else-if="errores.rutas" class="planner-empty" role="status">
      <strong>No fue posible cargar el catálogo de rutas</strong>
      <span>Comprueba que el microservicio esté encendido e inténtalo de nuevo.</span>
      <button class="planner-retry" type="button" @click="cargarRutas">Reintentar</button>
    </div>
    <div v-else-if="rutasStore.lista.length === 0" class="planner-empty" role="status">
      <strong>
        {{ auth.role === 'USUARIO' ? 'Aún no hay rutas disponibles' : 'Aún no hay rutas para analizar' }}
      </strong>
      <span>
        {{
          auth.role === 'USUARIO'
            ? 'Cuando se publiquen rutas activas, podrás consultar recorridos, horarios y tarifas aquí.'
            : 'Registra rutas en Gestión de rutas y vuelve a intentarlo.'
        }}
      </span>
      <RouterLink v-if="auth.role !== 'USUARIO'" to="/rutas">Ir a gestión de rutas</RouterLink>
    </div>

    <template v-else>
      <section class="planner-trip-card">
        <div class="planner-trip-intro">
          <span class="planner-trip-icon" aria-hidden="true">⌁</span>
          <p>PLANEA TU RECORRIDO</p>
          <h2>¿A dónde necesitas llegar?</h2>
          <span>Consulta rutas directas o con transbordo, con paradas, tiempo estimado y tarifa.</span>
        </div>

        <form class="planner-trip-form" @submit.prevent="planificarViaje">
          <div class="planner-trip-fields">
            <div class="field">
              <label for="trip-origin">Punto de partida</label>
              <div class="planner-input">
                <span class="planner-point planner-point-origin" aria-hidden="true"></span>
                <input
                  id="trip-origin"
                  v-model="viaje.origin"
                  name="origin"
                  placeholder="Ej. Centro, La Paz…"
                  maxlength="120"
                  autocomplete="street-address"
                  required
                />
              </div>
            </div>
            <div class="planner-trip-direction" aria-hidden="true">→</div>
            <div class="field">
              <label for="trip-destination">Destino</label>
              <div class="planner-input">
                <span class="planner-point planner-point-destination" aria-hidden="true"></span>
                <input
                  id="trip-destination"
                  v-model="viaje.destination"
                  name="destination"
                  placeholder="Ej. Campanario, Cajete…"
                  maxlength="120"
                  required
                />
              </div>
            </div>
          </div>
          <div class="planner-trip-submit">
            <label class="sr-only" for="trip-mode">Tipo de recorrido</label>
            <select id="trip-mode" v-model="viaje.tipo" name="mode">
              <option value="directo">Ruta directa</option>
              <option value="transbordo">Con transbordo</option>
            </select>
            <button type="submit" :disabled="cargando.viaje">
              {{ cargando.viaje ? 'Buscando…' : 'Buscar recorrido' }}
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </form>

        <p v-if="errores.viaje" class="planner-inline-error" role="alert">{{ errores.viaje }}</p>

        <div v-if="viaje.resultado" class="planner-trip-result" aria-live="polite">
          <div v-if="!viaje.resultado.encontrado" class="planner-no-route">
            <span aria-hidden="true">ⓘ</span>
            <div>
              <strong
                >No encontramos una conexión
                {{ viaje.tipo === 'directo' ? 'directa' : 'con transbordo' }}.</strong
              >
              <p>{{ viaje.resultado.mensaje || 'Prueba con otros puntos de origen o destino.' }}</p>
            </div>
          </div>
          <template v-else>
            <div class="planner-result-heading">
              <div>
                <span class="planner-section-label">RECORRIDO RECOMENDADO</span>
                <h3>{{ viaje.origin }} <span>→</span> {{ viaje.destination }}</h3>
              </div>
              <div class="planner-result-actions">
                <span class="planner-result-type">
                  {{ viaje.tipo === 'directo' ? 'DIRECTO' : 'CON TRANSBORDO' }}
                </span>
                <a
                  class="planner-map-link"
                  :href="
                    urlGoogleMaps(
                      viaje.resultado.ruta_recomendada?.paradero_subida || viaje.origin,
                      viaje.resultado.ruta_recomendada?.paradero_bajada || viaje.destination,
                    )
                  "
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path
                      d="M10 17s6-5.3 6-10a6 6 0 1 0-12 0c0 4.7 6 10 6 10Z"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                    <circle cx="10" cy="7" r="2" stroke="currentColor" stroke-width="1.5" />
                  </svg>
                  Ver en Google Maps
                </a>
              </div>
            </div>
            <p class="planner-map-note">
              Google Maps puede sugerir un recorrido distinto al itinerario de EnRutate.
            </p>

            <div v-if="viaje.resultado.ruta_recomendada" class="planner-direct-route">
              <div class="planner-route-symbol" aria-hidden="true">↗</div>
              <div class="planner-route-info">
                <span>RUTA {{ viaje.resultado.ruta_recomendada.codigo }}</span>
                <strong>{{ viaje.resultado.ruta_recomendada.empresa }}</strong>
                <small>
                  {{ viaje.resultado.ruta_recomendada.paradero_subida }} →
                  {{ viaje.resultado.ruta_recomendada.paradero_bajada }}
                </small>
              </div>
              <div class="planner-route-facts">
                <span>{{ viaje.resultado.ruta_recomendada.paradas }} paradas</span>
                <strong>~{{ viaje.resultado.ruta_recomendada.minutos_estimados }} min</strong>
              </div>
              <div class="planner-route-fare">
                <small>TARIFA</small>
                <strong>{{ formatoCOP(viaje.resultado.ruta_recomendada.tarifa_cop) }}</strong>
              </div>
            </div>

            <div v-if="viaje.resultado.paso_1 && viaje.resultado.paso_2" class="planner-transfer">
              <article>
                <span class="planner-transfer-index">01</span>
                <div>
                  <small>PRIMER TRAMO · {{ viaje.resultado.paso_1.empresa }}</small>
                  <strong>{{ viaje.resultado.paso_1.ruta }}</strong>
                  <p>
                    {{ viaje.resultado.paso_1.subida }} →
                    {{ viaje.resultado.paso_1.bajada_transbordo }}
                  </p>
                </div>
              </article>
              <span class="planner-transfer-connector" aria-hidden="true">↓</span>
              <article>
                <span class="planner-transfer-index">02</span>
                <div>
                  <small>SEGUNDO TRAMO · {{ viaje.resultado.paso_2.empresa }}</small>
                  <strong>{{ viaje.resultado.paso_2.ruta }}</strong>
                  <p>
                    {{ viaje.resultado.paso_1.bajada_transbordo }} →
                    {{ viaje.resultado.paso_2.llegada }}
                  </p>
                </div>
              </article>
            </div>

            <div v-if="viaje.tipo === 'transbordo'" class="planner-trip-totals">
              <span
                >Duración aproximada
                <strong>~{{ viaje.resultado.minutos_estimados }} min</strong></span
              >
              <span
                >Tarifa total
                <strong>{{ formatoCOP(viaje.resultado.tarifa_total_cop) }}</strong></span
              >
            </div>
            <p v-if="viaje.resultado.resumen" class="planner-summary">
              {{ viaje.resultado.resumen }}
            </p>
          </template>
        </div>
      </section>

      <div class="planner-tools-heading">
        <div>
          <p class="planner-section-label">
            {{ auth.role === 'USUARIO' ? 'ANTES DE SALIR' : 'HERRAMIENTAS DE ANÁLISIS' }}
          </p>
          <h2>{{ auth.role === 'USUARIO' ? 'Elige mejor tu recorrido' : 'Consulta la operación' }}</h2>
        </div>
        <span>{{ rutasStore.lista.length }} rutas disponibles</span>
      </div>

      <div class="planner-tools-grid">
        <section class="card planner-tool">
          <div class="planner-tool-heading">
            <span class="planner-tool-icon planner-icon-traffic" aria-hidden="true">◉</span>
            <div>
              <h3>Congestión y confiabilidad</h3>
              <p>Estado vial e incidentes de la ruta</p>
            </div>
          </div>
          <form class="planner-tool-form" @submit.prevent="consultarCongestion">
            <div class="field">
              <label for="congestion-route">Ruta a evaluar</label>
              <select id="congestion-route" v-model.number="congestion.route_id" required>
                <option v-for="ruta in rutasStore.lista" :key="ruta.id" :value="ruta.id">
                  {{ ruta.code }} · {{ ruta.company }}
                </option>
              </select>
            </div>
            <button class="planner-tool-button" type="submit" :disabled="cargando.congestion">
              {{ cargando.congestion ? 'Evaluando…' : 'Evaluar ruta' }}
              <span aria-hidden="true">→</span>
            </button>
          </form>
          <p v-if="errores.congestion" class="planner-inline-error" role="alert">
            {{ errores.congestion }}
          </p>
          <div v-if="congestion.resultado" class="planner-analysis-result" aria-live="polite">
            <div class="planner-analysis-main">
              <span
                :class="[
                  'planner-congestion',
                  `level-${String(congestion.resultado.nivel_congestion).toLowerCase()}`,
                ]"
              >
                {{ congestion.resultado.nivel_congestion }}
              </span>
              <strong>{{ congestion.resultado.confiabilidad }} <small>confiabilidad</small></strong>
            </div>
            <div class="planner-analysis-detail">
              <span
                ><strong>{{ congestion.resultado.incidentes_activos }}</strong> incidentes
                activos</span
              >
              <span
                ><strong>+{{ congestion.resultado.demora_minutos }} min</strong> de demora
                estimada</span
              >
            </div>
            <p>{{ congestion.resultado.diagnostico }}</p>
          </div>
        </section>

        <section class="card planner-tool">
          <div class="planner-tool-heading">
            <span class="planner-tool-icon planner-icon-clock" aria-hidden="true">◷</span>
            <div>
              <h3>Simulación de tráfico</h3>
              <p>Estima duración según hora de salida</p>
            </div>
          </div>
          <form class="planner-tool-form" @submit.prevent="simularTrafico">
            <div class="planner-tool-fields">
              <div class="field">
                <label for="traffic-route">Ruta</label>
                <select id="traffic-route" v-model.number="trafico.route_id" required>
                  <option v-for="ruta in rutasStore.lista" :key="ruta.id" :value="ruta.id">
                    {{ ruta.code }}
                  </option>
                </select>
              </div>
              <div class="field">
                <label for="traffic-time">Hora de salida</label>
                <input id="traffic-time" v-model="trafico.hora" name="hora" type="time" required />
              </div>
            </div>
            <button class="planner-tool-button" type="submit" :disabled="cargando.trafico">
              {{ cargando.trafico ? 'Calculando…' : 'Simular viaje' }}
              <span aria-hidden="true">→</span>
            </button>
          </form>
          <p v-if="errores.trafico" class="planner-inline-error" role="alert">
            {{ errores.trafico }}
          </p>
          <div v-if="trafico.resultado" class="planner-analysis-result" aria-live="polite">
            <div class="planner-analysis-main">
              <span
                :class="[
                  'planner-congestion',
                  trafico.resultado.es_hora_pico ? 'level-critico' : 'level-normal',
                ]"
              >
                {{ trafico.resultado.es_hora_pico ? 'HORA PICO' : 'TRÁFICO FLUIDO' }}
              </span>
              <strong>{{ trafico.resultado.minutos_reales }} <small>minutos</small></strong>
            </div>
            <div class="planner-analysis-detail">
              <span
                >Salida <strong>{{ trafico.resultado.hora_salida }}</strong></span
              >
              <span
                >Llegada estimada
                <strong>{{ trafico.resultado.hora_llegada_estimada }}</strong></span
              >
            </div>
            <p>{{ trafico.resultado.consejo }}</p>
          </div>
        </section>

        <section class="card planner-tool planner-comparison">
          <div class="planner-tool-heading">
            <span class="planner-tool-icon planner-icon-compare" aria-hidden="true">⇄</span>
            <div>
              <h3>Comparar rutas</h3>
              <p>Compara tiempo estimado y costo del pasaje</p>
            </div>
          </div>
          <form class="planner-tool-form planner-compare-form" @submit.prevent="compararRutas">
            <div class="planner-tool-fields">
              <div class="field">
                <label for="compare-route-a">Alternativa A</label>
                <select id="compare-route-a" v-model.number="comparativa.ruta1" required>
                  <option v-for="ruta in rutasStore.lista" :key="ruta.id" :value="ruta.id">
                    {{ ruta.code }} · {{ ruta.company }}
                  </option>
                </select>
              </div>
              <div class="field">
                <label for="compare-route-b">Alternativa B</label>
                <select id="compare-route-b" v-model.number="comparativa.ruta2" required>
                  <option v-for="ruta in rutasStore.lista" :key="ruta.id" :value="ruta.id">
                    {{ ruta.code }} · {{ ruta.company }}
                  </option>
                </select>
              </div>
            </div>
            <button
              class="planner-tool-button"
              type="submit"
              :disabled="cargando.comparativa || rutasStore.lista.length < 2"
            >
              {{ cargando.comparativa ? 'Comparando…' : 'Comparar alternativas' }}
              <span aria-hidden="true">→</span>
            </button>
          </form>
          <p v-if="rutasStore.lista.length < 2" class="planner-helper">
            Registra al menos dos rutas para habilitar la comparación.
          </p>
          <p v-if="errores.comparativa" class="planner-inline-error" role="alert">
            {{ errores.comparativa }}
          </p>
          <div v-if="comparativa.resultado" class="planner-comparison-results" aria-live="polite">
            <article v-for="[nombre, ruta] in resultadosComparacion" :key="nombre">
              <span>{{ nombre.replace('ruta_', 'RUTA ') }}</span>
              <strong>{{ ruta.empresa }}</strong>
              <div>
                <span>{{ ruta.paradas }} paradas · {{ ruta.tiempo_min }} min</span>
                <strong>{{ formatoCOP(ruta.tarifa_cop) }}</strong>
              </div>
            </article>
            <div class="planner-winners">
              <span
                >⚡ Más rápida
                <strong>{{ comparativa.resultado.mejor_por_velocidad }}</strong></span
              >
              <span
                >◈ Más económica
                <strong>{{ comparativa.resultado.mejor_por_economia }}</strong></span
              >
            </div>
            <p>{{ comparativa.resultado.veredicto }}</p>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>

<style scoped>
.planner-page {
  --planner-ink: #17233e;
  --planner-muted: #74819a;
  --planner-blue: #2f5dcc;
  --planner-border: #e7ebf2;
  padding-bottom: 3rem;
}

.planner-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.4rem;
}

.planner-eyebrow,
.planner-section-label {
  color: #7887a2;
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.planner-eyebrow {
  margin-bottom: 0.5rem;
}

.planner-eyebrow span {
  padding: 0 0.3rem;
  color: #8da7e2;
}

.planner-heading .page-title {
  color: var(--planner-ink);
  font-size: clamp(1.7rem, 3vw, 2.2rem);
  letter-spacing: -0.045em;
}

.planner-heading .page-subtitle {
  margin-top: 0.4rem;
  font-size: 0.92rem;
}

.planner-live {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.7rem;
  border: 1px solid #dfeee7;
  border-radius: 999px;
  background: #f3fbf7;
  color: #47866a;
  font-size: 0.69rem;
  font-weight: 700;
  white-space: nowrap;
}

.planner-live span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #40a879;
}

.planner-trip-card {
  margin-bottom: 1.7rem;
  overflow: hidden;
  border-radius: 15px;
  background:
    radial-gradient(ellipse at 91% 4%, rgba(108, 158, 255, 0.22), transparent 35%),
    linear-gradient(120deg, #16264d 0%, #233d76 100%);
  box-shadow: 0 12px 30px rgba(28, 48, 94, 0.13);
  color: white;
}

.planner-trip-intro {
  position: relative;
  padding: 1.5rem 1.6rem 0;
}

.planner-trip-icon {
  display: grid;
  width: 35px;
  height: 35px;
  margin-bottom: 0.8rem;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.09);
  color: #a9d8ff;
  font-size: 1.4rem;
}

.planner-trip-intro > p {
  color: #9fb5df;
  font-size: 0.64rem;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.planner-trip-intro h2 {
  margin-top: 0.3rem;
  color: white;
  font-size: 1.35rem;
  letter-spacing: -0.03em;
}

.planner-trip-intro > span:last-child {
  display: block;
  margin-top: 0.3rem;
  color: #c1cce1;
  font-size: 0.8rem;
}

.planner-trip-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 0.8rem;
  margin: 1.25rem 1.6rem 1.55rem;
  padding: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 11px;
  background: rgba(9, 21, 49, 0.35);
}

.planner-trip-fields {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: end;
  gap: 0.7rem;
}

.planner-trip-form .field label {
  margin: 0 0 0.4rem 0.1rem;
  color: #c7d3e9;
  font-size: 0.67rem;
  font-weight: 700;
}

.planner-input {
  display: flex;
  min-height: 43px;
  align-items: center;
  gap: 0.55rem;
  padding: 0 0.7rem;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.97);
}

.planner-point {
  flex: 0 0 8px;
  width: 8px;
  height: 8px;
  border: 2px solid #3764ca;
  border-radius: 50%;
}

.planner-point-destination {
  border-color: #e49a42;
}

.planner-input input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--planner-ink);
  font: inherit;
  font-size: 0.78rem;
}

.planner-input input::placeholder {
  color: #9aa5b7;
}

.planner-trip-direction {
  padding-bottom: 0.6rem;
  color: #b7c8e8;
  font-size: 1.05rem;
}

.planner-trip-submit {
  display: flex;
  gap: 0.5rem;
}

.planner-trip-submit select {
  min-height: 43px;
  max-width: 145px;
  padding: 0 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.17);
  border-radius: 8px;
  background: #fff;
  color: #4a5872;
  font: inherit;
  font-size: 0.72rem;
}

.planner-trip-submit button {
  display: inline-flex;
  min-height: 43px;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0 0.9rem;
  border: 0;
  border-radius: 8px;
  background: #71d5c3;
  color: #163f51;
  font-size: 0.74rem;
  font-weight: 800;
  white-space: nowrap;
}

.planner-trip-submit button:hover:not(:disabled) {
  background: #8ce2d2;
}

.planner-trip-submit button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.planner-inline-error {
  margin: 0.8rem 1.6rem;
  color: #c43f45;
  font-size: 0.79rem;
  font-weight: 600;
}

.planner-trip-card > .planner-inline-error {
  color: #ffc8c8;
}

.planner-trip-result {
  margin: 0 1.6rem 1.5rem;
  padding: 1.1rem;
  border: 1px solid #e6ecf5;
  border-radius: 11px;
  background: #fff;
  color: var(--planner-ink);
}

.planner-no-route {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  color: #86601e;
}

.planner-no-route > span {
  color: #d29d3e;
  font-size: 1.1rem;
}

.planner-no-route strong {
  font-size: 0.85rem;
}

.planner-no-route p {
  margin-top: 0.25rem;
  color: #78839a;
  font-size: 0.76rem;
}

.planner-result-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
}

.planner-result-actions {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
}

.planner-map-link {
  display: inline-flex;
  min-height: 34px;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0 0.65rem;
  border: 1px solid #dfe6f0;
  border-radius: 8px;
  background: #fff;
  color: #355a9e;
  font-size: 0.68rem;
  font-weight: 750;
  text-decoration: none;
  white-space: nowrap;
}

.planner-map-link:hover {
  border-color: #b7c8e4;
  background: #f5f8fd;
}

.planner-map-link svg {
  width: 15px;
  height: 15px;
}

.planner-map-note {
  margin: -0.5rem 0 1rem;
  color: #8691a3;
  font-size: 0.68rem;
}

.planner-result-heading .planner-section-label {
  color: #8290a7;
  font-size: 0.61rem;
}

.planner-result-heading h3 {
  margin-top: 0.25rem;
  color: var(--planner-ink);
  font-size: 1.05rem;
}

.planner-result-heading h3 span {
  margin: 0 0.2rem;
  color: #8d9db8;
}

.planner-result-type {
  padding: 0.3rem 0.55rem;
  border-radius: 999px;
  background: #edf2ff;
  color: #4164b3;
  font-size: 0.61rem;
  font-weight: 800;
  white-space: nowrap;
}

.planner-direct-route {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem;
  border: 1px solid #ebeff5;
  border-radius: 9px;
  background: #fbfcfe;
}

.planner-route-symbol {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 10px;
  background: #edf2ff;
  color: #4167c4;
  font-size: 1.25rem;
}

.planner-route-info > span,
.planner-route-fare small {
  display: block;
  color: #8290a7;
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.planner-route-info strong {
  display: block;
  margin-top: 0.12rem;
  color: #283957;
  font-size: 0.82rem;
}

.planner-route-info small {
  display: block;
  margin-top: 0.14rem;
  color: #7d899d;
  font-size: 0.7rem;
}

.planner-route-facts {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  color: #77849a;
  font-size: 0.7rem;
}

.planner-route-facts strong {
  color: #293a5a;
  font-size: 0.78rem;
}

.planner-route-fare {
  padding-left: 0.85rem;
  border-left: 1px solid #e6eaf1;
}

.planner-route-fare strong {
  display: block;
  margin-top: 0.28rem;
  color: #24385c;
  font-size: 0.8rem;
  white-space: nowrap;
}

.planner-transfer {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.4rem;
}

.planner-transfer article {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.7rem;
  border: 1px solid #ebeff5;
  border-radius: 8px;
  background: #fbfcfe;
}

.planner-transfer-index {
  display: grid;
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  place-items: center;
  border-radius: 9px;
  background: #edf2ff;
  color: #4265b5;
  font-size: 0.68rem;
  font-weight: 800;
}

.planner-transfer article div {
  min-width: 0;
}

.planner-transfer article small {
  display: block;
  color: #8490a4;
  font-size: 0.58rem;
  font-weight: 800;
  letter-spacing: 0.07em;
}

.planner-transfer article strong {
  display: block;
  margin-top: 0.12rem;
  color: #283957;
  font-size: 0.8rem;
}

.planner-transfer article p {
  margin-top: 0.1rem;
  color: #79869a;
  font-size: 0.7rem;
}

.planner-transfer-connector {
  padding-left: 1.35rem;
  color: #8b9bb9;
  font-size: 0.8rem;
}

.planner-trip-totals {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  margin-top: 0.85rem;
  color: #758198;
  font-size: 0.72rem;
}

.planner-trip-totals strong {
  margin-left: 0.25rem;
  color: #283957;
}

.planner-summary {
  margin-top: 0.85rem;
  padding-top: 0.75rem;
  border-top: 1px solid #ebeff5;
  color: #66738b;
  font-size: 0.74rem;
  line-height: 1.6;
}

.planner-tools-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.85rem;
}

.planner-tools-heading h2 {
  margin-top: 0.22rem;
  color: var(--planner-ink);
  font-size: 1.12rem;
  letter-spacing: -0.025em;
}

.planner-tools-heading > span {
  color: #8490a4;
  font-size: 0.72rem;
}

.planner-tools-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: start;
  gap: 1rem;
}

.planner-tool {
  padding: 1.15rem;
  border-color: var(--planner-border);
  border-radius: 12px;
  box-shadow: 0 5px 17px rgba(31, 48, 82, 0.035);
}

.planner-tool-heading {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.planner-tool-icon {
  display: grid;
  flex: 0 0 39px;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 11px;
  font-size: 1.3rem;
  font-weight: 700;
}

.planner-icon-traffic {
  background: #fff4e8;
  color: #d2872b;
}

.planner-icon-clock {
  background: #eaf5ff;
  color: #3384b8;
}

.planner-icon-compare {
  background: #f2edff;
  color: #7956bd;
}

.planner-tool-heading h3 {
  color: #263652;
  font-size: 0.88rem;
}

.planner-tool-heading p {
  margin-top: 0.18rem;
  color: #8390a4;
  font-size: 0.7rem;
}

.planner-tool-form {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.planner-tool-form .field label {
  color: #5f6e86;
  font-size: 0.68rem;
}

.planner-tool-form select,
.planner-tool-form input {
  min-height: 39px;
  border-color: #e2e7ef;
  border-radius: 7px;
  background: #fbfcfe;
  font-size: 0.76rem;
}

.planner-tool-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
}

.planner-tool-button {
  display: flex;
  min-height: 37px;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border: 1px solid #dce5f5;
  border-radius: 7px;
  background: #f4f7fd;
  color: #355aab;
  font-size: 0.73rem;
  font-weight: 700;
}

.planner-tool-button:hover:not(:disabled) {
  border-color: #b9c9e8;
  background: #edf2fc;
}

.planner-tool-button:disabled {
  cursor: wait;
  opacity: 0.6;
}

.planner-analysis-result {
  margin-top: 0.95rem;
  padding: 0.85rem;
  border: 1px solid #e9edf4;
  border-radius: 8px;
  background: #fbfcfe;
}

.planner-analysis-main,
.planner-analysis-detail {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.planner-analysis-main > strong {
  color: #2c3c5a;
  font-size: 0.9rem;
}

.planner-analysis-main > strong small {
  color: #8290a5;
  font-size: 0.64rem;
  font-weight: 600;
}

.planner-congestion {
  padding: 0.27rem 0.5rem;
  border-radius: 999px;
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.level-normal {
  background: #e8f7ef;
  color: #258257;
}

.level-moderado {
  background: #fff4df;
  color: #a36a18;
}

.level-alto,
.level-critico {
  background: #ffeded;
  color: #b74444;
}

.planner-analysis-detail {
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 0.45rem 1.1rem;
  margin-top: 0.65rem;
  color: #7b879b;
  font-size: 0.68rem;
}

.planner-analysis-detail strong {
  color: #44536d;
}

.planner-analysis-result > p {
  margin-top: 0.7rem;
  padding-top: 0.6rem;
  border-top: 1px solid #e8edf4;
  color: #76839a;
  font-size: 0.69rem;
  line-height: 1.5;
}

.planner-helper {
  margin-top: 0.65rem;
  color: #9a6b22;
  font-size: 0.7rem;
}

.planner-comparison {
  grid-column: 1 / -1;
}

.planner-comparison-results {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 0.95rem;
}

.planner-comparison-results article {
  padding: 0.7rem;
  border: 1px solid #e8edf4;
  border-radius: 8px;
  background: #fbfcfe;
}

.planner-comparison-results article > span {
  display: block;
  color: #7f8ba0;
  font-size: 0.61rem;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.planner-comparison-results article > strong {
  display: block;
  margin-top: 0.2rem;
  color: #2d3d5a;
  font-size: 0.76rem;
}

.planner-comparison-results article > div {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.6rem;
  color: #7e899c;
  font-size: 0.68rem;
}

.planner-comparison-results article > div strong {
  color: #344966;
  white-space: nowrap;
}

.planner-winners {
  display: flex;
  grid-column: 1 / -1;
  flex-wrap: wrap;
  gap: 0.5rem 1.2rem;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  background: #f2f6ff;
  color: #687895;
  font-size: 0.7rem;
}

.planner-winners strong {
  margin-left: 0.25rem;
  color: #3156a0;
}

.planner-comparison-results > p {
  grid-column: 1 / -1;
  color: #78849a;
  font-size: 0.7rem;
  line-height: 1.5;
}

.planner-loading,
.planner-empty {
  display: flex;
  min-height: 210px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  color: var(--planner-muted);
  text-align: center;
}

.planner-empty strong {
  color: var(--planner-ink);
  font-size: 1rem;
}

.planner-empty span {
  font-size: 0.82rem;
}

.planner-empty a {
  margin-top: 0.3rem;
  color: var(--planner-blue);
  font-size: 0.8rem;
  font-weight: 700;
  text-decoration: none;
}

.planner-retry {
  margin-top: 0.3rem;
  padding: 0.4rem 0.7rem;
  border: 1px solid #dce5f5;
  border-radius: 7px;
  background: #f4f7fd;
  color: var(--planner-blue);
  font-size: 0.78rem;
  font-weight: 700;
}

.planner-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #dfe7f6;
  border-top-color: #3764ca;
  border-radius: 50%;
  animation: planner-spin 0.8s linear infinite;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

@keyframes planner-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .planner-trip-form {
    grid-template-columns: 1fr;
  }

  .planner-trip-submit {
    justify-content: flex-end;
  }
}

@media (max-width: 700px) {
  .planner-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .planner-result-actions {
    width: 100%;
    align-items: center;
    flex-wrap: wrap;
  }

  .planner-trip-intro {
    padding: 1.2rem 1rem 0;
  }

  .planner-trip-form {
    margin: 1rem;
    padding: 0.7rem;
  }

  .planner-trip-fields {
    grid-template-columns: 1fr;
  }

  .planner-trip-direction {
    display: none;
  }

  .planner-trip-submit {
    flex-wrap: wrap;
  }

  .planner-trip-submit select {
    flex: 1;
    max-width: none;
  }

  .planner-trip-submit button {
    flex: 1 1 100%;
  }

  .planner-inline-error {
    margin: 0.7rem 1rem;
  }

  .planner-trip-result {
    margin: 0 1rem 1rem;
    padding: 0.8rem;
  }

  .planner-direct-route {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .planner-route-facts,
  .planner-route-fare {
    grid-column: 2;
  }

  .planner-route-fare {
    padding: 0.5rem 0 0;
    border-top: 1px solid #e6eaf1;
    border-left: 0;
  }

  .planner-tools-grid {
    grid-template-columns: 1fr;
  }

  .planner-comparison {
    grid-column: auto;
  }
}

@media (max-width: 450px) {
  .planner-tools-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.25rem;
  }

  .planner-tool-fields,
  .planner-comparison-results {
    grid-template-columns: 1fr;
  }

  .planner-winners,
  .planner-comparison-results > p {
    grid-column: auto;
  }

  .planner-result-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.45rem;
  }
}
</style>
