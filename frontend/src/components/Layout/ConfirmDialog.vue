<template>
  <div class="confirm-overlay" @click.self="$emit('cancel')">
    <div class="confirm-dialog">
      <div class="confirm-icon">⚠️</div>
      <h3>{{ title }}</h3>
      <p class="confirm-message">{{ message }}</p>
      <div class="confirm-actions">
        <button class="btn-cancel" @click="$emit('cancel')">{{ cancelText }}</button>
        <button class="btn-confirm" @click="$emit('confirm')">{{ confirmText }}</button>
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
  background: rgba(0, 0, 0, 0.5);
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

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.875rem;
}

.btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #e53935;
  color: white;
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-confirm:hover {
  background: #c62828;
}
</style>
