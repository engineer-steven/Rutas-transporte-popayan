<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const mostrarPassword = ref(false)
const error = ref('')
const cargando = ref(false)

async function onSubmit() {
  error.value = ''
  const usuario = username.value.trim()

  if (!/^[a-zA-Z0-9._-]{3,40}$/.test(usuario)) {
    error.value = 'El usuario debe tener entre 3 y 40 caracteres: letras, números, punto, guion o guion bajo.'
    return
  }

  if (!password.value.trim() || password.value.length > 128) {
    error.value = 'Ingresa una contraseña válida de máximo 128 caracteres.'
    return
  }

  cargando.value = true
  try {
    await auth.login(usuario, password.value)
    await router.push({ name: auth.inicio })
  } catch (e) {
    error.value =
      e.response?.data?.mensaje ||
      e.response?.data?.error ||
      e.response?.data?.message ||
      'No fue posible conectar con el servicio. Inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-shell" aria-label="Acceso a EnRutate">
      <aside class="login-art" aria-label="EnRutate, transporte urbano de Popayán">
        <RouterLink class="login-brand" to="/login" aria-label="EnRutate">
          <span class="login-brand-icon" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none">
              <path
                d="M7 5.5h18a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-12a3 3 0 0 1 3-3Z"
                stroke="currentColor"
                stroke-width="2"
              />
              <path d="M5 15h22M9 9h14v4H9z" stroke="currentColor" stroke-width="2" />
              <circle cx="10" cy="23.5" r="2.5" fill="currentColor" />
              <circle cx="22" cy="23.5" r="2.5" fill="currentColor" />
            </svg>
          </span>
          <span>En<span>Rutate</span></span>
        </RouterLink>

        <svg class="route-art" viewBox="0 0 520 390" fill="none" aria-hidden="true">
          <path
            d="M31 302C102 302 86 215 160 215S219 312 287 250 348 120 423 143 455 82 502 66"
            stroke="rgba(220,231,255,.12)"
            stroke-width="34"
            stroke-linecap="round"
          />
          <path
            d="M31 302C102 302 86 215 160 215S219 312 287 250 348 120 423 143 455 82 502 66"
            stroke="#c9d8f4"
            stroke-width="3"
            stroke-linecap="round"
            stroke-dasharray="2 12"
          />
          <circle cx="160" cy="215" r="13" fill="#233b70" stroke="#8da9ed" stroke-width="4" />
          <circle cx="287" cy="250" r="13" fill="#233b70" stroke="#8da9ed" stroke-width="4" />
          <circle cx="423" cy="143" r="13" fill="#233b70" stroke="#8da9ed" stroke-width="4" />
          <circle cx="31" cy="302" r="9" fill="#8da9ed" />
          <circle cx="502" cy="66" r="9" fill="#8da9ed" />
          <g transform="translate(331 153) rotate(-30)">
            <rect width="82" height="58" rx="17" fill="#8da9ed" />
            <path
              d="M14 12h54a6 6 0 0 1 6 6v21H8V18a6 6 0 0 1 6-6Z"
              fill="#233b70"
            />
            <path d="M17 18h20v13H17zM44 18h20v13H44z" fill="#edf3ff" />
            <circle cx="20" cy="49" r="6" fill="#233b70" />
            <circle cx="62" cy="49" r="6" fill="#233b70" />
          </g>
        </svg>

        <div class="login-location">
          <span class="location-dot"></span>
          POPAYÁN <span class="location-divider">/</span> CAUCA
        </div>
      </aside>

      <section class="login-panel" aria-labelledby="login-title">
        <div class="login-content">
          <div class="login-heading">
            <span class="login-overline">BIENVENIDO DE NUEVO</span>
            <h1 id="login-title">Iniciar sesión</h1>
            <p>Ingresa tus datos para continuar.</p>
          </div>

          <p v-if="error" class="login-error" role="alert">
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.7" />
              <path
                d="M10 6v4.5M10 13.5v.1"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linecap="round"
              />
            </svg>
            {{ error }}
          </p>

          <form class="login-form" novalidate @submit.prevent="onSubmit">
            <div class="login-field">
              <label for="username">Usuario</label>
              <div class="login-input-wrap">
                <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <circle cx="10" cy="6.5" r="3" stroke="currentColor" stroke-width="1.6" />
                  <path
                    d="M4.5 16v-1.2a5.5 5.5 0 0 1 11 0V16h-11Z"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linejoin="round"
                  />
                </svg>
                <input
                  id="username"
                  v-model="username"
                  name="username"
                  type="text"
                  placeholder="Tu nombre de usuario"
                  autocomplete="username"
                  minlength="3"
                  maxlength="40"
                  pattern="[A-Za-z0-9._-]{3,40}"
                  aria-describedby="username-help"
                  required
                  autofocus
                />
              </div>
              <small id="username-help">3 a 40 caracteres: letras, números, punto, guion o guion bajo.</small>
            </div>

            <div class="login-field">
              <label for="password">Contraseña</label>
              <div class="login-input-wrap">
                <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <rect
                    x="4"
                    y="8.5"
                    width="12"
                    height="9"
                    rx="2"
                    stroke="currentColor"
                    stroke-width="1.6"
                  />
                  <path
                    d="M6.5 8.5V6a3.5 3.5 0 1 1 7 0v2.5M10 12v2"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                  />
                </svg>
                <input
                  id="password"
                  v-model="password"
                  name="password"
                  :type="mostrarPassword ? 'text' : 'password'"
                  placeholder="Tu contraseña"
                  autocomplete="current-password"
                  maxlength="128"
                  required
                />
                <button
                  class="password-toggle"
                  type="button"
                  :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                  @click="mostrarPassword = !mostrarPassword"
                >
                  <svg v-if="!mostrarPassword" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path
                      d="M2.5 10s2.7-5 7.5-5 7.5 5 7.5 5-2.7 5-7.5 5-7.5-5-7.5-5Z"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                    <circle cx="10" cy="10" r="2" stroke="currentColor" stroke-width="1.5" />
                  </svg>
                  <svg v-else viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path
                      d="m3 3 14 14M8.6 5.2A7.7 7.7 0 0 1 10 5c4.8 0 7.5 5 7.5 5a12 12 0 0 1-2.1 2.6M6.2 6.2C3.8 7.5 2.5 10 2.5 10s2.7 5 7.5 5c.8 0 1.5-.1 2.1-.4"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <button class="login-submit" type="submit" :disabled="cargando">
              <span>{{ cargando ? 'Validando…' : 'Entrar' }}</span>
              <svg v-if="!cargando" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path
                  d="M4 10h12m-5-5 5 5-5 5"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <span v-else class="login-spinner" aria-hidden="true"></span>
            </button>
          </form>

          <p class="login-register">
            ¿Aún no tienes cuenta?
            <RouterLink to="/register">Crear cuenta</RouterLink>
          </p>

          <div class="login-footer">
            <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
              <path
                d="M8 1.5 13 3.4v4.1c0 3.1-2.1 5.5-5 7-2.9-1.5-5-3.9-5-7V3.4l5-1.9Z"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linejoin="round"
              />
              <path
                d="m5.8 7.8 1.5 1.5 3-3"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            Acceso seguro
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  position: relative;
  display: grid;
  min-height: 100vh;
  overflow: hidden;
  padding: clamp(1rem, 4vw, 3rem);
  place-items: center;
  background: #f5f7fb;
}

.login-page::before,
.login-page::after {
  position: absolute;
  width: 28rem;
  height: 28rem;
  border: 1px solid rgba(50, 97, 200, 0.08);
  border-radius: 50%;
  content: '';
  pointer-events: none;
}

.login-page::before {
  top: -19rem;
  left: -12rem;
  box-shadow: 0 0 0 38px rgba(50, 97, 200, 0.025), 0 0 0 78px rgba(50, 97, 200, 0.02);
}

.login-page::after {
  right: -17rem;
  bottom: -19rem;
  box-shadow: 0 0 0 38px rgba(50, 97, 200, 0.025), 0 0 0 78px rgba(50, 97, 200, 0.02);
}

.login-shell {
  position: relative;
  z-index: 1;
  display: grid;
  width: min(100%, 1030px);
  min-height: 610px;
  overflow: hidden;
  grid-template-columns: 0.92fr 1.08fr;
  border: 1px solid #e8edf5;
  border-radius: 25px;
  background: #fff;
  box-shadow: 0 24px 70px rgba(27, 44, 77, 0.1);
}

.login-art {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  padding: 2.5rem 2.6rem 2rem;
  background:
    radial-gradient(ellipse at 18% 83%, rgba(109, 143, 224, 0.23), transparent 47%),
    linear-gradient(145deg, #17213a 0%, #263b70 100%);
  color: #fff;
}

.login-art::before,
.login-art::after {
  position: absolute;
  width: 370px;
  height: 370px;
  border: 1px solid rgba(237, 243, 255, 0.08);
  border-radius: 50%;
  content: '';
  pointer-events: none;
}

.login-art::before {
  top: 20%;
  left: -56%;
}

.login-art::after {
  top: 26%;
  left: -63%;
  width: 440px;
  height: 440px;
}

.login-brand {
  position: relative;
  z-index: 1;
  display: inline-flex;
  width: fit-content;
  align-items: center;
  gap: 0.75rem;
  color: #fff;
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  text-decoration: none;
}

.login-brand > span:last-child > span {
  color: #a9bdf5;
}

.login-brand-icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid rgba(169, 189, 245, 0.35);
  border-radius: 14px;
  background: rgba(169, 189, 245, 0.12);
  color: #a9bdf5;
}

.login-brand-icon svg {
  width: 25px;
  height: 25px;
}

.route-art {
  position: absolute;
  top: 50%;
  left: 50%;
  width: min(125%, 570px);
  transform: translate(-50%, -48%);
}

.login-location {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: rgba(237, 243, 255, 0.78);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.16em;
}

.location-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #a9bdf5;
  box-shadow: 0 0 0 4px rgba(169, 189, 245, 0.12);
}

