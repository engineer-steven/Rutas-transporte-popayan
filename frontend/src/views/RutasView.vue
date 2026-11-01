<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useRutasStore } from '@/stores/rutas'
import { useAuthStore } from '@/stores/auth'

const rutasStore = useRutasStore()
const auth = useAuthStore()
const cargando = ref(false)
const guardando = ref(false)
const eliminandoId = ref(null)
const error = ref('')
const exito = ref('')
const editandoId = ref(null)
const filtroZona = ref('')
const filtroTexto = ref('')

const rutaVacia = () => ({
  code: '',
  company: '',
  origin: '',
  destination: '',
  fare: 3000,
  schedule: '05:30 - 21:00',
  status: 'ACTIVA',
})

const form = reactive(rutaVacia())

const rutasVisibles = computed(() => {
  const termino = filtroTexto.value.trim().toLocaleLowerCase('es')
  if (!termino) return rutasStore.lista

  return rutasStore.lista.filter((ruta) =>
    [ruta.code, ruta.company, ruta.origin, ruta.destination, ruta.schedule, ruta.status]
      .filter(Boolean)
      .some((valor) => String(valor).toLocaleLowerCase('es').includes(termino)),
  )
})

const rutasActivas = computed(
  () => rutasStore.lista.filter((ruta) => String(ruta.status).toUpperCase() === 'ACTIVA').length,
)

const empresas = computed(() => new Set(rutasStore.lista.map((ruta) => ruta.company)).size)

const formatoCOP = (valor) =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(Number(valor) || 0)

function urlGoogleMaps(origen, destino) {
  const query = new URLSearchParams({
    api: '1',
    origin: `${origen}, Popayán, Cauca, Colombia`,
    destination: `${destino}, Popayán, Cauca, Colombia`,
    travelmode: 'transit',
  })
  return `https://www.google.com/maps/dir/?${query.toString()}`
}

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

function limpiarMensajes() {
  error.value = ''
  exito.value = ''
}

function resetForm() {
  Object.assign(form, rutaVacia())
  editandoId.value = null
}

async function cargarRutas() {
  cargando.value = true
  error.value = ''
  try {
    await rutasStore.cargar()
  } catch (e) {
    error.value = mensajeError(
      e,
      'No se pudieron cargar las rutas. Verifica la conexión con el microservicio.',
    )
  } finally {
    cargando.value = false
  }
}

async function buscarPorZona() {
  limpiarMensajes()
  cargando.value = true
  try {
    await rutasStore.buscar(filtroZona.value.trim())
  } catch (e) {
    error.value = mensajeError(e, 'No se pudo completar la búsqueda por zona.')
  } finally {
    cargando.value = false
  }
}

async function verTodas() {
  filtroZona.value = ''
  filtroTexto.value = ''
  limpiarMensajes()
  cargando.value = true
  try {
    await rutasStore.limpiarFiltro()
  } catch (e) {
    error.value = mensajeError(e, 'No se pudieron recuperar todas las rutas.')
  } finally {
    cargando.value = false
  }
}

