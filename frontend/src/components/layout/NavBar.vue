<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const menuAbierto = ref(false)

function cerrarSesion() {
  menuAbierto.value = false
  auth.logout()
  router.push('/login')
}

</script>

<template>
  <header class="topbar">
    <RouterLink :to="{ name: auth.estaAutenticado ? auth.inicio : 'login' }" class="brand" @click="menuAbierto = false">
      <span class="brand-icon">🚌</span>
      <span class="brand-text">EnRutate</span>
    </RouterLink>

    <button
      v-if="auth.estaAutenticado"
      class="menu-toggle"
      type="button"
      :aria-expanded="menuAbierto"
      aria-controls="primary-navigation"
      :aria-label="menuAbierto ? 'Cerrar menú' : 'Abrir menú'"
      @click="menuAbierto = !menuAbierto"
    >
      <span></span><span></span><span></span>
    </button>

    <nav
      v-if="auth.estaAutenticado"
      id="primary-navigation"
      :class="['topbar-links', { 'topbar-links-open': menuAbierto }]"
      aria-label="Navegación principal"
    >
      <RouterLink to="/rutas" @click="menuAbierto = false">
        {{ auth.role === 'USUARIO' ? 'Explorar rutas' : 'Rutas' }}
      </RouterLink>
      <RouterLink
        v-if="['ADMIN', 'SUPERVISOR', 'OPERADOR'].includes(auth.role)"
        to="/operaciones"
        @click="menuAbierto = false"
      >Operaciones</RouterLink>
      <RouterLink
        v-if="['ADMIN', 'SUPERVISOR'].includes(auth.role)"
        to="/alertas"
        @click="menuAbierto = false"
      >Alertas</RouterLink>
      <RouterLink
        v-if="['ADMIN', 'SUPERVISOR', 'OPERADOR'].includes(auth.role)"
        to="/despacho"
        @click="menuAbierto = false"
      >Despacho</RouterLink>
      <RouterLink
        v-if="['ADMIN', 'SUPERVISOR', 'OPERADOR', 'USUARIO'].includes(auth.role)"
        to="/planificador"
        @click="menuAbierto = false"
      >{{ auth.role === 'USUARIO' ? 'Planear viaje' : 'Planificador' }}</RouterLink>
    </nav>

    <div class="topbar-right">
      <div v-if="auth.estaAutenticado" class="user-badge">
        <span class="username">👤 {{ auth.username }}</span>
        <span class="role-pill">{{ auth.role }}</span>
      </div>
      <span v-if="auth.estaAutenticado" class="role-label">{{ auth.role }}</span>
      <button v-if="auth.estaAutenticado" class="btn btn-secondary btn-sm" @click="cerrarSesion">
        Cerrar sesión
      </button>
      <RouterLink v-else to="/login" class="btn btn-accent btn-sm">
        Iniciar sesión
      </RouterLink>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.85rem 1.75rem;
  background: var(--color-primary-dark);
  color: var(--color-white);
  border-radius: 0 0 var(--radius) var(--radius);
  box-shadow: 0 4px 18px var(--color-shadow);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--color-white);
  font-weight: 800;
  font-size: 1.25rem;
  letter-spacing: -0.02em;
}

.brand-icon {
  font-size: 1.4rem;
}

.topbar-links {
  display: flex;
  gap: 1.1rem;
  flex: 1;
}

.menu-toggle,
.role-label {
  display: none;
}

.topbar-links a {
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.92rem;
  padding: 0.35rem 0.2rem;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.topbar-links a:hover {
  color: var(--color-white);
}

.topbar-links a.router-link-active {
  border-bottom-color: var(--color-accent);
  color: var(--color-white);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-left: auto;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.82rem;
}

.username {
  font-weight: 600;
}

.role-pill {
  background: var(--color-accent);
  color: var(--color-white);
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

@media (max-width: 820px) {
  .topbar {
    position: relative;
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 1rem;
  }

  .brand { grid-column: 1; }

  .menu-toggle {
    display: flex;
    grid-column: 2;
    grid-row: 1;
    width: 40px;
    height: 40px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 9px;
    background: rgba(255, 255, 255, 0.08);
  }

  .menu-toggle span {
    width: 17px;
    height: 2px;
    border-radius: 2px;
    background: white;
  }

  .topbar-links {
    display: none;
    grid-column: 1 / -1;
    grid-row: 2;
    width: 100%;
    flex-direction: column;
    gap: 0;
    padding: 0.35rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }

  .topbar-links-open {
    display: flex;
  }

  .topbar-links a {
    padding: 0.7rem 0.3rem;
    border: 0;
  }

  .topbar-right {
    grid-column: 1 / -1;
    grid-row: 3;
    width: 100%;
    margin: 0;
    padding-top: 0.7rem;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }

  .role-label {
    display: inline;
    margin-left: auto;
    color: #b7c4dd;
    font-size: 0.72rem;
    font-weight: 700;
  }

  .topbar-right .user-badge .role-pill {
    display: none;
  }
}
</style>
