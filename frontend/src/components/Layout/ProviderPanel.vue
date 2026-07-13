<template>
  <div class="provider-panel">
    <div class="view-header">
      <div>
        <h2 class="section-title">{{ $t('i18n.provider_title') }}</h2>
        <p class="panel-caption">
          {{ $t('i18n.provider_active_caption') }}
          <strong>{{ providerStore.activeProvider || $t('i18n.provider_none') }}</strong>
        </p>
      </div>
      <div class="header-actions">
        <button class="action-btn" type="button" :disabled="providerStore.loading" @click="loadProviders">
          {{ providerStore.loading ? $t('i18n.provider_refreshing') : $t('i18n.provider_refresh') }}
        </button>
      </div>
    </div>

    <div
      v-if="providerStore.loading && providerStore.providers.length === 0"
      class="panel-state"
      role="status"
      aria-live="polite"
    >
      <span class="state-spinner" aria-hidden="true"></span>
      <strong>{{ $t('i18n.provider_loading') }}</strong>
    </div>

    <div v-else-if="providerStore.error" class="panel-state panel-state--error" role="alert">
      <span class="state-indicator" aria-hidden="true">!</span>
      <strong>{{ $t('i18n.provider_load_failed') }}</strong>
      <p>{{ providerStore.error }}</p>
      <button class="action-btn" type="button" @click="loadProviders">{{ $t('i18n.retry') }}</button>
    </div>

    <div v-else-if="providerStore.providers.length === 0" class="panel-state">
      <span class="state-indicator state-indicator--empty" aria-hidden="true"></span>
      <strong>{{ $t('i18n.provider_no_providers') }}</strong>
      <p>{{ $t('i18n.provider_no_providers_hint') }}</p>
      <button class="action-btn" type="button" @click="loadProviders">{{ $t('i18n.provider_refresh') }}</button>
    </div>

    <template v-else>
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-value">{{ providerStore.providers.length }}</div>
          <div class="summary-label">{{ $t('i18n.provider_registered') }}</div>
        </div>
        <div class="summary-card" :class="{ success: providerStore.healthyCount > 0 }">
          <div class="summary-value">{{ providerStore.healthyCount }}</div>
          <div class="summary-label">{{ $t('i18n.provider_healthy') }}</div>
        </div>
        <div class="summary-card" :class="{ warn: providerStore.unhealthyCount > 0 }">
          <div class="summary-value">{{ providerStore.unhealthyCount }}</div>
          <div class="summary-label">{{ $t('i18n.provider_attention') }}</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ fallbackCount }}</div>
          <div class="summary-label">{{ $t('i18n.provider_fallback') }}</div>
        </div>
      </div>

      <ProviderObservabilityPanel :autoload="false" />

      <form class="strategy-form" @submit.prevent="saveStrategy">
        <div class="form-grid">
          <div class="form-field">
            <label for="active-provider">{{ $t('i18n.provider_active') }}</label>
            <select
              id="active-provider"
              v-model="draft.activeProvider"
              class="form-input"
              @change="dropActiveFromFallback"
            >
              <option
                v-for="provider in providerStore.providers"
                :key="provider.name"
                :value="provider.name"
              >
                {{ provider.name }} ({{ provider.type }})
              </option>
            </select>
          </div>

          <div class="form-field">
            <label>{{ $t('i18n.provider_fallback_providers') }}</label>
            <div class="fallback-list">
              <label
                v-for="provider in fallbackOptions"
                :key="provider.name"
                class="fallback-option"
                :class="{ selected: draft.fallbackProviders.includes(provider.name) }"
              >
                <input
                  type="checkbox"
                  :checked="draft.fallbackProviders.includes(provider.name)"
                  @change="toggleFallback(provider.name)"
                />
                <span>{{ provider.name }}</span>
                <span class="provider-mini">{{ provider.type }}</span>
              </label>
            </div>
          </div>

          <div class="numeric-grid">
            <div class="form-field">
              <label for="timeout-seconds">{{ $t('i18n.provider_timeout') }}</label>
              <input
                id="timeout-seconds"
                v-model.number="draft.timeoutSeconds"
                class="form-input"
                type="number"
                min="0.1"
                step="0.1"
              />
            </div>
            <div class="form-field">
              <label for="retry-attempts">{{ $t('i18n.provider_retry_attempts') }}</label>
              <input
                id="retry-attempts"
                v-model.number="draft.retryAttempts"
                class="form-input"
                type="number"
                min="1"
                step="1"
              />
            </div>
            <div class="form-field">
              <label for="retry-backoff">{{ $t('i18n.provider_retry_backoff') }}</label>
              <input
                id="retry-backoff"
                v-model.number="draft.retryBackoffSeconds"
                class="form-input"
                type="number"
                min="0"
                step="0.05"
              />
            </div>
          </div>

          <div class="toggle-grid">
            <div class="toggle-row">
              <span>{{ $t('i18n.provider_parallel_query') }}</span>
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: draft.parallelQuery }"
                :aria-label="$t('i18n.provider_parallel_query')"
                :aria-pressed="draft.parallelQuery"
                @click="draft.parallelQuery = !draft.parallelQuery"
              >
                {{ draft.parallelQuery
                  ? $t('i18n.provider_toggle_on')
                  : $t('i18n.provider_toggle_off') }}
              </button>
            </div>
            <div class="toggle-row">
              <span>{{ $t('i18n.provider_debug_raw') }}</span>
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: draft.debugRawResponse }"
                :aria-label="$t('i18n.provider_debug_raw')"
                :aria-pressed="draft.debugRawResponse"
                @click="draft.debugRawResponse = !draft.debugRawResponse"
              >
                {{ draft.debugRawResponse
                  ? $t('i18n.provider_toggle_on')
                  : $t('i18n.provider_toggle_off') }}
              </button>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button class="action-btn action-btn--accent" type="submit" :disabled="providerStore.saving">
            {{ providerStore.saving ? $t('i18n.provider_saving') : $t('i18n.provider_save_strategy') }}
          </button>
          <button class="action-btn" type="button" :disabled="providerStore.loading" @click="refreshHealth">
            {{ $t('i18n.provider_check_health') }}
          </button>
          <span v-if="saveOk" class="save-ok" role="status">{{ $t('i18n.saved') }}</span>
        </div>
      </form>

      <div class="provider-list">
        <div
          v-for="provider in providerStore.providers"
          :key="provider.name"
          class="provider-card"
          :class="{ disabled: !provider.enabled, active: provider.active }"
        >
          <div class="provider-card-main">
            <div class="provider-title">
              <span class="health-dot" :class="healthClass(provider.name)"></span>
              <span class="provider-name">{{ provider.name }}</span>
              <span class="provider-type-badge">{{ provider.type }}</span>
              <span v-if="provider.active" class="state-badge active-badge">
                {{ $t('i18n.provider_status_active') }}
              </span>
              <span v-if="provider.fallback" class="state-badge fallback-badge">
                {{ $t('i18n.provider_status_fallback') }}
              </span>
            </div>
            <div class="provider-meta">
              <span>{{ healthLabel(provider.name) }}</span>
              <span>{{ provider.enabled ? $t('i18n.enabled') : $t('i18n.disabled') }}</span>
              <span>{{ capabilityLabel(provider) }}</span>
            </div>
            <div v-if="providerError(provider.name)" class="provider-error">
              {{ providerError(provider.name) }}
            </div>
          </div>
          <button
            v-if="!provider.active"
            class="action-btn action-btn--sm"
            type="button"
            :disabled="providerStore.saving"
            @click="makeActive(provider.name)"
          >
            {{ $t('i18n.provider_make_active') }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProviderStore } from '@/stores/providers'
