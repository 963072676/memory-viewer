<template>
  <div class="empty-state">
    <div class="empty-icon" aria-hidden="true">{{ icon }}</div>
    <h3 v-if="title" class="empty-title">{{ title }}</h3>
    <p class="empty-text">{{ message }}</p>
    <button v-if="actionText" class="empty-action" @click="$emit('action')">
      {{ actionText }}
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  title?: string
  message: string
  actionText?: string
}>(), {
  icon: '📭',
  title: '',
  actionText: '',
})

defineEmits<{
  action: []
}>()
</script>

<style scoped>
/* P37: Geist 风格空状态 — 居中、宽松、CTA 突出 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 24px;
  color: var(--text-secondary);
  gap: 8px;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.5;
  filter: grayscale(0.3);
  line-height: 1;
}

.empty-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

.empty-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 360px;
  margin: 0 0 16px;
}

.empty-action {
  display: inline-flex;
  align-items: center;
  padding: 9px 18px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: var(--card);
  font-size: 0.8125rem;
  font-weight: 500;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.15s ease, transform 0.1s ease;
}

.empty-action:hover {
  background: var(--primary-muted);
  transform: translateY(-1px);
}
</style>
