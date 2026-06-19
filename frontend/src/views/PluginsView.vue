<template>
  <div class="plugins-view">
    <div class="view-header">
      <div>
        <h2 class="section-title">Plugin Ecosystem</h2>
      </div>
      <div class="header-actions">
        <button class="action-btn" type="button" :disabled="loading" @click="loadAll">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="loading && !manifest" class="state-block">Loading plugin manifest...</div>

    <div v-else-if="error" class="state-block state-block--error">
      <p>{{ error }}</p>
      <button class="action-btn" type="button" @click="loadAll">Retry</button>
    </div>

    <template v-else-if="manifest">
      <div class="summary-row">
        <div class="summary-card">
          <span>Plugins</span>
          <strong>{{ manifest.total }}</strong>
        </div>
        <div class="summary-card" :class="{ success: enabledCount > 0 }">
          <span>Enabled</span>
          <strong>{{ enabledCount }}</strong>
        </div>
        <div class="summary-card">
          <span>Capabilities</span>
          <strong>{{ manifest.capabilities.length }}</strong>
        </div>
        <div class="summary-card">
          <span>Hooks</span>
          <strong>{{ manifest.supportedHooks.length }}</strong>
        </div>
      </div>

      <div class="tab-strip" role="tablist" aria-label="Plugin ecosystem sections">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          type="button"
          role="tab"
          :aria-selected="activeTab === tab.id"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <section v-if="activeTab === 'plugins'" class="plugins-grid">
        <article
          v-for="plugin in manifest.plugins"
          :key="plugin.name"
          class="plugin-card"
          :class="{ disabled: !plugin.enabled }"
        >
          <div class="plugin-main">
            <div class="plugin-title">
              <span class="status-dot" :class="{ active: plugin.enabled }"></span>
              <h3>{{ plugin.name }}</h3>
              <span class="version-pill">v{{ plugin.version }}</span>
            </div>
            <p class="plugin-description">{{ plugin.description || 'No description provided.' }}</p>
            <div class="meta-row">
              <span>{{ plugin.capabilities.length }} capabilities</span>
              <span>{{ plugin.permissions.length }} permissions</span>
              <span>{{ plugin.hooks.length }} hooks</span>
            </div>
          </div>

          <div class="plugin-detail-grid">
            <div>
              <span class="detail-label">Capabilities</span>
              <div class="chip-row">
                <span
                  v-for="capability in plugin.capabilities"
                  :key="`${plugin.name}-${capability.name}`"
                  class="chip"
                >
                  {{ capability.name }}
                </span>
                <span v-if="plugin.capabilities.length === 0" class="muted">None declared</span>
              </div>
            </div>
            <div>
              <span class="detail-label">Permissions</span>
              <div class="chip-row">
                <span
                  v-for="permission in plugin.permissions"
                  :key="`${plugin.name}-${permission}`"
                  class="chip chip--quiet"
                >
                  {{ permission }}
                </span>
                <span v-if="plugin.permissions.length === 0" class="muted">No elevated permissions</span>
              </div>
            </div>
            <div>
              <span class="detail-label">Entry points</span>
              <div class="entry-list">
                <span
                  v-for="[target, entry] in Object.entries(plugin.entryPoints)"
                  :key="`${plugin.name}-${target}`"
                >
                  <strong>{{ target }}</strong>: {{ entry }}
                </span>
                <span v-if="Object.keys(plugin.entryPoints).length === 0" class="muted">Not declared</span>
              </div>
            </div>
          </div>

          <div class="plugin-footer">
            <span>{{ plugin.enabled ? 'Enabled' : 'Disabled' }}</span>
            <button
              class="action-btn action-btn--sm"
              :class="{ 'action-btn--danger': plugin.enabled }"
              type="button"
              :disabled="busyPlugin === plugin.name"
              @click="togglePlugin(plugin)"
            >
              {{ toggleLabel(plugin) }}
            </button>
          </div>
        </article>

        <div v-if="manifest.plugins.length === 0" class="state-block">No plugins installed.</div>
      </section>

      <section v-else-if="activeTab === 'capabilities'" class="capability-layout">
        <div class="capability-list">
          <article
            v-for="capability in manifest.capabilities"
            :key="capability.name"
            class="capability-card"
          >
            <div class="capability-title">
              <h3>{{ capability.name }}</h3>
              <span>{{ capability.category }}</span>
            </div>
            <p>{{ capability.description || 'No description provided.' }}</p>
            <div class="capability-meta">
              <span>{{ capability.plugins.join(', ') }}</span>
              <span>{{ capability.hooks.length }} hooks</span>
            </div>
            <div class="chip-row">
              <span v-for="hook in capability.hooks" :key="`${capability.name}-${hook}`" class="chip">
                {{ hook }}
              </span>
            </div>
          </article>
        </div>

        <aside class="hook-panel">
          <h3>Supported hooks</h3>
          <div class="hook-list">
            <span v-for="hook in manifest.supportedHooks" :key="hook" class="hook-row">
              {{ hook }}
            </span>
          </div>
        </aside>
      </section>

      <section v-else class="logs-section">
        <div class="section-toolbar">
          <div>
            <h3>Recent hook activity</h3>
          </div>
          <button class="action-btn action-btn--sm" type="button" :disabled="logsLoading" @click="loadLogs">
            {{ logsLoading ? 'Refreshing...' : 'Refresh logs' }}
          </button>
        </div>

        <div v-if="logs.length === 0" class="state-block">No plugin executions recorded yet.</div>
        <div v-else class="log-list">
          <div
            v-for="(log, index) in logs"
            :key="`${log.plugin}-${log.hook}-${log.timestamp}-${index}`"
            class="log-row"
            :class="{ failed: !log.success }"
          >
            <span class="log-status">{{ log.success ? 'OK' : 'ERR' }}</span>
            <strong>{{ log.plugin }}</strong>
            <span>{{ log.hook }}</span>
            <span>{{ log.duration_ms }}ms</span>
            <span>{{ formatTime(log.timestamp) }}</span>
            <span v-if="log.error" class="log-error">{{ log.error }}</span>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  fetchPluginLogs,
  fetchPluginManifest,
  setPluginEnabled,
  type PluginInfo,
  type PluginLogEntry,
  type PluginManifestResponse,
} from '@/api/plugins'

