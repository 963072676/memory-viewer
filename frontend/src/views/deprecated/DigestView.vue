<template>
  <div class="digest-view">
    <div class="digest-header">
      <h2>📋 AI Memory Digest</h2>
      <div class="header-controls">
        <select v-model="digestType" class="period-select">
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="custom">Custom Range</option>
        </select>
        <input v-if="digestType === 'custom'" v-model="startDate" type="date" class="date-input" />
        <input v-if="digestType === 'custom'" v-model="endDate" type="date" class="date-input" />
        <button class="btn-generate" @click="generateDigest" :disabled="generating">
          {{ generating ? '⏳ Generating...' : '🔄 Generate Now' }}
        </button>
      </div>
    </div>

    <div class="digest-content">
      <!-- Current Digest -->
      <div class="digest-main">
        <div v-if="!currentDigest && !generating" class="empty-state">
          <div class="empty-icon">📋</div>
          <p>No digest generated yet. Click "Generate Now" to create one.</p>
        </div>
        <div v-if="generating" class="loading-state">
          <div class="spinner"></div>
          <p>Generating digest...</p>
        </div>
        <DigestCard v-if="currentDigest" :digest="currentDigest" />
      </div>

      <!-- History Sidebar -->
      <div class="digest-sidebar">
        <h3>📜 History</h3>
        <div v-if="history.length === 0" class="empty-hint">No digests yet</div>
        <DigestTimeline v-else :items="history" @select="selectDigest" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import DigestCard from '@/components/Layout/DigestCard.vue'
import DigestTimeline from '@/components/Layout/DigestTimeline.vue'

const toast = useToast()
const generating = ref(false)
const digestType = ref('daily')
const startDate = ref('')
const endDate = ref('')
const currentDigest = ref<any>(null)
const history = ref<any[]>([])

async function loadLatest() {
  try {
    const res = await request<any>('/digest/latest')
    currentDigest.value = res.digest
  } catch {}
}

async function loadHistory() {
  try {
    const res = await request<any>('/digest/history')
    history.value = res.digests || []
  } catch {}
}

async function generateDigest() {
  generating.value = true
  try {
    const body: any = { type: digestType.value }
    if (digestType.value === 'custom') {
      body.start_date = startDate.value
      body.end_date = endDate.value
    }
    const res = await request<any>('/digest/generate', {
      method: 'POST',
      body: JSON.stringify(body),
    })
    currentDigest.value = res.digest
    toast.success('Digest generated!')
    await loadHistory()
  } catch (e: any) {
    toast.error(e.message || 'Failed to generate digest')
  } finally {
    generating.value = false
  }
}

async function selectDigest(id: string) {
  try {
    const res = await request<any>(`/digest/${id}`)
    currentDigest.value = res.digest
  } catch {}
}

onMounted(() => {
  loadLatest()
  loadHistory()
})
</script>

<style scoped>
.digest-view { padding-bottom: 40px; }
.digest-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px; flex-wrap: wrap; gap: 12px;
}
.digest-header h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary, #007aff); margin: 0; }
.header-controls { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.period-select, .date-input {
  padding: 6px 10px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; background: var(--card, #fff); font-size: 0.85rem;
  font-family: var(--font); color: var(--text, #1d1d1f);
}
.btn-generate {
  padding: 8px 14px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; background: var(--accent, #007aff); color: #fff;
  font-size: 0.8rem; cursor: pointer; font-family: var(--font);
}
.btn-generate:disabled { opacity: 0.5; }
.digest-content { display: grid; grid-template-columns: 1fr 300px; gap: 24px; }
@media (max-width: 767px) { .digest-content { grid-template-columns: 1fr; } }
.digest-sidebar {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 16px; height: fit-content;
}
.digest-sidebar h3 { margin: 0 0 12px; font-size: 1rem; font-weight: 600; }
.empty-hint { text-align: center; color: var(--text-secondary, #86868b); font-size: 0.85rem; padding: 20px; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary, #86868b); }
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.loading-state { text-align: center; padding: 60px 20px; }
.spinner { width: 32px; height: 32px; border: 3px solid var(--border, #e5e5ea); border-top-color: var(--accent, #007aff); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
