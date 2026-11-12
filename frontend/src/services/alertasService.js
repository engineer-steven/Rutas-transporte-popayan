import { apiMonitoreo } from './api'

export default {
  obtenerTodas() {
    return apiMonitoreo.get('/monitoreo/alertas')
  },
  obtenerPorId(id) {
    return apiMonitoreo.get(`/monitoreo/alertas/${id}`)
  },
  crear(alerta) {
    return apiMonitoreo.post('/monitoreo/alertas', alerta)
  },
  actualizar(id, datos) {
    return apiMonitoreo.put(`/monitoreo/alertas/${id}`, datos)
  },
  eliminar(id) {
    return apiMonitoreo.delete(`/monitoreo/alertas/${id}`)
  },
}
