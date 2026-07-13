<template>
  <section class="provider-observability" aria-labelledby="provider-observability-title">
    <div class="observability-header">
      <h3 id="provider-observability-title">{{ $t('i18n.provider_observability') }}</h3>
      <button
        class="action-btn"
        type="button"
        :disabled="isLoading"
        @click="refreshObservability"
      >
        {{ isLoading ? $t('i18n.provider_refreshing') : $t('i18n.provider_refresh_telemetry') }}
      </button>
    </div>

    <div
      v-if="isLoading && !observability"
      class="observability-state"
      role="status"
      aria-live="polite"
    >
      <span class="state-spinner" aria-hidden="true"></span>
      <strong>{{ $t('i18n.provider_loading_telemetry') }}</strong>
    </div>

    <div v-else-if="loadError" class="observability-state observability-state--error" role="alert">
      <span class="state-indicator" aria-hidden="true">!</span>
      <strong>{{ $t('i18n.provider_telemetry_failed') }}</strong>
      <p>{{ loadError }}</p>
      <button class="action-btn" type="button" @click="refreshObservability">{{ $t('i18n.retry') }}</button>
    </div>

    <template v-else-if="observability">
      <div class="telemetry-grid">
        <div class="telemetry-card">
          <div class="telemetry-label">{{ $t('i18n.provider_active_latency') }}</div>
          <div class="telemetry-value">{{ formatLatency(activeStats?.avgLatencyMs) }}</div>
          <div class="telemetry-note">
            {{ providerStore.activeProvider || $t('i18n.provider_no_active') }}
          </div>
        </div>
        <div class="telemetry-card">
          <div class="telemetry-label">{{ $t('i18n.provider_fallback_used') }}</div>
          <div class="telemetry-value">{{ observability.routing.fallbackUsed }}</div>
          <div class="telemetry-note">
            {{ $t('i18n.provider_fallback_routes', { count: observability.routing.fallback }) }}
          </div>
        </div>
        <div class="telemetry-card" :class="{ warn: observability.routing.routeErrors > 0 }">
          <div class="telemetry-label">{{ $t('i18n.provider_route_errors') }}</div>
          <div class="telemetry-value">{{ observability.routing.routeErrors }}</div>
          <div class="telemetry-note">
            {{ $t('i18n.provider_unhealthy_now', { count: providerStore.unhealthyCount }) }}
          </div>
        </div>
        <div class="telemetry-card">
          <div class="telemetry-label">{{ $t('i18n.provider_recent_calls') }}</div>
          <div class="telemetry-value">{{ observability.recentCalls.length }}</div>
          <div class="telemetry-note">
            {{ $t('i18n.provider_last_call', { time: formatTime(lastCall?.timestamp) }) }}
          </div>
        </div>
      </div>

      <div class="telemetry-layout">
        <div class="telemetry-panel">
          <div class="telemetry-panel-title">{{ $t('i18n.provider_latency') }}</div>
          <div class="provider-metrics">
            <div class="provider-metric-row provider-metric-row--head">
              <span>{{ $t('i18n.provider_column') }}</span>
              <span>{{ $t('i18n.provider_average') }}</span>
              <span>{{ $t('i18n.provider_error_rate') }}</span>
              <span>{{ $t('i18n.provider_fallback_wins') }}</span>
            </div>
            <div v-for="row in telemetryRows" :key="row.name" class="provider-metric-row">
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
          <div class="telemetry-panel-title">{{ $t('i18n.provider_recent_routes') }}</div>
          <div v-if="recentRoutes.length === 0" class="empty-telemetry">
            {{ $t('i18n.provider_no_routes') }}
          </div>
          <div v-else class="route-list">
            <div
              v-for="route in recentRoutes"
              :key="`${route.timestamp}-${route.strategy}-${route.providers.join('-')}`"
              class="route-row"
              :class="{ warn: route.errors.length > 0, fallback: route.fallbackUsed }"
            >
              <div class="route-main">
                <span class="route-strategy">{{ routeStrategyLabel(route.strategy) }}</span>
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

    <div v-else class="observability-state">
      <span class="state-indicator state-indicator--empty" aria-hidden="true"></span>
      <strong>{{ $t('i18n.provider_no_telemetry') }}</strong>
      <p>{{ $t('i18n.provider_no_telemetry_hint') }}</p>
      <button class="action-btn" type="button" @click="refreshObservability">
        {{ $t('i18n.provider_refresh_telemetry') }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProviderStore } from '@/stores/providers'
import type { ProviderRouteEvent } from '@/api/providers'

const props = withDefaults(defineProps<{ autoload?: boolean }>(), {
  autoload: true,
})

const providerStore = useProviderStore()
const { t } = useI18n()
const observability = computed(() => providerStore.observability)
const isLoading = computed(() => providerStore.loading || providerStore.observabilityLoading)
const loadError = computed(() => providerStore.observabilityError || (
  providerStore.providers.length === 0 ? providerStore.error : null
))
const activeStats = computed(() => {
  const active = providerStore.activeProvider
  return active ? observability.value?.providers[active] || null : null
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

async function refreshObservability() {
  try {
    if (!providerStore.loaded && !providerStore.loading) {
      await providerStore.load()
    }
    await providerStore.loadObservability(25)
  } catch {
    // The store owns the user-facing provider and telemetry errors.
  }
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
  if (!timestamp) return t('i18n.provider_time_none')
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function routePath(route: ProviderRouteEvent) {
  return route.providers.length ? route.providers.join(' -> ') : t('i18n.provider_no_route')
}

function routeStrategyLabel(strategy: string) {
  const labels: Record<string, string> = {
    direct: t('i18n.provider_route_strategy_direct'),
    fallback: t('i18n.provider_route_strategy_fallback'),
    parallel: t('i18n.provider_route_strategy_parallel'),
  }
  return labels[strategy] || strategy
}

function routeOutcome(route: ProviderRouteEvent) {
  if (route.successfulProviders.length > 1) return route.successfulProviders.join(', ')
  if (route.successfulProvider) return route.successfulProvider
  if (route.errors.length) return t('i18n.provider_route_failed')
  return t('i18n.provider_no_result')
}

function errorText(error: Record<string, unknown>) {
  const provider = typeof error.provider === 'string' ? error.provider : ''
  const code = typeof error.code === 'string' ? error.code : ''
  const message = typeof error.message === 'string' ? error.message : ''
  return [provider, code || message].filter(Boolean).join(': ') || t('i18n.provider_error_generic')
}

onMounted(() => {
  if (props.autoload) refreshObservability()
})
</script>

<style scoped>
.provider-observability {
  margin-bottom: 24px;
}

.observability-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.observability-header h3 {
  margin: 0;
  color: var(--primary);
  font-size: 1rem;
  font-weight: 700;
}

.observability-state {
  display: flex;
  min-height: 132px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px;
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  background: var(--card);
  color: var(--text-secondary);
  text-align: center;
}

.observability-state strong {
  color: var(--primary);
  font-size: 0.95rem;
}

.observability-state p {
  max-width: 560px;
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.observability-state--error {
  border-style: solid;
  border-color: color-mix(in srgb, var(--error-text) 28%, var(--border));
  background: var(--error-bg);
  color: var(--error-text);
}

.observability-state--error strong {
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

@media (max-width: 767px) {
  .observability-header .action-btn {
    width: 100%;
  }

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
}
</style>