function editar(ruta) {
  limpiarMensajes()
  editandoId.value = ruta.id
  Object.assign(form, {
    code: ruta.code || '',
    company: ruta.company || '',
    origin: ruta.origin || '',
    destination: ruta.destination || '',
    fare: Number(ruta.fare) || 0,
    schedule: ruta.schedule || '',
    status: ruta.status || 'ACTIVA',
  })
  document.getElementById('formulario-ruta')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

async function guardarRuta() {
  limpiarMensajes()
  guardando.value = true

  const payload = {
    code: form.code.trim().toUpperCase(),
    company: form.company.trim(),
    origin: form.origin.trim(),
    destination: form.destination.trim(),
    fare: Number(form.fare),
    schedule: form.schedule.trim(),
    status: form.status,
  }

  try {
    if (editandoId.value !== null) {
      await rutasStore.actualizar(editandoId.value, payload)
      exito.value = `La ruta ${payload.code} se actualizó correctamente.`
    } else {
      await rutasStore.crear(payload)
      exito.value = `La ruta ${payload.code} se registró correctamente.`
    }
    resetForm()
  } catch (e) {
    error.value = mensajeError(
      e,
      'No se pudo guardar la ruta. Revisa los datos e inténtalo de nuevo.',
    )
  } finally {
    guardando.value = false
  }
}

async function eliminarRuta(ruta) {
  if (
    !window.confirm(`¿Quieres eliminar la ruta ${ruta.code}? Esta acción no se puede deshacer.`)
  ) {
    return
  }

  limpiarMensajes()
  eliminandoId.value = ruta.id
  try {
    await rutasStore.eliminar(ruta.id)
    exito.value = `La ruta ${ruta.code} se eliminó correctamente.`
  } catch (e) {
    error.value = mensajeError(e, `No se pudo eliminar la ruta ${ruta.code}.`)
  } finally {
    eliminandoId.value = null
  }
}

onMounted(cargarRutas)
</script>

<template>
  <section class="page routes-page">
    <header class="routes-heading">
      <div>
        <RouterLink
          v-if="auth.role === 'USUARIO'"
          class="routes-home-link"
          :to="{ name: auth.inicio }"
        >
          <span aria-hidden="true">←</span> Volver al inicio
        </RouterLink>
        <p class="routes-eyebrow">
          {{ auth.esAdmin ? 'MICROSERVICIO 01 • RED DE TRANSPORTE' : 'MOVILIDAD • POPAYÁN' }}
        </p>
        <h1 class="page-title">{{ auth.esAdmin ? 'Gestión de rutas' : 'Explora las rutas' }}</h1>
        <p class="page-subtitle">
          {{
            auth.esAdmin
              ? 'Administra recorridos, operadores y horarios del transporte urbano.'
              : 'Consulta recorridos, horarios y tarifas; elige una ruta para planear tu viaje.'
          }}
        </p>
      </div>
      <a v-if="auth.esAdmin" class="routes-primary-link" href="#formulario-ruta">
        <span aria-hidden="true">＋</span> Nueva ruta
      </a>
    </header>

    <div class="routes-metrics" aria-label="Resumen de rutas">
      <article class="routes-metric">
        <span class="routes-metric-icon routes-metric-icon-blue" aria-hidden="true">↗</span>
        <div>
          <p>Rutas encontradas</p>
          <strong>{{ rutasStore.lista.length }}</strong>
        </div>
      </article>
      <article class="routes-metric">
        <span class="routes-metric-icon routes-metric-icon-green" aria-hidden="true">✓</span>
        <div>
          <p>En operación</p>
          <strong>{{ rutasActivas }}</strong>
        </div>
      </article>
      <article class="routes-metric">
        <span class="routes-metric-icon routes-metric-icon-violet" aria-hidden="true">▦</span>
        <div>
          <p>Empresas vinculadas</p>
          <strong>{{ empresas }}</strong>
        </div>
      </article>
    </div>

    <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>
    <p v-if="exito" class="alert alert-success" role="status">{{ exito }}</p>

    <section v-if="auth.esAdmin" id="formulario-ruta" class="card route-form-card">
      <div class="routes-section-heading">
        <div>
          <p class="routes-section-kicker">
            {{ editandoId !== null ? 'EDICIÓN' : 'CONFIGURACIÓN' }}
          </p>
          <h2>{{ editandoId !== null ? 'Editar ruta' : 'Registrar una ruta' }}</h2>
        </div>
        <span class="routes-form-tag">{{
          editandoId !== null ? `ID ${editandoId}` : 'NUEVO RECORRIDO'
        }}</span>
      </div>

      <form class="routes-form" @submit.prevent="guardarRuta">
        <div class="field">
          <label for="route-code">Código de ruta</label>
          <input
            id="route-code"
            v-model="form.code"
            name="code"
            placeholder="Ej. RUTA-01"
            maxlength="30"
            required
          />
        </div>
        <div class="field">
          <label for="route-company">Empresa operadora</label>
          <input
            id="route-company"
            v-model="form.company"
            name="company"
            placeholder="Ej. Sotracauca"
            maxlength="100"
            required
          />
        </div>
        <div class="field">
          <label for="route-origin">Origen</label>
          <input
            id="route-origin"
            v-model="form.origin"
            name="origin"
            placeholder="Barrio o punto de salida"
            maxlength="150"
            required
          />
        </div>
        <div class="field">
          <label for="route-destination">Destino</label>
          <input
            id="route-destination"
            v-model="form.destination"
            name="destination"
            placeholder="Barrio o punto de llegada"
            maxlength="150"
            required
          />
        </div>
        <div class="field">
          <label for="route-fare">Tarifa (COP)</label>
          <input
            id="route-fare"
            v-model.number="form.fare"
            name="fare"
            type="number"
            min="0"
            step="100"
            required
          />
        </div>
        <div class="field">
          <label for="route-schedule">Horario de operación</label>
          <input
            id="route-schedule"
            v-model="form.schedule"
            name="schedule"
            placeholder="05:30 - 21:00"
            maxlength="80"
            required
          />
        </div>
        <div class="field">
          <label for="route-status">Estado</label>
          <select id="route-status" v-model="form.status" name="status">
            <option value="ACTIVA">Activa</option>
            <option value="INACTIVA">Inactiva</option>
            <option value="MANTENIMIENTO">En mantenimiento</option>
          </select>
        </div>
        <div class="routes-form-actions">
          <button class="btn btn-primary" type="submit" :disabled="guardando">
            {{ guardando ? 'Guardando…' : editandoId !== null ? 'Guardar cambios' : 'Crear ruta' }}
          </button>
          <button
            v-if="editandoId !== null"
            class="btn btn-secondary"
            type="button"
            :disabled="guardando"
            @click="resetForm"
          >
            Cancelar
          </button>
        </div>
      </form>
    </section>

    <section class="card routes-list-card">
      <div class="routes-section-heading routes-list-heading">
        <div>
          <p class="routes-section-kicker">DIRECTORIO</p>
          <h2>
            {{ auth.esAdmin ? 'Rutas del sistema' : 'Rutas disponibles' }}
            <span class="routes-count">{{ rutasVisibles.length }}</span>
          </h2>
        </div>
        <button class="routes-refresh" type="button" :disabled="cargando" @click="cargarRutas">
          <span aria-hidden="true">↻</span> Actualizar
        </button>
      </div>

      <div class="routes-search-row">
        <form class="routes-search" role="search" @submit.prevent="buscarPorZona">
          <label class="sr-only" for="route-zone-search">Buscar por barrio o zona</label>
          <span aria-hidden="true">⌕</span>
          <input
            id="route-zone-search"
            v-model="filtroZona"
            name="zona"
            placeholder="Buscar por barrio o zona..."
            autocomplete="off"
          />
          <button type="submit" :disabled="cargando">Buscar zona</button>
        </form>
        <label class="routes-quick-filter">
          <span aria-hidden="true">⌕</span>
          <span class="sr-only">Filtrar rutas mostradas por nombre, código o empresa</span>
          <input
            v-model="filtroTexto"
            name="filtro"
            placeholder="Filtrar resultados..."
            autocomplete="off"
          />
        </label>
        <button class="routes-clear" type="button" :disabled="cargando" @click="verTodas">
          Limpiar
        </button>
      </div>

      <p class="routes-simulation-note">
        Los recorridos 11–24 son simulaciones e incluyen 85 barrios, sectores y puntos de referencia
        para practicar búsquedas y transbordos. Las empresas aparecen solo como referencia; no son
        asignaciones ni recorridos oficiales, y la lista no es un inventario municipal completo.
      </p>

      <p v-if="cargando" class="routes-empty-state" role="status">
        <span class="routes-loader" aria-hidden="true"></span>
        Cargando información de rutas…
      </p>
      <div v-else-if="error && rutasStore.lista.length === 0" class="routes-empty-state">
        <strong>No se pudo cargar el directorio</strong>
        <span>Verifica la conexión con el microservicio e inténtalo de nuevo.</span>
        <button class="routes-retry" type="button" @click="cargarRutas">Reintentar</button>
      </div>
      <div v-else-if="rutasVisibles.length === 0" class="routes-empty-state">
        <span class="routes-empty-icon" aria-hidden="true">⌕</span>
        <strong>No encontramos rutas</strong>
        <span>Prueba con otro término o limpia los filtros de búsqueda.</span>
      </div>
      <div v-else-if="auth.role === 'USUARIO'" class="passenger-route-grid">
        <article v-for="ruta in rutasVisibles" :key="ruta.id" class="passenger-route-card">
          <div class="passenger-route-heading">
            <span class="route-code-icon" aria-hidden="true">↗</span>
            <div>
              <strong>{{ ruta.code }}</strong>
              <small>{{ ruta.company }}</small>
            </div>
            <span class="route-status route-status-active"><span></span> ACTIVA</span>
          </div>

          <div class="passenger-route-journey">
            <span class="passenger-route-stop">
              <span class="passenger-stop-dot passenger-stop-origin"></span>
              {{ ruta.origin }}
            </span>
            <span class="passenger-route-line" aria-hidden="true"></span>
            <span class="passenger-route-stop">
              <span class="passenger-stop-dot passenger-stop-destination"></span>
              {{ ruta.destination }}
            </span>
          </div>

          <div class="passenger-route-details">
            <div>
              <small>HORARIO</small>
              <strong>{{ ruta.schedule || 'Consultar horario' }}</strong>
            </div>
            <div>
              <small>TARIFA</small>
              <strong>{{ formatoCOP(ruta.fare) }}</strong>
            </div>
          </div>

          <RouterLink
            class="passenger-route-plan"
            :to="{
              name: 'planificador',
              query: { origin: ruta.origin, destination: ruta.destination },
            }"
          >
            Planear un viaje con esta ruta <span aria-hidden="true">→</span>
          </RouterLink>
          <a
            class="passenger-route-map"
            :href="urlGoogleMaps(ruta.origin, ruta.destination)"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ver trayecto en Google Maps <span aria-hidden="true">↗</span>
          </a>
        </article>
      </div>
      <div v-else class="routes-table-wrap">
        <table class="data-table routes-table">
          <thead>
            <tr>
              <th>Ruta</th>
              <th>Recorrido</th>
              <th>Horario</th>
              <th>Tarifa</th>
              <th>Estado</th>
              <th><span class="sr-only">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ruta in rutasVisibles" :key="ruta.id">
              <td>
                <div class="route-identity">
                  <span class="route-code-icon" aria-hidden="true">↗</span>
                  <span>
                    <strong>{{ ruta.code }}</strong>
                    <small>{{ ruta.company }}</small>
                  </span>
                </div>
              </td>
              <td>
                <div class="route-itinerary">
                  <span>{{ ruta.origin }}</span>
                  <span class="route-arrow" aria-hidden="true">→</span>
                  <span>{{ ruta.destination }}</span>
                </div>
              </td>
              <td>{{ ruta.schedule || 'Sin horario' }}</td>
              <td class="route-fare">{{ formatoCOP(ruta.fare) }}</td>
              <td>
                <span
                  :class="[
                    'route-status',
                    String(ruta.status).toUpperCase() === 'ACTIVA'
                      ? 'route-status-active'
                      : 'route-status-paused',
                  ]"
                >
                  <span></span>{{ ruta.status || 'SIN ESTADO' }}
                </span>
              </td>
              <td>
                <div class="route-actions">
                  <button
                    v-if="auth.esAdmin"
                    class="route-action route-action-edit"
                    type="button"
                    :aria-label="`Editar ruta ${ruta.code}`"
                    @click="editar(ruta)"
                  >
                    Editar
                  </button>
                  <button
                    v-if="auth.esAdmin"
                    class="route-action route-action-delete"
                    type="button"
                    :aria-label="`Eliminar ruta ${ruta.code}`"
                    :disabled="eliminandoId === ruta.id"
                    @click="eliminarRuta(ruta)"
                  >
                    {{ eliminandoId === ruta.id ? '…' : 'Eliminar' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>

<style scoped>
.routes-page {
  --routes-ink: #17233e;
  --routes-muted: #74819a;
  --routes-blue: #2e5bce;
  --routes-border: #e7ebf2;
  padding-bottom: 3rem;
}

.routes-heading,
.routes-section-heading,
.routes-list-heading,
.routes-search-row,
.routes-form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.routes-heading {
  margin-bottom: 1.65rem;
}

.routes-eyebrow,
.routes-section-kicker {
  color: #7887a2;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.routes-home-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.65rem;
  color: #536a9d;
  font-size: 0.76rem;
  font-weight: 700;
  text-decoration: none;
}

.routes-home-link:hover {
  color: #294d9e;
}

.routes-home-link span {
  font-size: 1.05rem;
}

.routes-eyebrow {
  margin-bottom: 0.5rem;
}

.routes-eyebrow span {
  padding: 0 0.3rem;
  color: #8da7e2;
}

.routes-heading .page-title {
  color: var(--routes-ink);
  font-size: clamp(1.7rem, 3vw, 2.2rem);
  letter-spacing: -0.045em;
}

.routes-heading .page-subtitle {
  margin-top: 0.4rem;
  font-size: 0.92rem;
}

.routes-primary-link {
  display: inline-flex;
  min-height: 43px;
  align-items: center;
  gap: 0.45rem;
  padding: 0 1rem;
  border-radius: 9px;
  background: #2f5dcc;
  box-shadow: 0 5px 12px rgba(47, 93, 204, 0.17);
  color: white;
  font-size: 0.84rem;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

.routes-primary-link span {
  font-size: 1.1rem;
}

.routes-primary-link:hover {
  background: #244eaf;
}

.routes-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.routes-metric {
  display: flex;
  min-height: 96px;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--routes-border);
  border-radius: 12px;
  background: white;
  box-shadow: 0 4px 14px rgba(31, 48, 82, 0.035);
}

.routes-metric-icon {
  display: grid;
  flex: 0 0 43px;
  width: 43px;
  height: 43px;
  place-items: center;
  border-radius: 12px;
  font-size: 1.3rem;
  font-weight: 700;
}

.routes-metric-icon-blue {
  background: #edf2ff;
  color: #416ad0;
}

.routes-metric-icon-green {
  background: #eaf8f1;
  color: #21946a;
}

.routes-metric-icon-violet {
  background: #f3efff;
  color: #7956c7;
}

.routes-metric p {
  color: var(--routes-muted);
  font-size: 0.78rem;
  font-weight: 600;
}

.routes-metric strong {
  display: block;
  margin-top: 0.15rem;
  color: var(--routes-ink);
  font-size: 1.45rem;
  line-height: 1.2;
}

.route-form-card,
.routes-list-card {
  padding: clamp(1rem, 2.5vw, 1.5rem);
  border-color: var(--routes-border);
  border-radius: 13px;
  box-shadow: 0 5px 18px rgba(31, 48, 82, 0.04);
}

.route-form-card {
  margin-bottom: 1.25rem;
  scroll-margin-top: 1.25rem;
}

.routes-section-heading {
  margin-bottom: 1.1rem;
}

.routes-section-heading h2 {
  margin-top: 0.22rem;
  color: var(--routes-ink);
  font-size: 1.12rem;
  letter-spacing: -0.02em;
}

.routes-form-tag,
.routes-count {
  display: inline-flex;
  min-height: 25px;
  align-items: center;
  justify-content: center;
  padding: 0.1rem 0.55rem;
  border-radius: 999px;
  background: #f0f4fc;
  color: #5e7198;
  font-size: 0.64rem;
  font-weight: 800;
  letter-spacing: 0.07em;
}

.routes-form {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.routes-form .field label {
  color: #50607d;
  font-size: 0.72rem;
}

.routes-form .field input,
.routes-form .field select {
  min-height: 42px;
  border-color: #e1e6ef;
  border-radius: 8px;
  background: #fbfcfe;
  font-size: 0.86rem;
}

.routes-form .field input:focus,
.routes-form .field select:focus {
  border-color: #7594df;
  background: white;
  box-shadow: 0 0 0 3px rgba(62, 103, 204, 0.11);
}

.routes-form-actions {
  justify-content: flex-start;
  align-self: end;
}

.routes-form-actions .btn {
  min-height: 40px;
  border-radius: 8px;
  font-size: 0.8rem;
}

.routes-form-actions .btn-primary {
  background: #2f5dcc;
}

.routes-count {
  min-width: 25px;
  margin-left: 0.4rem;
  background: #edf2ff;
  color: #365fc7;
  font-size: 0.72rem;
  letter-spacing: 0;
  vertical-align: 2px;
}

.routes-refresh,
.routes-clear {
  display: inline-flex;
  min-height: 35px;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0 0.75rem;
  border: 1px solid #e3e8f0;
  border-radius: 8px;
  background: white;
  color: #566783;
  font-size: 0.77rem;
  font-weight: 700;
  white-space: nowrap;
}

.routes-refresh span {
  font-size: 1rem;
}

.routes-refresh:hover,
.routes-clear:hover {
  border-color: #bdcbed;
  color: #2f5dcc;
}

.routes-refresh:disabled,
.routes-clear:disabled {
  cursor: wait;
  opacity: 0.55;
}

.routes-search-row {
  margin: 0.2rem 0 1rem;
}

.routes-simulation-note {
  margin: 0 0 1rem;
  color: #78839a;
  font-size: 0.75rem;
  line-height: 1.5;
}

.routes-search,
.routes-quick-filter {
  display: flex;
  min-height: 40px;
  align-items: center;
  gap: 0.55rem;
  padding: 0 0.65rem 0 0.8rem;
  border: 1px solid #e2e7ef;
  border-radius: 8px;
  background: #fbfcfe;
  color: #98a3b5;
}

.routes-search {
  flex: 1.15;
}

.routes-quick-filter {
  flex: 0.85;
  min-width: 150px;
}

.routes-search > span,
.routes-quick-filter > span:not(.sr-only) {
  font-size: 1.15rem;
}

.routes-search input,
.routes-quick-filter input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--routes-ink);
  font: inherit;
  font-size: 0.8rem;
}

.routes-search:focus-within,
.routes-quick-filter:focus-within {
  border-color: #7594df;
  box-shadow: 0 0 0 3px rgba(62, 103, 204, 0.09);
}

.routes-search button {
  flex: 0 0 auto;
  min-height: 29px;
  padding: 0 0.65rem;
  border: 0;
  border-radius: 6px;
  background: #edf2ff;
  color: #3159bc;
  font-size: 0.73rem;
  font-weight: 700;
}

.routes-search button:disabled {
  cursor: wait;
  opacity: 0.6;
}

.routes-empty-state {
  display: flex;
  min-height: 190px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  color: var(--routes-muted);
  font-size: 0.84rem;
  text-align: center;
}

.routes-empty-state strong {
  margin-top: 0.2rem;
  color: var(--routes-ink);
}

.routes-empty-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 50%;
  background: #f0f4fb;
  color: #7688ac;
  font-size: 1.55rem;
}

