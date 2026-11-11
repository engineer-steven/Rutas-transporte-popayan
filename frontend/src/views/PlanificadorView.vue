<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRutasStore } from '@/stores/rutas'
import planificadorService from '@/services/planificadorService'
import OpenStreetMapRoutes from '@/components/maps/OpenStreetMapRoutes.vue'

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

const alternativasPasajero = reactive([])
const errorPasajero = ref('')
const plusDemoActivo = ref(false)
const avisoPago = ref('')

const resultadosComparacion = computed(() => {
  if (!comparativa.resultado) return []

  return Object.entries(comparativa.resultado).filter(
    ([, valor]) => valor && typeof valor === 'object' && !Array.isArray(valor),
  )
})

const tramosMapa = computed(() => {
  const coloresEmpresa = ['#2865d8', '#e26a3d', '#189b77', '#8a5bd1', '#d2a323']
  const empresas = new Map()
  const tramos = []
  const colorEmpresa = (empresa) => {
    if (!empresas.has(empresa)) {
      empresas.set(empresa, coloresEmpresa[empresas.size % coloresEmpresa.length])
    }
    return empresas.get(empresa)
  }

  for (const alternativa of alternativasPasajero) {
    if (alternativa.tipo === 'directo') {
      const ruta = alternativa.resultado.ruta_recomendada
      tramos.push({
        empresa: ruta.empresa,
        codigo: ruta.codigo,
        origen: ruta.paradero_subida,
        destino: ruta.paradero_bajada,
        color: colorEmpresa(ruta.empresa),
      })
      continue
    }

    const { paso_1: primero, paso_2: segundo } = alternativa.resultado
    if (primero && segundo) {
      tramos.push(
        {
          empresa: primero.empresa,
          codigo: primero.ruta,
          origen: primero.subida,
          destino: primero.bajada_transbordo,
          color: colorEmpresa(primero.empresa),
        },
        {
          empresa: segundo.empresa,
          codigo: segundo.ruta,
          origen: primero.bajada_transbordo,
          destino: segundo.llegada,
          color: colorEmpresa(segundo.empresa),
        },
      )
    }
  }

  return tramos
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

async function buscarViajePasajero() {
  const origen = viaje.origin.trim()
  const destino = viaje.destination.trim()
  errorPasajero.value = ''
  alternativasPasajero.splice(0)

  if (!origen || !destino) {
    errorPasajero.value = 'Escribe un punto de origen y uno de destino.'
    return
  }
  if (origen.toLocaleLowerCase('es') === destino.toLocaleLowerCase('es')) {
    errorPasajero.value = 'El origen y el destino deben ser diferentes.'
    return
  }

  cargando.viaje = true
  const respuestas = await Promise.allSettled([
    planificadorService.planificarViajeDirecto(origen, destino),
    planificadorService.planificarViajeTransbordo(origen, destino),
  ])
  const tipos = ['directo', 'transbordo']

  respuestas.forEach((respuesta, index) => {
    if (respuesta.status === 'fulfilled' && respuesta.value.data.encontrado) {
      alternativasPasajero.push({
        tipo: tipos[index],
        resultado: respuesta.value.data,
      })
    }
  })

  if (respuestas.every((respuesta) => respuesta.status === 'rejected')) {
    errorPasajero.value = mensajeError(
      respuestas[0].reason,
      'No fue posible consultar las rutas. Inténtalo nuevamente.',
    )
  } else if (respuestas.some((respuesta) => respuesta.status === 'rejected')) {
    errorPasajero.value = 'No se pudieron consultar todas las alternativas. Algunas opciones pueden faltar.'
  }

  if (!alternativasPasajero.length && !errorPasajero.value) {
    viaje.resultado = {
      encontrado: false,
      mensaje: 'Prueba con otros barrios o puntos de referencia de Popayán.',
    }
  } else {
    viaje.resultado = null
  }

  cargando.viaje = false
}

function alternarDemoPlus() {
  plusDemoActivo.value = !plusDemoActivo.value
  avisoPago.value = plusDemoActivo.value
    ? 'Demo Plus activada: ahora puedes ver los tiempos estimados y detalles de las alternativas.'
    : 'Demo Plus desactivada: vuelves a ver únicamente las rutas.'
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
  <section v-if="auth.role === 'USUARIO'" class="passenger-planner">
    <header class="passenger-planner-heading">
      <div class="passenger-hero-copy">
        <p class="passenger-planner-eyebrow">ENRUTATE · POPAYÁN</p>
        <h1>Muévete por tu ciudad <span>de forma inteligente</span></h1>
        <p>
          {{
            plusDemoActivo
              ? 'Consulta rutas y tiempos estimados para elegir cómo llegar.'
              : 'Tu ciudad, mejor conectada. Encuentra las rutas para llegar a tu destino.'
          }}
        </p>
      </div>
      <div class="passenger-hero-visual" aria-hidden="true">
        <span class="passenger-hero-city">POPAYÁN, CAUCA</span>
        <svg viewBox="0 0 360 220" fill="none">
          <path
            d="M25 164C78 145 82 88 140 104s47 73 103 42 50-74 92-86"
            stroke="currentColor"
            stroke-width="8"
            stroke-linecap="round"
            stroke-dasharray="2 15"
          />
          <path
            d="M18 194c54-18 83-12 118-47s65-20 99-2 68 20 119-16"
            stroke="#85d5c7"
            stroke-width="3"
            stroke-linecap="round"
          />
          <circle cx="25" cy="164" r="13" fill="#fff" stroke="#159c8a" stroke-width="6" />
          <circle cx="335" cy="60" r="13" fill="#fff" stroke="#ed684f" stroke-width="6" />
          <g transform="translate(145 36)">
            <rect width="83" height="74" rx="22" fill="#fff" />
            <path
              d="M21 45V31c0-7 5-12 12-12h17c7 0 12 5 12 12v14M18 45h47v9H18zM26 54v5m31-5v5M29 30h25"
              stroke="#174c78"
              stroke-width="5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <circle cx="29" cy="45" r="3" fill="#159c8a" />
            <circle cx="55" cy="45" r="3" fill="#159c8a" />
          </g>
        </svg>
        <span class="passenger-hero-map-label">Rutas conectadas</span>
      </div>
    </header>

    <section id="passenger-search" class="passenger-search-card">
      <form class="passenger-search-form" @submit.prevent="buscarViajePasajero">
        <div class="passenger-search-fields">
          <label class="passenger-location-field" for="passenger-origin">
            <span class="passenger-location-icon passenger-origin-icon" aria-hidden="true"></span>
            <span>
              <small>PUNTO DE ORIGEN</small>
              <input
                id="passenger-origin"
                v-model="viaje.origin"
                name="origin"
                autocomplete="street-address"
                placeholder="Ej. La Paz, Centro..."
                maxlength="120"
                required
              />
            </span>
          </label>
          <span class="passenger-search-arrow" aria-hidden="true">→</span>
          <label class="passenger-location-field" for="passenger-destination">
            <span class="passenger-location-icon passenger-destination-icon" aria-hidden="true"></span>
            <span>
              <small>PUNTO DE DESTINO</small>
              <input
                id="passenger-destination"
                v-model="viaje.destination"
                name="destination"
                placeholder="Ej. Campanario, Hospital..."
                maxlength="120"
                required
              />
            </span>
          </label>
        </div>
        <button class="passenger-search-button" type="submit" :disabled="cargando.viaje">
          {{ cargando.viaje ? 'Buscando rutas…' : 'Buscar mi recorrido' }}
          <span aria-hidden="true">→</span>
        </button>
      </form>
      <p class="passenger-search-hint">
        <span aria-hidden="true">ⓘ</span>
        Escribe barrios o paraderos registrados en Popayán para encontrar coincidencias.
      </p>
    </section>

    <nav class="passenger-quick-links" aria-label="Accesos rápidos">
      <a class="passenger-quick-card" href="#passenger-search">
        <span class="passenger-quick-icon quick-icon-plan" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none">
            <path d="M6 24V9l7-4 7 4 6-3v15l-6 4-7-4-7 3Z" />
            <path d="M13 5v16m7-12v16" />
          </svg>
        </span>
        <span><strong>Planear viaje</strong><small>Origen y destino</small></span>
        <span class="passenger-quick-arrow" aria-hidden="true">›</span>
      </a>
      <RouterLink class="passenger-quick-card" to="/rutas">
        <span class="passenger-quick-icon quick-icon-routes" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none">
            <path d="M7 25V8m0 0 4 4m-4-4L3 12m22-5v17m0 0-4-4m4 4 4-4M7 16h9a4 4 0 0 0 4-4V8" />
            <circle cx="20" cy="8" r="3" />
          </svg>
        </span>
        <span><strong>Explorar rutas</strong><small>Ver recorridos</small></span>
        <span class="passenger-quick-arrow" aria-hidden="true">›</span>
      </RouterLink>
      <a class="passenger-quick-card" href="#passenger-plans">
        <span class="passenger-quick-icon quick-icon-plus" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none">
            <path d="m16 3 3.8 7.7 8.5 1.2-6.2 6 1.5 8.5-7.6-4-7.6 4 1.5-8.5-6.2-6 8.5-1.2L16 3Z" />
          </svg>
        </span>
        <span><strong>Planes EnRutate</strong><small>Conoce Plus</small></span>
        <span class="passenger-quick-arrow" aria-hidden="true">›</span>
      </a>
    </nav>

    <p v-if="errorPasajero" class="passenger-error" role="alert">{{ errorPasajero }}</p>

    <section v-if="alternativasPasajero.length" class="passenger-results" aria-live="polite">
      <div class="passenger-results-heading">
        <div>
          <p>ALTERNATIVAS PARA TU VIAJE</p>
          <h2>{{ viaje.origin }} <span>→</span> {{ viaje.destination }}</h2>
        </div>
        <span>{{ alternativasPasajero.length }} opciones encontradas</span>
      </div>

      <div class="passenger-results-layout">
        <OpenStreetMapRoutes class="passenger-map-card" :segments="tramosMapa" />

        <div class="passenger-alternatives">
          <article
            v-for="alternativa in alternativasPasajero"
            :key="alternativa.tipo"
            class="passenger-alternative-card"
          >
            <div class="passenger-alternative-topline">
              <span
                v-if="plusDemoActivo"
                :class="['passenger-alternative-badge', `badge-${alternativa.tipo}`]"
              >
                {{ alternativa.tipo === 'directo' ? 'DIRECTA' : 'CON TRANSBORDO' }}
              </span>
              <span
                v-if="alternativa.tipo === 'directo'"
                class="passenger-company-dot"
                :style="{
                  '--company-color':
                    tramosMapa.find(
                      (tramo) => tramo.codigo === alternativa.resultado.ruta_recomendada.codigo,
                    )?.color || '#2865d8',
                }"
              ></span>
            </div>

            <template v-if="alternativa.tipo === 'directo'">
              <h3>{{ alternativa.resultado.ruta_recomendada.codigo }}</h3>
              <p class="passenger-company">{{ alternativa.resultado.ruta_recomendada.empresa }}</p>
              <p v-if="plusDemoActivo" class="passenger-alternative-path">
                {{ alternativa.resultado.ruta_recomendada.paradero_subida }}
                <span>→</span>
                {{ alternativa.resultado.ruta_recomendada.paradero_bajada }}
              </p>
              <div v-if="plusDemoActivo" class="passenger-alternative-facts">
                <span>~{{ alternativa.resultado.ruta_recomendada.minutos_estimados }} min</span>
                <span>Sin transbordo</span>
                <strong>{{ formatoCOP(alternativa.resultado.ruta_recomendada.tarifa_cop) }}</strong>
              </div>
            </template>
            <template v-else>
              <h3>
                {{ alternativa.resultado.paso_1.ruta }}
                <span>+</span>
                {{ alternativa.resultado.paso_2.ruta }}
              </h3>
              <p class="passenger-company">
                {{ alternativa.resultado.paso_1.empresa }}
                <span>·</span>
                {{ alternativa.resultado.paso_2.empresa }}
              </p>
              <p v-if="plusDemoActivo" class="passenger-alternative-path">
                Transbordo en {{ alternativa.resultado.paso_1.bajada_transbordo }}
              </p>
              <div v-if="plusDemoActivo" class="passenger-alternative-facts">
                <span>~{{ alternativa.resultado.minutos_estimados }} min</span>
                <span>1 transbordo</span>
                <strong>{{ formatoCOP(alternativa.resultado.tarifa_total_cop) }}</strong>
              </div>
            </template>
          </article>
        </div>
      </div>
      <p class="passenger-map-disclaimer">
        Los trazos del mapa son aproximaciones sobre calles de OpenStreetMap; no representan los
        recorridos oficiales de los buses.
        <template v-if="plusDemoActivo">Tiempos y tarifas son estimados.</template>
      </p>
    </section>
    <section
      v-else-if="viaje.resultado && !viaje.resultado.encontrado"
      class="passenger-no-results"
      role="status"
    >
      <span aria-hidden="true">⌕</span>
      <strong>No encontramos una ruta para esos puntos</strong>
      <p>{{ viaje.resultado.mensaje }}</p>
    </section>

    <section id="passenger-plans" class="passenger-plans">
      <header class="passenger-plans-heading">
        <div>
          <p>ELIGE CÓMO MOVERTE</p>
          <h2>Nuestros planes</h2>
        </div>
        <a href="#passenger-plan-plus">Conoce más <span aria-hidden="true">→</span></a>
      </header>

      <div class="passenger-plans-grid">
        <article class="passenger-plan-card passenger-plan-basic">
          <span class="passenger-plan-badge">BÁSICO</span>
          <h3>Gratis</h3>
          <p>Consulta rutas y encuentra tu destino.</p>
          <ul>
            <li><span aria-hidden="true">✓</span> Consultar rutas</li>
            <li><span aria-hidden="true">✓</span> Mapa interactivo</li>
          </ul>
          <button
            class="passenger-plan-button passenger-plan-button-basic"
            type="button"
            :disabled="!plusDemoActivo"
            :aria-pressed="!plusDemoActivo"
            @click="plusDemoActivo && alternarDemoPlus()"
          >
            {{ plusDemoActivo ? 'Usar plan básico' : 'Plan básico activo' }}
          </button>
        </article>

        <article id="passenger-plan-plus" class="passenger-plan-card passenger-plan-plus">
          <span class="passenger-plan-ornament" aria-hidden="true">✦</span>
          <span class="passenger-plan-badge">✦ PLUS</span>
          <h3>Más beneficios para ti</h3>
          <p>Información adicional para elegir mejor tu recorrido.</p>
          <ul>
            <li><span aria-hidden="true">✓</span> Tiempo estimado de viaje</li>
            <li><span aria-hidden="true">✓</span> Alternativas con menos transbordos</li>
            <li><span aria-hidden="true">✓</span> Detalles de cada recorrido</li>
          </ul>
          <button
            class="passenger-plan-button passenger-plan-button-plus"
            type="button"
            :disabled="plusDemoActivo"
            :aria-pressed="plusDemoActivo"
            @click="!plusDemoActivo && alternarDemoPlus()"
          >
            {{ plusDemoActivo ? 'Demo Plus activa' : 'Probar Plus' }}
            <span aria-hidden="true">{{ plusDemoActivo ? '✓' : '→' }}</span>
          </button>
          <span class="passenger-plan-reassurance">Demo sin cobros ni suscripción</span>
        </article>
      </div>
      <p v-if="avisoPago" class="passenger-plan-notice" role="status" aria-live="polite">
        {{ avisoPago }}
      </p>
    </section>
  </section>

  <section v-else class="page planner-page">
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
.passenger-planner {
  --passenger-ink: #17213a;
  --passenger-muted: #74819a;
  --passenger-blue: #174c78;
  --passenger-teal: #079985;
  width: min(100%, 1220px);
  margin: 0 auto;
  padding: clamp(0.75rem, 2.4vw, 1.8rem) 0 4rem;
}

.passenger-planner-heading {
  position: relative;
  display: grid;
  min-height: 285px;
  grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.9fr);
  align-items: center;
  gap: 1rem;
  overflow: hidden;
  margin-bottom: 1.15rem;
  padding: clamp(1.5rem, 5vw, 3.6rem);
  border: 1px solid #dce9f5;
  border-radius: 26px;
  background:
    radial-gradient(ellipse at 86% 16%, rgba(161, 218, 228, 0.42), transparent 38%),
    linear-gradient(112deg, #f3f8ff 0%, #eef8f7 100%);
  box-shadow: 0 16px 40px rgba(27, 68, 104, 0.08);
}

.passenger-planner-heading::before,
.passenger-planner-heading::after {
  position: absolute;
  z-index: 0;
  border: 1px solid rgba(17, 146, 132, 0.09);
  border-radius: 50%;
  content: '';
  pointer-events: none;
}

.passenger-planner-heading::before {
  top: -155px;
  right: 3%;
  width: 410px;
  height: 410px;
}

.passenger-planner-heading::after {
  right: 9%;
  bottom: -232px;
  width: 420px;
  height: 420px;
}

.passenger-hero-copy,
.passenger-hero-visual {
  position: relative;
  z-index: 1;
}

.passenger-planner-eyebrow,
.passenger-results-heading > div > p,
.passenger-plans-heading > div > p {
  color: #7887a2;
  font-size: 0.65rem;
  font-weight: 850;
  letter-spacing: 0.14em;
}

.passenger-planner-heading h1 {
  max-width: 650px;
  margin-top: 0.75rem;
  color: #102d54;
  font-size: clamp(2.15rem, 5vw, 3.6rem);
  font-weight: 820;
  letter-spacing: -0.06em;
  line-height: 1.02;
}

.passenger-planner-heading h1 span {
  display: block;
  margin-top: 0.2rem;
  color: var(--passenger-teal);
  font-style: italic;
}

.passenger-hero-copy > p:last-child {
  max-width: 43ch;
  margin-top: 0.85rem;
  color: #64758e;
  font-size: 0.95rem;
  line-height: 1.65;
}

.passenger-hero-visual {
  display: grid;
  min-height: 205px;
  align-content: center;
  justify-items: center;
  color: #149889;
}

.passenger-hero-visual svg {
  width: min(100%, 360px);
  overflow: visible;
  filter: drop-shadow(0 13px 15px rgba(29, 96, 114, 0.12));
}

.passenger-hero-city,
.passenger-hero-map-label {
  color: #63839a;
  font-size: 0.58rem;
  font-weight: 850;
  letter-spacing: 0.16em;
}

.passenger-hero-map-label {
  margin-top: -0.15rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(14, 147, 132, 0.15);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #128c7d;
  letter-spacing: 0.04em;
}

.passenger-search-card {
  position: relative;
  z-index: 2;
  width: min(100%, 990px);
  margin: -2.25rem auto 0;
  padding: clamp(1rem, 2.4vw, 1.55rem);
  border: 1px solid rgba(222, 230, 240, 0.94);
  border-radius: 21px;
  background: #fff;
  box-shadow: 0 20px 46px rgba(30, 65, 101, 0.14);
}

.passenger-search-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.passenger-search-fields {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
  overflow: hidden;
  border: 1px solid #e6ebf2;
  border-radius: 15px;
  background: #fff;
}

.passenger-location-field {
  display: flex;
  min-width: 0;
  min-height: 76px;
  align-items: center;
  gap: 0.9rem;
  padding: 0 1rem;
  background: #fff;
  cursor: text;
}

.passenger-location-field + .passenger-search-arrow {
  display: none;
}

.passenger-location-field + .passenger-search-arrow + .passenger-location-field {
  border-top: 1px solid #e8edf3;
}

.passenger-location-field:focus-within {
  background: #fbfdff;
  box-shadow: inset 3px 0 #139b8b;
}

.passenger-location-field > span:last-child {
  display: block;
  min-width: 0;
  flex: 1;
}

.passenger-location-field small {
  display: block;
  margin-bottom: 0.24rem;
  color: #7889a1;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.passenger-location-field input {
  width: 100%;
  min-width: 0;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--passenger-ink);
  font: inherit;
  font-size: 1rem;
}

.passenger-location-field input::placeholder {
  color: #a4afbf;
}

.passenger-location-icon {
  position: relative;
  display: block;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border: 0;
  border-radius: 50% 50% 50% 4px;
  background: #e6f5f2;
  transform: rotate(-45deg);
}

.passenger-location-icon::before {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 14px;
  height: 14px;
  border: 3px solid #119b89;
  border-radius: 50%;
  content: '';
}

.passenger-origin-icon::after {
  position: absolute;
  display: none;
  content: '';
}

.passenger-destination-icon {
  background: #fff0ec;
}

.passenger-destination-icon::before {
  border-color: #e35d42;
}

.passenger-search-arrow {
  display: none;
}

.passenger-search-button {
  display: inline-flex;
  width: 100%;
  min-height: 55px;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 0 1.1rem;
  border: 0;
  border-radius: 13px;
  background: linear-gradient(105deg, #124675, #18558a);
  box-shadow: 0 8px 18px rgba(20, 75, 122, 0.2);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 780;
  white-space: nowrap;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease;
}

.passenger-search-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 11px 22px rgba(20, 75, 122, 0.26);
}

.passenger-search-button:focus-visible,
.passenger-plan-button:focus-visible,
.passenger-quick-card:focus-visible {
  outline: 3px solid #77c8bb;
  outline-offset: 3px;
}

.passenger-search-button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.passenger-search-hint {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  margin: 0.8rem 0 0 0.2rem;
  color: #8390a4;
  font-size: 0.69rem;
  line-height: 1.5;
}

.passenger-search-hint span {
  color: #168f81;
}

.passenger-quick-links {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
  margin: 1.2rem 0 1.5rem;
}

.passenger-quick-card {
  display: grid;
  min-width: 0;
  grid-template-columns: 52px minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.65rem;
  padding: 0.9rem;
  border: 1px solid #e6ebf2;
  border-radius: 15px;
  background: #fff;
  box-shadow: 0 8px 22px rgba(24, 42, 75, 0.045);
  color: inherit;
  text-decoration: none;
  transition:
    transform 160ms ease,
    border-color 160ms ease,
    box-shadow 160ms ease;
}

.passenger-quick-card:hover {
  transform: translateY(-2px);
  border-color: #c6e4df;
  box-shadow: 0 12px 25px rgba(24, 82, 100, 0.09);
}

.passenger-quick-icon {
  display: grid;
  width: 50px;
  height: 50px;
  place-items: center;
  border-radius: 14px;
  background: #e8f4fc;
  color: #1675ae;
}

.passenger-quick-icon svg {
  width: 31px;
  height: 31px;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.quick-icon-routes {
  background: #e9f7f3;
  color: #0c9b82;
}

.quick-icon-plus {
  background: #f1edff;
  color: #7354c4;
}

.passenger-quick-card > span:nth-child(2) {
  display: grid;
  min-width: 0;
  gap: 0.25rem;
}

.passenger-quick-card strong {
  overflow: hidden;
  color: #193354;
  font-size: 0.8rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.passenger-quick-card small {
  color: #7a879b;
  font-size: 0.68rem;
}

.passenger-quick-arrow {
  color: #1d5e98;
  font-size: 1.5rem;
  line-height: 1;
}

.passenger-error {
  margin-top: 0.8rem;
  padding: 0.75rem 0.9rem;
  border: 1px solid #fecaca;
  border-radius: 9px;
  background: #fff5f5;
  color: #b42332;
  font-size: 0.78rem;
}

.passenger-results {
  margin-top: 1.4rem;
}

.passenger-results-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.8rem;
}

.passenger-results-heading h2 {
  margin-top: 0.22rem;
  color: var(--passenger-ink);
  font-size: clamp(1.05rem, 2.5vw, 1.35rem);
  letter-spacing: -0.03em;
}

.passenger-results-heading h2 span {
  padding: 0 0.2rem;
  color: #8d9db8;
}

.passenger-results-heading > span {
  color: #8290a4;
  font-size: 0.71rem;
  white-space: nowrap;
}

.passenger-results-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(290px, 0.75fr);
  align-items: start;
  gap: 1rem;
}

.passenger-alternatives {
  display: grid;
  gap: 0.7rem;
}

.passenger-alternative-card {
  padding: 1rem;
  border: 1px solid #e6eaf1;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 8px 20px rgba(24, 42, 75, 0.045);
}

.passenger-alternative-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.passenger-alternative-badge {
  padding: 0.28rem 0.5rem;
  border-radius: 999px;
  font-size: 0.57rem;
  font-weight: 850;
  letter-spacing: 0.06em;
}

.badge-directo {
  background: #edf3ff;
  color: #315fc4;
}

.badge-transbordo {
  background: #fff3e8;
  color: #b56b2c;
}

.passenger-company-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--company-color);
}

