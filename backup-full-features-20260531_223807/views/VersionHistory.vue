<template>
  <div class="version-history-view">
    <div class="view-header">
      <h2>📋 版本历史</h2>
      <button class="action-btn" @click="goBack">← 返回</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="memory" class="content">
      <div class="memory-info">
        <h3>{{ memory.title }}</h3>
        <p class="memory-meta">ID: {{ memory.id }} · 当前版本: v{{ memory.version }}</p>
      </div>

      <div v-if="versions.length === 0" class="empty">暂无历史版本</div>

      <div v-else class="version-list">
        <div v-for="v in versions" :key="v.version" class="version-card" :class="{ selected: selectedVersion === v.version }">
          <div class="version-header" @click="selectVersion(v)">
            <div class="version-info">
              <span class="version-num">v{{ v.version }}</span>
              <span class="version-time">{{ formatTime(v.timestamp) }}</span>
            </div>
            <button class="action-btn rollback-btn" @click.stop="rollback(v.version)" :disabled="rollingBack !== null">
              {{ rollingBack === v.version ? '回滚中...' : '回滚' }}
            </button>
          </div>
          <transition name="expand">
            <div v-if="selectedVersion === v.version" class="version-detail">
              <div class="detail-section">
                <label>标题</label>
                <span>{{ v.snapshot.title }}</span>
              </div>
              <div class="detail-section">
                <label>类型</label>
                <span>{{ v.snapshot.type }}</span>
              </div>
              <div class="detail-section">
                <label>强度</label>
                <span>{{ v.snapshot.strength * 10 }}%</span>
              </div>
              <div class="detail-section">
                <label>概念</label>
                <div class="tags">
                  <span class="tag" v-for="c in v.snapshot.concepts" :key="c">{{ c }}</span>
                </div>
              </div>
              <div class="detail-section">
                <label>内容</label>
                <pre class="content-preview">{{ v.snapshot.content }}</pre>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <div v-else class="empty">记忆未找到</div>
    <div v-if="message" :class="['message', message.type]">{{ message.text }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface VersionSnapshot {
  title: string
  content: string
  concepts: string[]
  strength: number
  type: string
}

interface Version {
  version: number
  snapshot: VersionSnapshot
  timestamp: string
}

interface MemoryInfo {
  id: string
  title: string
  version: number
  content: string
}

const route = useRoute()
const router = useRouter()
const memoryId = route.params.id as string

const loading = ref(false)
const memory = ref<MemoryInfo | null>(null)
const versions = ref<Version[]>([])
const selectedVersion = ref<number | null>(null)
const rollingBack = ref<number | null>(null)
const message = ref<{ text: string; type: string } | null>(null)

function showMessage(text: string, type: string = 'info') {
  message.value = { text, type }
  setTimeout(() => { message.value = null }, 4000)
}

function formatTime(ts: string) {
  try {
    return new Date(ts).toLocaleString('zh-CN')
  } catch {
    return ts
  }
}

function goBack() {
  router.push('/agentmemory')
}

function selectVersion(v: Version) {
  selectedVersion.value = selectedVersion.value === v.version ? null : v.version
}

async function fetchData() {
  loading.value = true
  try {
    const [memRes, verRes] = await Promise.all([
      fetch(`/api/agentmemory/${memoryId}`),
      fetch(`/api/agentmemory/${memoryId}/versions`),
    ])

    if (memRes.ok) {
      const memData = await memRes.json()
      memory.value = memData.memory || memData
    }

    if (verRes.ok) {
      const verData = await verRes.json()
      versions.value = (verData.versions || []).reverse()
    }
  } catch (e) {
    console.error('Failed to load version history:', e)
  } finally {
    loading.value = false
  }
}

async function rollback(version: number) {
  if (!confirm(`确定要回滚到 v${version} 吗？`)) return
  rollingBack.value = version
  try {
    const res = await fetch(`/api/agentmemory/${memoryId}/versions/${version}/rollback`, { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      showMessage(`已回滚到 v${version}`, 'success')
      await fetchData()
    } else {
      showMessage(`回滚失败: ${data.error || '未知错误'}`, 'error')
    }
  } catch (e) {
    showMessage('回滚失败', 'error')
  } finally {
    rollingBack.value = null
  }
}

onMounted(() => fetchData())
</script>

<style scoped>
.version-history-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--text-secondary); }
.memory-info { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 20px; }
.memory-info h3 { font-size: 1.1rem; color: var(--primary); margin-bottom: 4px; }
.memory-meta { font-size: 0.8rem; color: var(--text-secondary); }
.version-list { display: flex; flex-direction: column; gap: 12px; }
.version-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
.version-card.selected { border-color: var(--accent); }
.version-header { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; cursor: pointer; }
.version-header:hover { background: var(--tag-bg); }
.version-info { display: flex; align-items: center; gap: 12px; }
.version-num { font-weight: 700; font-size: 0.95rem; color: var(--accent); }
.version-time { font-size: 0.8rem; color: var(--text-secondary); }
.rollback-btn { font-size: 0.75rem; padding: 4px 12px; }
.version-detail { padding: 0 16px 16px; border-top: 1px solid var(--border); }
.detail-section { margin-top: 12px; }
.detail-section label { font-size: 0.75rem; color: var(--text-secondary); font-weight: 500; display: block; margin-bottom: 4px; }
.detail-section span { font-size: 0.85rem; color: var(--primary); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { font-size: 0.7rem; padding: 3px 8px; border-radius: 12px; background: var(--tag-bg); color: var(--text-secondary); }
.content-preview { font-size: 0.8rem; background: var(--bg); padding: 10px; border-radius: 6px; white-space: pre-wrap; word-break: break-word; max-height: 200px; overflow-y: auto; margin: 0; }
.message { margin-top: 16px; padding: 12px 16px; border-radius: 8px; font-size: 0.875rem; }
.message.success { background: var(--success-bg); color: var(--success-text); }
.message.error { background: var(--error-bg); color: var(--error-text); }
.expand-enter-active, .expand-leave-active { transition: all 0.25s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; }
.expand-enter-to, .expand-leave-from { opacity: 1; max-height: 500px; }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .version-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .rollback-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
