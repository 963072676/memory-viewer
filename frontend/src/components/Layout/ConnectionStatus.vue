<template>
  <div class="connection-status" :class="statusClass" :title="statusText">
    <span class="status-dot"></span>
    <span class="status-text">{{ statusText }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { request } from '@/api/index'

type Status = 'connected' | 'connecting' | 'disconnected'

const status = ref<Status>('disconnected')
let timer: ReturnType<typeof setInterval> | null = null

const statusClass = computed(() => status.value)
const statusText = computed(() => {
  switch (status.value) {
    case 'connected': return 'Live'
    case 'connecting': return 'Connecting...'
    case 'disconnected': return 'Offline'
  }
})

async function checkStatus() {
  status.value = 'connecting'
  try {
    await request<any>('/realtime/status')
    // API responded = backend is alive, regardless of WS client count
    status.value = 'connected'
  } catch {
    status.value = 'disconnected'
  }
}

onMounted(() => {
  checkStatus()
  timer = setInterval(checkStatus, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.connection-status {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;
}
.connection-status.connected { background: rgba(52,199,89,0.1); }
.connection-status.connecting { background: rgba(255,149,0,0.1); }
.connection-status.disconnected { background: rgba(134,134,139,0.1); }
.status-dot {
  width: 6px; height: 6px; border-radius: 50%;
}
.connected .status-dot { background: #34c759; }
.connecting .status-dot { background: #ff9500; animation: pulse 1.5s infinite; }
.disconnected .status-dot { background: #86868b; }
.status-text { font-weight: 500; }
.connected .status-text { color: #34c759; }
.connecting .status-text { color: #ff9500; }
.disconnected .status-text { color: #86868b; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
</style>