.passenger-alternative-card h3 {
  margin-top: 0.65rem;
  color: #1d2b48;
  font-size: 1.05rem;
}

.passenger-alternative-card h3 span {
  color: #8794a9;
}

.passenger-company {
  margin-top: 0.12rem;
  color: #73819a;
  font-size: 0.72rem;
}

.passenger-company span {
  padding: 0 0.2rem;
}

.passenger-alternative-path {
  margin-top: 0.7rem;
  color: #3d4c67;
  font-size: 0.76rem;
  line-height: 1.45;
}

.passenger-alternative-path span {
  padding: 0 0.25rem;
  color: #8d9db8;
}

.passenger-alternative-facts {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.8rem;
  padding-top: 0.7rem;
  border-top: 1px solid #edf0f5;
  color: #6e7c94;
  font-size: 0.67rem;
}

.passenger-alternative-facts strong {
  color: #263a5f;
  font-size: 0.73rem;
}

.passenger-map-disclaimer {
  margin-top: 0.55rem;
  color: #8994a6;
  font-size: 0.66rem;
  line-height: 1.55;
}

.passenger-no-results {
  display: grid;
  justify-items: center;
  gap: 0.35rem;
  margin-top: 1.4rem;
  padding: 1.5rem;
  border: 1px dashed #dfe5ef;
  border-radius: 14px;
  background: #fbfcfe;
  text-align: center;
}

