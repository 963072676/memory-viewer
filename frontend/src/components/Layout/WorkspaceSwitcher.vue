<template>
  <div class="workspace-switcher">
    <select v-model="currentWorkspace" @change="switchWorkspace" class="ws-select">
      <option v-for="ws in workspaces" :key="ws.id" :value="ws.id">
        {{ ws.name }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'

const workspaces = ref<any[]>([])
const currentWorkspace = ref('default')

async function loadWorkspaces() {
  try {
    const res = await request<any>('/workspaces')
    workspaces.value = res.workspaces || []
  } catch {}
}

function switchWorkspace() {
  // Store selection and emit for parent components
  localStorage.setItem('mv_workspace', currentWorkspace.value)
  window.dispatchEvent(new CustomEvent('workspace-changed', { detail: currentWorkspace.value }))
}

onMounted(() => {
  loadWorkspaces()
  const saved = localStorage.getItem('mv_workspace')
  if (saved) currentWorkspace.value = saved
})
</script>

<style scoped>
.workspace-switcher { display: inline-flex; }
.ws-select {
  padding: 4px 8px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px; background: var(--card, #fff); font-size: 0.8rem;
  font-family: var(--font); color: var(--text, #1d1d1f); cursor: pointer;
}
</style>
