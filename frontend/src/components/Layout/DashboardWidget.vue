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
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  /* P38 r12: 统一 hover transition 曲线 + 时长，与全站 Card 视觉同源
     (MemoryCard 0.3s, CollectionCard 0.2s — 取中位 0.25s, cubic-bezier 与 P38 调色板一致) */
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}

.dashboard-widget:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-color: var(--border-strong);
}

.widget-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  border-radius: 0;
  background: var(--bg);
  transform: none; /* 全屏态取消 hover 提升效果 */
}

.widget-fullscreen:hover {
  transform: none;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.widget-title {
  font-size: 0.85rem;
  font-weight: 600;
  /* P38 r12: var(--text) 不存在 → var(--primary)（与 MemoryCard / CollectionCard 同源） */
  color: var(--primary);
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
  color: var(--text-secondary);
  transition: background 0.15s ease, color 0.15s ease;
}

.widget-btn:hover {
  background: var(--tag-bg);
  color: var(--primary);
}

.widget-btn--remove:hover {
  /* P38 r12: pink 硬编码 #ffebee → var(--error-bg) token，与全站 danger 视觉同源
     删除硬编码 #ffebee 之后, error hover 反馈会跟随主题变量切换 (Dark 模式自动加深) */
  background: var(--error-bg);
  color: var(--error);
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