.routes-retry {
  margin-top: 0.3rem;
  padding: 0.4rem 0.7rem;
  border: 1px solid #dce5f5;
  border-radius: 7px;
  background: #f4f7fd;
  color: #355aab;
  font-size: 0.74rem;
  font-weight: 700;
}

.routes-loader {
  width: 22px;
  height: 22px;
  border: 2px solid #dfe7f6;
  border-top-color: #3764ca;
  border-radius: 50%;
  animation: routes-spin 0.8s linear infinite;
}

.routes-table-wrap {
  overflow-x: auto;
}

.passenger-route-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr));
  gap: 1rem;
}

.passenger-route-card {
  min-width: 0;
  padding: 1.1rem;
  border: 1px solid #e8ebf0;
  border-radius: 13px;
  background: #fff;
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.18s;
}

.passenger-route-card:hover {
  transform: translateY(-2px);
  border-color: #cbd6eb;
  box-shadow: 0 10px 24px rgba(34, 55, 92, 0.07);
}

.passenger-route-heading {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.passenger-route-heading > div {
  min-width: 0;
  flex: 1;
}

.passenger-route-heading strong,
.passenger-route-heading small {
  display: block;
}

.passenger-route-heading strong {
  color: var(--routes-ink);
  font-size: 0.88rem;
}

.passenger-route-heading small {
  margin-top: 0.1rem;
  color: #858fa1;
  font-size: 0.71rem;
}

.passenger-route-journey {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  margin: 1.15rem 0;
}

.passenger-route-stop {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.6rem;
  color: #40506a;
  font-size: 0.79rem;
  font-weight: 650;
  overflow-wrap: anywhere;
}

.passenger-stop-dot {
  flex: 0 0 9px;
  width: 9px;
  height: 9px;
  border: 2px solid #5276c4;
  border-radius: 50%;
}

.passenger-stop-destination {
  border-color: #df9b53;
  border-radius: 2px;
  transform: rotate(45deg);
}

.passenger-route-line {
  width: 1px;
  height: 12px;
  margin-left: 4px;
  background: #d7dce5;
}

.passenger-route-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
  padding: 0.75rem 0;
  border-top: 1px solid #eef0f4;
}

