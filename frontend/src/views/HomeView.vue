<script setup>
import { RouterLink } from 'vue-router'
import { ArrowRight, Check, Clock3, Map, MapPin, Menu, Route, ShieldCheck, Sparkles } from '@lucide/vue'
</script>

<template>
  <div class="public-home">
    <header class="public-header">
      <RouterLink to="/" class="public-brand" aria-label="EnRutate, inicio">
        <span class="public-brand-mark"><Route :size="22" /></span>
        <span>EnRutate</span>
      </RouterLink>

      <nav class="public-nav" aria-label="Navegación principal">
        <a href="#beneficios">Beneficios</a>
        <a href="#como-funciona">Cómo funciona</a>
      </nav>

      <div class="public-header-actions">
        <RouterLink to="/login" class="public-login">Iniciar sesión</RouterLink>
        <RouterLink to="/register" class="public-header-cta">Crear cuenta <ArrowRight :size="16" /></RouterLink>
      </div>
      <button class="public-menu" type="button" aria-label="Abrir menú"><Menu :size="21" /></button>
    </header>

    <main>
      <section class="public-hero">
        <div class="public-hero-copy">
          <p class="public-eyebrow"><Sparkles :size="16" /> Transporte más simple para tu día</p>
          <h1>Tu ciudad.<br /><em>Tu ruta.</em><br />Tu tiempo.</h1>
          <p class="public-hero-text">
            Encuentra la mejor forma de moverte por Popayán, planifica tus recorridos y viaja con más tranquilidad desde un solo lugar.
          </p>
          <div class="public-hero-actions">
            <RouterLink to="/register" class="public-primary-button">Empieza gratis <ArrowRight :size="18" /></RouterLink>
            <RouterLink to="/login" class="public-secondary-button">Ya tengo una cuenta</RouterLink>
          </div>
          <p class="public-trust"><Check :size="15" /> Regístrate en pocos segundos · Sin complicaciones</p>
        </div>

        <div class="public-hero-visual" aria-label="Vista previa de una ruta en EnRutate">
          <div class="public-orbit public-orbit-one"></div>
          <div class="public-orbit public-orbit-two"></div>
          <div class="public-map-card">
            <div class="public-map-top"><span><MapPin :size="15" /> Popayán, Cauca</span><span class="public-live"><i></i> En vivo</span></div>
            <div class="public-route-map">
              <div class="map-road map-road-one"></div>
              <div class="map-road map-road-two"></div>
              <div class="map-road map-road-three"></div>
              <div class="map-route-line"></div>
              <span class="map-point map-start"><MapPin :size="20" /></span>
              <span class="map-point map-end"><MapPin :size="20" /></span>
              <span class="map-label map-label-start">Origen</span>
              <span class="map-label map-label-end">Destino</span>
              <span class="map-bus">🚌</span>
            </div>
            <div class="public-route-info"><div><strong>Ruta óptima</strong><small>La mejor opción para ti</small></div><strong class="public-route-time"><Clock3 :size="17" /> 18 min</strong></div>
          </div>
          <div class="public-floating-card public-floating-card-top"><span class="public-floating-icon"><ShieldCheck :size="18" /></span><div><strong>Viaja con confianza</strong><small>Información clara en cada paso</small></div></div>
          <div class="public-floating-card public-floating-card-bottom"><span class="public-floating-icon purple"><Map :size="18" /></span><div><strong>Todo en un mapa</strong><small>Explora tus opciones</small></div></div>
        </div>
      </section>

      <section id="beneficios" class="public-benefits">
        <div class="public-section-heading"><p class="public-eyebrow">HECHO PARA MOVERTE MEJOR</p><h2>Menos vueltas.<br /><span>Más tiempo para ti.</span></h2></div>
        <div class="public-benefit-grid">
          <article class="public-benefit-card"><span class="public-benefit-icon blue"><Map :size="22" /></span><h3>Encuentra tu ruta</h3><p>Busca recorridos y descubre opciones pensadas para llegar a donde necesitas.</p></article>
          <article class="public-benefit-card"><span class="public-benefit-icon green"><Clock3 :size="22" /></span><h3>Planifica sin estrés</h3><p>Organiza tus viajes con información sencilla, clara y fácil de consultar.</p></article>
          <article class="public-benefit-card"><span class="public-benefit-icon orange"><ShieldCheck :size="22" /></span><h3>Viaja con confianza</h3><p>Guarda tus favoritos y ten tus rutas importantes siempre a la mano.</p></article>
        </div>
      </section>

      <section id="como-funciona" class="public-cta"><div><p class="public-eyebrow">TU PRÓXIMO VIAJE EMPIEZA AQUÍ</p><h2>Muévete con intención.</h2><p>Crea tu cuenta y empieza a descubrir una forma más fácil de recorrer la ciudad.</p></div><RouterLink to="/register" class="public-primary-button light">Crear mi cuenta <ArrowRight :size="18" /></RouterLink></section>
    </main>
    <footer class="public-footer"><span>© 2026 EnRutate</span><span>Movilidad inteligente para Popayán</span></footer>
  </div>
