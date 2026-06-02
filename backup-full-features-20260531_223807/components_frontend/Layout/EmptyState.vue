<template>
  <div class="empty-state">
    <div class="empty-icon">{{ icon }}</div>
    <p class="empty-text">{{ message }}</p>
    <button v-if="actionText" class="empty-action" @click="$emit('action')">
      {{ actionText }}
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string
  message: string
  actionText?: string
}>(), {
  icon: '📭',
  actionText: '',
})

defineEmits<{
  action: []
}>()
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-text {
  font-size: 1rem;
  margin-bottom: 16px;
  line-height: 1.5;
}

.empty-action {
  display: inline-block;
  padding: 8px 20px;
  border: 1px solid var(--accent);
  border-radius: 8px;
  background: transparent;
  color: var(--accent);
  font-size: 0.875rem;
  font-family: var(--font);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.empty-action:hover {
  background: var(--accent);
  color: #fff;
}
</style>
