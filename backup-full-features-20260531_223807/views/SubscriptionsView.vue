<template>
  <div class="subscriptions-view">
    <div class="view-header">
      <h2>🔗 Webhook 订阅管理</h2>
      <button class="action-btn primary" @click="showCreate = !showCreate">
        {{ showCreate ? '取消' : '+ 新建订阅' }}
      </button>
    </div>

    <!-- Create form -->
    <transition name="expand">
      <div v-if="showCreate" class="create-form">
        <div class="form-group">
          <label>Webhook URL</label>
          <input v-model="newUrl" type="url" placeholder="https://example.com/webhook" class="form-input" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <input v-model="newDesc" type="text" placeholder="可选描述" class="form-input" />
        </div>
        <div class="form-group">
          <label>事件类型</label>
          <div class="event-checkboxes">
            <label v-for="evt in eventOptions" :key="evt" class="checkbox-label">
              <input type="checkbox" v-model="newEvents[evt]" />
              <span>{{ evt }}</span>
            </label>
          </div>
        </div>
        <button class="action-btn primary" @click="createSub" :disabled="!newUrl || creating">
          {{ creating ? '创建中...' : '创建订阅' }}
        </button>
      </div>
    </transition>

    <div v-if="loading" class="loading">加载中...</div>

    <EmptyState v-else-if="loadError" icon="⚠️" message="订阅列表加载失败" action-text="点击重试" @action="fetchSubs" />

    <div v-else-if="subscriptions.length === 0 && !loading" class="empty">暂无订阅</div>

    <div v-else class="sub-list">
      <div v-for="sub in subscriptions" :key="sub.id" class="sub-card">
        <div class="sub-info">
          <div class="sub-url">{{ sub.url }}</div>
          <div class="sub-meta">
            <span class="sub-events">{{ (sub.events || []).join(', ') }}</span>
            <span v-if="sub.description" class="sub-desc">{{ sub.description }}</span>
            <span class="sub-status" :class="{ active: sub.enabled }">{{ sub.enabled ? '启用' : '禁用' }}</span>
          </div>
        </div>
        <button class="action-btn delete-btn" @click="deleteSub(sub.id)" :disabled="deleting === sub.id">
          {{ deleting === sub.id ? '删除中...' : '删除' }}
        </button>
      </div>
    </div>

    <div v-if="message" :class="['message', message.type]">{{ message.text }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import EmptyState from '@/components/Layout/EmptyState.vue'

interface Subscription {
  id: string
  url: string
  events: string[]
  description: string
  enabled: boolean
  created_at: string
}

const eventOptions = ['create', 'update', 'delete']
const subscriptions = ref<Subscription[]>([])
const loading = ref(false)
const loadError = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const deleting = ref<string | null>(null)
const newUrl = ref('')
const newDesc = ref('')
const newEvents = reactive<Record<string, boolean>>({ create: true, update: true, delete: true })
const message = ref<{ text: string; type: string } | null>(null)

function showMessage(text: string, type: string = 'info') {
  message.value = { text, type }
  setTimeout(() => { message.value = null }, 4000)
}

async function fetchSubs() {
  loading.value = true
  loadError.value = false
  try {
    const res = await fetch('/api/webhook/subscriptions')
    const data = await res.json()
    subscriptions.value = data.subscriptions || []
  } catch (e) {
    console.error('Failed to fetch subscriptions:', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

async function createSub() {
  if (!newUrl.value) return
  creating.value = true
  try {
    const events = eventOptions.filter(e => newEvents[e])
    const res = await fetch('/api/webhook/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: newUrl.value, events, description: newDesc.value }),
    })
    const data = await res.json()
    if (data.success) {
      showMessage('订阅创建成功', 'success')
      newUrl.value = ''
      newDesc.value = ''
      showCreate.value = false
      await fetchSubs()
    } else {
      showMessage('创建失败', 'error')
    }
  } catch (e) {
    showMessage('创建失败', 'error')
  } finally {
    creating.value = false
  }
}

async function deleteSub(id: string) {
  if (!confirm('确定删除此订阅？')) return
  deleting.value = id
  try {
    const res = await fetch(`/api/webhook/subscriptions/${id}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      showMessage('订阅已删除', 'success')
      await fetchSubs()
    } else {
      showMessage('删除失败', 'error')
    }
  } catch (e) {
    showMessage('删除失败', 'error')
  } finally {
    deleting.value = null
  }
}

onMounted(() => fetchSubs())
</script>

<style scoped>
.subscriptions-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.primary { background: var(--primary); color: white; border-color: var(--primary); }
.delete-btn { font-size: 0.75rem; padding: 4px 12px; color: var(--error-text); border-color: var(--error-text); }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty { text-align: center; padding: 40px; color: var(--text-secondary); }
.create-form { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; margin-bottom: 24px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 6px; font-weight: 500; }
.form-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg); color: var(--primary); font-size: 0.85rem; font-family: var(--font); box-sizing: border-box; }
.event-checkboxes { display: flex; gap: 12px; }
.checkbox-label { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; }
.checkbox-label input[type='checkbox'] { accent-color: var(--accent); }
.sub-list { display: flex; flex-direction: column; gap: 10px; }
.sub-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; display: flex; justify-content: space-between; align-items: center; }
.sub-url { font-weight: 600; font-size: 0.9rem; color: var(--primary); word-break: break-all; }
.sub-meta { display: flex; gap: 12px; margin-top: 4px; flex-wrap: wrap; }
.sub-events { font-size: 0.75rem; color: var(--accent); }
.sub-desc { font-size: 0.75rem; color: var(--text-secondary); }
.sub-status { font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; background: var(--tag-bg); color: var(--text-secondary); }
.sub-status.active { background: var(--success-bg); color: var(--success-text); }
.message { margin-top: 16px; padding: 12px 16px; border-radius: 8px; font-size: 0.875rem; }
.message.success { background: var(--success-bg); color: var(--success-text); }
.message.error { background: var(--error-bg); color: var(--error-text); }
.expand-enter-active, .expand-leave-active { transition: all 0.25s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; }
.expand-enter-to, .expand-leave-from { opacity: 1; max-height: 400px; }

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .sub-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .sub-card .action-btn {
    width: 100%;
    text-align: center;
  }

  .event-checkboxes {
    flex-wrap: wrap;
  }
}
</style>