import ProviderObservabilityPanel from '@/components/Layout/ProviderObservabilityPanel.vue'
import type { ProviderInfo } from '@/api/providers'

const providerStore = useProviderStore()
const { t } = useI18n()
const saveOk = ref(false)

const draft = reactive({
  activeProvider: '',
  fallbackProviders: [] as string[],
  parallelQuery: false,
  timeoutSeconds: 10,
  retryAttempts: 1,
  retryBackoffSeconds: 0.1,
  debugRawResponse: false,
})

const fallbackOptions = computed(() => (
  providerStore.providers.filter(provider => provider.name !== draft.activeProvider)
))
const fallbackCount = computed(() => draft.fallbackProviders.length)

function syncDraft() {
  const strategy = providerStore.strategy
  if (!strategy) return
  draft.activeProvider = strategy.activeProvider
  draft.fallbackProviders = [...strategy.fallbackProviders]
  draft.parallelQuery = strategy.parallelQuery
  draft.timeoutSeconds = strategy.timeoutSeconds
  draft.retryAttempts = strategy.retryAttempts
  draft.retryBackoffSeconds = strategy.retryBackoffSeconds
  draft.debugRawResponse = strategy.debugRawResponse
}

function dropActiveFromFallback() {
  draft.fallbackProviders = draft.fallbackProviders.filter(name => name !== draft.activeProvider)
}

