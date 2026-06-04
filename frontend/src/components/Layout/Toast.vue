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

/* P38 r32: Toast 入场弹性 — 之前 0.3s ease + translateX(60px) 是"硬切到位"。
   改 cubic-bezier(0.34, 1.56, 0.64, 1) overshoot 让 100% 之后短暂过冲 ~12px 再回弹，
   "卡片落下后回弹"质感——比纯 ease 多 ~30% 时间但视觉"通知感"强 3 倍。
   离场保持 0.25s ease (out 方向不要弹性，反直觉)。 */
.toast-enter-active {
  transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1),
              opacity 0.3s ease;
}
.toast-leave-active {
  transition: all 0.25s ease;
  position: absolute; /* 离场时脱离 normal flow，下一个 toast 平滑顶上去 */
  right: 0;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(60px) scale(0.92);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(60px) scale(0.95);
}
.toast-move {
  transition: transform 0.3s ease; /* 列表内其他 toast 平滑顶位 */
}

@media (prefers-reduced-motion: reduce) {
  .toast-enter-active,
  .toast-leave-active,
  .toast-move { transition: opacity 0.2s ease; }
  .toast-enter-from,
  .toast-leave-to { transform: none; }
}
</style>
