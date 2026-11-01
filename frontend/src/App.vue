<script setup>
import { RouterView, useRoute } from 'vue-router'
import NavBar from '@/components/layout/NavBar.vue'

const route = useRoute()
</script>

<template>
  <div :class="{ 'auth-layout': route.meta.authLayout }">
    <NavBar v-if="!route.meta.authLayout" />
    <main>
      <RouterView />
    </main>
  </div>
</template>
