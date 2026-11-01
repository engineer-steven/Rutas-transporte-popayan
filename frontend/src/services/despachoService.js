import { apiMonitoreo } from './api'

export default {
  generarHorario(datos) {
    return apiMonitoreo.post('/despacho/horario', datos)
  },
  calcularFrecuencias(datos) {
    return apiMonitoreo.post('/despacho/frecuencias', datos)
  },
  asignarTipoVehiculo(datos) {
    return apiMonitoreo.post('/despacho/tipo-vehiculo', datos)
  },
  calcularDescansoTerminal(datos) {
    return apiMonitoreo.post('/despacho/descanso-terminal', datos)
  },
  optimizarRotacionConductor(datos) {
    return apiMonitoreo.post('/despacho/rotacion-conductor', datos)
  },
}