function toggleFallback(name: string) {
  if (name === draft.activeProvider) return
  const next = new Set(draft.fallbackProviders)
  if (next.has(name)) {
    next.delete(name)
  } else {
    next.add(name)
  }
  draft.fallbackProviders = Array.from(next)
}

function normalizedStrategy() {
  return {
    activeProvider: draft.activeProvider,
    fallbackProviders: draft.fallbackProviders.filter(name => name !== draft.activeProvider),
    parallelQuery: draft.parallelQuery,
    timeoutSeconds: Math.max(0.1, Number(draft.timeoutSeconds) || 10),
    retryAttempts: Math.max(1, Math.trunc(Number(draft.retryAttempts) || 1)),
    retryBackoffSeconds: Math.max(0, Number(draft.retryBackoffSeconds) || 0),
    debugRawResponse: draft.debugRawResponse,
  }
}

async function loadProviders() {
  await providerStore.load()
  syncDraft()
  await refreshObservability()
}

async function refreshHealth() {
  await providerStore.refreshHealth()
  await refreshObservability()
}

async function refreshObservability() {
  try {
    await providerStore.loadObservability(25)
  } catch {
    // The store keeps the user-facing telemetry error.
  }
}

async function saveStrategy() {
  await providerStore.saveStrategy(normalizedStrategy())
  syncDraft()
  await refreshObservability()
  saveOk.value = true
  setTimeout(() => { saveOk.value = false }, 2000)
}

async function makeActive(name: string) {
  draft.activeProvider = name
  dropActiveFromFallback()
  await providerStore.switchActiveProvider(name)
  syncDraft()
  await refreshObservability()
}

function providerError(name: string) {
  const error = providerStore.health[name]?.error
  if (!error) return ''
  const message = error.message
  const code = error.code
  if (typeof message === 'string') return message
  if (typeof code === 'string') return code
  return t('i18n.provider_health_check_failed')
}

function healthClass(name: string) {
  const item = providerStore.health[name]
  if (!item) return 'unknown'
  return item.healthy ? 'healthy' : 'unhealthy'
}

function healthLabel(name: string) {
  const item = providerStore.health[name]
  if (!item) return t('i18n.provider_health_unknown')
  return item.healthy ? t('i18n.healthy') : t('i18n.unhealthy')
}

function capabilityLabel(provider: ProviderInfo) {
  return provider.capabilities.length
    ? provider.capabilities.join(', ')
    : t('i18n.provider_basic_capability')
}


watch(() => providerStore.strategy, syncDraft, { immediate: true })