.location-divider {
  color: #a9bdf5;
}

.login-panel {
  display: grid;
  min-width: 0;
  padding: clamp(2.5rem, 6vw, 5rem);
  place-items: center;
  background: #fff;
}

.login-content {
  width: min(100%, 370px);
}

.login-heading {
  margin-bottom: 2.25rem;
}

.login-overline {
  color: #7181a0;
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.16em;
}

.login-heading h1 {
  margin-top: 0.55rem;
  color: #17213a;
  font-size: clamp(2rem, 4vw, 2.45rem);
  letter-spacing: -0.06em;
}

.login-heading p {
  margin-top: 0.45rem;
  color: #74819a;
  font-size: 0.91rem;
}

.login-error {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  margin: -1rem 0 1.25rem;
  padding: 0.8rem;
  border: 1px solid #f2c7bf;
  border-radius: 11px;
  background: #fff4f1;
  color: #a63c2b;
  font-size: 0.82rem;
  line-height: 1.5;
}

.login-error svg {
  flex: 0 0 19px;
  width: 19px;
  height: 19px;
  margin-top: 1px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.3rem;
}

.login-field label {
  display: block;
  margin-bottom: 0.5rem;
  color: #293752;
  font-size: 0.79rem;
  font-weight: 750;
}

.login-input-wrap {
  display: flex;
  min-height: 54px;
  align-items: center;
  gap: 0.75rem;
  padding: 0 0.9rem;
  border: 1px solid #dfe5ef;
  border-radius: 12px;
  background: #fbfcfe;
  transition: border-color 0.18s, box-shadow 0.18s, background-color 0.18s;
}

