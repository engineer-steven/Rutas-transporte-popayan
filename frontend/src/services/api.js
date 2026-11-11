import axios from 'axios'

function createApiClient(baseURL) {
  const instance = axios.create({ baseURL, timeout: 10000 })

  instance.interceptors.request.use((config) => {
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  })

  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      const requestUrl = error.config?.url || ''
      const isAuthRequest = /\/(?:login|register)(?:[?#]|$)/.test(requestUrl)

      if (
        error.response?.status === 401 &&
        !isAuthRequest &&
        typeof window !== 'undefined'
      ) {
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('username')
        sessionStorage.removeItem('role')
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('role')

        if (window.location.pathname !== '/login') {
          window.location.replace('/login')
        }
      }

      return Promise.reject(error)
    },
  )

  return instance
}

export const apiRutas = createApiClient(
  import.meta.env.VITE_RUTAS_URL || 'http://127.0.0.1:5001',
)

export const apiOperaciones = createApiClient(
  import.meta.env.VITE_OPERACIONES_URL || 'http://127.0.0.1:5002',
)

export const apiMonitoreo = createApiClient(
  import.meta.env.VITE_MONITOREO_URL || 'http://127.0.0.1:5003',
)

const api = createApiClient(import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000')

export default api
