import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import RutasView from '@/views/RutasView.vue'
import OperacionesView from '@/views/OperacionesView.vue'
import AlertasView from '@/views/AlertasView.vue'
import DespachoView from '@/views/DespachoView.vue'
import PlanificadorView from '@/views/PlanificadorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/rutas' },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { soloInvitados: true, authLayout: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { soloInvitados: true, authLayout: true },
    },
    {
      path: '/rutas',
      name: 'rutas',
      component: RutasView,
      meta: { requiereAuth: true, roles: ['ADMIN', 'SUPERVISOR', 'OPERADOR', 'USUARIO'] },
    },
    {
      path: '/operaciones',
      name: 'operaciones',
      component: OperacionesView,
      meta: { requiereAuth: true, roles: ['ADMIN', 'SUPERVISOR', 'OPERADOR'] },
    },
    {
      path: '/alertas',
      name: 'alertas',
      component: AlertasView,
      meta: { requiereAuth: true, roles: ['ADMIN', 'SUPERVISOR'] },
    },
    {
      path: '/despacho',
      name: 'despacho',
      component: DespachoView,
      meta: { requiereAuth: true, roles: ['ADMIN', 'SUPERVISOR', 'OPERADOR'] },
    },
    {
      path: '/planificador',
      name: 'planificador',
      component: PlanificadorView,
      meta: { requiereAuth: true, roles: ['ADMIN', 'SUPERVISOR', 'OPERADOR', 'USUARIO'] },
    },
  ],
})

// Guardia de navegación: protege rutas privadas y redirige al dashboard si ya inició sesión
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiereAuth && !auth.estaAutenticado) {
    return { name: 'login' }
  }
  if (to.meta.soloInvitados && auth.estaAutenticado) {
    return { name: auth.inicio }
  }
  if (to.meta.roles && !to.meta.roles.includes(auth.role)) {
    return { name: auth.inicio }
  }
})

export default router
