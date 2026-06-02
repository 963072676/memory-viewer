<template>
  <div class="version-history-view">
    <div class="view-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h2>📋 版本历史</h2>
      <div class="version-selector" v-if="versions.length >= 2">
        <span class="selector-label">对比版本:</span>
        <select v-model.number="compareFrom" class="version-select">
          <option v-for="v in versions" :key="v.version" :value="v.version">v{{ v.version }}</option>
        </select>
        <span class="selector-arrow">→</span>
        <select v-model.number="compareTo" class="version-select">
          <option v-for="v in versions" :key="v.version" :value="v.version">v{{ v.version }}</option>
        </select>
        <button class="action-btn" @click="fetchDiff" :disabled="!compareFrom || !compareTo">对比</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="action-btn" @click="fetchVersions">重试</button>
    </div>

    <template v-else>
      <div class="memory-info" v-if="memory">
        <div class="memory-header-row">
          <h3>{{ memory.title }}</h3>
          <span class="current-version">当前版本: v{{ currentVersion }}</span>
        </div>
        <p class="memory-meta">ID: {{ memoryId }}</p>
      </div>

      <div v-if="versions.length === 0" class="empty-state">
        <p>暂无历史版本</p>
      </div>

      <div v-else class="version-list">
        <div
          v-for="v in versions"
          :key="v.version"
          class="version-card"
          :class="{ selected: selectedVersion === v.version, current: v.version === currentVersion }"
        >
          <div class="version-header" @click="toggleVersion(v.version)">
            <div class="version-info">
              <span class="version-num">
                v{{ v.version }}
                <span v-if="v.version === currentVersion" class="current-badge">当前</span>
              </span>
              <span class="version-time">{{ formatTime(v.created_at) }}</span>
            </div>
            <div class="version-actions">
              <button
                class="action-btn rollback-btn"
                @click.stop="confirmRollback(v.version)"
                :disabled="rollingBack === v.version || v.version === currentVersion"
              >
                {{ rollingBack === v.version ? '回滚中...' : '回滚' }}
              </button>
            </div>
          </div>

          <transition name="expand">
            <div v-if="selectedVersion === v.version" class="version-detail">
              <div class="detail-grid">
                <div class="detail-item">
                  <label>标题</label>
                  <span>{{ v.title }}</span>
                </div>
                <div class="detail-item">
                  <label>内容</label>
                  <pre class="content-preview">{{ v.content }}</pre>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Diff Panel -->
      <div v-if="diffData" class="diff-panel">
        <div class="diff-header">
          <h4>版本对比: v{{ diffData.from_version }} → v{{ diffData.to_version }}</h4>
          <button class="close-btn" @click="diffData = null">×</button>
        </div>
        <div class="diff-content">
          <div class="diff-section" v-if="diffData.diff.title_changed">
            <span class="diff-label">标题</span>
            <div class="diff-change">
              <pre class="diff-old">{{ diffData.diff.title_diff?.split('|||')[0] || '' }}</pre>
              <pre class="diff-new">{{ diffData.diff.title_diff?.split('|||')[1] || '' }}</pre>
            </div>
          </div>
          <div class="diff-section" v-if="diffData.diff.content_changed">
            <span class="diff-label">内容</span>
            <div class="diff-change">
              <pre class="diff-old">{{ diffData.diff.content_diff?.split('|||')[0] || '' }}</pre>
              <pre class="diff-new">{{ diffData.diff.content_diff?.split('|||')[1] || '' }}</pre>
            </div>
          </div>
          <div v-if="!diffData.diff.title_changed && !diffData.diff.content_changed" class="no-diff">
            两版本无变化
          </div>
        </div>
      </div>
    </template>

    <!-- Rollback Confirmation Modal -->
    <div v-if="rollbackConfirmVersion !== null" class="modal-overlay" @click.self="rollbackConfirmVersion = null">
      <div class="modal-content">
        <h3>确认回滚</h3>
        <p>确定要将记忆回滚到 <strong>v{{ rollbackConfirmVersion }}</strong> 吗？</p>
        <p class="modal-warning">⚠️ 此操作将创建一个新版本，不会删除历史版本。</p>
        <div class="modal-actions">
          <button class="action-btn" @click="rollbackConfirmVersion = null">取消</button>
          <button class="action-btn primary" @click="executeRollback" :disabled="rollingBack !== null">
            {{ rollingBack !== null ? '回滚中...' : '确认回滚' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Message Toast -->
    <transition name="fade">
      <div v-if="message" :class="['message-toast', message.type]">
        {{ message.text }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getVersions, getVersionDiff, rollbackVersion, VersionInfo } from '@/api/versioning'

const route = useRoute()
const router = useRouter()

const memoryId = computed(() => route.params.id as string)

// State
const loading = ref(false)
const error = ref<string | null>(null)
const memory = ref<{ id: string; title: string } | null>(null)
const versions = ref<VersionInfo[]>([])
const currentVersion = ref(0)
const selectedVersion = ref<number | null>(null)

// Comparison state
const compareFrom = ref<number | null>(null)
const compareTo = ref<number | null>(null)
const diffData = ref<{
  from_version: number
  to_version: number
  diff: {
    title_changed: boolean
    content_changed: boolean
    title_diff?: string
    content_diff?: string
  }
} | null>(null)

// Rollback state
const rollbackConfirmVersion = ref<number | null>(null)
const rollingBack = ref<number | null>(null)

// Message
const message = ref<{ text: string; type: 'success' | 'error' | 'info' } | null>(null)

function showMessage(text: string, type: 'success' | 'error' | 'info' = 'info') {
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
  router.push(`/memory/${memoryId.value}`)
}

function toggleVersion(version: number) {
  selectedVersion.value = selectedVersion.value === version ? null : version
}

async function fetchVersions() {
  loading.value = true
  error.value = null
  try {
    const data = await getVersions(memoryId.value)
    memory.value = { id: data.memory_id, title: '' }
    currentVersion.value = data.current_version
    // Reverse to show newest first
    versions.value = [...data.versions].reverse()
    
    // Set default comparison values
    if (data.versions.length >= 2) {
      const sorted = [...data.versions].sort((a, b) => b.version - a.version)
      compareFrom.value = sorted[1]?.version ?? null
      compareTo.value = sorted[0]?.version ?? null
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载版本历史失败'
    console.error('Failed to fetch versions:', e)
  } finally {
    loading.value = false
  }
}

async function fetchDiff() {
  if (!compareFrom.value || !compareTo.value) return
  try {
    diffData.value = await getVersionDiff(memoryId.value, compareFrom.value, compareTo.value)
  } catch (e) {
    showMessage('获取版本差异失败', 'error')
    console.error('Failed to fetch diff:', e)
  }
}

function confirmRollback(version: number) {
  rollbackConfirmVersion.value = version
}

async function executeRollback() {
  if (rollbackConfirmVersion.value === null) return
  
  rollingBack.value = rollbackConfirmVersion.value
  try {
    const result = await rollbackVersion(memoryId.value, rollbackConfirmVersion.value)
    showMessage(`已回滚到 v${rollbackConfirmVersion.value}`, 'success')
    rollbackConfirmVersion.value = null
    await fetchVersions()
  } catch (e) {
    showMessage('回滚失败', 'error')
    console.error('Failed to rollback:', e)
  } finally {
    rollingBack.value = null
  }
}

onMounted(() => {
  fetchVersions()
})
</script>

<style scoped>
.version-history-view {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--text);
  cursor: pointer;
  font-size: 0.9rem;
}

.back-btn:hover {
  background: var(--tag-bg);
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);
  flex: 1;
}

.version-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--card);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
}

