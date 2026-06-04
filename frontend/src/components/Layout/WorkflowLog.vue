<template>
  <div v-if="logs.length > 0" class="workflow-log">
    <div class="log-header" @click="expanded = !expanded">
      <span>{{ expanded ? '▼' : '▶' }} {{ $t('zh_b4a3fa') }} ({{ logs.length }})</span>
    </div>
    <div v-if="expanded" class="log-entries">
      <div v-for="(log, i) in logs.slice(0, 10)" :key="i" class="log-entry">
        <span class="log-time">{{ formatTime(log.timestamp) }}</span>
        <span class="log-status" :class="log.status">{{ log.status === 'success' ? '✅' : '❌' }}</span>
        <span class="log-detail">{{ log.detail || `影响 ${log.affected || 0} 条记忆` }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ logs: any[] }>()

const expanded = ref(false)

function formatTime(ts: string) {
  if (!ts) return '-'
  try {
    return new Date(ts).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}
</script>

<style scoped>
.workflow-log { margin-top: 8px; border-top: 1px solid var(--border, #eee); padding-top: 8px; }
.log-header { cursor: pointer; font-size: 12px; color: #666; user-select: none; }
.log-header:hover { color: #007aff; }
.log-entries { margin-top: 6px; }
.log-entry { display: flex; gap: 8px; align-items: center; font-size: 12px; padding: 3px 0; }
.log-time { color: #999; min-width: 100px; }
.log-detail { color: #333; }
</style>
