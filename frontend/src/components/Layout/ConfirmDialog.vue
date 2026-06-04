<template>
  <div class="confirm-overlay" @click.self="$emit('cancel')">
    <div class="confirm-dialog">
      <div class="confirm-icon">⚠️</div>
      <h3>{{ title }}</h3>
      <p class="confirm-message">{{ message }}</p>
      <div class="confirm-actions">
        <button class="action-btn" @click="$emit('cancel')">{{ cancelText }}</button>
        <button class="action-btn action-btn--danger" @click="$emit('confirm')">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
}>()

defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-backdrop);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.confirm-dialog {
  background: var(--card);
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 400px;
  text-align: center;
}

.confirm-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 8px;
}

.confirm-message {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* P38 r23: btn-cancel / btn-confirm → .action-btn + --danger (r21 global system).
   旧的 .btn-confirm 直接填充 --error 实底, 太抢眼; r21 --danger 是 outline + 软红 bg
   (error 8% alpha), 更克制, 跟 MemoryDetailView 顶栏删除按钮同源。 */
</style>