.login-input-wrap:focus-within {
  border-color: #6d8fe0;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(47, 93, 204, 0.1);
}

.login-input-wrap > svg {
  flex: 0 0 19px;
  width: 19px;
  height: 19px;
  color: #7181a0;
}

.login-input-wrap input {
  width: 100%;
  min-width: 0;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: #17213a;
  font: inherit;
  font-size: 0.87rem;
}

.login-input-wrap input::placeholder {
  color: #a4a69e;
}

.login-field > small {
  display: block;
  margin-top: 0.48rem;
  color: #96978e;
  font-size: 0.68rem;
  line-height: 1.4;
}

.password-toggle {
  display: grid;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #7181a0;
}

.password-toggle:hover {
  background: #edf3ff;
  color: #2856c0;
}

.password-toggle svg {
  width: 18px;
  height: 18px;
}

.login-submit {
  display: flex;
  min-height: 54px;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.3rem;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(105deg, #2856c0, #3c6ddd);
  box-shadow: 0 7px 16px rgba(47, 93, 204, 0.2);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 750;
  transition: background-color 0.18s, box-shadow 0.18s, transform 0.18s;
}

.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #244eaa;
  box-shadow: 0 11px 22px rgba(47, 93, 204, 0.25);
}

.login-submit:focus-visible,
.password-toggle:focus-visible {
  outline: 3px solid rgba(47, 93, 204, 0.36);
  outline-offset: 3px;
}

