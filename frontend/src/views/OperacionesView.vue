<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRutasStore } from '@/stores/rutas'
import operacionesService from '@/services/operacionesService'

const rutasStore = useRutasStore()

const rutaSeleccionada = ref(1)
const paraderos = ref([])
const incidentes = ref([])
const cargandoParaderos = ref(false)
const cargandoIncidentes = ref(false)
const error = ref('')
const exito = ref('')

// Formulario de incidente
const formIncidente = reactive({
  route_id: 1,
  incident_type: 'CONGESTION',
  description: '',
  reported_by: 'Operador en Vía',
})

// Calculadora de intervalo entre buses
const calcBuses = reactive({
  route_id: 1,
  bus1: 'TPK-102',
  bus2: 'SOT-451',
  resultado: null,
  error: '',
  cargando: false,
})

// Calculadora de diferencia horaria
const calcHoras = reactive({
  hora1: '06:30',
  hora2: '07:15',
  resultado: null,
  error: '',
})

async function cargarDatosRuta() {
  error.value = ''
  cargandoParaderos.value = true
  cargandoIncidentes.value = true
  try {
    const resP = await operacionesService.obtenerParaderos(rutaSeleccionada.value)
    paraderos.value = resP.data.paraderos || resP.data.data || []
  } catch (e) {
    paraderos.value = []
  } finally {
    cargandoParaderos.value = false
  }

  try {
    const resI = await operacionesService.obtenerIncidentes(rutaSeleccionada.value)
    incidentes.value = resI.data.incidentes || resI.data.data || []
  } catch (e) {
    incidentes.value = []
  } finally {
    cargandoIncidentes.value = false
  }
}

onMounted(async () => {
  if (rutasStore.lista.length === 0) {
    await rutasStore.cargar()
  }
  if (rutasStore.lista.length > 0) {
    rutaSeleccionada.value = rutasStore.lista[0].id
    formIncidente.route_id = rutaSeleccionada.value
    calcBuses.route_id = rutaSeleccionada.value
  }
  await cargarDatosRuta()
})

