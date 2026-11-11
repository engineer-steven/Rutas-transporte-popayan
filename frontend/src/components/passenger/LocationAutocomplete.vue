<script setup>
import { computed, ref } from 'vue'
import { MapPin } from '@lucide/vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  id: { type: String, required: true },
  label: { type: String, required: true },
  placeholder: { type: String, required: true },
  suggestions: { type: Array, required: true },
  destination: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])
const open = ref(false)
const activeIndex = ref(-1)

const filteredSuggestions = computed(() => {
  const query = props.modelValue.trim().toLocaleLowerCase('es')
  if (!query) return props.suggestions.slice(0, 5)
  return props.suggestions
    .filter((place) => place.toLocaleLowerCase('es').includes(query))
    .slice(0, 5)
})

function elegir(place) {
  emit('update:modelValue', place)
  open.value = false
  activeIndex.value = -1
}

function manejarTeclas(event) {
  if (event.key === 'Escape') {
    open.value = false
    return
  }
  if (event.key === 'ArrowDown' && filteredSuggestions.value.length) {
    event.preventDefault()
    open.value = true
    activeIndex.value = (activeIndex.value + 1) % filteredSuggestions.value.length
  }
  if (event.key === 'Enter' && open.value && activeIndex.value >= 0) {
    event.preventDefault()
    elegir(filteredSuggestions.value[activeIndex.value])
  }
}
</script>

<template>
  <div
    :class="[
      'location-autocomplete',
      destination ? 'location-autocomplete-destination' : 'location-autocomplete-origin',
    ]"
    @focusout="(event) => !event.currentTarget.contains(event.relatedTarget) && (open = false)"
  >
    <span class="location-autocomplete-marker" aria-hidden="true">
      <MapPin class="location-autocomplete-icon" :size="20" />
    </span>
    <label class="location-autocomplete-content" :for="id">
      <span class="location-autocomplete-label">{{ label }}</span>
      <input
        :id="id"
        :value="modelValue"
        :placeholder="placeholder"
        autocomplete="off"
        maxlength="100"
        required
        role="combobox"
        :aria-expanded="open && filteredSuggestions.length > 0"
        :aria-controls="`${id}-suggestions`"
        aria-autocomplete="list"
        @input="emit('update:modelValue', $event.target.value); open = true; activeIndex = -1"
        @focus="open = true"
        @keydown="manejarTeclas"
      />
    </label>
    <ul
      v-if="open && filteredSuggestions.length"
      :id="`${id}-suggestions`"
      class="location-suggestions"
      role="listbox"
    >
      <li v-for="(place, index) in filteredSuggestions" :key="place" role="presentation">
        <button
          type="button"
          role="option"
          :aria-selected="activeIndex === index"
          @mousedown.prevent="elegir(place)"
        >
          <MapPin :size="16" aria-hidden="true" />
          {{ place }}
        </button>
      </li>
    </ul>
  </div>
</template>

<style>
.location-autocomplete {
  position: relative;
  z-index: 1;
  display: grid;
  min-width: 0;
  min-height: 74px;
  grid-template-columns: 42px minmax(0, 1fr);
  align-items: center;
  gap: 0.8rem;
  padding: 0.65rem 0.85rem;
  border: 1px solid #e4eaf2;
  border-radius: 15px;
  background: linear-gradient(110deg, #fff, #fbfdff);
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease;
}

.location-autocomplete-origin::after {
  position: absolute;
  z-index: 0;
  top: 48px;
  bottom: -39px;
  left: 34px;
  border-left: 2px dashed #c8d8e6;
  content: '';
  pointer-events: none;
}

.location-autocomplete:focus-within {
  z-index: 5;
  border-color: #7aaee0;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(37, 117, 190, 0.1);
}

.location-autocomplete-marker {
  position: relative;
  z-index: 1;
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid #d5eee8;
  border-radius: 13px;
  background: #eaf8f4;
  color: #168574;
}

.location-autocomplete-destination .location-autocomplete-marker {
  border-color: #d9e8fb;
  background: #edf4ff;
  color: #3279c2;
}

.location-autocomplete-content {
  display: grid;
  min-width: 0;
  gap: 0.2rem;
  cursor: text;
}

.location-autocomplete-label {
  color: #60738b;
  font-size: 0.67rem;
  font-weight: 780;
  letter-spacing: 0.015em;
}

.location-autocomplete-content input {
  width: 100%;
  min-width: 0;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: #18395d;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 680;
}

.location-autocomplete-content input::placeholder {
  color: #9aa8b9;
  font-weight: 450;
}

.location-suggestions {
  position: absolute;
  z-index: 8;
  top: calc(100% + 0.4rem);
  right: 0.4rem;
  left: 0.4rem;
  display: grid;
  gap: 0.2rem;
  margin: 0;
  padding: 0.4rem;
  border: 1px solid #e0e8f1;
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 12px 30px rgba(22, 52, 83, 0.16);
  list-style: none;
}

.location-suggestions button {
  display: flex;
  width: 100%;
  min-height: 42px;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.65rem;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: #38536f;
  font: inherit;
  font-size: 0.79rem;
  text-align: left;
  cursor: pointer;
}

.location-suggestions button:hover,
.location-suggestions button:focus-visible {
  outline: 0;
  background: #f0f6fc;
  color: #175f9c;
}

.location-suggestions button svg {
  flex: 0 0 auto;
  color: #3a85c5;
}

@media (max-width: 480px) {
  .location-autocomplete {
    min-height: 68px;
    grid-template-columns: 38px minmax(0, 1fr);
    gap: 0.65rem;
    padding: 0.55rem 0.65rem;
    border-radius: 13px;
  }

  .location-autocomplete-marker {
    width: 38px;
    height: 38px;
    border-radius: 11px;
  }

  .location-autocomplete-origin::after {
    top: 43px;
    bottom: -34px;
    left: 29px;
  }
}
</style>
