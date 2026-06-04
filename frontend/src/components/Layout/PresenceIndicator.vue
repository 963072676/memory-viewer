<template>
  <div class="presence-indicator" v-if="users.length > 0">
    <div class="presence-avatars">
      <span v-for="user in displayUsers" :key="user.user_id" class="presence-dot" :title="user.user_id">
        {{ user.user_id.charAt(0).toUpperCase() }}
      </span>
      <span v-if="users.length > maxDisplay" class="presence-count">+{{ users.length - maxDisplay }}</span>
    </div>
    <span class="presence-label">{{ users.length }} online</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { request } from '@/api/index'

const users = ref<any[]>([])
const maxDisplay = 5
const displayUsers = computed(() => users.value.slice(0, maxDisplay))

let timer: ReturnType<typeof setInterval> | null = null

async function loadPresence() {
  try {
    const res = await request<any>('/realtime/status')
    // Use status data for presence
  } catch {}
}

onMounted(() => {
  loadPresence()
  timer = setInterval(loadPresence, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.presence-indicator { display: flex; align-items: center; gap: 8px; }
.presence-avatars { display: flex; gap: -4px; }
.presence-dot {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--accent, #007aff); color: var(--card); font-size: 0.65rem;
  font-weight: 700; display: flex; align-items: center; justify-content: center;
  /* P38 r33: border 保留 #fff 硬编码 — 这是 ring effect (avatar 之间的分隔环),
     需要始终是白色才有"分离"感. 仅 inner text 改为 var(--card). */
  border: 2px solid #fff; margin-left: -4px;
}
.presence-dot:first-child { margin-left: 0; }
.presence-count {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--tag-bg, #f5f5f7); font-size: 0.6rem;
  display: flex; align-items: center; justify-content: center;
  margin-left: -4px; font-weight: 600;
}
.presence-label { font-size: 0.75rem; color: var(--text-secondary, #86868b); }
</style>
