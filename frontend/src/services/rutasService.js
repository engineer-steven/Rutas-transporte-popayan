import { apiRutas } from './api'

export default {
  obtenerTodas() {
    return apiRutas.get('/rutas')
  },
  obtenerPorId(id) {
    return apiRutas.get(`/rutas/${id}`)
  },
  buscarPorZona(zona) {
    return apiRutas.get(`/rutas/buscar?zona=${encodeURIComponent(zona)}`)
  },
  crear(ruta) {
    return apiRutas.post('/rutas', ruta)
  },
  actualizar(id, ruta) {
    return apiRutas.put(`/rutas/${id}`, ruta)
  },
  eliminar(id) {
    return apiRutas.delete(`/rutas/${id}`)
  },
}