</template>

<style scoped>
.public-home { --ink: #102d54; --muted: #667891; --blue: #17649d; --teal: #0b9686; min-height: 100vh; overflow: hidden; color: var(--ink); background: #f8fbff; }
.public-header { position: relative; z-index: 2; display: flex; align-items: center; max-width: 1240px; margin: auto; padding: 1.25rem clamp(1.25rem, 4vw, 3.2rem); gap: 2rem; }
.public-brand { display: inline-flex; align-items: center; gap: .6rem; color: var(--ink); font-size: 1.25rem; font-weight: 850; text-decoration: none; letter-spacing: -.04em; }
.public-brand-mark { display: grid; width: 38px; height: 38px; place-items: center; border-radius: 12px; color: white; background: linear-gradient(135deg, #1568a5, #0e9e90); box-shadow: 0 7px 16px #17649d33; }
.public-nav { display: flex; gap: 1.8rem; margin-left: 3rem; }.public-nav a { color: var(--muted); font-size: .8rem; font-weight: 700; text-decoration: none; }.public-nav a:hover { color: var(--blue); }
.public-header-actions { display: flex; align-items: center; gap: 1.25rem; margin-left: auto; }.public-login { color: var(--ink); font-size: .8rem; font-weight: 750; text-decoration: none; }.public-header-cta, .public-primary-button { display: inline-flex; align-items: center; justify-content: center; gap: .5rem; border-radius: 999px; background: var(--ink); color: white; font-size: .8rem; font-weight: 800; text-decoration: none; }.public-header-cta { padding: .7rem 1.1rem; }.public-menu { display: none; border: 0; background: transparent; color: var(--ink); }
.public-hero { display: grid; max-width: 1240px; min-height: 635px; margin: auto; grid-template-columns: .86fr 1.14fr; align-items: center; padding: 2rem clamp(1.25rem, 4vw, 3.2rem) 4.5rem; gap: 2rem; }.public-hero-copy { position: relative; z-index: 1; }.public-eyebrow { display: flex; align-items: center; gap: .4rem; margin-bottom: 1rem; color: var(--teal); font-size: .68rem; font-weight: 850; letter-spacing: .16em; }.public-hero h1 { margin: 0; font-size: clamp(3.4rem, 7vw, 6.15rem); font-weight: 850; letter-spacing: -.09em; line-height: .91; }.public-hero h1 em { color: var(--teal); font-style: italic; }.public-hero-text { max-width: 39ch; margin-top: 1.5rem; color: var(--muted); font-size: .94rem; line-height: 1.7; }.public-hero-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .9rem; margin-top: 2rem; }.public-primary-button { padding: 1rem 1.4rem; background: linear-gradient(110deg, #104575, #128c83); box-shadow: 0 12px 20px #137c7a2e; }.public-secondary-button { color: var(--blue); font-size: .78rem; font-weight: 800; text-decoration: none; }.public-trust { display: flex; align-items: center; gap: .4rem; margin-top: 1.1rem; color: #8a98aa; font-size: .68rem; }.public-trust svg { color: var(--teal); }
.public-hero-visual { position: relative; min-height: 500px; }.public-hero-visual::before { position: absolute; top: 8%; right: 2%; width: 82%; height: 86%; border-radius: 50%; background: radial-gradient(ellipse, #dbf2ee 0%, #edf8f7 48%, transparent 70%); content: ''; }.public-orbit { position: absolute; border: 1px dashed #99cdc8; border-radius: 50%; transform: rotate(-25deg); }.public-orbit-one { top: 10%; left: 5%; width: 90%; height: 70%; }.public-orbit-two { top: 25%; left: 14%; width: 75%; height: 62%; border-color: #b5d9e3; transform: rotate(35deg); }.public-map-card { position: absolute; top: 13%; right: 11%; width: min(470px, 82%); overflow: hidden; border: 8px solid white; border-radius: 22px; background: white; box-shadow: 0 24px 55px #163e5b26; transform: rotate(2deg); }.public-map-top, .public-route-info { display: flex; align-items: center; justify-content: space-between; padding: .8rem 1rem; font-size: .66rem; font-weight: 800; }.public-map-top span:first-child { display: flex; align-items: center; gap: .35rem; }.public-map-top svg { color: var(--teal); }.public-live { display: flex; align-items: center; gap: .3rem; color: #2e9b72; }.public-live i { width: 6px; height: 6px; border-radius: 50%; background: #2e9b72; }.public-route-map { position: relative; height: 250px; overflow: hidden; background-color: #e9f1ed; background-image: linear-gradient(24deg, transparent 47%, #d6e5df 48% 51%, transparent 52%), linear-gradient(140deg, transparent 44%, #d2e2dc 45% 48%, transparent 49%), linear-gradient(76deg, transparent 47%, #d8e7e3 48% 50%, transparent 51%); }.map-road { position: absolute; border-radius: 50%; border: 10px solid #fff; opacity: .72; }.map-road-one { top: -80px; left: 35%; width: 180px; height: 400px; transform: rotate(28deg); }.map-road-two { top: 45%; left: -20%; width: 620px; height: 90px; transform: rotate(-12deg); }.map-road-three { top: 10%; left: -15%; width: 460px; height: 250px; transform: rotate(40deg); }.map-route-line { position: absolute; top: 11%; left: 29%; width: 44%; height: 79%; border: 5px solid var(--teal); border-top-color: transparent; border-radius: 50%; transform: rotate(-36deg); filter: drop-shadow(0 2px 3px #157f7244); }.map-point { position: absolute; z-index: 1; display: grid; place-items: center; color: #fff; filter: drop-shadow(0 3px 4px #1d506055); }.map-point svg { fill: var(--blue); stroke: white; }.map-start { top: 23%; left: 25%; }.map-end { right: 23%; bottom: 13%; }.map-end svg { fill: #ef8555; }.map-label { position: absolute; z-index: 1; padding: .28rem .45rem; border-radius: 5px; background: white; color: var(--ink); font-size: .55rem; font-weight: 800; box-shadow: 0 3px 8px #143d4a22; }.map-label-start { top: 19%; left: 33%; }.map-label-end { right: 9%; bottom: 15%; }.map-bus { position: absolute; top: 43%; left: 55%; display: grid; width: 35px; height: 35px; place-items: center; border-radius: 50%; background: white; box-shadow: 0 4px 10px #143d4a22; font-size: 1.15rem; }.public-route-info { padding: .8rem 1rem .55rem; }.public-route-info small { display: block; margin-top: .15rem; color: #91a0ae; font-size: .58rem; font-weight: 600; }.public-route-time { display: flex; align-items: center; gap: .25rem; color: var(--teal); }
.public-floating-card { position: absolute; z-index: 1; display: flex; align-items: center; gap: .65rem; padding: .75rem; border: 1px solid #e5edf4; border-radius: 13px; background: #fff; box-shadow: 0 13px 28px #1d50601c; }.public-floating-card-top { top: 11%; left: 0; }.public-floating-card-bottom { right: 0; bottom: 15%; }.public-floating-card strong, .public-floating-card small { display: block; }.public-floating-card strong { font-size: .65rem; }.public-floating-card small { margin-top: .15rem; color: #8a98aa; font-size: .54rem; }.public-floating-icon { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 10px; color: var(--teal); background: #e7f7f3; }.public-floating-icon.purple { color: #6b65c8; background: #eeedff; }
.public-benefits { max-width: 1240px; margin: auto; padding: 4.5rem clamp(1.25rem, 4vw, 3.2rem); }.public-section-heading h2 { margin: 0; font-size: clamp(2rem, 4vw, 3.2rem); letter-spacing: -.06em; line-height: 1; }.public-section-heading h2 span { color: var(--teal); }.public-benefit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 2.5rem; }.public-benefit-card { padding: 1.5rem; border: 1px solid #e3edf3; border-radius: 17px; background: white; }.public-benefit-icon { display: grid; width: 46px; height: 46px; place-items: center; margin-bottom: 1rem; border-radius: 13px; }.public-benefit-icon.blue { color: #177db4; background: #e7f5fc; }.public-benefit-icon.green { color: #159279; background: #e7f7f3; }.public-benefit-icon.orange { color: #d87b45; background: #fff1e7; }.public-benefit-card h3 { margin-bottom: .45rem; font-size: 1rem; }.public-benefit-card p { color: var(--muted); font-size: .78rem; line-height: 1.6; }.public-cta { display: flex; align-items: center; justify-content: space-between; max-width: 1176px; margin: 1rem auto 3rem; padding: 3.3rem clamp(1.25rem, 5vw, 4rem); border-radius: 24px; color: white; background: linear-gradient(110deg, #113e69, #147f7b); }.public-cta .public-eyebrow { color: #91e2d1; }.public-cta h2 { color: white; font-size: clamp(2rem, 4vw, 3rem); letter-spacing: -.06em; }.public-cta p:last-child { margin-top: .6rem; color: #c7e1e3; font-size: .82rem; }.public-primary-button.light { background: white; color: var(--ink); box-shadow: none; }.public-footer { display: flex; justify-content: space-between; max-width: 1240px; margin: auto; padding: 1.5rem clamp(1.25rem, 4vw, 3.2rem); color: #92a1b2; font-size: .65rem; }
@media (max-width: 800px) { .public-nav { display: none; }.public-header-actions { margin-left: auto; }.public-menu { display: grid; place-items: center; }.public-hero { grid-template-columns: 1fr; padding-top: 3rem; }.public-hero-visual { min-height: 430px; margin-top: -1rem; }.public-map-card { right: 8%; }.public-floating-card-top { left: 2%; }.public-benefit-grid { grid-template-columns: 1fr; }.public-cta { align-items: flex-start; flex-direction: column; gap: 1.7rem; margin-right: 1rem; margin-left: 1rem; } }
@media (max-width: 500px) { .public-header { padding: .85rem 1rem; }.public-header-actions { gap: .7rem; }.public-header-cta { padding: .6rem .7rem; font-size: .7rem; }.public-login { font-size: .7rem; }.public-hero { min-height: 0; padding-top: 3rem; }.public-hero h1 { font-size: 3.55rem; }.public-hero-visual { min-height: 355px; }.public-map-card { top: 11%; right: 2%; width: 91%; }.public-route-map { height: 190px; }.public-floating-card { transform: scale(.84); transform-origin: left center; }.public-floating-card-bottom { right: -1.5rem; transform-origin: right center; }.public-footer { flex-direction: column; gap: .3rem; } }
</style>
