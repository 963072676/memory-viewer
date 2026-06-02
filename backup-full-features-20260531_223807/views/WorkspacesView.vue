<template>
  <div class="workspaces-view">
    <div class="ws-header">
      <h2>🏢 Team Workspaces</h2>
      <button class="btn-create" @click="showCreate = true">+ New Workspace</button>
    </div>

    <!-- Create Workspace Modal -->
    <div v-if="showCreate" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3>Create Workspace</h3>
          <button class="btn-close" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Name</label>
            <input v-model="newWs.name" placeholder="Workspace name" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <input v-model="newWs.description" placeholder="Description" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showCreate = false">Cancel</button>
          <button class="btn-save" @click="createWs" :disabled="!newWs.name">Create</button>
        </div>
      </div>
    </div>

    <!-- Member Manager Modal -->
    <div v-if="showMembers" class="modal-overlay">
      <MemberManager :workspace="activeWorkspace" @close="showMembers = false" />
    </div>

    <!-- Workspace List -->
    <div class="ws-grid">
      <div v-for="ws in workspaces" :key="ws.id" class="ws-card" :class="{ default: ws.is_default }">
        <div class="ws-card-header">
          <h3>{{ ws.name }}</h3>
          <RoleBadge v-if="ws.is_default" role="admin" label="Default" />
        </div>
        <p class="ws-desc">{{ ws.description || 'No description' }}</p>
        <div class="ws-meta">
          <span>Created: {{ formatDate(ws.created_at) }}</span>
        </div>
        <div class="ws-actions">
          <button class="btn-manage" @click="openMembers(ws)">Members</button>
          <button v-if="!ws.is_default" class="btn-delete" @click="deleteWs(ws)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import RoleBadge from '@/components/Layout/RoleBadge.vue'
import MemberManager from '@/components/Layout/MemberManager.vue'

const toast = useToast()
const workspaces = ref<any[]>([])
const showCreate = ref(false)
const showMembers = ref(false)
const activeWorkspace = ref<any>(null)
const newWs = ref({ name: '', description: '' })

async function loadWorkspaces() {
  try {
    const res = await request<any>('/workspaces')
    workspaces.value = res.workspaces || []
  } catch {}
}

async function createWs() {
  try {
    await request<any>('/workspaces', {
      method: 'POST',
      body: JSON.stringify(newWs.value),
    })
    toast.success('Workspace created!')
    showCreate.value = false
    newWs.value = { name: '', description: '' }
    await loadWorkspaces()
  } catch {}
}

async function deleteWs(ws: any) {
  try {
    await request<any>(`/workspaces/${ws.id}`, { method: 'DELETE' })
    toast.success('Workspace deleted')
    await loadWorkspaces()
  } catch {}
}

function openMembers(ws: any) {
  activeWorkspace.value = ws
  showMembers.value = true
}

function formatDate(iso: string): string {
  if (!iso) return ''
  try { return new Date(iso).toLocaleDateString() } catch { return iso }
}

onMounted(() => loadWorkspaces())
</script>

<style scoped>
.workspaces-view { padding-bottom: 40px; }
.ws-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;
}
.ws-header h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary, #007aff); margin: 0; }
.btn-create {
  padding: 8px 16px; border: none; border-radius: 8px;
  background: var(--accent, #007aff); color: #fff; font-size: 0.85rem;
  cursor: pointer; font-family: var(--font);
}
.ws-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.ws-card {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 16px;
}
.ws-card.default { border-left: 4px solid var(--accent, #007aff); }
.ws-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ws-card-header h3 { margin: 0; font-size: 1rem; }
.ws-desc { font-size: 0.85rem; color: var(--text-secondary, #86868b); margin: 0 0 8px; }
.ws-meta { font-size: 0.75rem; color: var(--text-secondary, #86868b); margin-bottom: 12px; }
.ws-actions { display: flex; gap: 8px; }
.btn-manage, .btn-delete {
  padding: 6px 12px; border-radius: 6px; font-size: 0.8rem;
  cursor: pointer; font-family: var(--font);
}
.btn-manage { background: var(--tag-bg, #f5f5f7); border: 1px solid var(--border, #e5e5ea); }
.btn-delete { background: none; border: 1px solid var(--error, #ff3b30); color: var(--error, #ff3b30); }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal {
  background: var(--card, #fff); border-radius: 16px; width: 100%; max-width: 500px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border, #e5e5ea);
}
.modal-header h3 { margin: 0; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: 20px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px; }
.form-group input {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 8px; font-size: 0.85rem; font-family: var(--font); box-sizing: border-box;
}
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid var(--border, #e5e5ea);
}
.btn-cancel, .btn-save {
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-cancel { background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea); }
.btn-save { background: var(--accent, #007aff); color: #fff; border: none; }
.btn-save:disabled { opacity: 0.5; }
</style>
