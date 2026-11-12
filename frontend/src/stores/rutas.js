import { defineStore } from 'pinia'
import rutasService from '@/services/rutasService'

export const useRutasStore = defineStore('rutas', {
  state: () => ({
    lista: [],
    filtroZona: '',
  }),
  actions: {
    async cargar() {
      let res
      if (this.filtroZona && this.filtroZona.trim() !== '') {
        res = await rutasService.buscarPorZona(this.filtroZona.trim())
      } else {
        res = await rutasService.obtenerTodas()
      }
      this.lista = res.data.rutas || res.data.data || []
    },
    async crear(ruta) {
      await rutasService.crear(ruta)
      await this.cargar()
    },
    async actualizar(id, ruta) {
      await rutasService.actualizar(id, ruta)
      await this.cargar()
    },
    async eliminar(id) {
      await rutasService.eliminar(id)
      await this.cargar()
    },
    async buscar(zona) {
      this.filtroZona = zona
      await this.cargar()
    },
    async limpiarFiltro() {
      this.filtroZona = ''
      await this.cargar()
    },
  },
})

