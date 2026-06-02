<template>
  <div class="audit-view">
    <div class="view-header">
      <h2>📋 操作审计日志</h2>
      <div class="filters">
        <select v-model="filterMethod" @change="fetchAudit">
          <option value="">全部方法</option>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="PATCH">PATCH</option>
          <option value="DELETE">DELETE</option>
        </select>
        <input v-model="filterPath" placeholder="路径筛选..." @keyup.enter="fetchAudit" />
        <button class="action-btn" @click="fetchAudit">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <EmptyState v-else-if="loadError" icon="⚠️" message="审计日志加载失败" action-text="点击重试" @action="fetchAudit" />

    <div v-else-if="entries.length === 0" class="empty">暂无审计记录</div>

    <div v-else class="audit-table-wrap">
      <table class="audit-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>方法</th>
            <th>路径</th>
            <th>状态</th>
            <th>耗时</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(entry, i) in entries" :key="i">
            <td class="time-cell">{{ formatTime(entry.time) }}</td>
            <td><span :class="'method-badge method-' + entry.method?.toLowerCase()">{{ entry.method }}</span></td>
            <td class="path-cell">{{ entry.path }}</td>
            <td><span :class="['status-badge', entry.status < 400 ? 'status-ok' : 'status-err']">{{ entry.status }}</span></td>
            <td>{{ entry.duration_ms?.toFixed(1) }}ms</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import EmptyState from '@/components/Layout/EmptyState.vue'

interface AuditEntry { method: string; path: string; status: number; time: string; duration_ms: number; body?: string }

const loading = ref(false)
const entries = ref<AuditEntry[]>([])
const filterMethod = ref('')
const filterPath = ref('')
const loadError = ref(false)

function formatTime(t: string): string {
  if (!t) return ''
  const d = new Date(t)
  return d.toLocaleString('zh-CN')
}

async function fetchAudit() {
  loading.value = true
  loadError.value = false
  try {
    const params = new URLSearchParams({ limit: '200' })
    if (filterMethod.value) params.set('method', filterMethod.value)
    if (filterPath.value) params.set('path', filterPath.value)
    const res = await fetch(`/api/audit?${params}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    entries.value = data.entries || []
  } catch (e) {
    console.error('Failed to fetch audit log:', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchAudit())
</script>

<style scoped>
.audit-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
.filters { display: flex; gap: 8px; align-items: center; }
.filters select, .filters input { padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--card); color: var(--primary); font-size: 0.85rem; }
.action-btn { padding: 6px 14px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--text-secondary); }
.audit-table-wrap { overflow-x: auto; }
.audit-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.audit-table th { text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border); color: var(--text-secondary); font-weight: 600; }
.audit-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
.time-cell { white-space: nowrap; font-size: 0.8rem; }
.path-cell { font-family: monospace; font-size: 0.8rem; }
.method-badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.method-get { background: var(--info-bg); color: var(--info-text); }
.method-post { background: var(--success-bg); color: var(--success-text); }
.method-put { background: var(--warn-bg); color: var(--warn-text); }
.method-patch { background: var(--error-bg); color: var(--error-text); }
.method-delete { background: var(--error-bg); color: var(--error-text); }
.status-badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.status-ok { background: var(--success-bg); color: var(--success-text); }
.status-err { background: var(--error-bg); color: var(--error-text); }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters {
    flex-wrap: wrap;
    width: 100%;
  }

  .filters select,
  .filters input {
    flex: 1;
    min-width: 0;
  }
}
</style>