async function registrarIncidente() {
  error.value = ''
  exito.value = ''
  try {
    await operacionesService.reportarIncidente({
      route_id: Number(formIncidente.route_id),
      incident_type: formIncidente.incident_type,
      description: formIncidente.description,
      reported_by: formIncidente.reported_by,
    })
    exito.value = 'Incidente registrado exitosamente en la base de datos'
    formIncidente.description = ''
    if (Number(formIncidente.route_id) === Number(rutaSeleccionada.value)) {
      await cargarDatosRuta()
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudo reportar el incidente'
  }
}

async function calcularDiferenciaBuses() {
  calcBuses.error = ''
  calcBuses.resultado = null
  calcBuses.cargando = true
  try {
    const res = await operacionesService.calcularDiferenciaBuses(
      calcBuses.route_id,
      calcBuses.bus1,
      calcBuses.bus2
    )
    calcBuses.resultado = res.data
  } catch (e) {
    calcBuses.error = e.response?.data?.error || 'No se pudo calcular el intervalo'
  } finally {
    calcBuses.cargando = false
  }
}

async function calcularDiferenciaHoras() {
  calcHoras.error = ''
  calcHoras.resultado = null
  try {
    const res = await operacionesService.calcularDiferenciaHoras(calcHoras.hora1, calcHoras.hora2)
    calcHoras.resultado = res.data
  } catch (e) {
    calcHoras.error = e.response?.data?.error || 'Formato de hora inválido'
  }
}
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Operaciones en Vía e Incidentes</h1>
        <p class="page-subtitle">Seguimiento de paraderos georreferenciados, novedades y separación entre buses</p>
      </div>
    </div>

    <p v-if="error" class="alert alert-error">{{ error }}</p>
    <p v-if="exito" class="alert alert-success">{{ exito }}</p>

    <!-- SELECTOR DE RUTA -->
    <div class="card" style="margin-bottom: 1.5rem">
      <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
        <label for="select-ruta" style="font-weight: 700; color: var(--color-primary)">
          Seleccione una Ruta para Inspeccionar Operaciones:
        </label>
        <select
          id="select-ruta"
          v-model="rutaSeleccionada"
          style="padding: 0.5rem 0.8rem; border-radius: 8px; border: 1px solid var(--color-border); font-size: 0.95rem"
          @change="cargarDatosRuta"
        >
          <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
            {{ r.code }} - {{ r.company }} ({{ r.origin }} → {{ r.destination }})
          </option>
        </select>
        <button class="btn btn-secondary btn-sm" @click="cargarDatosRuta">Actualizar</button>
      </div>
    </div>

    <div class="operations-grid operations-grid-spaced">
      <!-- PARADEROS DE LA RUTA -->
      <div class="card">
        <h3 class="card-title">📍 Paraderos Georreferenciados</h3>
        <p v-if="cargandoParaderos" class="empty-state">Cargando paraderos...</p>
        <p v-else-if="paraderos.length === 0" class="empty-state">
          No hay paraderos registrados para esta ruta.
        </p>
        <div v-else class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Nombre del Paradero</th>
                <th>Punto de Referencia</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in paraderos" :key="p.id">
                <td><strong>{{ p.orden }}</strong></td>
                <td>{{ p.nombre }}</td>
                <td>{{ p.referencia || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- INCIDENTES ACTIVOS DE LA RUTA -->
      <div class="card">
        <h3 class="card-title">⚠️ Novedades Viales Reportadas</h3>
        <p v-if="cargandoIncidentes" class="empty-state">Cargando incidentes...</p>
        <p v-else-if="incidentes.length === 0" class="empty-state">
          ✅ No hay incidentes viales activos en esta ruta. Operando con normalidad.
        </p>
        <div v-else class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Descripción</th>
                <th>Reportado</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inc in incidentes" :key="inc.id">
                <td>
                  <span
                    :class="[
                      'badge',
                      inc.tipo === 'ACCIDENTE' ? 'badge-danger' :
                      inc.tipo === 'CONGESTION' ? 'badge-warning' : 'badge-info'
                    ]"
                  >
                    {{ inc.tipo }}
                  </span>
                </td>
                <td>{{ inc.descripcion }}</td>
                <td style="font-size: 0.8rem">{{ inc.reportado_por }}</td>
                <td><span class="badge badge-warning">{{ inc.estado }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- REPORTAR NUEVO INCIDENTE -->
    <div class="card" style="margin-bottom: 1.5rem">
      <h3 class="card-title">📢 Reportar Novedad Vial en Ruta</h3>
      <form @submit.prevent="registrarIncidente">
        <div class="form-grid">
          <div class="field">
            <label for="inc-ruta">Ruta Afectada</label>
            <select id="inc-ruta" v-model="formIncidente.route_id" required>
              <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
                {{ r.code }} ({{ r.origin }} → {{ r.destination }})
              </option>
            </select>
          </div>

          <div class="field">
            <label for="inc-tipo">Tipo de Evento</label>
            <select id="inc-tipo" v-model="formIncidente.incident_type" required>
              <option value="CONGESTION">Congestión Pesada</option>
              <option value="ACCIDENTE">Colisión / Accidente Vial</option>
              <option value="DESVIO">Desvío Temporal / Obra</option>
              <option value="FALLA_MECANICA">Falla Mecánica de Colectivo</option>
              <option value="MANIFESTACION">Manifestación Ciudadana</option>
            </select>
          </div>

          <div class="field">
            <label for="inc-reportante">Reportado Por</label>
            <input id="inc-reportante" v-model="formIncidente.reported_by" required />
          </div>

          <div class="field" style="grid-column: 1 / -1">
            <label for="inc-desc">Descripción Detallada del Suceso</label>
            <input
              id="inc-desc"
              v-model="formIncidente.description"
              placeholder="Ej: Tráfico paralizado en glorieta Campanario por colisión leve"
              required
            />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary">Registrar Novedad</button>
        </div>
      </form>
    </div>

    <!-- CALCULADORAS EN VÍA (HEADWAY Y BRECHA HORARIA) -->
    <div class="operations-grid">
      <!-- INTERVALO ENTRE 2 BUSES (HEADWAY) -->
      <div class="card">
        <h3 class="card-title">⏱️ Intervalo entre Buses (Headway)</h3>
        <p class="page-subtitle" style="margin-bottom: 1rem">
          Calcula la separación en minutos entre dos salidas de colectivos en la misma ruta.
        </p>

        <p v-if="calcBuses.error" class="alert alert-error">{{ calcBuses.error }}</p>

        <form @submit.prevent="calcularDiferenciaBuses">
          <div class="form-grid">
            <div class="field">
              <label for="cb-ruta">Ruta</label>
              <select id="cb-ruta" v-model="calcBuses.route_id">
                <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
                  {{ r.code }} - {{ r.company }}
                </option>
              </select>
            </div>
            <div class="field">
              <label for="cb-bus1">Placa Colectivo 1</label>
              <input id="cb-bus1" v-model="calcBuses.bus1" placeholder="Ej: TPK-102" required />
            </div>
            <div class="field">
              <label for="cb-bus2">Placa Colectivo 2</label>
              <input id="cb-bus2" v-model="calcBuses.bus2" placeholder="Ej: SOT-451" required />
            </div>
          </div>
          <button type="submit" class="btn btn-accent" :disabled="calcBuses.cargando">
            {{ calcBuses.cargando ? 'Calculando...' : 'Calcular Separación' }}
          </button>
        </form>

        <div v-if="calcBuses.resultado" class="result-metric" style="margin-top: 1rem">
          <div class="metric-label">Separación Temporal</div>
          <div class="metric-value">{{ calcBuses.resultado.diferencia_minutos }} Minutos</div>
          <p style="margin-top: 0.5rem; font-size: 0.9rem">{{ calcBuses.resultado.resumen }}</p>
        </div>
      </div>

      <!-- CALCULADORA DE BRECHA HORARIA -->
      <div class="card">
        <h3 class="card-title">🕐 Calculadora Horaria Directa</h3>
        <p class="page-subtitle" style="margin-bottom: 1rem">
          Calcula la diferencia exacta en minutos entre dos tiempos especificados.
        </p>

        <p v-if="calcHoras.error" class="alert alert-error">{{ calcHoras.error }}</p>

        <form @submit.prevent="calcularDiferenciaHoras">
          <div class="form-grid">
            <div class="field">
              <label for="ch-h1">Hora Inicial (HH:MM)</label>
              <input id="ch-h1" v-model="calcHoras.hora1" type="time" required />
            </div>
            <div class="field">
              <label for="ch-h2">Hora Final (HH:MM)</label>
              <input id="ch-h2" v-model="calcHoras.hora2" type="time" required />
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Calcular Brecha</button>
        </form>

        <div v-if="calcHoras.resultado" class="result-metric" style="margin-top: 1rem">
          <div class="metric-label">Diferencia Neta</div>
          <div class="metric-value">{{ calcHoras.resultado.diferencia_minutos }} Minutos</div>
          <p style="margin-top: 0.5rem; font-size: 0.9rem">{{ calcHoras.resultado.mensaje }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
