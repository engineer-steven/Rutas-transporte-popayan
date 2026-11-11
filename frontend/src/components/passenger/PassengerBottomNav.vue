<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { Crown, House, UserRound } from '@lucide/vue'

const route = useRoute()
const tabs = [
  { name: 'inicio', label: 'Inicio', icon: House },
  { name: 'planes', label: 'Planes', icon: Crown },
  { name: 'perfil', label: 'Perfil', icon: UserRound },
]
</script>

<template>
  <nav class="passenger-bottom-nav" aria-label="Navegación principal">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.name"
      :to="{ name: tab.name }"
      :class="{ 'passenger-tab-active': route.name === tab.name }"
      :aria-current="route.name === tab.name ? 'page' : undefined"
    >
      <component :is="tab.icon" :size="21" :stroke-width="2.2" aria-hidden="true" />
      <span>{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>