.selector-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.version-select {
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.85rem;
}

.selector-arrow {
  color: var(--text-secondary);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state h3 {
  color: var(--error-text);
  margin-bottom: 8px;
}

.memory-info {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.memory-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.memory-info h3 {
  font-size: 1.1rem;
  color: var(--primary);
}

.current-version {
  font-size: 0.85rem;
  color: var(--accent);
  font-weight: 600;
}

.memory-meta {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.version-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.version-card.selected {
  border-color: var(--accent);
}

.version-card.current {
  border-left: 3px solid var(--accent);
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.version-header:hover {
  background: var(--tag-bg);
}

.version-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.version-num {
  font-weight: 700;
  font-size: 1rem;
  color: var(--primary);
}

.current-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  background: var(--accent);
  color: white;
  border-radius: 4px;
  margin-left: 8px;
  font-weight: 500;
}

.version-time {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.version-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: var(--tag-bg);
  border-color: var(--accent);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.rollback-btn {
  color: var(--warning-text, #d97706);
}

.version-detail {
  padding: 0 20px 16px;
  border-top: 1px solid var(--border);
}

.detail-grid {
  padding-top: 16px;
}

.detail-item {
  margin-bottom: 12px;
}

.detail-item label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
}

.detail-item span {
  font-size: 0.9rem;
  color: var(--primary);
}

.content-preview {
  font-size: 0.85rem;
  background: var(--bg);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
  margin: 0;
}

/* Diff Panel */
.diff-panel {
  margin-top: 24px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--tag-bg);
  border-bottom: 1px solid var(--border);
}

.diff-header h4 {
  font-size: 0.95rem;
  color: var(--primary);
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 1.2rem;
  cursor: pointer;
  border-radius: 4px;
}

.close-btn:hover {
  background: var(--border);
}

.diff-content {
  padding: 16px;
}

.diff-section {
  margin-bottom: 16px;
}

.diff-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.diff-change {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.diff-old {
  background: var(--error-bg, #fef2f2);
  padding: 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: pre-wrap;
  margin: 0;
  color: var(--error-text, #dc2626);
}

.diff-new {
  background: var(--success-bg, #f0fdf4);
  padding: 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: pre-wrap;
  margin: 0;
  color: var(--success-text, #16a34a);
}

.no-diff {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--card);
  border-radius: 12px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  margin-bottom: 12px;
  color: var(--primary);
}

.modal-content p {
  margin-bottom: 12px;
  color: var(--text);
}

.modal-warning {
  font-size: 0.85rem;
  color: var(--warning-text, #d97706);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

/* Message Toast */
.message-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1001;
}

.message-toast.success {
  background: var(--success-bg, #dcfce7);
  color: var(--success-text, #16a34a);
}

.message-toast.error {
  background: var(--error-bg, #fee2e2);
  color: var(--error-text, #dc2626);
}

.message-toast.info {
  background: var(--accent);
  color: white;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 400px;
}

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .version-selector {
    width: 100%;
    flex-wrap: wrap;
  }

  .version-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .version-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .diff-change {
    grid-template-columns: 1fr;
  }
}
</style>