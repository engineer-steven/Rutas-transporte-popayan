<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRutasStore } from '@/stores/rutas'
import despachoService from '@/services/despachoService'

const rutasStore = useRutasStore()
const tabActiva = ref('horario')
const cargando = ref(false)
const error = ref('')

// LÓGICA 1: Tabla Horaria
const formHorario = reactive({
  route_id: 1,
  tipo_dia: 'HABIL',
  hora_inicio: '05:00',
  hora_fin: '22:00',
  resultado: null,
})

// LÓGICA 2: Frecuencias Mínimas
const formFrecuencias = reactive({
  route_id: 1,
  hora: 7,
  tipo_dia: 'HABIL',
  capacidad_bus: 19,
  resultado: null,
})

// LÓGICA 3: Asignación de Colectivo
const formVehiculo = reactive({
  route_id: 1,
  hora: 8,
  pasajeros_estimados: 24,
  longitud_ruta_km: 15,
  es_vereda: false,
  resultado: null,
})

// LÓGICA 4: Descanso en Cabecera
const formDescanso = reactive({
  route_id: 1,
  bus_plate: 'TPK-102',
  horas_en_ruta: 4.5,
  km_recorridos: 85,
  hora_llegada: '13:00',
  resultado: null,
})

// LÓGICA 5: Rotación y Fatiga
const formRotacion = reactive({
  conductor_id: 3,
  nombre_conductor: 'Jairo Ordóñez',
  empresa: 'Sotracauca',
  horas_acumuladas: 7.5,
  km_acumulados: 160,
  turnos_del_dia: 1,
  incidentes_reportados: 1,
  vueltas_completadas: 5,
  resultado: null,
})

onMounted(async () => {
  if (rutasStore.lista.length === 0) {
    await rutasStore.cargar()
  }
})

async function ejecutarHorario() {
  error.value = ''
  cargando.value = true
  try {
    const res = await despachoService.generarHorario({
      route_id: Number(formHorario.route_id),
      tipo_dia: formHorario.tipo_dia,
      hora_inicio: formHorario.hora_inicio,
      hora_fin: formHorario.hora_fin,
    })
    formHorario.resultado = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al generar tabla horaria'
  } finally {
    cargando.value = false
  }
}

async function ejecutarFrecuencias() {
  error.value = ''
  cargando.value = true
  try {
    const res = await despachoService.calcularFrecuencias({
      route_id: Number(formFrecuencias.route_id),
      hora: Number(formFrecuencias.hora),
      tipo_dia: formFrecuencias.tipo_dia,
      capacidad_bus: Number(formFrecuencias.capacidad_bus),
    })
    formFrecuencias.resultado = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al calcular frecuencias'
  } finally {
    cargando.value = false
  }
}

async function ejecutarVehiculo() {
  error.value = ''
  cargando.value = true
  try {
    const res = await despachoService.asignarTipoVehiculo({
      route_id: Number(formVehiculo.route_id),
      hora: Number(formVehiculo.hora),
      pasajeros_estimados: Number(formVehiculo.pasajeros_estimados),
      longitud_ruta_km: Number(formVehiculo.longitud_ruta_km),
      es_vereda: formVehiculo.es_vereda,
    })
    formVehiculo.resultado = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al asignar vehículo'
  } finally {
    cargando.value = false
  }
}

async function ejecutarDescanso() {
  error.value = ''
  cargando.value = true
  try {
    const res = await despachoService.calcularDescansoTerminal({
      route_id: Number(formDescanso.route_id),
      bus_plate: formDescanso.bus_plate,
      horas_en_ruta: Number(formDescanso.horas_en_ruta),
      km_recorridos: Number(formDescanso.km_recorridos),
      hora_llegada: formDescanso.hora_llegada,
    })
    formDescanso.resultado = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al calcular descanso'
  } finally {
    cargando.value = false
  }
}

