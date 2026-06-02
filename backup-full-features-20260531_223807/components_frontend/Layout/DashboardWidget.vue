<template>
  <div class="dashboard-widget" :class="{ 'widget-fullscreen': isFullscreen }">
    <div class="widget-header">
      <h3 class="widget-title">{{ title }}</h3>
      <div class="widget-actions">
        <button class="widget-btn" title="刷新" @click="$emit('refresh')">🔄</button>
        <button class="widget-btn" title="全屏" @click="isFullscreen = !isFullscreen">
          {{ isFullscreen ? '🔲' : '⛶' }}
        </button>
        <button class="widget-btn widget-btn--remove" title="移除" @click="$emit('remove')">✕</button>
      </div>
    </div>
    <div class="widget-body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  title: string
}>()

defineEmits<{
  (e: 'refresh'): void
  (e: 'remove'): void
}>()

const isFullscreen = ref(false)
</script>

<style scoped>
.dashboard-widget {
  background: var(--card, #fff);
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s ease;
}

.dashboard-widget:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.widget-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  border-radius: 0;
  background: var(--bg, #fff);
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #e5e5ea);
  flex-shrink: 0;
}

.widget-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin: 0;
}

.widget-actions {
  display: flex;
  gap: 4px;
}

.widget-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #86868b);
  transition: background 0.15s ease;
}

.widget-btn:hover {
  background: var(--tag-bg, #f2f2f7);
}

.widget-btn--remove:hover {
  background: #ffebee;
  color: var(--error, #ff3b30);
}

.widget-body {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.widget-fullscreen .widget-body {
  padding: 24px;
}
</style>
