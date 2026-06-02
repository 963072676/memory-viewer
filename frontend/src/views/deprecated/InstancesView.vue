<template>
  <div class="instances-view">
    <div class="view-header">
      <h2>🖥️ 多实例管理</h2>
      <button class="action-btn" @click="fetchInstances">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="instances.length === 0" class="empty">暂无配置实例</div>

    <div v-else class="instance-list">
      <div v-for="(inst, i) in instances" :key="i" class="instance-card">
        <div class="instance-info">
          <div class="instance-name">
            {{ inst.name }}
            <span v-if="inst._status === 'online'" class="status-dot status-online" title="在线"></span>
            <span v-else-if="inst._status === 'offline'" class="status-dot status-offline" title="离线"></span>
          </div>
          <div class="instance-url">{{ inst.url }}</div>
          <div v-if="inst.description" class="instance-desc">{{ inst.description }}</div>
        </div>
        <div class="instance-actions">
          <a :href="inst.url" target="_blank" class="action-btn">打开 ↗</a>
          <button class="action-btn primary" @click="viewMemories(inst)" :disabled="inst._loading">
            {{ inst._loading ? '加载中...' : '查看记忆' }}
          </button>
        </div>
      </div>

      <!-- Proxy data display -->
      <div v-if="proxyError" class="proxy-error">{{ proxyError }}</div>
      <div v-if="proxyData" class="proxy-result">
        <div class="proxy-header">
          <h3>{{ proxyInstance }} 的记忆</h3>
          <button class="action-btn" @click="proxyData = null">关闭</button>
        </div>
        <div v-if="proxyData.status === 'offline'" class="proxy-offline">
          ⚠️ 实例不可达: {{ proxyData.error }}
        </div>
        <div v-else-if="proxyData.endpoint === 'agentmemory' && proxyData.data" class="proxy-memories">
          <div class="proxy-summary">共 {{ proxyData.data.memories?.length || 0 }} 条记忆</div>
          <div class="card-grid">
            <div v-for="mem in (proxyData.data.memories || []).slice(0, 50)" :key="mem.id" class="memory-card">
              <div class="card-type" :class="'type-' + mem.type">{{ mem.type }}</div>
              <h4>{{ mem.title }}</h4>
              <p>{{ mem.content?.substring(0, 120) }}{{ (mem.content?.length || 0) > 120 ? '...' : '' }}</p>
            </div>
          </div>
        </div>
        <div v-else-if="proxyData.endpoint === 'health' && proxyData.data" class="proxy-health">
          <pre>{{ JSON.stringify(proxyData.data, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface Instance {
  id: string
  name: string
  url: string
  description?: string
  _status?: 'online' | 'offline' | null
  _loading?: boolean
}

interface ProxyResult {
  instance: string
  endpoint: string
  status: string
  data?: any
  error?: string
}

const loading = ref(false)
const instances = ref<Instance[]>([])
const proxyData = ref<ProxyResult | null>(null)
const proxyInstance = ref('')
const proxyError = ref<string | null>(null)

async function fetchInstances() {
  loading.value = true
  try {
    const res = await fetch('/api/instances')
    const data = await res.json()
    instances.value = (data.instances || []).map((inst: Instance) => ({
      ...inst,
      _status: null,
      _loading: false,
    }))
  } catch (e) {
    console.error('Failed to fetch instances:', e)
  } finally {
    loading.value = false
  }
}

async function viewMemories(inst: Instance) {
  inst._loading = true
  proxyError.value = null
  proxyData.value = null
  proxyInstance.value = inst.name

  try {
    const res = await fetch(`/api/instances/${encodeURIComponent(inst.name)}/proxy?endpoint=agentmemory`)
    const data: ProxyResult = await res.json()
    proxyData.value = data

    if (data.status === 'offline') {
      inst._status = 'offline'
    } else {
      inst._status = 'online'
    }
  } catch (e: any) {
    proxyError.value = `请求失败: ${e.message}`
    inst._status = 'offline'
  } finally {
    inst._loading = false
  }
}

onMounted(() => fetchInstances())
</script>

<style scoped>
.instances-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; text-decoration: none; display: inline-block; font-family: var(--font); }
.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.primary { background: var(--accent); color: white; border-color: var(--accent); }
.action-btn.primary:hover { background: var(--accent-hover); }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--text-secondary); }
.instance-list { display: flex; flex-direction: column; gap: 12px; }
.instance-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; display: flex; justify-content: space-between; align-items: center; }
.instance-info { flex: 1; }
.instance-name { font-weight: 600; font-size: 1rem; color: var(--primary); display: flex; align-items: center; gap: 8px; }
.instance-url { font-size: 0.8rem; color: var(--text-secondary); font-family: monospace; margin-top: 4px; }
.instance-desc { font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px; }
.instance-actions { display: flex; gap: 8px; flex-shrink: 0; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.status-online { background: #22c55e; }
.status-offline { background: #ef4444; }

.proxy-error { margin-top: 16px; padding: 12px; background: var(--error-bg); border: 1px solid var(--error-text); border-radius: var(--radius); color: var(--error-text); font-size: 0.85rem; }
.proxy-result { margin-top: 20px; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.proxy-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.proxy-header h3 { font-size: 1.1rem; color: var(--primary); margin: 0; }
.proxy-offline { padding: 20px; text-align: center; color: var(--error-text); font-size: 0.9rem; }
.proxy-summary { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px; }
.proxy-health pre { font-size: 0.75rem; color: var(--text-secondary); background: var(--bg); padding: 12px; border-radius: 8px; overflow-x: auto; }

.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }
.memory-card { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
.memory-card h4 { font-size: 0.9rem; color: var(--primary); margin: 8px 0 4px; }
.memory-card p { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5; }
.card-type { font-size: 0.65rem; font-weight: 500; padding: 2px 8px; border-radius: 10px; display: inline-block; text-transform: capitalize; }
.type-pattern { background: #e8f5e9; color: #2e7d32; }
.type-fact { background: #e3f2fd; color: #1565c0; }
.type-preference { background: #fce4ec; color: #c62828; }
.type-bug { background: #fff3e0; color: #e65100; }
.type-workflow { background: #f3e5f5; color: #7b1fa2; }
.type-architecture { background: #e0f2f1; color: #00695c; }
[data-theme='dark'] .type-pattern { background: #1b3a1b; color: #66bb6a; }
[data-theme='dark'] .type-fact { background: #0d2744; color: #64b5f6; }
[data-theme='dark'] .type-preference { background: #3e1a1a; color: #ef9a9a; }
[data-theme='dark'] .type-bug { background: #3e2a0a; color: #ffcc80; }
[data-theme='dark'] .type-workflow { background: #2a1a3a; color: #ce93d8; }
[data-theme='dark'] .type-architecture { background: #0a2a2a; color: #80cbc4; }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .instance-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .instance-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
