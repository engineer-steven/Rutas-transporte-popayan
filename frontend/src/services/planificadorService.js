import { apiRutas } from './api'

export default {
  planificarViajeDirecto(orig, dest) {
    return apiRutas.get(`/logicas/viaje-directo?origin=${encodeURIComponent(orig)}&destination=${encodeURIComponent(dest)}`)
  },
  planificarViajeTransbordo(orig, dest) {
    return apiRutas.get(`/logicas/viaje-transbordo?origin=${encodeURIComponent(orig)}&destination=${encodeURIComponent(dest)}`)
  },
  calcularCongestion(routeId) {
    return apiRutas.get(`/logicas/congestion/${routeId}`)
  },
  simularTrafico(routeId, hora) {
    return apiRutas.get(`/logicas/trafico/${routeId}?hora=${encodeURIComponent(hora)}`)
  },
  compararRutas(r1, r2) {
    return apiRutas.get(`/logicas/comparar?ruta1=${r1}&ruta2=${r2}`)
  },
}
