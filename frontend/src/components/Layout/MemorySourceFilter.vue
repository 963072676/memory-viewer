<template>
  <div class="memory-source-filter">
    <label :for="inputId" class="memory-source-filter__label">{{ $t('i18n.data_source') }}</label>
    <div class="memory-source-filter__input">
      <select
        :id="inputId"
        :value="modelValue"
        class="memory-source-filter__select"
        :aria-busy="loading"
        @change="onChange"
      >
        <option value="">{{ $t('en_all') }}</option>
        <option v-for="source in sources" :key="source" :value="source">
          {{ source }}
        </option>
      </select>
      <span v-if="loading" class="memory-source-filter__state" role="status">
        {{ $t('i18n.source_filter_loading') }}
      </span>
      <button
        v-else-if="error"
        type="button"
        class="memory-source-filter__refresh"
        :aria-label="$t('i18n.source_filter_retry')"
        :title="$t('i18n.source_filter_retry')"
        @click="$emit('retry')"
      >
        ↻
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  modelValue: string
  sources: string[]
  loading?: boolean
  error?: boolean
  inputId?: string
}>(), {
  loading: false,
  error: false,
  inputId: 'memory-source-filter',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
  (e: 'retry'): void
}>()

function onChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.memory-source-filter,
.memory-source-filter__input {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.memory-source-filter__label {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.memory-source-filter__select {
  min-width: 140px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
  color: var(--primary);
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.85rem;
  outline: none;
}

.memory-source-filter__select:focus-visible {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.memory-source-filter__state {
  color: var(--text-tertiary);
  font-size: 0.75rem;
  white-space: nowrap;
}

.memory-source-filter__refresh {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 30px;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card);
  color: var(--text-secondary);
  cursor: pointer;
  font: inherit;
}

.memory-source-filter__refresh:hover,
.memory-source-filter__refresh:focus-visible {
  border-color: var(--accent);
  color: var(--accent);
  outline: none;
}

@media (max-width: 767px) {
  .memory-source-filter {
    width: 100%;
    align-items: stretch;
    flex-direction: column;
  }

  .memory-source-filter__input {
    width: 100%;
  }

  .memory-source-filter__select {
    flex: 1;
    min-width: 0;
    width: 100%;
  }
}
</style>
