<template>
  <div class="plugins-view">
    <div class="plugins-header">
      <h2>🧩 插件管理</h2>
      <button class="btn-refresh" @click="loadPlugins" :disabled="loading">🔄 刷新</button>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="error" class="error-state">
      <p>⚠️ {{ error }}</p>
      <button class="btn-retry" @click="loadPlugins">点击重试</button>
    </div>
    <div v-else>
      <!-- Plugin List -->
      <div v-if="plugins.length === 0" class="empty-state">
        <div class="empty-icon">🧩</div>
        <p>暂无已安装的插件</p>
        <p class="empty-hint">将插件放置于 <code>backend/app/plugins/</code> 目录中</p>
      </div>

      <div v-else class="plugin-list">
        <div v-for="plugin in plugins" :key="plugin.name" class="plugin-card">
          <div class="plugin-info">
            <div class="plugin-name-row">
              <span class="plugin-name">{{ plugin.name }}</span>
              <span class="plugin-version">v{{ plugin.version }}</span>
              <span class="plugin-status" :class="{ enabled: plugin.enabled }">
                {{ plugin.enabled ? '✅ 已启用' : '⏸️ 已禁用' }}
              </span>
            </div>
            <p class="plugin-desc">{{ plugin.description || '无描述' }}</p>
            <div class="plugin-hooks">
              <span v-for="hook in plugin.hooks" :key="hook" class="hook-tag">{{ hook }}</span>
            </div>
          </div>
          <div class="plugin-actions">
            <button
              class="plugin-toggle"
              :class="{ disable: plugin.enabled }"
              @click="togglePlugin(plugin)"
            >
              {{ plugin.enabled ? '禁用' : '启用' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Execution Logs -->
      <div class="logs-section">
        <div class="logs-header">
          <h3>📋 执行日志</h3>
          <button class="btn-refresh" @click="loadLogs" :disabled="loadingLogs">🔄</button>
        </div>
        <div v-if="logs.length === 0" class="logs-empty">暂无执行记录</div>
        <div v-else class="logs-list">
          <div v-for="(log, idx) in logs" :key="idx" class="log-entry" :class="{ error: !log.success }">
            <span class="log-plugin">{{ log.plugin }}</span>
            <span class="log-hook">{{ log.hook }}</span>
            <span class="log-duration">{{ log.duration_ms }}ms</span>
            <span class="log-status">{{ log.success ? '✅' : '❌' }}</span>
            <span v-if="log.error" class="log-error">{{ log.error }}</span>
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import type { PluginInfo, PluginListResponse, PluginLogEntry } from '@/types'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const loading = ref(false)
const loadingLogs = ref(false)
const error = ref<string | null>(null)
const plugins = ref<PluginInfo[]>([])
const logs = ref<PluginLogEntry[]>([])

async function loadPlugins() {
  loading.value = true
  error.value = null
  try {
    const data = await request<PluginListResponse>('/plugins')
    plugins.value = data.plugins
  } catch (e: any) {
    error.value = e.message || '加载插件失败'
  } finally {
    loading.value = false
  }
}

async function loadLogs() {
  loadingLogs.value = true
  try {
    const data = await request<{ logs: PluginLogEntry[] }>('/plugins/logs/recent')
    logs.value = data.logs
  } catch (e: any) {
    console.error('Failed to load logs:', e)
  } finally {
    loadingLogs.value = false
  }
}

async function togglePlugin(plugin: PluginInfo) {
  const action = plugin.enabled ? 'disable' : 'enable'
  try {
    await request(`/plugins/${plugin.name}/${action}`, { method: 'POST' })
    plugin.enabled = !plugin.enabled
    toast.success(`插件 ${plugin.name} 已${plugin.enabled ? '启用' : '禁用'}`)
  } catch (e: any) {
    toast.error(e.message || '操作失败')
  }
}

function formatTime(ts: string): string {
  if (!ts) return ''
  try {
    const d = new Date(ts)
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ts
  }
}

onMounted(() => {
  loadPlugins()
  loadLogs()
})
</script>

<style scoped>
.plugins-view {
  padding-bottom: 40px;
}

.plugins-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.plugins-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0;
}

.btn-refresh {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
}

.btn-refresh:hover {
  background: var(--tag-bg);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.error-state {
  color: var(--error, #d93025);
}

.btn-retry {
  margin-top: 12px;
  padding: 8px 20px;
  border: 1px solid var(--error, #d93025);
  border-radius: 8px;
  background: transparent;
  color: var(--error, #d93025);
  font-size: 0.875rem;
  font-family: var(--font);
  cursor: pointer;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.empty-hint {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.empty-hint code {
  background: var(--tag-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.plugin-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
}

.plugin-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.plugin-info {
  flex: 1;
  min-width: 0;
}

.plugin-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.plugin-name {
  font-weight: 600;
  font-size: 1rem;
  color: var(--primary);
}

.plugin-version {
  font-size: 0.75rem;
  color: var(--text-secondary);
  background: var(--tag-bg);
  padding: 1px 6px;
  border-radius: 4px;
}

.plugin-status {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.plugin-status.enabled {
  color: #137333;
}

[data-theme='dark'] .plugin-status.enabled {
  color: #81c995;
}

.plugin-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 4px 0 8px;
}

.plugin-hooks {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.hook-tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-family: monospace;
}

.plugin-actions {
  flex-shrink: 0;
}

.plugin-toggle {
  padding: 6px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: all 0.2s;
}

.plugin-toggle:hover {
  background: var(--tag-bg);
}

.plugin-toggle.disable {
  border-color: var(--error, #d93025);
  color: var(--error, #d93025);
}

.plugin-toggle.disable:hover {
  background: rgba(229, 57, 53, 0.1);
}

/* Logs Section */
.logs-section {
  margin-top: 24px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.logs-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
}

.logs-empty {
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.75rem;
  flex-wrap: wrap;
}

.log-entry.error {
  border-color: rgba(229, 57, 53, 0.3);
  background: rgba(229, 57, 53, 0.05);
}

[data-theme='dark'] .log-entry.error {
  border-color: rgba(242, 139, 130, 0.3);
  background: rgba(242, 139, 130, 0.05);
}

.log-plugin {
  font-weight: 600;
  color: var(--accent);
  min-width: 80px;
}

.log-hook {
  color: var(--primary);
  font-family: monospace;
  min-width: 120px;
}

.log-duration {
  color: var(--text-secondary);
  min-width: 60px;
}

.log-status {
  min-width: 20px;
}

.log-error {
  color: var(--error, #d93025);
  flex: 1;
  min-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-time {
  color: var(--text-secondary);
  margin-left: auto;
  font-family: monospace;
}

@media (max-width: 767px) {
  .plugin-card {
    flex-direction: column;
  }

  .log-entry {
    font-size: 0.7rem;
  }
}
</style>
