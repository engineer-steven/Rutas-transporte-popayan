import { defineStore } from 'pinia'

function leerLocal(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch (error) {
    console.error(`No se pudo leer la preferencia local "${key}".`, error)
    return fallback
  }
}

export const usePasajeroStore = defineStore('pasajero', {
  state: () => {
    const username = sessionStorage.getItem('username') || 'invitado'
    const scope = username.toLocaleLowerCase('es')

    return {
      scope,
      favorites: leerLocal(`popayanbus:${scope}:favorites`, []),
      history: leerLocal(`popayanbus:${scope}:history`, []),
      plan: leerLocal(`popayanbus:${scope}:plan`, 'basic'),
      preferences: leerLocal(`popayanbus:${scope}:preferences`, {
        alerts: true,
        reducedMotion: false,
      }),
    }
  },
  getters: {
    esPlus: (state) => state.plan === 'plus',
    esFavorito: (state) => (routeId) =>
      state.favorites.some((favorite) => favorite.routeId === routeId),
  },
  actions: {
    guardar(key, value) {
      try {
        localStorage.setItem(`popayanbus:${this.scope}:${key}`, JSON.stringify(value))
      } catch (error) {
        console.error(`No se pudo guardar la preferencia local "${key}".`, error)
        throw new Error('No se pudieron guardar los cambios en este dispositivo.')
      }
    },
    seleccionarPlan(plan) {
      this.plan = plan
      this.guardar('plan', plan)
    },
    alternarPlan() {
      this.seleccionarPlan(this.esPlus ? 'basic' : 'plus')
    },
    agregarFavorito(favorite) {
      if (this.esFavorito(favorite.routeId)) return
      this.favorites.unshift({ ...favorite, savedAt: new Date().toISOString() })
      this.guardar('favorites', this.favorites)
    },
    eliminarFavorito(routeId) {
      this.favorites = this.favorites.filter((favorite) => favorite.routeId !== routeId)
      this.guardar('favorites', this.favorites)
    },
    agregarViaje(trip) {
      this.history.unshift({ ...trip, id: `${Date.now()}-${trip.routeId}` })
      this.guardar('history', this.history)
    },
    borrarHistorial() {
      this.history = []
      this.guardar('history', this.history)
    },
    actualizarPreferencias(preferences) {
      this.preferences = { ...this.preferences, ...preferences }
      this.guardar('preferences', this.preferences)
    },
  },
})
