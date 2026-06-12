<template>
  <div class="export-btn-group">
    <button class="export-btn" @click="showMenu = !showMenu">
      {{ $t('i18n.export') }} ▾
    </button>
    <div v-if="showMenu" class="export-menu">
      <button @click="exportJson">JSON {{ $t('i18n.format') }}</button>
      <button @click="exportMarkdown">Markdown {{ $t('i18n.format') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { exportAgentMemory } from '@/api/agentmemory'

const props = defineProps<{
  ids?: string
}>()

const showMenu = ref(false)

function triggerDownload(url: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = ''
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  showMenu.value = false
}

function exportJson() {
  triggerDownload(exportAgentMemory('json', props.ids))
}

function exportMarkdown() {
  triggerDownload(exportAgentMemory('markdown', props.ids))
}
</script>

<style scoped>
.export-btn-group {
  position: relative;
  display: inline-block;
}

.export-btn {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s;
}

.export-btn:hover {
  background: var(--tag-bg);
}

.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
  z-index: 100;
  min-width: 140px;
}

.export-menu button {
  display: block;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.export-menu button:hover {
  background: var(--tag-bg);
}
</style>