.passenger-no-results > span {
  color: #7288b8;
  font-size: 1.5rem;
}

.passenger-no-results strong {
  color: #293752;
  font-size: 0.9rem;
}

.passenger-no-results p {
  color: #74819a;
  font-size: 0.76rem;
}

.passenger-plans {
  margin-top: 2rem;
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

.passenger-plans-heading h2 {
  margin-top: 0.15rem;
  color: #152f53;
  font-size: clamp(1.35rem, 3vw, 1.8rem);
  letter-spacing: -0.035em;
}

.passenger-plans-heading > a {
  color: #1b6593;
  font-size: 0.76rem;
  font-weight: 750;
  text-decoration: none;
}

.passenger-plans-heading > a:hover {
  color: #078e79;
}

.passenger-plans-heading > a span {
  padding-left: 0.25rem;
  font-size: 1rem;
  text-decoration: none;
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

.passenger-plan-plus h3 {
  font-size: clamp(1.05rem, 2.5vw, 1.45rem);
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
  align-items: flex-start;
  gap: 0.55rem;
}

.passenger-plan-card li span {
  color: #1687c0;
  font-size: 0.92rem;
  font-weight: 900;
  line-height: 1.1;
}

.passenger-plan-plus li span {
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

.passenger-plan-reassurance {
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

.passenger-plan-notice {
  margin-top: 0.75rem;
  padding: 0.8rem 1rem;
  border: 1px solid #cce9e3;
  border-radius: 12px;
  background: #f0faf7;
  color: #38695f;
  font-size: 0.75rem;
  line-height: 1.5;
}

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
  .passenger-planner-heading {
    grid-template-columns: minmax(0, 1fr) minmax(220px, 0.75fr);
  }

  .passenger-hero-visual {
    min-height: 170px;
  }

  .passenger-results-layout {
    grid-template-columns: 1fr;
  }

  .planner-trip-form {
    grid-template-columns: 1fr;
  }

  .planner-trip-submit {
    justify-content: flex-end;
  }
}

@media (max-width: 700px) {
  .passenger-planner-heading {
    min-height: 220px;
    grid-template-columns: minmax(0, 1fr) minmax(90px, 0.35fr);
    gap: 0.25rem;
    padding: 1.45rem 1.2rem 2.6rem;
    border-radius: 21px;
  }

  .passenger-planner-heading h1 {
    margin-top: 0.55rem;
    font-size: clamp(1.75rem, 7vw, 2.35rem);
  }

  .passenger-hero-copy > p:last-child {
    margin-top: 0.6rem;
    font-size: 0.79rem;
  }

  .passenger-hero-visual {
    min-height: 130px;
    min-width: 0;
  }

  .passenger-hero-visual svg {
    width: 100%;
    max-width: 140px;
  }

  .passenger-hero-city {
    font-size: 0.43rem;
  }

  .passenger-hero-map-label {
    padding: 0.3rem 0.5rem;
    font-size: 0.55rem;
    white-space: nowrap;
  }

  .passenger-search-card {
    margin-top: -1.65rem;
    padding: 0.85rem;
    border-radius: 17px;
  }

  .passenger-location-field {
    min-height: 67px;
    gap: 0.65rem;
    padding: 0 0.7rem;
  }

  .passenger-location-icon {
    width: 29px;
    height: 29px;
    flex-basis: 29px;
  }

  .passenger-location-icon::before {
    top: 8px;
    left: 8px;
    width: 13px;
    height: 13px;
  }

  .passenger-quick-links {
    gap: 0.45rem;
    margin: 0.9rem 0 1.25rem;
  }

  .passenger-quick-card {
    position: relative;
    display: flex;
    min-height: 115px;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    gap: 0.45rem;
    padding: 0.65rem;
    border-radius: 13px;
  }

  .passenger-quick-icon {
    width: 39px;
    height: 39px;
    border-radius: 11px;
  }

  .passenger-quick-icon svg {
    width: 26px;
    height: 26px;
  }

  .passenger-quick-card > span:nth-child(2) {
    gap: 0.12rem;
  }

  .passenger-quick-card strong {
    max-width: 100%;
    font-size: 0.64rem;
    white-space: normal;
  }

  .passenger-quick-card small {
    font-size: 0.56rem;
  }

  .passenger-quick-arrow {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    font-size: 1rem;
  }

  .passenger-results-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.25rem;
  }

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

  .passenger-plans-heading > a {
    font-size: 0.68rem;
    white-space: nowrap;
  }

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
