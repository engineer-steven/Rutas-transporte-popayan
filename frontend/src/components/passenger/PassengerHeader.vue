<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { BusFront, UserRound } from '@lucide/vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function irAlPerfil() {
  router.push({ name: 'perfil' })
}
</script>

<template>
  <header class="passenger-topbar">
    <RouterLink class="passenger-brand" :to="{ name: 'inicio' }" aria-label="EnRutate, inicio">
      <span class="passenger-brand-mark"><BusFront :size="24" aria-hidden="true" /></span>
      <span class="passenger-brand-name">En<span>Rutate</span></span>
    </RouterLink>
    <button class="passenger-profile-shortcut" type="button" aria-label="Abrir perfil" @click="irAlPerfil">
      <UserRound :size="22" aria-hidden="true" />
    </button>
  </header>
</template>
