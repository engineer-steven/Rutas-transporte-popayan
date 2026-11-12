<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const mostrarPassword = ref(false)
const mostrarConfirmacion = ref(false)
const error = ref('')
const exito = ref(false)
const cargando = ref(false)

async function onSubmit() {
  error.value = ''
  exito.value = false
  const usuario = username.value.trim()

  if (!/^[a-zA-Z0-9._-]{3,40}$/.test(usuario)) {
    error.value = 'El usuario debe tener entre 3 y 40 caracteres: letras, números, punto, guion o guion bajo.'
    return
  }

  if (
    password.value.length < 8 ||
    password.value.length > 128 ||
    !/[A-Za-z]/.test(password.value) ||
    !/[0-9]/.test(password.value)
  ) {
    error.value = 'La contraseña debe tener entre 8 y 128 caracteres, con al menos una letra y un número.'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }

  cargando.value = true
  try {
    await authService.registrar(usuario, password.value)
    exito.value = true
    username.value = ''
    password.value = ''
    confirmPassword.value = ''
  } catch (e) {
    error.value =
      e.response?.data?.mensaje ||
      e.response?.data?.error ||
      e.response?.data?.message ||
      'No fue posible crear la cuenta. Inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <main class="register-page">
    <section class="register-card" aria-labelledby="register-title">
      <RouterLink class="register-brand" to="/login" aria-label="EnRutate">
        <span class="register-brand-icon" aria-hidden="true">🚌</span>
        <span>En<span>Rutate</span></span>
      </RouterLink>

      <div class="register-heading">
        <span class="register-overline">NUEVA CUENTA</span>
        <h1 id="register-title">Crear cuenta</h1>
        <p>Regístrate como usuario para consultar el servicio.</p>
      </div>

      <p v-if="error" class="register-message register-message-error" role="alert">{{ error }}</p>
      <div v-if="exito" class="register-message register-message-success" role="status">
        <strong>Tu cuenta está lista.</strong>
        <span>Se creó con acceso de usuario. Ya puedes iniciar sesión.</span>
        <button type="button" @click="router.push('/login')">Ir a iniciar sesión</button>
      </div>

      <form v-else class="register-form" novalidate @submit.prevent="onSubmit">
        <div class="register-field">
          <label for="register-username">Usuario</label>
          <input
            id="register-username"
            v-model="username"
            name="username"
            type="text"
            placeholder="Ej. maria.popayan"
            autocomplete="username"
            minlength="3"
            maxlength="40"
            pattern="[A-Za-z0-9._-]{3,40}"
            required
          />
          <small>3 a 40 caracteres: letras, números, punto, guion o guion bajo.</small>
        </div>

        <div class="register-field">
          <label for="register-password">Contraseña</label>
          <div class="register-password">
            <input
              id="register-password"
              v-model="password"
              name="new-password"
              :type="mostrarPassword ? 'text' : 'password'"
              placeholder="Crea una contraseña"
              autocomplete="new-password"
              minlength="8"
              maxlength="128"
              required
            />
            <button
              type="button"
              :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="mostrarPassword = !mostrarPassword"
            >
              {{ mostrarPassword ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
          <small>Mínimo 8 caracteres, con al menos una letra y un número.</small>
        </div>

        <div class="register-field">
          <label for="confirm-password">Confirmar contraseña</label>
          <div class="register-password">
            <input
              id="confirm-password"
              v-model="confirmPassword"
              name="confirm-password"
              :type="mostrarConfirmacion ? 'text' : 'password'"
              placeholder="Repite la contraseña"
              autocomplete="new-password"
              maxlength="128"
              required
            />
            <button
              type="button"
              :aria-label="mostrarConfirmacion ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              @click="mostrarConfirmacion = !mostrarConfirmacion"
            >
              {{ mostrarConfirmacion ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
        </div>

        <button class="register-submit" type="submit" :disabled="cargando">
          {{ cargando ? 'Creando cuenta…' : 'Crear cuenta de usuario' }}
        </button>
      </form>

      <p class="register-login">
        ¿Ya tienes cuenta?
        <RouterLink to="/login">Inicia sesión</RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.register-page {
  display: grid;
  min-height: 100vh;
  padding: clamp(1rem, 4vw, 2.5rem);
  place-items: center;
  background:
    radial-gradient(ellipse at 12% 10%, rgba(196, 218, 255, 0.45), transparent 35%),
    radial-gradient(ellipse at 88% 90%, rgba(210, 241, 238, 0.55), transparent 32%),
    #f5f7fb;
}

.register-card {
  width: min(100%, 430px);
  padding: clamp(1.5rem, 6vw, 2.6rem);
  border: 1px solid #e8edf5;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 24px 70px rgba(27, 44, 77, 0.1);
}

.register-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  color: #17213a;
  font-size: 1.12rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  text-decoration: none;
}

.register-brand > span:last-child > span {
  color: #3261c8;
}

.register-brand-icon {
  display: grid;
  width: 41px;
  height: 41px;
  place-items: center;
  border-radius: 12px;
  background: #edf3ff;
  font-size: 1.3rem;
}

.register-heading {
  margin: 2rem 0 1.35rem;
}

.register-overline {
  color: #7181a0;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.register-heading h1 {
  margin-top: 0.4rem;
  color: #17213a;
  font-size: clamp(1.8rem, 7vw, 2.15rem);
  letter-spacing: -0.05em;
}

.register-heading p,
.register-field small {
  color: #74819a;
  font-size: 0.78rem;
}

.register-heading p {
  margin-top: 0.35rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 0.95rem;
}

.register-field label {
  display: block;
  margin-bottom: 0.4rem;
  color: #293752;
  font-size: 0.77rem;
  font-weight: 700;
}

.register-field > input,
.register-password {
  width: 100%;
  min-height: 47px;
  border: 1px solid #dfe5ef;
  border-radius: 9px;
  background: #fbfcfe;
}

.register-field > input,
.register-password input {
  padding: 0 0.8rem;
  color: #17213a;
  font: inherit;
  font-size: 0.82rem;
}

.register-field > input:focus,
.register-password:focus-within {
  border-color: #6d8fe0;
  outline: 0;
  box-shadow: 0 0 0 3px rgba(47, 93, 204, 0.1);
}

.register-password {
  display: flex;
  align-items: center;
  padding-right: 0.35rem;
}

.register-password input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
}

.register-password input::placeholder,
.register-field > input::placeholder {
  color: #a4afbf;
}

.register-password button {
  padding: 0.3rem;
  border: 0;
  background: transparent;
  color: #315fc4;
  font-size: 0.68rem;
  font-weight: 700;
}

.register-field small {
  display: block;
  margin-top: 0.35rem;
  font-size: 0.65rem;
}

.register-submit {
  min-height: 48px;
  margin-top: 0.25rem;
  border: 0;
  border-radius: 9px;
  background: linear-gradient(105deg, #2856c0, #3c6ddd);
  box-shadow: 0 7px 16px rgba(47, 93, 204, 0.2);
  color: white;
  font-size: 0.84rem;
  font-weight: 750;
}

.register-submit:disabled {
  cursor: wait;
  opacity: 0.7;
}

.register-message {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 9px;
  font-size: 0.78rem;
  line-height: 1.5;
}

.register-message-error {
  border: 1px solid #fecaca;
  background: #fff5f5;
  color: #b42332;
}

.register-message-success {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  border: 1px solid #bce6ce;
  background: #f0fbf4;
  color: #26744c;
}

.register-message-success button {
  align-self: flex-start;
  margin-top: 0.35rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: #2856c0;
  font-size: 0.75rem;
  font-weight: 700;
}

.register-login {
  margin-top: 1.35rem;
  color: #77839a;
  font-size: 0.77rem;
  text-align: center;
}

.register-login a {
  margin-left: 0.2rem;
  color: #315fc4;
  font-weight: 700;
  text-decoration: none;
}

.register-login a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .register-page {
    padding: 0.75rem;
  }

  .register-card {
    padding: 1.35rem;
    border-radius: 14px;
  }

  .register-heading {
    margin-top: 1.6rem;
  }
}
</style>
