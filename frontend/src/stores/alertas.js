import { defineStore } from 'pinia'
import alertasService from '@/services/alertasService'

export const useAlertasStore = defineStore('alertas', {
  state: () => ({
    lista: [],
  }),
  actions: {
    async cargar() {
      const { data } = await alertasService.obtenerTodas()
      this.lista = data.alertas || data.data || []
    },
    async crear(alerta) {
      await alertasService.crear(alerta)
      await this.cargar()
    },
    async actualizar(id, datos) {
      await alertasService.actualizar(id, datos)
      await this.cargar()
    },
    async eliminar(id) {
      await alertasService.eliminar(id)
      await this.cargar()
    },
  },
})

