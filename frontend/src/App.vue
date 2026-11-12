<script setup>
import { RouterView, useRoute } from 'vue-router'
import NavBar from '@/components/layout/NavBar.vue'
import PassengerHeader from '@/components/passenger/PassengerHeader.vue'
import PassengerBottomNav from '@/components/passenger/PassengerBottomNav.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
</script>

<template>
  <div
    :class="[
      { 'auth-layout': route.meta.authLayout },
      { 'passenger-layout': auth.estaAutenticado && auth.role === 'USUARIO' && !route.meta.authLayout },
    ]"
  >
    <PassengerHeader
      v-if="auth.estaAutenticado && auth.role === 'USUARIO' && !route.meta.authLayout"
    />
    <NavBar v-else-if="!route.meta.authLayout" />
    <main :class="{ 'passenger-main': auth.estaAutenticado && auth.role === 'USUARIO' }">
      <RouterView />
    </main>
    <PassengerBottomNav
      v-if="auth.estaAutenticado && auth.role === 'USUARIO' && !route.meta.authLayout"
    />
  </div>
</template>
