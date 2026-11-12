import { defineStore } from 'pinia'
import authService from '@/services/authService'

function normalizarRol(rol) {
  const normalizado = String(rol || '').trim().toUpperCase()
  const equivalencias = {
    PASAJERO: 'USUARIO',
    CONDUCTOR: 'OPERADOR',
  }
  const rolesValidos = new Set(['ADMIN', 'SUPERVISOR', 'OPERADOR', 'USUARIO'])

  const rolFinal = equivalencias[normalizado] || normalizado
  return rolesValidos.has(rolFinal) ? rolFinal : 'USUARIO'
}

function limpiarSesionPersistente() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    limpiarSesionPersistente()
    return {
      token: sessionStorage.getItem('token') || null,
      username: sessionStorage.getItem('username') || null,
      role: normalizarRol(sessionStorage.getItem('role')),
    }
  },
  getters: {
    estaAutenticado: (state) => !!state.token,
    esAdmin: (state) => state.role === 'ADMIN',
    inicio: (state) => {
      if (state.role === 'OPERADOR' || state.role === 'SUPERVISOR') return 'operaciones'
      if (state.role === 'USUARIO') return 'inicio'
      return 'rutas'
    },
  },
  actions: {
    async login(username, password) {
      const { data } = await authService.login(username, password)
      this.token = data.token
      this.username = data.username || username
      this.role = normalizarRol(data.role)
      sessionStorage.setItem('token', data.token)
      sessionStorage.setItem('username', this.username)
      sessionStorage.setItem('role', this.role)
    },
    logout() {
      this.token = null
      this.username = null
      this.role = null
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('username')
      sessionStorage.removeItem('role')
      limpiarSesionPersistente()
    },
  },
})
