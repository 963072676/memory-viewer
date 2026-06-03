<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', `toast-${toast.type}`]"
          @click="removeToast(toast.id)"
        >
          <span class="toast-icon">{{ icon(toast.type) }}</span>
          <span class="toast-text">{{ toast.text }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'
import type { ToastType } from '@/composables/useToast'

const { toasts, removeToast } = useToast()

function icon(type: ToastType): string {
  switch (type) {
    case 'success': return '✓'
    case 'error': return '✕'
    case 'info': return 'ℹ'
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-family: var(--font);
  color: #fff;
  pointer-events: auto;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.08);
  max-width: 400px;
  word-break: break-word;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* P38 (round 7): Toast 跨主题色 token 化 — 之前 3 个 .92 alpha 硬编码 Apple 系统色。
   --toast-info 改用项目 --accent 而非 Apple #007AFF（统一品牌蓝）；
   --toast-success/--toast-error 与 --success/--error 同色源。 */
.toast-success {
  background: var(--toast-success);
}

.toast-error {
  background: var(--toast-error);
}

.toast-info {
  background: var(--toast-info);
}

.toast-icon {
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
}

.toast-text {
  line-height: 1.4;
}

/* Transition */
.toast-enter-active {
  transition: all 0.3s ease;
}
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(60px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(60px);
}
</style>
