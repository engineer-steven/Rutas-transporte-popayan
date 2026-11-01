import { defineStore } from 'pinia'
import operacionesService from '@/services/operacionesService'

export const useOperacionesStore = defineStore('operaciones', {
  state: () => ({
    paraderos: [],
    incidentes: [],
    rutaSeleccionada: null,
  }),
  actions: {
    async cargarParaderos(routeId) {
      this.rutaSeleccionada = routeId
      const { data } = await operacionesService.obtenerParaderos(routeId)
      this.paraderos = data.paraderos || data.data || []
    },
    async cargarIncidentes(routeId) {
      this.rutaSeleccionada = routeId
      const { data } = await operacionesService.obtenerIncidentes(routeId)
      this.incidentes = data.incidentes || data.data || []
    },
    async reportarIncidente(payload) {
      await operacionesService.reportarIncidente(payload)
      if (this.rutaSeleccionada) {
        await this.cargarIncidentes(this.rutaSeleccionada)
      }
    },
  },
})

