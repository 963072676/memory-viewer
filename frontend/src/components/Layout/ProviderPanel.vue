<template>
  <div class="provider-panel">
    <div class="view-header">
      <div>
        <h2 class="section-title">Memory Providers</h2>
        <p class="panel-caption">
          Active: <strong>{{ providerStore.activeProvider || 'none' }}</strong>
        </p>
      </div>
      <div class="header-actions">
        <button class="action-btn" type="button" :disabled="providerStore.loading" @click="loadProviders">
          {{ providerStore.loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="providerStore.loading && providerStore.providers.length === 0" class="loading">
      Loading providers...
    </div>

    <div v-else-if="providerStore.error" class="error-state">
      <p>{{ providerStore.error }}</p>
      <button class="action-btn" type="button" @click="loadProviders">Retry</button>
    </div>

    <template v-else>
      <div class="summary-row">
        <div class="summary-card">
          <div class="summary-value">{{ providerStore.providers.length }}</div>
          <div class="summary-label">Registered</div>
        </div>
        <div class="summary-card" :class="{ success: providerStore.healthyCount > 0 }">
          <div class="summary-value">{{ providerStore.healthyCount }}</div>
          <div class="summary-label">Healthy</div>
        </div>
        <div class="summary-card" :class="{ warn: providerStore.unhealthyCount > 0 }">
          <div class="summary-value">{{ providerStore.unhealthyCount }}</div>
          <div class="summary-label">Attention</div>
        </div>
        <div class="summary-card">
          <div class="summary-value">{{ fallbackCount }}</div>
          <div class="summary-label">Fallback</div>
        </div>
      </div>

      <section class="observability-section">
        <div class="subsection-header">
          <div>
            <h3>Provider Observability</h3>
          </div>
          <button
            class="action-btn"
            type="button"
            :disabled="providerStore.observabilityLoading"
            @click="refreshObservability"
          >
            {{ providerStore.observabilityLoading ? 'Refreshing...' : 'Refresh telemetry' }}
          </button>
        </div>

        <div
          v-if="providerStore.observabilityLoading && !providerStore.observability"
          class="loading loading--compact"
        >
          Loading telemetry...
        </div>

        <div v-else-if="providerStore.observabilityError" class="error-state error-state--compact">
          <p>{{ providerStore.observabilityError }}</p>
          <button class="action-btn" type="button" @click="refreshObservability">Retry</button>
        </div>

        <template v-else-if="observability">
          <div class="telemetry-grid">
            <div class="telemetry-card">
              <div class="telemetry-label">Active latency</div>
              <div class="telemetry-value">{{ formatLatency(activeStats?.avgLatencyMs) }}</div>
              <div class="telemetry-note">{{ providerStore.activeProvider || 'no active provider' }}</div>
            </div>
            <div class="telemetry-card">
              <div class="telemetry-label">Fallback used</div>
              <div class="telemetry-value">{{ observability.routing.fallbackUsed }}</div>
              <div class="telemetry-note">{{ observability.routing.fallback }} fallback routes</div>
            </div>
            <div class="telemetry-card" :class="{ warn: observability.routing.routeErrors > 0 }">
              <div class="telemetry-label">Route errors</div>
              <div class="telemetry-value">{{ observability.routing.routeErrors }}</div>
              <div class="telemetry-note">{{ providerStore.unhealthyCount }} unhealthy now</div>
            </div>
            <div class="telemetry-card">
              <div class="telemetry-label">Recent calls</div>
              <div class="telemetry-value">{{ observability.recentCalls.length }}</div>
              <div class="telemetry-note">last {{ formatTime(lastCall?.timestamp) }}</div>
            </div>
          </div>

          <div class="telemetry-layout">
            <div class="telemetry-panel">
              <div class="telemetry-panel-title">Provider latency</div>
              <div class="provider-metrics">
                <div class="provider-metric-row provider-metric-row--head">
                  <span>Provider</span>
                  <span>Avg</span>
                  <span>Error rate</span>
                  <span>Fallback wins</span>
                </div>
                <div
                  v-for="row in telemetryRows"
                  :key="row.name"
                  class="provider-metric-row"
                >
                  <span class="metric-provider">
                    <strong>{{ row.name }}</strong>
                    <small>{{ row.type }}</small>
                  </span>
                  <span>{{ formatLatency(row.avgLatencyMs) }}</span>
                  <span :class="{ danger: row.errorRate > 0 }">{{ formatRate(row.errorRate) }}</span>
                  <span>{{ row.fallbackSuccesses }}</span>
                </div>
              </div>
            </div>

            <div class="telemetry-panel">
              <div class="telemetry-panel-title">Recent routing paths</div>
              <div v-if="recentRoutes.length === 0" class="empty-telemetry">
                No routes recorded yet.
              </div>
              <div v-else class="route-list">
                <div
                  v-for="route in recentRoutes"
                  :key="`${route.timestamp}-${route.strategy}-${route.providers.join('-')}`"
                  class="route-row"
                  :class="{ warn: route.errors.length > 0, fallback: route.fallbackUsed }"
                >
                  <div class="route-main">
                    <span class="route-strategy">{{ route.strategy }}</span>
                    <strong>{{ routePath(route) }}</strong>
                  </div>
                  <div class="route-meta">
                    <span>{{ routeOutcome(route) }}</span>
                    <span>{{ formatLatency(route.latencyMs) }}</span>
                    <span>{{ formatTime(route.timestamp) }}</span>
                  </div>
                  <div v-if="route.errors.length" class="route-error">
                    {{ errorText(route.errors[0]) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="empty-telemetry">
          No provider telemetry yet.
        </div>
      </section>

      <form class="strategy-form" @submit.prevent="saveStrategy">
        <div class="form-grid">
          <div class="form-field">
            <label for="active-provider">Active provider</label>
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
            <label>Fallback providers</label>
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
              <label for="timeout-seconds">Timeout seconds</label>
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
              <label for="retry-attempts">Retry attempts</label>
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
              <label for="retry-backoff">Retry backoff</label>
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
              <span>Parallel query</span>
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: draft.parallelQuery }"
                @click="draft.parallelQuery = !draft.parallelQuery"
              >
                {{ draft.parallelQuery ? 'ON' : 'OFF' }}
              </button>
            </div>
            <div class="toggle-row">
              <span>Debug raw response</span>
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: draft.debugRawResponse }"
                @click="draft.debugRawResponse = !draft.debugRawResponse"
              >
                {{ draft.debugRawResponse ? 'ON' : 'OFF' }}
              </button>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button class="action-btn action-btn--accent" type="submit" :disabled="providerStore.saving">
            {{ providerStore.saving ? 'Saving...' : 'Save strategy' }}
          </button>
          <button class="action-btn" type="button" :disabled="providerStore.loading" @click="refreshHealth">
            Check health
          </button>
          <span v-if="saveOk" class="save-ok">Saved</span>
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
              <span v-if="provider.active" class="state-badge active-badge">ACTIVE</span>
              <span v-if="provider.fallback" class="state-badge fallback-badge">FALLBACK</span>
            </div>
            <div class="provider-meta">
              <span>{{ healthLabel(provider.name) }}</span>
              <span>{{ provider.enabled ? 'enabled' : 'disabled' }}</span>
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
            Make active
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useProviderStore } from '@/stores/providers'
import type { ProviderInfo, ProviderRouteEvent } from '@/api/providers'

const providerStore = useProviderStore()
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
const observability = computed(() => providerStore.observability)
const activeStats = computed(() => {
  const active = providerStore.activeProvider
  if (!active) return null
  return observability.value?.providers[active] || null
})
const lastCall = computed(() => {
  const calls = observability.value?.recentCalls || []
  return calls.length ? calls[calls.length - 1] : null
})
const telemetryRows = computed(() => (
  providerStore.providers.map(provider => {
    const stats = observability.value?.providers[provider.name]
    return {
      name: provider.name,
      type: stats?.type || provider.type,
      avgLatencyMs: stats?.avgLatencyMs || 0,
      errorRate: stats?.errorRate || 0,
      fallbackSuccesses: stats?.fallbackSuccesses || 0,
    }
  })
))
const recentRoutes = computed(() => (
  [...(observability.value?.routing.recentRoutes || [])].reverse().slice(0, 6)
))

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
  return 'Health check failed'
}