type TabId = 'plugins' | 'capabilities' | 'logs'

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'plugins', label: 'Plugins' },
  { id: 'capabilities', label: 'Capabilities' },
  { id: 'logs', label: 'Activity' },
]

const manifest = ref<PluginManifestResponse | null>(null)
const logs = ref<PluginLogEntry[]>([])
const activeTab = ref<TabId>('plugins')
const loading = ref(false)
const logsLoading = ref(false)
const busyPlugin = ref('')
const error = ref<string | null>(null)

const enabledCount = computed(() => (
  manifest.value?.plugins.filter(plugin => plugin.enabled).length || 0
))

async function loadAll() {
  loading.value = true
  error.value = null
  try {
    const [manifestResult, logResult] = await Promise.all([
      fetchPluginManifest(),
      fetchPluginLogs(30),
    ])
    manifest.value = manifestResult
    logs.value = logResult.logs
  } catch (e: any) {
    error.value = e?.message || 'Failed to load plugin ecosystem'
  } finally {
    loading.value = false
  }
}

async function loadLogs() {
  logsLoading.value = true
  try {
    logs.value = (await fetchPluginLogs(30)).logs
  } catch (e: any) {
    error.value = e?.message || 'Failed to load plugin logs'
  } finally {
    logsLoading.value = false
  }
}

async function togglePlugin(plugin: PluginInfo) {
  busyPlugin.value = plugin.name
  error.value = null
  try {
    const result = await setPluginEnabled(plugin.name, !plugin.enabled)
    plugin.enabled = result.enabled
  } catch (e: any) {
    error.value = e?.message || `Failed to update ${plugin.name}`
  } finally {
    busyPlugin.value = ''
  }
}

