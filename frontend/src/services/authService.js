import { apiMonitoreo } from './api'

export default {
  login(username, password) {
    return apiMonitoreo.post('/login', { username, password })
  },
  registrar(username, password) {
    return apiMonitoreo.post('/register', { username, password })
  },
  obtenerPerfil() {
    return apiMonitoreo.get('/me')
  },
}