.login-submit:disabled {
  cursor: wait;
  opacity: 0.7;
}

.login-submit svg {
  width: 18px;
  height: 18px;
}

.login-spinner {
  width: 17px;
  height: 17px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: white;
  border-radius: 50%;
  animation: login-spin 0.7s linear infinite;
}

.login-register {
  margin-top: 1.65rem;
  color: #74819a;
  font-size: 0.8rem;
  text-align: center;
}

.login-register a {
  margin-left: 0.2rem;
  color: #315fc4;
  font-weight: 750;
  text-decoration: none;
}

.login-register a:hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}

.login-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.42rem;
  margin-top: 2rem;
  padding-top: 1.3rem;
  border-top: 1px solid #e8edf5;
  color: #74819a;
  font-size: 0.71rem;
}

.login-footer svg {
  width: 15px;
  height: 15px;
  color: #3261c8;
}

@keyframes login-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 820px) {
  .login-page {
    padding: clamp(0.75rem, 4vw, 1.5rem);
  }

  .login-shell {
    width: min(100%, 510px);
    min-height: 0;
    grid-template-columns: minmax(0, 1fr);
  }

  .login-art {
    min-height: 156px;
    padding: 1.4rem 1.65rem;
  }

  .login-art::before {
    top: -5rem;
    left: 42%;
  }

  .login-art::after {
    top: -7rem;
    left: 38%;
  }

  .route-art {
    top: 48%;
    left: auto;
    right: -1.5rem;
    width: 220px;
    transform: translateY(-50%);
  }

  .login-location {
    margin-top: 1.5rem;
    font-size: 0.6rem;
  }

  .login-panel {
    padding: clamp(1.7rem, 7vw, 2.6rem);
  }

  .login-heading {
    margin-bottom: 1.75rem;
  }
}

@media (max-width: 420px) {
  .login-page {
    padding: 0;
    background: #fff;
  }

  .login-shell {
    min-height: 100vh;
    border: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .login-art {
    min-height: 142px;
    padding: 1.15rem 1.25rem;
  }

  .login-brand {
    font-size: 1.05rem;
  }

  .login-brand-icon {
    width: 38px;
    height: 38px;
  }

  .route-art {
    right: -2.7rem;
    width: 190px;
  }

  .login-panel {
    align-items: start;
    padding: 2.2rem 1.35rem 1.6rem;
  }

  .login-heading h1 {
    font-size: 2rem;
  }

  .login-footer {
    margin-top: 1.6rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .login-spinner {
    animation-duration: 1.5s;
  }
}
</style>
