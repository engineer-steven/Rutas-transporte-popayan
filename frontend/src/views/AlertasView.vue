<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useAlertasStore } from '@/stores/alertas'
import { useRutasStore } from '@/stores/rutas'
import { useAuthStore } from '@/stores/auth'

const alertasStore = useAlertasStore()
const rutasStore = useRutasStore()
const auth = useAuthStore()

const cargando = ref(false)
const error = ref('')
const exito = ref('')
const editandoId = ref(null)

const form = reactive({
  route_id: 1,
  bus_plate: '',
  alert_type: 'BOTON_PANICO',
  severity_level: 'ALTA',
  criticality_score: 85,
  max_response_time_minutes: 10,
  location_landmark: 'Parque Caldas - Centro',
  description: '',
  status: 'ACTIVA',
})

function resetForm() {
  form.route_id = rutasStore.lista[0]?.id || 1
  form.bus_plate = ''
  form.alert_type = 'BOTON_PANICO'
  form.severity_level = 'ALTA'
  form.criticality_score = 85
  form.max_response_time_minutes = 10
  form.location_landmark = 'Parque Caldas - Centro'
  form.description = ''
  form.status = 'ACTIVA'
  editandoId.value = null
}

async function cargarTodo() {
  cargando.value = true
  error.value = ''
  try {
    await alertasStore.cargar()
    if (rutasStore.lista.length === 0) {
      await rutasStore.cargar()
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudieron cargar las alertas'
  } finally {
    cargando.value = false
  }
}

onMounted(cargarTodo)

function editar(alerta) {
  editandoId.value = alerta.id
  form.route_id = alerta.route_id
  form.bus_plate = alerta.bus_plate
  form.alert_type = alerta.alert_type
  form.severity_level = alerta.severity_level
  form.criticality_score = alerta.criticality_score || 85
  form.max_response_time_minutes = alerta.max_response_time_minutes || 10
  form.location_landmark = alerta.location_landmark
  form.description = alerta.description
  form.status = alerta.status || 'ACTIVA'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function guardar() {
  error.value = ''
  exito.value = ''
  const payload = {
    route_id: Number(form.route_id),
    bus_plate: form.bus_plate.trim().toUpperCase(),
    alert_type: form.alert_type,
    severity_level: form.severity_level,
    criticality_score: Number(form.criticality_score),
    max_response_time_minutes: Number(form.max_response_time_minutes),
    location_landmark: form.location_landmark.trim(),
    description: form.description.trim(),
    status: form.status,
  }

  try {
    if (editandoId.value) {
      await alertasStore.actualizar(editandoId.value, payload)
      exito.value = `Alerta #${editandoId.value} actualizada correctamente`
    } else {
      await alertasStore.crear(payload)
      exito.value = `Alerta crítica registrada con éxito`
    }
    resetForm()
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudo guardar la alerta'
  }
}

async function cambiarEstado(alerta) {
  const nuevoEstado = alerta.status === 'ACTIVA' ? 'RESUELTA' : 'ACTIVA'
  try {
    await alertasStore.actualizar(alerta.id, { status: nuevoEstado })
    exito.value = `Alerta #${alerta.id} marcada como ${nuevoEstado}`
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudo cambiar el estado'
  }
}

async function eliminar(id) {
  if (!confirm(`¿Eliminar la alerta #${id}?`)) return
  error.value = ''
  exito.value = ''
  try {
    await alertasStore.eliminar(id)
    exito.value = `Alerta #${id} eliminada`
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudo eliminar la alerta'
  }
}
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Centro de Alertas de Emergencia</h1>
        <p class="page-subtitle">Monitoreo en tiempo real de botón de pánico, fallas mecánicas y colisiones viales</p>
      </div>
      <div>
        <span class="badge badge-danger">Alertas Registradas: {{ alertasStore.lista.length }}</span>
      </div>
    </div>

    <p v-if="error" class="alert alert-error">{{ error }}</p>
    <p v-if="exito" class="alert alert-success">{{ exito }}</p>

    <!-- FORMULARIO DE ALERTA -->
    <div v-if="auth.esAdmin" class="card" style="margin-bottom: 1.5rem">
      <h3 class="card-title">
        <span>{{ editandoId ? '✏️ Actualizar Alerta de Emergencia' : '🚨 Registrar Alerta Crítica' }}</span>
      </h3>
      <form @submit.prevent="guardar">
        <div class="form-grid">
          <div class="field">
            <label for="al-ruta">Ruta Afectada</label>
            <select id="al-ruta" v-model="form.route_id" required>
              <option v-for="r in rutasStore.lista" :key="r.id" :value="r.id">
                {{ r.code }} - {{ r.company }}
              </option>
            </select>
          </div>

          <div class="field">
            <label for="al-placa">Placa del Bus Colectivo</label>
            <input id="al-placa" v-model="form.bus_plate" placeholder="Ej: TPK-102, SOT-451" required />
          </div>

          <div class="field">
            <label for="al-tipo">Tipo de Alerta</label>
            <select id="al-tipo" v-model="form.alert_type" required>
              <option value="BOTON_PANICO">Botón de Pánico (Seguridad)</option>
              <option value="ACCIDENTE_VIAL">Accidente / Colisión Vial</option>
              <option value="FALLA_MECANICA">Falla Mecánica de Bus</option>
              <option value="SOBRECUPO_GRAVE">Sobrecupo Grave / Riesgo</option>
            </select>
          </div>

          <div class="field">
            <label for="al-severidad">Nivel de Severidad</label>
            <select id="al-severidad" v-model="form.severity_level" required>
              <option value="CRITICA">CRÍTICA (Respuesta inmediata)</option>
              <option value="ALTA">ALTA</option>
              <option value="MEDIA">MEDIA</option>
              <option value="BAJA">BAJA</option>
            </select>
          </div>

          <div class="field">
            <label for="al-score">Score Criticidad (0-100)</label>
            <input id="al-score" v-model="form.criticality_score" type="number" step="0.1" min="0" max="100" required />
          </div>

          <div class="field">
            <label for="al-resp">Tiempo Máx. Respuesta (min)</label>
            <input id="al-resp" v-model="form.max_response_time_minutes" type="number" min="1" max="120" required />
          </div>

          <div class="field">
            <label for="al-lugar">Lugar / Punto de Referencia</label>
            <input id="al-lugar" v-model="form.location_landmark" placeholder="Ej: Frente a Campanario" required />
          </div>

          <div class="field">
            <label for="al-estado">Estado de la Alerta</label>
            <select id="al-estado" v-model="form.status">
              <option value="ACTIVA">ACTIVA</option>
              <option value="EN_ATENCION">EN ATENCIÓN</option>
              <option value="RESUELTA">RESUELTA</option>
            </select>
          </div>

          <div class="field" style="grid-column: 1 / -1">
            <label for="al-desc">Descripción de los Hechos</label>
            <textarea
              id="al-desc"
              v-model="form.description"
              rows="2"
              placeholder="Describa la situación en vía..."
              required
            ></textarea>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            {{ editandoId ? 'Guardar Cambios' : 'Emitir Alerta' }}
          </button>
          <button v-if="editandoId" type="button" class="btn btn-secondary" @click="resetForm">
            Cancelar
          </button>
        </div>
      </form>
    </div>

    <!-- TABLA DE ALERTAS -->
    <div class="card table-wrapper">
      <p v-if="cargando" class="empty-state">Cargando alertas de monitoreo...</p>
      <p v-else-if="alertasStore.lista.length === 0" class="empty-state">
        No hay alertas de emergencia registradas en el sistema.
      </p>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tipo / Severidad</th>
            <th>Vehículo</th>
            <th>Ubicación / Descripción</th>
            <th>Score</th>
            <th>Estado</th>
            <th style="text-align: right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="al in alertasStore.lista" :key="al.id">
            <td><strong>#{{ al.id }}</strong></td>
            <td>
              <div>{{ al.alert_type }}</div>
              <span
                :class="[
                  'badge',
                  al.severity_level === 'CRITICA' ? 'badge-danger' :
                  al.severity_level === 'ALTA' ? 'badge-warning' : 'badge-info'
                ]"
              >
                {{ al.severity_level }}
              </span>
            </td>
            <td><strong>{{ al.bus_plate }}</strong></td>
            <td>
              <div style="font-weight: 600">{{ al.location_landmark }}</div>
              <div style="font-size: 0.85rem; color: var(--color-text-muted)">{{ al.description }}</div>
            </td>
            <td>{{ al.criticality_score }} pts</td>
            <td>
              <button
                v-if="auth.esAdmin"
                :class="[
                  'badge',
                  al.status === 'ACTIVA' ? 'badge-danger' : 'badge-success'
                ]"
                style="border: none; cursor: pointer"
                title="Haga clic para alternar estado"
                @click="cambiarEstado(al)"
              >
                {{ al.status }} 🔄
              </button>
              <span v-else class="badge" :class="al.status === 'ACTIVA' ? 'badge-danger' : 'badge-success'">
                {{ al.status }}
              </span>
            </td>
            <td class="row-actions">
              <template v-if="auth.esAdmin">
                <button class="btn btn-secondary btn-sm" @click="editar(al)">Editar</button>
                <button class="btn btn-danger btn-sm" @click="eliminar(al.id)">Eliminar</button>
              </template>
              <span v-else>Solo lectura</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