async function ejecutarRotacion() {
  error.value = ''
  cargando.value = true
  try {
    const res = await despachoService.optimizarRotacionConductor({
      conductor_id: formRotacion.conductor_id,
      nombre_conductor: formRotacion.nombre_conductor,
      empresa: formRotacion.empresa,
      horas_acumuladas: Number(formRotacion.horas_acumuladas),
      km_acumulados: Number(formRotacion.km_acumulados),
      turnos_del_dia: Number(formRotacion.turnos_del_dia),
      incidentes_reportados: Number(formRotacion.incidentes_reportados),
      vueltas_completadas: Number(formRotacion.vueltas_completadas),
    })
    formRotacion.resultado = res.data.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al calcular rotación'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Programación y Despacho Operativo</h1>
        <p class="page-subtitle">Algoritmos no lineales de dimensionamiento, factor Unicauca y descanso de conductores</p>
      </div>
    </div>

    <p v-if="error" class="alert alert-error">{{ error }}</p>

    <!-- NAVEGACIÓN POR PESTAÑAS -->
    <div style="display: flex; gap: 0.5rem; overflow-x: auto; margin-bottom: 1.5rem; padding-bottom: 0.25rem;">
      <button
        :class="['btn', tabActiva === 'horario' ? 'btn-primary' : 'btn-secondary']"
        @click="tabActiva = 'horario'"
      >
        📅 1. Tabla Horaria
      </button>
      <button
        :class="['btn', tabActiva === 'frecuencias' ? 'btn-primary' : 'btn-secondary']"
        @click="tabActiva = 'frecuencias'"
      >
        🎓 2. Factor Unicauca
      </button>
      <button
        :class="['btn', tabActiva === 'vehiculo' ? 'btn-primary' : 'btn-secondary']"
        @click="tabActiva = 'vehiculo'"
      >
        🚐 3. Tamaño Bus & Recaudo
      </button>
      <button
        :class="['btn', tabActiva === 'descanso' ? 'btn-primary' : 'btn-secondary']"
        @click="tabActiva = 'descanso'"
      >
        ☕ 4. Descanso Cabecera
      </button>
      <button
        :class="['btn', tabActiva === 'rotacion' ? 'btn-primary' : 'btn-secondary']"
        @click="tabActiva = 'rotacion'"
      >
        👤 5. Score Fatiga Conductor
      </button>
    </div>

    <!-- PESTAÑA 1: TABLA HORARIA -->
    <div v-if="tabActiva === 'horario'" class="card">
      <h3 class="card-title">📅 Generador de Tabla Horaria Dinámica</h3>
      <p class="page-subtitle" style="margin-bottom: 1.25rem">
        Calcula salidas desde cabecera con frecuencias adaptadas al tipo de día en Popayán (Habil, Sábado comercial, Domingo y Festivo).
      </p>

      <form @submit.prevent="ejecutarHorario">
        <div class="form-grid">
          <div class="field">
            <label for="th-ruta">Ruta</label>
            <select id="th-ruta" v-model="formHorario.route_id">
              <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
                {{ r.code }} - {{ r.company }}
              </option>
            </select>
          </div>
          <div class="field">
            <label for="th-dia">Tipo de Día</label>
            <select id="th-dia" v-model="formHorario.tipo_dia">
              <option value="HABIL">Día Hábil (Picos a 8 min)</option>
              <option value="SABADO">Sábado (Comercial 10-12 min)</option>
              <option value="DOMINGO">Domingo (15-20 min)</option>
              <option value="FESTIVO">Festivo (Inicia 08:00)</option>
            </select>
          </div>
          <div class="field">
            <label for="th-inicio">Hora Inicio</label>
            <input id="th-inicio" v-model="formHorario.hora_inicio" type="time" required />
          </div>
          <div class="field">
            <label for="th-fin">Hora Fin</label>
            <input id="th-fin" v-model="formHorario.hora_fin" type="time" required />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="cargando">
          {{ cargando ? 'Generando...' : 'Generar Tabla Horaria' }}
        </button>
      </form>

      <div v-if="formHorario.resultado" style="margin-top: 1.5rem">
        <div class="results-grid">
          <div class="result-metric">
            <div class="metric-label">Total Despachos Programados</div>
            <div class="metric-value">{{ formHorario.resultado.total_salidas }} Salidas</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Frecuencia Promedio</div>
            <div class="metric-value">{{ formHorario.resultado.frecuencia_promedio_min }} Min</div>
          </div>
        </div>

        <div class="table-wrapper" style="margin-top: 1rem; max-height: 350px">
          <table class="data-table">
            <thead>
              <tr>
                <th>Hora Salida</th>
                <th>Frecuencia Próxima</th>
                <th>Franja de Demanda</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(s, idx) in formHorario.resultado.tabla_horaria" :key="idx">
                <td><strong>{{ s.hora_salida }}</strong></td>
                <td>{{ s.frecuencia_min }} min</td>
                <td><span class="badge badge-info">{{ s.franja }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- PESTAÑA 2: FACTOR UNICAUCA -->
    <div v-if="tabActiva === 'frecuencias'" class="card">
      <h3 class="card-title">🎓 Frecuencias Mínimas y Factor Universitario (Unicauca)</h3>
      <p class="page-subtitle" style="margin-bottom: 1.25rem">
        Modela la sobrecarga del 20% en horarios pico estudiantiles hacia campus universitarios de Popayán.
      </p>

      <form @submit.prevent="ejecutarFrecuencias">
        <div class="form-grid">
          <div class="field">
            <label for="fu-ruta">Ruta de Transporte</label>
            <select id="fu-ruta" v-model="formFrecuencias.route_id">
              <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
                {{ r.code }} - {{ r.company }} ({{ r.origin }} → {{ r.destination }})
              </option>
            </select>
          </div>
          <div class="field">
            <label for="fu-hora">Hora del Día (0-23)</label>
            <input id="fu-hora" v-model="formFrecuencias.hora" type="number" min="0" max="23" required />
          </div>
          <div class="field">
            <label for="fu-dia">Tipo de Día</label>
            <select id="fu-dia" v-model="formFrecuencias.tipo_dia">
              <option value="HABIL">Día Hábil</option>
              <option value="SABADO">Sábado</option>
              <option value="DOMINGO">Domingo</option>
              <option value="FESTIVO">Festivo</option>
            </select>
          </div>
          <div class="field">
            <label for="fu-cap">Capacidad Buseta</label>
            <input id="fu-cap" v-model="formFrecuencias.capacidad_bus" type="number" min="10" max="45" required />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="cargando">
          Calcular Colectivos Necesarios
        </button>
      </form>

      <div v-if="formFrecuencias.resultado" style="margin-top: 1.5rem">
        <div class="results-grid">
          <div class="result-metric">
            <div class="metric-label">Demanda Proyectada</div>
            <div class="metric-value">{{ formFrecuencias.resultado.pasajeros_hora_estimados }} Pasajeros/h</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Flota Mínima Requerida</div>
            <div class="metric-value">{{ formFrecuencias.resultado.buses_requeridos }} Colectivos</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Intervalo de Despacho</div>
            <div class="metric-value">Cada {{ formFrecuencias.resultado.intervalo_minutos }} Min</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Factor Unicauca</div>
            <div class="metric-value">{{ formFrecuencias.resultado.factor_unicauca }}x</div>
          </div>
        </div>
        <p class="alert alert-info" style="margin-top: 1rem">
          {{ formFrecuencias.resultado.impacto_universitario }}
        </p>
      </div>
    </div>

    <!-- PESTAÑA 3: TAMAÑO DE VEHÍCULO Y RECAUDO -->
    <div v-if="tabActiva === 'vehiculo'" class="card">
      <h3 class="card-title">🚐 Asignación de Colectivo y Balance de Recaudo</h3>
      <p class="page-subtitle" style="margin-bottom: 1.25rem">
        Homologa microbús (19), buseta (25) o extendida (32) y liquida tarifa ($3.000 COP o recargo rural).
      </p>

      <form @submit.prevent="ejecutarVehiculo">
        <div class="form-grid">
          <div class="field">
            <label for="tv-ruta">Ruta</label>
            <select id="tv-ruta" v-model="formVehiculo.route_id">
              <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
                {{ r.code }} - {{ r.company }}
              </option>
            </select>
          </div>
          <div class="field">
            <label for="tv-pasajeros">Pasajeros Estimados</label>
            <input id="tv-pasajeros" v-model="formVehiculo.pasajeros_estimados" type="number" min="1" max="60" required />
          </div>
          <div class="field">
            <label for="tv-long">Longitud Ruta (km)</label>
            <input id="tv-long" v-model="formVehiculo.longitud_ruta_km" type="number" step="0.5" min="2" max="60" required />
          </div>
          <div class="field">
            <label for="tv-vereda">¿Ruta Veredal?</label>
            <select id="tv-vereda" v-model="formVehiculo.es_vereda">
              <option :value="false">No (Tarifa Urbana $3.000)</option>
              <option :value="true">Sí (Tarifa Vereda $3.400)</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="cargando">
          Evaluar Vehículo y Recaudo
        </button>
      </form>

      <div v-if="formVehiculo.resultado" style="margin-top: 1.5rem">
        <div class="results-grid">
          <div class="result-metric">
            <div class="metric-label">Vehículo Recomendado</div>
            <div class="metric-value">{{ formVehiculo.resultado.vehiculo_asignado.tamano }}</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Recaudo Estimado</div>
            <div class="metric-value">{{ formVehiculo.resultado.analisis_asientos_y_pasajes.total_recaudo_pasajes }}</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Costo Operativo Vuelta</div>
            <div class="metric-value">{{ formVehiculo.resultado.analisis_asientos_y_pasajes.costo_operativo_ruta }}</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Balance Neto Vuelta</div>
            <div class="metric-value">{{ formVehiculo.resultado.analisis_asientos_y_pasajes.balance_neto_vuelta }}</div>
          </div>
        </div>
        <p class="alert alert-warning" style="margin-top: 1rem">
          {{ formVehiculo.resultado.alerta }}
        </p>
      </div>
    </div>

    <!-- PESTAÑA 4: DESCANSO CABECERA -->
    <div v-if="tabActiva === 'descanso'" class="card">
      <h3 class="card-title">☕ Control de Tiempos de Descanso en Terminal</h3>
      <p class="page-subtitle" style="margin-bottom: 1.25rem">
        Aplica la Resolución 315/2013: descanso mínimo de 15 min cada 2h con penalizaciones no lineales por fatiga.
      </p>

      <form @submit.prevent="ejecutarDescanso">
        <div class="form-grid">
          <div class="field">
            <label for="dc-placa">Placa Colectivo</label>
            <input id="dc-placa" v-model="formDescanso.bus_plate" required />
          </div>
          <div class="field">
            <label for="dc-horas">Horas Conducidas en Ruta</label>
            <input id="dc-horas" v-model="formDescanso.horas_en_ruta" type="number" step="0.1" min="0.5" max="14" required />
          </div>
          <div class="field">
            <label for="dc-km">Kilómetros Recorridos Hoy</label>
            <input id="dc-km" v-model="formDescanso.km_recorridos" type="number" step="1" min="10" max="300" required />
          </div>
          <div class="field">
            <label for="dc-llegada">Hora de Llegada a Terminal</label>
            <input id="dc-llegada" v-model="formDescanso.hora_llegada" type="time" required />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="cargando">
          Liquidar Descanso Reglamentario
        </button>
      </form>

      <div v-if="formDescanso.resultado" style="margin-top: 1.5rem">
        <div class="results-grid">
          <div class="result-metric">
            <div class="metric-label">Descanso Obligatorio</div>
            <div class="metric-value">{{ formDescanso.resultado.descanso_requerido_min }} Minutos</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Hora Salida Próximo Viaje</div>
            <div class="metric-value">{{ formDescanso.resultado.proxima_salida }}</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Nivel de Fatiga</div>
            <div class="metric-value">{{ formDescanso.resultado.nivel_fatiga }}</div>
          </div>
        </div>
        <p :class="['alert', formDescanso.resultado.cumple_reglamento ? 'alert-info' : 'alert-error']" style="margin-top: 1rem">
          {{ formDescanso.resultado.alerta }}
        </p>
      </div>
    </div>

    <!-- PESTAÑA 5: ROTACIÓN Y SCORE FATIGA -->
    <div v-if="tabActiva === 'rotacion'" class="card">
      <h3 class="card-title">👤 Optimizador de Rotación y Score de Fatiga</h3>
      <p class="page-subtitle" style="margin-bottom: 1.25rem">
        Calcula el score multidimensional de fatiga (0-100) y alerta relevos obligatorios según Decreto 1079/2015.
      </p>

      <form @submit.prevent="ejecutarRotacion">
        <div class="form-grid">
          <div class="field">
            <label for="rot-nombre">Nombre Conductor</label>
            <input id="rot-nombre" v-model="formRotacion.nombre_conductor" required />
          </div>
          <div class="field">
            <label for="rot-empresa">Empresa</label>
            <select id="rot-empresa" v-model="formRotacion.empresa">
              <option value="Sotracauca">Sotracauca</option>
              <option value="Transpubenza">Transpubenza</option>
              <option value="Translibertad">Translibertad</option>
            </select>
          </div>
          <div class="field">
            <label for="rot-horas">Horas Acumuladas Hoy</label>
            <input id="rot-horas" v-model="formRotacion.horas_acumuladas" type="number" step="0.5" min="1" max="14" required />
          </div>
          <div class="field">
            <label for="rot-km">Kilómetros Acumulados</label>
            <input id="rot-km" v-model="formRotacion.km_acumulados" type="number" min="10" max="350" required />
          </div>
          <div class="field">
            <label for="rot-turnos">Turnos Trabajados Hoy</label>
            <input id="rot-turnos" v-model="formRotacion.turnos_del_dia" type="number" min="1" max="4" required />
          </div>
          <div class="field">
            <label for="rot-inc">Incidentes / Riñas</label>
            <input id="rot-inc" v-model="formRotacion.incidentes_reportados" type="number" min="0" max="5" />
          </div>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="cargando">
          Calcular Score y Determinar Relevo
        </button>
      </form>

      <div v-if="formRotacion.resultado" style="margin-top: 1.5rem">
        <div class="results-grid">
          <div class="result-metric">
            <div class="metric-label">Score de Fatiga</div>
            <div class="metric-value">{{ formRotacion.resultado.score_fatiga }} / 100</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">Categoría</div>
            <div class="metric-value">{{ formRotacion.resultado.categoria_fatiga }}</div>
          </div>
          <div class="result-metric">
            <div class="metric-label">¿Requiere Relevo Inmediato?</div>
            <div class="metric-value">
              <span :class="['badge', formRotacion.resultado.necesita_relevo ? 'badge-danger' : 'badge-success']">
                {{ formRotacion.resultado.necesita_relevo ? 'SÍ (RELEVAR)' : 'NO (APTO)' }}
              </span>
            </div>
          </div>
        </div>
        <p :class="['alert', formRotacion.resultado.necesita_relevo ? 'alert-error' : 'alert-success']" style="margin-top: 1rem">
          {{ formRotacion.resultado.medida }}
        </p>
      </div>
    </div>
  </section>
</template>

