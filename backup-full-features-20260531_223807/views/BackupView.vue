<template>
  <div class="backup-view">
    <div class="view-header">
      <h2>💾 备份与恢复</h2>
      <button class="action-btn primary" @click="createBackup" :disabled="creating">
        {{ creating ? '创建中...' : '+ 创建备份' }}
      </button>
    </div>

    <div v-if="creating" class="loading">正在创建备份...</div>

    <EmptyState v-else-if="loadError" icon="⚠️" message="备份列表加载失败" action-text="点击重试" @action="fetchBackups" />

    <div v-else-if="backups.length === 0 && !creating" class="empty">暂无备份</div>

    <div v-else class="backup-list">
      <div v-for="(b, i) in backups" :key="i" class="backup-card">
        <div class="backup-info">
          <div class="backup-time">{{ b.created_at || b.timestamp }}</div>
          <div class="backup-files">{{ (b.files || []).join(', ') }}</div>
        </div>
        <button class="action-btn" @click="restoreBackup(b.backup_id || b.timestamp || '')" :disabled="restoring !== null">
          {{ restoring === (b.backup_id || b.timestamp || '') ? '恢复中...' : '恢复' }}
        </button>
      </div>
    </div>

    <div v-if="message" :class="['message', message.type]">{{ message.text }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import EmptyState from '@/components/Layout/EmptyState.vue'

interface Backup { backup_id?: string; timestamp?: string; created_at?: string; files?: string[] }

const backups = ref<Backup[]>([])
const creating = ref(false)
const restoring = ref<string | null>(null)
const message = ref<{ text: string; type: string } | null>(null)
const loadError = ref(false)

function showMessage(text: string, type: string = 'info') {
  message.value = { text, type }
  setTimeout(() => { message.value = null }, 4000)
}

async function fetchBackups() {
  loadError.value = false
  try {
    const res = await fetch('/api/backup/list')
    const data = await res.json()
    backups.value = data.backups || []
  } catch (e) {
    console.error('Failed to fetch backups:', e)
    loadError.value = true
  }
}

async function createBackup() {
  creating.value = true
  try {
    const res = await fetch('/api/backup/create', { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      showMessage('备份创建成功', 'success')
      await fetchBackups()
    } else {
      showMessage('备份创建失败', 'error')
    }
  } catch (e) {
    showMessage('备份创建失败', 'error')
  } finally {
    creating.value = false
  }
}

async function restoreBackup(backupId: string) {
  if (!confirm(`确定要恢复备份 ${backupId} 吗？当前数据将被覆盖。`)) return
  restoring.value = backupId
  try {
    const res = await fetch(`/api/backup/restore?backup_id=${encodeURIComponent(backupId)}`, { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      showMessage(`恢复成功: ${(data.restored_files || []).join(', ')}`, 'success')
    } else {
      showMessage('恢复失败', 'error')
    }
  } catch (e) {
    showMessage('恢复失败', 'error')
  } finally {
    restoring.value = null
  }
}

onMounted(() => fetchBackups())
</script>

<style scoped>
.backup-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.primary { background: var(--primary); color: white; border-color: var(--primary); }
.action-btn.primary:hover { opacity: 0.9; }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--text-secondary); }
.backup-list { display: flex; flex-direction: column; gap: 12px; }
.backup-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; display: flex; justify-content: space-between; align-items: center; }
.backup-time { font-weight: 600; font-size: 0.95rem; color: var(--primary); }
.backup-files { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }
.message { margin-top: 16px; padding: 12px 16px; border-radius: 8px; font-size: 0.875rem; }
.message.success { background: var(--success-bg); color: var(--success-text); }
.message.error { background: var(--error-bg); color: var(--error-text); }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .backup-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .backup-card .action-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
