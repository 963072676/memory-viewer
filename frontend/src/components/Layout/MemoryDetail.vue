<template>
  <div class="memory-detail">
    <h3>{{ title }}</h3>
    <div class="detail-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<style scoped>
.memory-detail {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
}

h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--primary);
}

.detail-content {
  font-size: 0.875rem;
  line-height: 1.7;
  color: var(--primary);
}
</style>
