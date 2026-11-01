import { apiOperaciones } from './api'

export default {
  obtenerParaderos(routeId) {
    return apiOperaciones.get(`/operaciones/paraderos/${routeId}`)
  },
  reportarIncidente(datos) {
    return apiOperaciones.post('/operaciones/incidente', datos)
  },
  obtenerIncidentes(routeId) {
    return apiOperaciones.get(`/operaciones/incidentes/${routeId}`)
  },
  calcularDiferenciaBuses(routeId, bus1, bus2) {
    return apiOperaciones.get(`/operaciones/diferencia-buses?route_id=${routeId}&bus1=${encodeURIComponent(bus1)}&bus2=${encodeURIComponent(bus2)}`)
  },
  calcularDiferenciaHoras(hora1, hora2) {
    return apiOperaciones.get(`/operaciones/diferencia-horas?hora1=${encodeURIComponent(hora1)}&hora2=${encodeURIComponent(hora2)}`)
  },
}
