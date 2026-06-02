<template>
  <div class="conflicts-view">
    <div class="conflicts-header">
      <h2>⚠️ 记忆冲突检测</h2>
      <div class="header-actions">
        <select v-model="filterSeverity" @change="loadConflicts" class="filter-select">
          <option value="">全部严重程度</option>
          <option value="high">🔴 高</option>
          <option value="medium">🟠 中</option>
          <option value="low">🟡 低</option>
        </select>
        <button class="btn-scan" @click="scanConflicts" :disabled="scanning">
          {{ scanning ? '扫描中...' : '🔍 扫描冲突' }}
        </button>
      </div>
    </div>

    <!-- Summary -->
    <div class="summary-bar">
      <span class="summary-item">待处理: <strong>{{ summary.total }}</strong></span>
      <span class="summary-item high">🔴 高: {{ summary.high }}</span>
      <span class="summary-item medium">🟠 中: {{ summary.medium }}</span>
      <span class="summary-item low">🟡 低: {{ summary.low }}</span>
    </div>

    <div v-if="loading" class="loading-state">加载冲突数据中...</div>
    <div v-else-if="conflicts.length === 0" class="empty-state">
      <p>🎉 暂未发现冲突</p>
      <p class="empty-hint">点击"扫描冲突"按钮开始检测</p>
    </div>
    <div v-else>
      <ConflictCard
        v-for="conflict in conflicts"
        :key="conflict.id"
        :conflict="conflict"
        @resolve="handleResolve"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import ConflictCard from '@/components/Layout/ConflictCard.vue'

const toast = useToast()
const loading = ref(false)
const scanning = ref(false)
const conflicts = ref<any[]>([])
const filterSeverity = ref('')
const summary = ref({ total: 0, high: 0, medium: 0, low: 0 })

async function loadConflicts() {
  loading.value = true
  try {
    const params = filterSeverity.value ? `?severity=${filterSeverity.value}` : ''
    const res = await request<any>(`/conflicts${params}`)
    conflicts.value = res.conflicts || []
  } catch (e: any) {
    toast.error(e.message || '加载冲突数据失败')
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const res = await request<any>('/conflicts/summary')
    summary.value = res
  } catch {}
}

async function scanConflicts() {
  scanning.value = true
  try {
    const res = await request<any>('/conflicts/scan', { method: 'POST' })
    toast.success(`扫描完成，发现 ${res.conflicts_found} 个冲突`)
    await Promise.all([loadConflicts(), loadSummary()])
  } catch (e: any) {
    toast.error(e.message || '扫描失败')
  } finally {
    scanning.value = false
  }
}

async function handleResolve(conflictId: string, action: string) {
  try {
    await request(`/conflicts/${conflictId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ action, user: 'user' }),
    })
    toast.success(`冲突已解决: ${action}`)
    await Promise.all([loadConflicts(), loadSummary()])
  } catch (e: any) {
    toast.error(e.message || '解决冲突失败')
  }
}

onMounted(() => {
  Promise.all([loadConflicts(), loadSummary()])
})
</script>

<style scoped>
.conflicts-view {
  padding-bottom: 40px;
}

.conflicts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.conflicts-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-select {
  padding: 6px 10px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px;
  background: var(--card, #fff);
  font-size: 0.85rem;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
}

.btn-scan {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--accent, #007aff);
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: var(--font);
  font-weight: 500;
}

.btn-scan:disabled { opacity: 0.5; }

.summary-bar {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
}

.summary-item strong {
  color: var(--primary, #007aff);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary, #86868b);
  font-size: 1rem;
}

.empty-hint {
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
}
</style>