function toggleLabel(plugin: PluginInfo) {
  if (busyPlugin.value === plugin.name) return 'Saving...'
  return plugin.enabled ? 'Disable' : 'Enable'
}

function formatTime(value: string) {
  if (!value) return 'unknown'
  try {
    return new Date(value).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return value
  }
}

onMounted(loadAll)
</script>

<style scoped>
.plugins-view {
  padding-bottom: 40px;
}

.view-header,
.section-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-5);
}

h2.section-title {
  position: relative;
  padding-left: 12px;
  color: var(--primary);
  font-size: 1.5rem;
  font-weight: 600;
}

h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 3px;
  height: 60%;
  border-radius: 0 2px 2px 0;
  background: var(--accent);
  transform: translateY(-50%);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.summary-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.summary-card span {
  display: block;
  color: var(--text-secondary);
  font-size: 0.78rem;
  text-transform: uppercase;
}

.summary-card strong {
  display: block;
  margin-top: var(--space-2);
  color: var(--primary);
  font-size: 1.8rem;
  line-height: 1;
}

.summary-card.success strong {
  color: var(--success-text);
}

.tab-strip {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  margin-bottom: var(--space-5);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
}

.tab-btn {
  min-width: 116px;
  padding: 8px 12px;
  border: 0;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
}

.tab-btn.active {
  background: var(--accent-subtle);
  color: var(--accent);
  font-weight: 600;
}

.plugins-grid,
.capability-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--space-4);
}

.plugin-card,
.capability-card,
.hook-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
}

.plugin-card.disabled {
  opacity: 0.72;
}

.plugin-title,
.capability-title,
.plugin-footer,
.meta-row,
.capability-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.plugin-title h3,
.capability-title h3,
.hook-panel h3,
.section-toolbar h3 {
  margin: 0;
  color: var(--primary);
  font-size: 1rem;
}

.status-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--text-secondary);
}

.status-dot.active {
  background: var(--success);
}

.version-pill,
.capability-title span {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.plugin-description,
.capability-card p {
  margin: var(--space-3) 0;
  color: var(--text-secondary);
  font-size: 0.88rem;
}

.meta-row,
.capability-meta {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.plugin-detail-grid {
  display: grid;
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.detail-label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.chip-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.chip {
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  background: var(--accent-subtle);
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 0.72rem;
}

.chip--quiet {
  background: var(--tag-bg);
  color: var(--text-secondary);
}

.entry-list,
.hook-list {
  display: grid;
  gap: var(--space-2);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.plugin-footer {
  justify-content: space-between;
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.capability-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: var(--space-4);
  align-items: start;
}

.hook-panel {
  position: sticky;
  top: var(--space-5);
}

.hook-row {
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.log-list {
  display: grid;
  gap: var(--space-2);
}

.log-row {
  display: grid;
  grid-template-columns: 52px minmax(120px, 1fr) minmax(120px, 1fr) 80px 110px minmax(0, 1.5fr);
  gap: var(--space-3);
  align-items: center;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.log-row.failed {
  border-color: color-mix(in srgb, var(--error) 35%, var(--border));
}

.log-status {
  color: var(--success-text);
  font-weight: 700;
}

.log-row.failed .log-status,
.log-error {
  color: var(--error);
}

.log-error {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.state-block {
  padding: var(--space-7);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
  color: var(--text-secondary);
  text-align: center;
}

.state-block--error {
  color: var(--error);
}

.state-block .action-btn {
  margin-top: var(--space-3);
}

.muted {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

@media (max-width: 900px) {
  .capability-layout {
    grid-template-columns: 1fr;
  }

  .hook-panel {
    position: static;
  }

  .log-row {
    grid-template-columns: 52px 1fr 1fr;
  }

  .log-error {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .tab-strip {
    width: 100%;
  }

  .tab-btn {
    flex: 1;
    min-width: 0;
  }

  .plugins-grid,
  .capability-list {
    grid-template-columns: 1fr;
  }

  .log-row {
    grid-template-columns: 1fr;
  }
}
</style>