onMounted(() => {
  if (!providerStore.loaded) {
    loadProviders().catch(() => {
      // The store keeps the user-facing error.
    })
    return
  }

  refreshObservability()
})
</script>

<style scoped>
.provider-panel {
  padding-bottom: 40px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

h2.section-title {
  position: relative;
  padding-left: 12px;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
}

h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

.panel-caption {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.header-actions,
.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.panel-state {
  display: flex;
  min-height: 160px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
  padding: 32px;
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  background: var(--card);
  color: var(--text-secondary);
}

.panel-state strong {
  color: var(--primary);
  font-size: 0.95rem;
}

.panel-state p {
  max-width: 560px;
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.panel-state--error {
  border-style: solid;
  border-color: color-mix(in srgb, var(--error-text) 28%, var(--border));
  background: var(--error-bg);
  color: var(--error-text);
}

.panel-state--error strong {
  color: var(--error-text);
}

.state-spinner,
.state-indicator {
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
}

.state-spinner {
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: provider-spin 0.75s linear infinite;
}

.state-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid currentColor;
  border-radius: 50%;
  font-weight: 800;
}

.state-indicator--empty {
  border-color: var(--border-strong);
  color: var(--text-secondary);
}

.state-indicator--empty::after {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

@keyframes provider-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .state-spinner { animation: none; }
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.summary-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
}

.summary-card.success {
  border-color: var(--success-text);
}

.summary-card.warn {
  border-color: var(--error-text);
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
}

.summary-label {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.strategy-form {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 24px;
}

.form-grid {
  display: grid;
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label,
.toggle-row span {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-family: var(--font);
  font-size: 0.875rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-glow);
}

.fallback-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.fallback-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 34px;
  padding: 7px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  cursor: pointer;
  font-size: 0.85rem;
}

.fallback-option.selected {
  background: var(--accent-subtle);
  border-color: color-mix(in srgb, var(--accent) 35%, var(--border));
  color: var(--accent);
}

.fallback-option input {
  width: 15px;
  height: 15px;
  accent-color: var(--accent);
}

.provider-mini {
  color: var(--text-secondary);
  font-size: 0.72rem;
  text-transform: uppercase;
}

.numeric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.toggle-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
}

.toggle-btn {
  min-width: 52px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 700;
}

.toggle-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--card);
}

.form-actions {
  margin-top: 18px;
}

.save-ok {
  color: var(--success-text);
  font-size: 0.85rem;
  font-weight: 600;
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.provider-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
}

.provider-card.active {
  border-color: color-mix(in srgb, var(--accent) 35%, var(--border));
}

.provider-card.disabled {
  opacity: 0.65;
}

.provider-card-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.provider-title,
.provider-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.provider-name {
  color: var(--primary);
  font-size: 1rem;
  font-weight: 700;
}

.provider-meta {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.provider-type-badge,
.state-badge {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.active-badge {
  background: var(--accent-subtle);
  color: var(--accent);
  border-color: color-mix(in srgb, var(--accent) 30%, var(--border));
}

.fallback-badge {
  background: var(--info-bg);
  color: var(--info-text);
  border-color: color-mix(in srgb, var(--info-text) 25%, var(--border));
}

.health-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex: 0 0 auto;
  background: var(--text-secondary);
}

.health-dot.healthy {
  background: var(--success-text);
  box-shadow: 0 0 6px color-mix(in srgb, var(--success-text) 40%, transparent);
}

.health-dot.unhealthy {
  background: var(--error-text);
  box-shadow: 0 0 6px color-mix(in srgb, var(--error-text) 40%, transparent);
}

.provider-error {
  color: var(--error-text);
  font-size: 0.8rem;
}

@media (max-width: 767px) {
  h2.section-title {
    font-size: 1.2rem;
  }

  .strategy-form,
  .provider-card {
    padding: 14px;
  }

  .numeric-grid,
  .toggle-grid {
    grid-template-columns: 1fr;
  }

  .provider-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
