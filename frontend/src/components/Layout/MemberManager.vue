<template>
  <div class="member-manager">
    <div class="mm-header">
      <h3>👥 Members — {{ workspace?.name }}</h3>
      <button class="btn-close" @click="$emit('close')">✕</button>
    </div>
    <div class="mm-body">
      <!-- Add Member -->
      <div class="add-member">
        <input v-model="newUserId" :placeholder="$t('en_user_id')" />
        <select v-model="newRole">
          <option value="viewer">{{ $t('en_role_viewer') }}</option>
          <option value="editor">{{ $t('en_role_editor') }}</option>
          <option value="admin">{{ $t('en_role_admin') }}</option>
        </select>
        <button class="btn-add" @click="addMember" :disabled="!newUserId">{{ $t('en_add') }}</button>
      </div>

      <!-- Member List -->
      <div class="member-list">
        <div v-for="m in members" :key="m.user_id" class="member-row">
          <span class="member-id">{{ m.user_id }}</span>
          <RoleBadge :role="m.role" />
          <select v-model="m.role" @change="updateRole(m)" class="role-select">
            <option value="viewer">{{ $t('en_role_viewer') }}</option>
            <option value="editor">{{ $t('en_role_editor') }}</option>
            <option value="admin">{{ $t('en_role_admin') }}</option>
          </select>
          <button class="btn-remove" @click="removeMember(m)">✕</button>
        </div>
        <div v-if="members.length === 0" class="empty-hint">{{ $t('en_no_members') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import RoleBadge from './RoleBadge.vue'

const props = defineProps<{ workspace: any }>()
const emit = defineEmits<{ close: [] }>()
const toast = useToast()

const members = ref<any[]>([])
const newUserId = ref('')
const newRole = ref('viewer')

async function loadMembers() {
  if (!props.workspace) return
  try {
    const res = await request<any>(`/workspaces/${props.workspace.id}/members`)
    members.value = res.members || []
  } catch {}
}

async function addMember() {
  try {
    await request<any>(`/workspaces/${props.workspace.id}/members`, {
      method: 'POST',
      body: JSON.stringify({ user_id: newUserId.value, role: newRole.value }),
    })
    toast.success('Member added')
    newUserId.value = ''
    await loadMembers()
  } catch {}
}

async function updateRole(m: any) {
  try {
    await request<any>(`/workspaces/${props.workspace.id}/members/${m.user_id}`, {
      method: 'PUT',
      body: JSON.stringify({ role: m.role }),
    })
  } catch {}
}

async function removeMember(m: any) {
  try {
    await request<any>(`/workspaces/${props.workspace.id}/members/${m.user_id}`, { method: 'DELETE' })
    toast.success('Member removed')
    await loadMembers()
  } catch {}
}

onMounted(() => loadMembers())
</script>

<style scoped>
.member-manager {
  background: var(--card, #fff); border-radius: 16px; width: 100%; max-width: 500px;
  box-shadow: var(--shadow-modal);
}
.mm-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border, #e5e5ea);
}
.mm-header h3 { margin: 0; font-size: 1rem; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.mm-body { padding: 20px; }
.add-member { display: flex; gap: 8px; margin-bottom: 16px; }
.add-member input { flex: 1; padding: 6px 10px; border: 1px solid var(--border, #e5e5ea); border-radius: 6px; font-size: 0.85rem; }
.add-member select { padding: 6px; border: 1px solid var(--border, #e5e5ea); border-radius: 6px; font-size: 0.85rem; }
.btn-add {
  padding: 6px 12px; background: var(--accent, #007aff); color: var(--card);
  border: none; border-radius: 6px; font-size: 0.85rem; cursor: pointer;
}
.btn-add:disabled { opacity: 0.5; }
.member-list { display: flex; flex-direction: column; gap: 8px; }
.member-row {
  display: flex; align-items: center; gap: 8px; padding: 8px 10px;
  background: var(--tag-bg, #f5f5f7); border-radius: 8px;
}
.member-id { flex: 1; font-size: 0.85rem; font-weight: 500; }
.role-select { padding: 4px; border: 1px solid var(--border, #e5e5ea); border-radius: 4px; font-size: 0.8rem; }
.btn-remove { background: none; border: none; color: var(--error, #ff3b30); cursor: pointer; font-size: 0.9rem; }
.empty-hint { text-align: center; color: var(--text-secondary, #86868b); font-size: 0.85rem; padding: 20px; }
</style>