.passenger-route-details small,
.passenger-route-details strong {
  display: block;
}

.passenger-route-details small {
  color: #8a94a5;
  font-size: 0.61rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.passenger-route-details strong {
  margin-top: 0.2rem;
  color: #34445f;
  font-size: 0.76rem;
  overflow-wrap: anywhere;
}

.passenger-route-plan {
  display: flex;
  min-height: 39px;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.25rem;
  padding: 0 0.75rem;
  border-radius: 8px;
  background: #edf3ff;
  color: #3158ad;
  font-size: 0.74rem;
  font-weight: 750;
  text-decoration: none;
}

.passenger-route-plan:hover {
  background: #e2ebfc;
}

.passenger-route-plan span {
  font-size: 1rem;
}

.passenger-route-map {
  display: flex;
  min-height: 34px;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.35rem 0.25rem 0;
  color: #567363;
  font-size: 0.7rem;
  font-weight: 700;
  text-decoration: none;
}

.passenger-route-map:hover {
  color: #2e6448;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.routes-table {
  min-width: 800px;
}

.routes-table th {
  padding: 0.7rem 0.8rem;
  background: #f7f9fc;
  color: #7a879d;
  font-size: 0.66rem;
}

.routes-table td {
  padding: 0.85rem 0.8rem;
  color: #596780;
  font-size: 0.79rem;
}

.routes-table tbody tr:last-child td {
  border-bottom: 0;
}

.route-identity {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.route-code-icon {
  display: grid;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 9px;
  background: #edf2ff;
  color: #4167c4;
  font-weight: 800;
}

.route-identity strong,
.route-identity small {
  display: block;
}

.route-identity strong {
  color: var(--routes-ink);
  font-size: 0.79rem;
}

.route-identity small {
  margin-top: 0.08rem;
  color: #8a96a9;
  font-size: 0.68rem;
}

.route-itinerary {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: #46546c;
}

.route-arrow {
  color: #90a0bb;
}

.route-fare {
  color: #273958 !important;
  font-weight: 700;
  white-space: nowrap;
}

.route-status {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  font-size: 0.63rem;
  font-weight: 800;
  white-space: nowrap;
}

.route-status > span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.route-status-active {
  background: #eaf7f0;
  color: #24865d;
}

.route-status-paused {
  background: #fff4e6;
  color: #a76a18;
}

.route-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.35rem;
}

.route-action {
  min-height: 29px;
  padding: 0 0.55rem;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  font-size: 0.7rem;
  font-weight: 700;
}

.route-action-edit {
  color: #3a5fae;
}

.route-action-edit:hover {
  background: #edf2ff;
}

.route-action-delete {
  color: #a94b4b;
}

.route-action-delete:hover {
  background: #fff0ef;
}

.route-action:disabled {
  cursor: wait;
  opacity: 0.5;
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

@keyframes routes-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 820px) {
  .routes-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .routes-heading {
    align-items: flex-start;
  }

  .routes-primary-link {
    min-height: 38px;
    padding: 0 0.7rem;
    font-size: 0.76rem;
  }

  .routes-metrics {
    grid-template-columns: 1fr;
    gap: 0.65rem;
  }

  .routes-metric {
    min-height: 75px;
    padding: 0.75rem 1rem;
  }

  .routes-metric-icon {
    flex-basis: 38px;
    width: 38px;
    height: 38px;
  }

  .routes-metric strong {
    font-size: 1.2rem;
  }

  .routes-form {
    grid-template-columns: 1fr;
  }

  .routes-search-row {
    flex-wrap: wrap;
  }

  .routes-search,
  .routes-quick-filter {
    flex: 1 1 100%;
  }

  .routes-list-heading h2 {
    font-size: 1rem;
  }

  .routes-refresh {
    padding: 0 0.55rem;
    font-size: 0.71rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .routes-loader {
    animation-duration: 1.5s;
  }
}
</style>
