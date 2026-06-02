<template>
  <div class="snapshots-view">
    <div class="sv-header">
      <h2>💾 Snapshots & Disaster Recovery</h2>
      <div class="sv-actions">
        <button class="btn-verify" @click="verifyAll" :disabled="verifying">
          {{ verifying ? '⏳ Verifying...' : '🔍 Verify All' }}
        </button>
        <button class="btn-create" @click="showCreate = true">+ Create Snapshot</button>
      </div>
    </div>

    <!-- Config Summary -->
    <div class="config-bar" v-if="config">
      <span>📅 Schedule: {{ config.schedule_enabled ? 'Every ' + config.interval_hours + 'h' : 'Disabled' }}</span>
      <span>📦 Retention: {{ config.max_snapshots }} max</span>
      <button class="btn-config" @click="showConfig = true">⚙ Configure</button>
    </div>

    <!-- Snapshot List -->
    <div class="snapshot-list">
      <div v-for="snap in snapshots" :key="snap.id" class="snapshot-card" :class="snap.type">
        <div class="snap-header">
          <div class="snap-id">
            <span class="snap-type-badge" :class="snap.type">{{ snap.type }}</span>
            <span class="snap-name">{{ snap.id }}</span>
          </div>
          <span class="snap-time">{{ formatTime(snap.created_at) }}</span>
        </div>
        <div class="snap-desc" v-if="snap.description">{{ snap.description }}</div>
        <div class="snap-stats">
          <span>📝 {{ snap.memory_count }} memories</span>
          <span>📦 {{ formatSize(snap.size_bytes) }}</span>
          <span class="checksum" :class="{ valid: snap._verified }">
            {{ snap._verified !== undefined ? (snap._verified ? '✅ Valid' : '❌ Corrupted') : '🔒 ' + snap.checksum_sha256?.substring(0, 12) + '...' }}
          </span>
        </div>
        <div class="snap-actions">
          <button class="btn-sm" @click="verifyOne(snap.id)">Verify</button>
          <button class="btn-sm btn-restore" @click="confirmRestore(snap)">Restore</button>
          <button class="btn-sm btn-danger" @click="deleteSnap(snap.id)">Delete</button>
        </div>
      </div>
      <div v-if="!snapshots.length" class="empty-state">
        <p>No snapshots yet. Create one to get started.</p>
        <button class="btn-create" @click="showCreate = true">Create First Snapshot</button>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Create Snapshot</h3>
          <button class="btn-close" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Description (optional)</label>
            <input v-model="newDescription" placeholder="e.g. Before major refactoring" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showCreate = false">Cancel</button>
          <button class="btn-save" @click="createSnap" :disabled="creating">
            {{ creating ? '⏳ Creating...' : '📸 Create Snapshot' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Restore Confirmation Modal -->
    <div v-if="showRestore" class="modal-overlay" @click.self="showRestore = false">
      <div class="modal">
        <div class="modal-header">
          <h3>⚠️ Confirm Restore</h3>
          <button class="btn-close" @click="showRestore = false">✕</button>
        </div>
        <div class="modal-body">
          <p>You are about to restore from snapshot <strong>{{ restoreTarget?.id }}</strong>.</p>
          <p>This will replace all current memories with the snapshot data ({{ restoreTarget?.memory_count }} memories).</p>
          <p class="warning-text">A pre-restore backup will be created automatically.</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showRestore = false">Cancel</button>
          <button class="btn-save btn-danger-confirm" @click="doRestore" :disabled="restoring">
            {{ restoring ? '⏳ Restoring...' : '✅ Confirm Restore' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Config Modal -->
    <div v-if="showConfig" class="modal-overlay" @click.self="showConfig = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Snapshot Configuration</h3>
          <button class="btn-close" @click="showConfig = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Schedule Enabled</label>
            <select v-model="editConfig.schedule_enabled">
              <option :value="true">Enabled</option>
              <option :value="false">Disabled</option>
            </select>
          </div>
          <div class="form-group">
            <label>Interval (hours)</label>
            <input v-model.number="editConfig.interval_hours" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Max Snapshots</label>
            <input v-model.number="editConfig.max_snapshots" type="number" min="1" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showConfig = false">Cancel</button>
          <button class="btn-save" @click="saveConfig">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const snapshots = ref<any[]>([])
const config = ref<any>(null)
const showCreate = ref(false)
const showRestore = ref(false)
const showConfig = ref(false)
const restoreTarget = ref<any>(null)
const newDescription = ref('')
const creating = ref(false)
const restoring = ref(false)
const verifying = ref(false)
const editConfig = reactive({
  schedule_enabled: true,
  interval_hours: 24,
  max_snapshots: 50,
})

async function loadSnapshots() {
  try {
    const res = await request<any>('/snapshots')
    snapshots.value = res.snapshots || []
  } catch {}
}

async function loadConfig() {
  try {
    const res = await request<any>('/snapshots/config/schedule')
    config.value = res
    Object.assign(editConfig, res)
  } catch {}
}

async function createSnap() {
  creating.value = true
  try {
    await request<any>('/snapshots', {
      method: 'POST',
      body: JSON.stringify({ description: newDescription.value }),
    })
    toast.success('Snapshot created!')
    showCreate.value = false
    newDescription.value = ''
    await loadSnapshots()
  } catch {}
  creating.value = false
}

async function verifyOne(id: string) {
  try {
    const res = await request<any>(`/snapshots/${id}/verify`)
    const snap = snapshots.value.find(s => s.id === id)
    if (snap) snap._verified = res.valid
    toast.success(res.valid ? '✅ Snapshot verified' : '❌ Checksum mismatch!')
  } catch {}
}

async function verifyAll() {
  verifying.value = true
  try {
    const res = await request<any>('/snapshots/verify', { method: 'POST' })
    toast.success(`Verified: ${res.valid}/${res.total} valid`)
    await loadSnapshots()
  } catch {}
  verifying.value = false
}

function confirmRestore(snap: any) {
  restoreTarget.value = snap
  showRestore.value = true
}

async function doRestore() {
  restoring.value = true
  try {
    await request<any>(`/snapshots/${restoreTarget.value.id}/restore`, { method: 'POST' })
    toast.success('Snapshot restored successfully!')
    showRestore.value = false
    await loadSnapshots()
  } catch {}
  restoring.value = false
}

async function deleteSnap(id: string) {
  try {
    await request<any>(`/snapshots/${id}`, { method: 'DELETE' })
    toast.success('Snapshot deleted')
    await loadSnapshots()
  } catch {}
}

async function saveConfig() {
  try {
    await request<any>('/snapshots/config/schedule', {
      method: 'PUT',
      body: JSON.stringify(editConfig),
    })
    toast.success('Configuration saved')
    showConfig.value = false
    await loadConfig()
  } catch {}
}

function formatTime(ts: string): string {
  if (!ts) return ''
  try { return new Date(ts).toLocaleString() } catch { return ts }
}

function formatSize(bytes: number): string {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  loadSnapshots()
  loadConfig()
})
</script>

<style scoped>
.snapshots-view { padding-bottom: 40px; }
.sv-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.sv-header h2 { font-size: 1.5rem; font-weight: 600; margin: 0; }
.sv-actions { display: flex; gap: 8px; }
.btn-verify, .btn-create {
  padding: 8px 16px; border: none; border-radius: 8px;
  font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-verify { background: var(--tag-bg); border: 1px solid var(--border); }
.btn-create { background: var(--accent); color: #fff; }
.btn-verify:disabled, .btn-create:disabled { opacity: 0.6; }

.config-bar {
  display: flex; align-items: center; gap: 20px; padding: 12px 16px;
  background: var(--card); border: 1px solid var(--border); border-radius: 10px;
  margin-bottom: 16px; font-size: 0.85rem; color: var(--text-secondary);
}
.btn-config {
  margin-left: auto; padding: 4px 12px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--tag-bg); cursor: pointer; font-size: 0.8rem; font-family: var(--font);
}

.snapshot-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px; margin-bottom: 12px;
}
.snapshot-card.pre-restore { border-left: 4px solid #ff9500; }
.snap-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.snap-id { display: flex; align-items: center; gap: 8px; }
.snap-name { font-family: monospace; font-size: 0.85rem; }
.snap-type-badge {
  padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 600;
  text-transform: uppercase;
}
.snap-type-badge.manual { background: #e3f2fd; color: #1565c0; }
.snap-type-badge.scheduled { background: #e8f5e9; color: #2e7d32; }
.snap-type-badge.pre-restore { background: #fff3e0; color: #e65100; }
.snap-time { font-size: 0.75rem; color: var(--text-secondary); }
.snap-desc { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px; }
.snap-stats { display: flex; gap: 16px; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 10px; }
.checksum.valid { color: #34c759; }
.snap-actions { display: flex; gap: 8px; }
.btn-sm {
  padding: 4px 10px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--tag-bg); cursor: pointer; font-size: 0.75rem; font-family: var(--font);
}
.btn-restore { border-color: var(--accent); color: var(--accent); }
.btn-danger { border-color: var(--error); color: var(--error); }
.empty-state { text-align: center; padding: 40px; color: var(--text-secondary); }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal {
  background: var(--card); border-radius: 16px; width: 100%; max-width: 480px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border);
}
.modal-header h3 { margin: 0; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: 20px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px; }
.form-group input, .form-group select {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border);
  border-radius: 8px; font-size: 0.85rem; font-family: var(--font); box-sizing: border-box;
}
.warning-text { color: #ff9500; font-weight: 600; font-size: 0.85rem; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid var(--border);
}
.btn-cancel, .btn-save {
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-cancel { background: var(--card); border: 1px solid var(--border); }
.btn-save { background: var(--accent); color: #fff; border: none; }
.btn-save:disabled { opacity: 0.5; }
.btn-danger-confirm { background: #ff3b30; }
</style>
