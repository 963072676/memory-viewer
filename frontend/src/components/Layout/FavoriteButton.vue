<template>
  <button
    class="favorite-btn"
    :class="{ favorited }"
    :title="favorited ? 'Remove from favorites' : 'Add to favorites'"
    @click.stop="$emit('toggle')"
  >
    <span class="star">{{ favorited ? '★' : '☆' }}</span>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  favorited: boolean
}>()

defineEmits<{
  (e: 'toggle'): void
}>()
</script>

<style scoped>
.favorite-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s, transform 0.15s;
}

.favorite-btn:hover {
  background: var(--tag-bg);
  transform: scale(1.1);
}

.star {
  font-size: 1.2rem;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.favorite-btn.favorited .star {
  color: #f59e0b;
}
</style>