function healthClass(name: string) {
  const item = providerStore.health[name]
  if (!item) return 'unknown'
  return item.healthy ? 'healthy' : 'unhealthy'
}

function healthLabel(name: string) {
  const item = providerStore.health[name]
  if (!item) return 'unknown'
  return item.healthy ? 'healthy' : 'unhealthy'
}

function capabilityLabel(provider: ProviderInfo) {
  return provider.capabilities.length ? provider.capabilities.join(', ') : 'basic'
}

function formatLatency(value?: number) {
  const latency = Number(value) || 0
  if (latency >= 1000) return `${(latency / 1000).toFixed(2)} s`
  return `${Math.round(latency)} ms`
}

function formatRate(value?: number) {
  return `${Math.round((Number(value) || 0) * 100)}%`
}

function formatTime(timestamp?: number | null) {
  if (!timestamp) return 'none'
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function routePath(route: ProviderRouteEvent) {
  return route.providers.length ? route.providers.join(' -> ') : 'no provider'
}

function routeOutcome(route: ProviderRouteEvent) {
  if (route.successfulProviders.length > 1) return route.successfulProviders.join(', ')
  if (route.successfulProvider) return route.successfulProvider
  if (route.errors.length) return 'failed'
  return 'no result'
}

function errorText(error: Record<string, unknown>) {
  const provider = typeof error.provider === 'string' ? error.provider : ''
  const code = typeof error.code === 'string' ? error.code : ''
  const message = typeof error.message === 'string' ? error.message : ''
  return [provider, code || message].filter(Boolean).join(': ') || 'Provider error'
}

watch(() => providerStore.strategy, syncDraft, { immediate: true })

onMounted(() => {
  if (!providerStore.loaded) {
    loadProviders().catch(() => {
      // The store keeps the user-facing error.
    })
  }
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

.loading,
.error-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.error-state {
  color: var(--error-text);
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

.observability-section {
  margin-bottom: 24px;
  padding-top: 2px;
}

.subsection-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.subsection-header h3 {
  color: var(--primary);
  font-size: 1rem;
  font-weight: 700;
}

.loading--compact,
.error-state--compact {
  padding: 20px;
}

.telemetry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.telemetry-card {
  min-height: 112px;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.telemetry-card.warn {
  border-color: color-mix(in srgb, var(--warn-text) 28%, var(--border));
}

.telemetry-label,
.telemetry-note {
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.telemetry-value {
  margin-top: 10px;
  color: var(--primary);
  font-size: 1.45rem;
  font-weight: 800;
  line-height: 1.1;
}

.telemetry-note {
  margin-top: 8px;
}

.telemetry-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
}

.telemetry-panel {
  min-width: 0;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.telemetry-panel-title {
  margin-bottom: 12px;
  color: var(--primary);
  font-size: 0.9rem;
  font-weight: 700;
}

.provider-metrics,
.route-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.provider-metric-row {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(70px, 0.75fr));
  gap: 10px;
  align-items: center;
  min-height: 40px;
  padding: 8px 0;
  border-top: 1px solid var(--border);
  color: var(--primary);
  font-size: 0.82rem;
}

.provider-metric-row--head {
  min-height: 28px;
  padding-top: 0;
  border-top: none;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.metric-provider {
  min-width: 0;
}

.metric-provider strong,
.metric-provider small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-provider small {
  margin-top: 2px;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.danger,
.route-error {
  color: var(--error-text);
}

.route-row {
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
}

.route-row.fallback {
  border-color: color-mix(in srgb, var(--info-text) 25%, var(--border));
}

.route-row.warn {
  background: var(--warn-bg);
  border-color: color-mix(in srgb, var(--warn-text) 30%, var(--border));
}

.route-main,
.route-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.route-main strong {
  min-width: 0;
  color: var(--primary);
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.route-strategy {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--accent-subtle);
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
}

.route-meta {
  margin-top: 6px;
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.route-error {
  margin-top: 6px;
  font-size: 0.76rem;
  overflow-wrap: anywhere;
}

.empty-telemetry {
  padding: 18px;
  border: 1px dashed var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.84rem;
  text-align: center;
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
  .toggle-grid,
  .telemetry-layout {
    grid-template-columns: 1fr;
  }

  .provider-metric-row {
    grid-template-columns: minmax(0, 1fr) repeat(3, minmax(58px, 0.55fr));
    gap: 8px;
    font-size: 0.76rem;
  }

  .provider-metric-row--head {
    font-size: 0.66rem;
  }

  .provider-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
